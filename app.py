from flask import Flask, render_template, request, redirect, url_for, flash, session, g, abort, jsonify
from jinja2 import TemplateNotFound
from markupsafe import Markup
import functools
import os
import sys
import json
import time
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from werkzeug.middleware.proxy_fix import ProxyFix

try:
    from email_service import notify_slot_booking
except Exception:
    def notify_slot_booking(*_a, **_k):
        pass

app = Flask(__name__)
# خلف Railway/Render/Nginx: ترويسات X-Forwarded-* صحيحة (HTTPS، المضيف)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

perf_logger = logging.getLogger('performance')
perf_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
perf_logger.propagate = False
_stderr = logging.StreamHandler(sys.stderr)
_stderr.setFormatter(formatter)
perf_logger.addHandler(_stderr)
_perf_log_path = os.environ.get('PERF_LOG_PATH')
if _perf_log_path:
    try:
        _fh = RotatingFileHandler(_perf_log_path, maxBytes=1_000_000, backupCount=3)
        _fh.setFormatter(formatter)
        perf_logger.addHandler(_fh)
    except (OSError, PermissionError):
        pass

# Adjust for PyInstaller --onefile mode
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    bundle_dir = sys._MEIPASS
    app.template_folder = os.path.join(bundle_dir, 'templates')
    app.static_folder = os.path.join(bundle_dir, 'static')

# Fixed secret key to keep user sessions active after restart
app.secret_key = 'PlaceGuide_Secret_Key_2026_Fixed'

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(application_path, 'db_config.json')
DEV_USERNAME = "dev"
DEV_PASSWORD = "123"

def _safe_time_str(t):
    """Return HH:MM string for template; avoids strftime on string/None."""
    if t is None: return ''
    if hasattr(t, 'strftime'): return t.strftime('%H:%M')
    return str(t)[:5] if t else ''

def _safe_date_str(d, fmt='%Y-%m-%d'):
    """Return date string for template; works for date/datetime/string."""
    if d is None: return '-'
    if hasattr(d, 'strftime'): return d.strftime(fmt)
    return str(d)[:10] if d else '-'


@app.template_filter('dmy')
def _tpl_dmy(d):
    """dd/mm/yyyy formatting for display (inputs remain type=date)."""
    if d is None:
        return '-'
    try:
        if hasattr(d, 'strftime'):
            return d.strftime('%d/%m/%Y')
        s = str(d).strip()
        if len(s) >= 10 and s[4] == '-' and s[7] == '-':
            return f"{s[8:10]}/{s[5:7]}/{s[0:4]}"
        return s[:10]
    except Exception:
        return str(d)[:10] if d else '-'


# حالات الواجب اليومي (Attendance grid) — تُخزَّن كنص في AssignmentStatus
ASSIGNMENT_STATUS_VALUES = ('Done', 'not submitted', 'cancelled', 'postponed')
ASSIGNMENT_STATUS_SET = frozenset(ASSIGNMENT_STATUS_VALUES)


def _normalize_assignment_status(raw):
    s = (raw or '').strip()
    return s if s in ASSIGNMENT_STATUS_SET else 'not submitted'


def _coerce_assignment_status_row(row):
    """قراءة آمنة من الصف: عمود نصي قديم أو AssignmentDone."""
    if not row:
        return 'not submitted'
    st = (row.get('AssignmentStatus') or '').strip()
    if st in ASSIGNMENT_STATUS_SET:
        return st
    ad = row.get('AssignmentDone')
    if ad is True or ad == 1:
        return 'Done'
    if ad is not None and str(ad).lower() in ('true', '1'):
        return 'Done'
    return 'not submitted'


def _assignment_done_bit_from_status(status_str):
    return 1 if status_str == 'Done' else 0


# --- مسار التدريب الكامل: Lead / Train to Hire / قوائم المبيعات والمختبر ---
TRAINING_LEAD_SUBTYPE_INTERESTED = 'interested'
TRAINING_LEAD_SUBTYPE_TRAIN_TO_HIRE = 'train_to_hire'

TRAINING_QUEUE_TO_BE_CLOSE = 'TO_BE_CLOSE'
TRAINING_QUEUE_ACCEPTANCE_TTH = 'ACCEPTANCE_TTH'
TRAINING_QUEUE_RETURN_SALES = 'RETURN_SALES'

TRAINING_TA_SUBSTATUS_PENDING = 'PENDING_FINAL'

TA_TRAINING_DECISION_VALUES = (
    'Accepted', 'No Show', 'Rejected', 'Resc', 'Pending', 'Redo', 'Unreachable',
)
# قرار قديم في الواجهة — يُعامل كـ Accepted لمسار «مهتم تدريب» في الإغلاق
TA_TRAINING_LEGACY_TRAINING_DECISION = 'Training'

TRAINING_CLOSING_STATUS_VALUES = (
    'Confirmed Training', 'Pending Month', 'Not Interested', 'Rejected', 'Unreachable',
    'Call Back', 'Pending', 'Reconsidering', 'Restrictions', 'GA Employee', 'Moved to Offshore',
)

_training_workflow_schema_done = False


def _ensure_training_workflow_schema():
    """أعمدة Candidates وجداول حضور الامتحان والضيوف — آمنة للتكرار."""
    global _training_workflow_schema_done
    if _training_workflow_schema_done:
        return
    alters = [
        "ALTER TABLE Candidates ADD TrainingLeadSubtype NVARCHAR(30) NULL",
        "ALTER TABLE Candidates ADD TrainToHire_Link_Degree NVARCHAR(512) NULL",
        "ALTER TABLE Candidates ADD TrainToHire_Link_AltEmail NVARCHAR(512) NULL",
        "ALTER TABLE Candidates ADD TrainToHire_Link_IdCard NVARCHAR(512) NULL",
        "ALTER TABLE Candidates ADD TrainToHire_Link_Contract NVARCHAR(512) NULL",
        "ALTER TABLE Candidates ADD UniversityCollege NVARCHAR(200) NULL",
        "ALTER TABLE Candidates ADD ResidenceArea NVARCHAR(200) NULL",
        "ALTER TABLE Candidates ADD BirthDate DATE NULL",
        "ALTER TABLE Candidates ADD TrainingSalesQueue NVARCHAR(40) NULL",
        "ALTER TABLE Candidates ADD TrainingTA_Substatus NVARCHAR(40) NULL",
        "ALTER TABLE Candidates ADD TrainingClosing_FollowUpDate DATE NULL",
        "ALTER TABLE Candidates ADD TrainingClosing_CloserUserID INT NULL",
        "ALTER TABLE Candidates ADD TrainingClosing_CloserName NVARCHAR(200) NULL",
        "ALTER TABLE Candidates ADD TrainingClosing_LanguageFeedback NVARCHAR(MAX) NULL",
        "ALTER TABLE Candidates ADD TrainingClosing_Status NVARCHAR(80) NULL",
        "ALTER TABLE Candidates ADD TrainingClosing_StatusDate DATE NULL",
        "ALTER TABLE Candidates ADD TrainingClosing_Reason NVARCHAR(MAX) NULL",
        "ALTER TABLE Candidates ADD Age INT NULL",
    ]
    for stmt in alters:
        try:
            query_db(stmt)
        except Exception:
            pass
    create_batch_presence = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='BatchExamSessionPresence' AND xtype='U')
    CREATE TABLE BatchExamSessionPresence (
        BatchID INT NOT NULL,
        SessionDate DATE NOT NULL,
        EnrollmentID INT NOT NULL,
        IsPresent BIT NOT NULL DEFAULT 1,
        UpdatedAt DATETIME DEFAULT GETDATE(),
        UpdatedBy INT NULL,
        PRIMARY KEY (BatchID, SessionDate, EnrollmentID)
    )
    """
    create_guests = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ClassSessionGuests' AND xtype='U')
    CREATE TABLE ClassSessionGuests (
        GuestID INT IDENTITY(1,1) PRIMARY KEY,
        BatchID INT NOT NULL,
        SessionDate DATE NOT NULL,
        FullName NVARCHAR(120) NOT NULL,
        Phone NVARCHAR(50) NULL,
        Email NVARCHAR(120) NULL,
        RecordedBy INT NULL,
        RecordedAt DATETIME DEFAULT GETDATE()
    )
    """
    try:
        query_db(create_batch_presence)
    except Exception:
        pass
    try:
        query_db(create_guests)
    except Exception:
        pass
    _training_workflow_schema_done = True


def _is_training_candidate_row(c):
    if not c:
        return False
    pi = (c.get('PrimaryIntent') or '').strip()
    st = (c.get('Status') or '').strip()
    return pi == 'Training' or st == 'Training_Lead'


def _candidate_has_training_exam_fee_paid(candidate_id):
    """فاتورة رسوم امتحان تحديد المستوى في InvoiceItems (نفس وصف Exam Fee)."""
    try:
        cid = int(candidate_id)
    except (TypeError, ValueError):
        return False
    try:
        row = query_db(
            """
            SELECT TOP 1 I.InvoiceID
            FROM InvoiceHeaders I
            INNER JOIN InvoiceItems II ON II.InvoiceID = I.InvoiceID
            WHERE I.CandidateID = ?
              AND (II.Description LIKE ? OR II.Description LIKE ?)
            """,
            (cid, '%' + EXAM_FEE_DESCRIPTION + '%', '%رسوم امتحان%'),
            one=True,
        )
        return bool(row and row.get('InvoiceID'))
    except Exception:
        return False


def _train_to_hire_docs_complete(c):
    if not c:
        return False
    for k in (
        'TrainToHire_Link_Degree',
        'TrainToHire_Link_AltEmail',
        'TrainToHire_Link_IdCard',
        'TrainToHire_Link_Contract',
    ):
        v = (c.get(k) or '').strip()
        if not v or not v.lower().startswith('http'):
            return False
    return True


def _candidate_training_lead_subtype(c):
    s = (c.get('TrainingLeadSubtype') or '').strip().lower()
    if s == TRAINING_LEAD_SUBTYPE_TRAIN_TO_HIRE:
        return TRAINING_LEAD_SUBTYPE_TRAIN_TO_HIRE
    return TRAINING_LEAD_SUBTYPE_INTERESTED


def _normalize_ta_training_decision(raw):
    d = (raw or '').strip()
    if d == TA_TRAINING_LEGACY_TRAINING_DECISION:
        return 'Accepted'
    if d in TA_TRAINING_DECISION_VALUES:
        return d
    if d in ('Accepted', 'Rejected'):
        return d
    return ''


def _trainer_attendance_status(enrollment_id, session_date):
    """حضور يوم الجلسة من جدول Attendance — مصدر المدرب/الكواوبريشن (شاشة التدريب Attendance)."""
    try:
        eid = int(enrollment_id)
    except (TypeError, ValueError):
        return ''
    if not session_date:
        return ''
    try:
        row = query_db(
            "SELECT Status FROM Attendance WHERE EnrollmentID = ? AND Date = CAST(? AS DATE)",
            (eid, session_date),
            one=True,
        )
        return (row.get('Status') or "").strip() if row else ""
    except Exception:
        return ""


def _trainer_attendance_allows_batch_exam(status_str):
    st = (status_str or "").strip()
    return st in ("Present", "Late")


def _trainer_attendance_blocks_batch_exam(status_str):
    st = (status_str or "").strip()
    return st in ("Absent", "Excused")


def _trainer_attendance_display(status_str):
    st = (status_str or "").strip()
    if st == "Present":
        return {"label_ar": "حاضر", "badge_classes": "bg-success", "allows_exam": True}
    if st == "Late":
        return {"label_ar": "حاضر (متأخر)", "badge_classes": "bg-warning text-dark", "allows_exam": True}
    if st == "Absent":
        return {"label_ar": "غائب", "badge_classes": "bg-danger", "allows_exam": False}
    if st == "Excused":
        return {"label_ar": "معذور", "badge_classes": "bg-secondary", "allows_exam": False}
    return {
        "label_ar": "لم يُسجَّل الحضور",
        "badge_classes": "bg-light text-dark border",
        "allows_exam": False,
    }


def _training_eval_triggers_sales_queue(evaluation_type):
    et = (evaluation_type or '').strip()
    return et in (
        'Training',
        EVAL_TRAINING_PLACEMENT,
        EVAL_TRAINING_GRADUATION,
    )


def _training_apply_post_ta_decision(candidate_id, decision, lead_subtype, evaluation_type):
    """تحديث TrainingSalesQueue / TrainingTA_Substatus بعد حفظ تقييم تدريب."""
    if not candidate_id:
        return
    try:
        cid = int(candidate_id)
    except (TypeError, ValueError):
        return
    try:
        crow = query_db(
            "SELECT PrimaryIntent, Status FROM Candidates WHERE CandidateID=?",
            (cid,),
            one=True,
        )
        if not _is_training_candidate_row(crow):
            return
    except Exception:
        return
    decision = _normalize_ta_training_decision(decision)
    lead_subtype = (lead_subtype or TRAINING_LEAD_SUBTYPE_INTERESTED).strip().lower()
    if not _training_eval_triggers_sales_queue(evaluation_type):
        return
    queue = None
    ta_sub = None
    if decision in ('Resc', 'Redo', 'Unreachable'):
        queue = TRAINING_QUEUE_RETURN_SALES
    elif decision == 'No Show':
        queue = TRAINING_QUEUE_RETURN_SALES
    elif decision == 'Pending':
        ta_sub = TRAINING_TA_SUBSTATUS_PENDING
    elif decision == 'Rejected':
        queue = None
        ta_sub = None
    elif decision == 'Accepted':
        if lead_subtype == TRAINING_LEAD_SUBTYPE_TRAIN_TO_HIRE:
            queue = TRAINING_QUEUE_ACCEPTANCE_TTH
        else:
            queue = TRAINING_QUEUE_TO_BE_CLOSE
    try:
        if decision == 'Rejected':
            query_db(
                """
                UPDATE Candidates SET TrainingSalesQueue = NULL, TrainingTA_Substatus = NULL
                WHERE CandidateID = ?
                """,
                (cid,),
            )
        else:
            query_db(
                """
                UPDATE Candidates SET TrainingSalesQueue = ?, TrainingTA_Substatus = ?
                WHERE CandidateID = ?
                """,
                (queue, ta_sub, cid),
            )
    except Exception:
        pass


def _taschedule_is_training_context(slot_row):
    if not slot_row:
        return False
    ctx = (slot_row.get('AssessmentContext') or '').strip()
    if ctx == TA_CTX_TRAINING:
        return True
    return False


def _row_user_id(row):
    if not row:
        return None
    return row.get('UserID') or row.get('userid')


def _norm_slot_time_key(t):
    """مقارنة أوقات المواعيد رغم اختلاف التخزين (10:00 مقابل 10:00:00)."""
    if t is None:
        return ''
    s = str(t).strip()
    if len(s) >= 5 and s[2] == ':':
        return s[:5]
    return s


TA_CTX_RECRUITMENT = 'Recruitment'
TA_CTX_TRAINING = 'Training'
_ta_assessment_context_column_ready = False

# فصل التوظيف/التدريب: سياق صريح في TASchedules (بعد ترحيل NULL من دور المستخدم).
# استبعاد مقيّمي التدريب من استعلامات التوظيف والعكس (حماية من أدوار خاطئة في Users_1).
_SQL_TA_T_RECRUITMENT = (
    " AND T.AssessmentContext = N'Recruitment' "
    " AND T.EvaluatorID IN (SELECT UserID FROM Users_1 "
    "      WHERE LOWER(LTRIM(RTRIM(Role))) IN (N'talent', N'talent_recruitment')) "
    " AND T.EvaluatorID NOT IN (SELECT UserID FROM Users_1 "
    "      WHERE LOWER(LTRIM(RTRIM(Role))) IN (N'talent_training', N'ta-training')) "
)
_SQL_TA_A_RECRUITMENT = (
    " AND AssessmentContext = N'Recruitment' "
    " AND EvaluatorID IN (SELECT UserID FROM Users_1 "
    "      WHERE LOWER(LTRIM(RTRIM(Role))) IN (N'talent', N'talent_recruitment')) "
    " AND EvaluatorID NOT IN (SELECT UserID FROM Users_1 "
    "      WHERE LOWER(LTRIM(RTRIM(Role))) IN (N'talent_training', N'ta-training')) "
)
_SQL_TA_T_TRAINING = (
    " AND T.AssessmentContext = N'Training' "
    " AND T.EvaluatorID IN (SELECT UserID FROM Users_1 "
    "      WHERE LOWER(LTRIM(RTRIM(Role))) IN (N'talent_training', N'ta-training')) "
    " AND T.EvaluatorID NOT IN (SELECT UserID FROM Users_1 "
    "      WHERE LOWER(LTRIM(RTRIM(Role))) IN (N'talent', N'talent_recruitment')) "
)
_SQL_TA_A_TRAINING = (
    " AND AssessmentContext = N'Training' "
    " AND EvaluatorID IN (SELECT UserID FROM Users_1 "
    "      WHERE LOWER(LTRIM(RTRIM(Role))) IN (N'talent_training', N'ta-training')) "
    " AND EvaluatorID NOT IN (SELECT UserID FROM Users_1 "
    "      WHERE LOWER(LTRIM(RTRIM(Role))) IN (N'talent', N'talent_recruitment')) "
)
# حجز الريكروتر / مبيعات التوظيف: فقط Talent_Recruitment (لا دور Talent العام) لتفادي خلط مختبري الأكاديمية.
_SQL_TA_T_RECRUITER_BOOKING = (
    " AND T.AssessmentContext = N'Recruitment' "
    " AND T.EvaluatorID IN (SELECT UserID FROM Users_1 "
    "      WHERE LOWER(LTRIM(RTRIM(Role))) = N'talent_recruitment') "
)
_SQL_TA_A_RECRUITER_BOOKING = (
    " AND AssessmentContext = N'Recruitment' "
    " AND EvaluatorID IN (SELECT UserID FROM Users_1 "
    "      WHERE LOWER(LTRIM(RTRIM(Role))) = N'talent_recruitment') "
)


def _backfill_taschedules_assessment_context_from_roles():
    """تعيين AssessmentContext للصفوف NULL حسب دور المقيّم (مرة واحدة فعّالة لكل الصفوف المتبقية)."""
    try:
        query_db(
            """
            UPDATE T SET T.AssessmentContext = N'Recruitment'
            FROM TASchedules T
            INNER JOIN Users_1 U ON U.UserID = T.EvaluatorID
            WHERE T.EvaluatorID IS NOT NULL
              AND (T.AssessmentContext IS NULL OR LTRIM(RTRIM(T.AssessmentContext)) = N'')
              AND LOWER(LTRIM(RTRIM(U.Role))) IN (N'talent', N'talent_recruitment')
            """
        )
        query_db(
            """
            UPDATE T SET T.AssessmentContext = N'Training'
            FROM TASchedules T
            INNER JOIN Users_1 U ON U.UserID = T.EvaluatorID
            WHERE T.EvaluatorID IS NOT NULL
              AND (T.AssessmentContext IS NULL OR LTRIM(RTRIM(T.AssessmentContext)) = N'')
              AND LOWER(LTRIM(RTRIM(U.Role))) IN (N'talent_training', N'ta-training')
            """
        )
    except Exception:
        pass


def _ensure_taschedules_assessment_context_column():
    global _ta_assessment_context_column_ready
    if _ta_assessment_context_column_ready:
        return
    try:
        query_db("""
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns
            WHERE Name = N'AssessmentContext' AND Object_ID = OBJECT_ID(N'TASchedules')
        )
        ALTER TABLE TASchedules ADD AssessmentContext NVARCHAR(20) NULL
        """)
    except Exception:
        pass
    _backfill_taschedules_assessment_context_from_roles()
    _ta_assessment_context_column_ready = True


def _ta_assessment_context_for_role(role):
    if (role or '').strip() in ('Talent_Training', 'TA-Training'):
        return TA_CTX_TRAINING
    return TA_CTX_RECRUITMENT


def _talent_schedule_ui_context():
    """سياق لوحة/حجز المواهب: توظيف أم تدريب. المدير يحدد عبر ?context= غير المدير يُفرض من الدور."""
    role = (session.get('role') or '').strip()
    raw = (request.args.get('context') or '').strip().lower()
    if role in ('Talent_Training', 'TA-Training'):
        return TA_CTX_TRAINING
    if role in ('Talent', 'Talent_Recruitment'):
        return TA_CTX_RECRUITMENT
    if role == 'Manager':
        if raw == 'training':
            return TA_CTX_TRAINING
        return TA_CTX_RECRUITMENT
    if raw == 'training':
        return TA_CTX_TRAINING
    return TA_CTX_RECRUITMENT


def _talent_schedule_sql_filters(ui_ctx):
    if ui_ctx == TA_CTX_TRAINING:
        return (_SQL_TA_T_TRAINING, _SQL_TA_A_TRAINING)
    return (_SQL_TA_T_RECRUITMENT, _SQL_TA_A_RECRUITMENT)


def _ta_peer_roles_for_schedule_context(ui_ctx):
    if ui_ctx == TA_CTX_TRAINING:
        return ('Talent_Training', 'TA-Training')
    return ('Talent', 'Talent_Recruitment')


def _add_self_slot_context_from_form():
    role = (session.get('role') or '').strip()
    raw = (request.form.get('talent_context') or '').strip().lower()
    if role in ('Talent_Training', 'TA-Training'):
        return TA_CTX_TRAINING
    if role in ('Talent', 'Talent_Recruitment'):
        return TA_CTX_RECRUITMENT
    if role == 'Manager':
        if raw == 'training':
            return TA_CTX_TRAINING
        return TA_CTX_RECRUITMENT
    return TA_CTX_RECRUITMENT


def _talent_redirect_query(ui_ctx):
    """للمدير فقط نمرّر context في الرابط ليبقى فرع التوظيف/التدريب."""
    if session.get('role') == 'Manager':
        return {'context': 'training' if ui_ctx == TA_CTX_TRAINING else 'recruitment'}
    return {}


def _talent_dashboard_redirect_after_slot_action(slot_row=None, date_str=None, form_talent_context=None):
    """رجوع للوحة المواهب مع الحفاظ على سياق التوظيف/التدريب للمدير."""
    d = date_str or datetime.today().strftime('%Y-%m-%d')
    kwargs = {'date': d}
    if session.get('role') == 'Manager':
        tc = (form_talent_context or '').strip().lower()
        if tc in ('recruitment', 'training'):
            kwargs['context'] = tc
        elif slot_row is not None:
            ac = (slot_row.get('AssessmentContext') or '').strip()
            kwargs['context'] = 'training' if ac == TA_CTX_TRAINING else 'recruitment'
    return redirect(url_for('talent_dashboard', **kwargs))


def _talent_book_self_redirect_from_form():
    tc = (request.form.get('talent_context') or '').strip().lower()
    extra = {}
    if session.get('role') == 'Manager' and tc in ('recruitment', 'training'):
        extra['context'] = tc
    return redirect(url_for('talent_book_self', **extra))


def _recruitment_ta_evaluator_ids():
    """مقيّمو اختبار التوظيف — فقط أدوار مختبر التوظيف (لا يُخلط مع مختبر التدريب)."""
    rows = query_db(
        """
        SELECT UserID FROM Users_1
        WHERE LOWER(LTRIM(RTRIM(Role))) IN (N'talent', N'talent_recruitment')
        """
    ) or []
    out = []
    for r in rows:
        uid = _row_user_id(r)
        if uid is not None:
            out.append(uid)
    return list(dict.fromkeys(out))


def _recruitment_ta_booking_evaluator_ids():
    """مقيّمون يظهرون في حجز الريكروتر/مبيعات التوظيف — دور Talent_Recruitment فقط (لا Talent العام)."""
    rows = query_db(
        """
        SELECT UserID FROM Users_1
        WHERE LOWER(LTRIM(RTRIM(Role))) = N'talent_recruitment'
        """
    ) or []
    out = []
    for r in rows:
        uid = _row_user_id(r)
        if uid is not None:
            out.append(uid)
    return list(dict.fromkeys(out))


def _training_ta_evaluator_ids():
    rows = query_db(
        """
        SELECT UserID FROM Users_1
        WHERE LOWER(LTRIM(RTRIM(Role))) IN (N'talent_training', N'ta-training')
        """
    ) or []
    out = []
    for r in rows:
        uid = _row_user_id(r)
        if uid is not None:
            out.append(uid)
    return list(dict.fromkeys(out))


def _recruitment_slot_times_quarters():
    """فترات 15 دقيقة للحجز — من 8 صباحاً حتى 10:45 مساءً (يشمل دوام مسائي كالأكاديمية)."""
    slot_times = []
    for hour in range(8, 23):
        for minute in (0, 15, 30, 45):
            slot_times.append(f"{hour:02d}:{minute:02d}")
    return slot_times


def _ensure_ta_slots_for_date_range(user_ids, d_start, d_end, assessment_context=TA_CTX_RECRUITMENT):
    """يملأ الأوقات الناقصة لكل (مقيّم، يوم، سياق) ضمن [d_start, d_end] شاملين."""
    if not user_ids or d_end < d_start:
        return
    _ensure_taschedules_assessment_context_column()
    slot_times = _recruitment_slot_times_quarters()
    start_s = d_start.strftime('%Y-%m-%d')
    end_s = d_end.strftime('%Y-%m-%d')
    num_days = (d_end - d_start).days + 1
    db = get_db()
    if not db:
        return
    cur = db.cursor()
    ctx = assessment_context if assessment_context in (TA_CTX_RECRUITMENT, TA_CTX_TRAINING) else TA_CTX_RECRUITMENT
    insert_sql = (
        "INSERT INTO TASchedules (SlotDate, SlotTime, Status, EvaluatorID, AssessmentContext) VALUES (?, ?, ?, ?, ?)"
    )
    ctx_sql = (
        "(AssessmentContext = N'Recruitment')"
        if ctx == TA_CTX_RECRUITMENT
        else "(AssessmentContext = N'Training')"
    )
    try:
        if getattr(cur, "fast_executemany", None) is not None:
            try:
                cur.fast_executemany = True
            except Exception:
                pass
        for uid in user_ids:
            cur.execute(
                f"""
                SELECT CAST(SlotDate AS DATE) AS D, SlotTime
                FROM TASchedules
                WHERE EvaluatorID = ?
                  AND CAST(SlotDate AS DATE) >= CAST(? AS DATE)
                  AND CAST(SlotDate AS DATE) <= CAST(? AS DATE)
                  AND ({ctx_sql})
                """,
                (uid, start_s, end_s),
            )
            by_date = {}
            for r in cur.fetchall() or []:
                dkey = r[0]
                if hasattr(dkey, 'strftime'):
                    dkey = dkey.strftime('%Y-%m-%d')
                else:
                    dkey = str(dkey)[:10]
                by_date.setdefault(dkey, set()).add(_norm_slot_time_key(r[1]))
            for i in range(num_days):
                day = d_start + timedelta(days=i)
                slot_date = day.strftime('%Y-%m-%d')
                taken = by_date.get(slot_date, set())
                missing = []
                for st in slot_times:
                    if _norm_slot_time_key(st) not in taken:
                        missing.append((slot_date, st, 'Available', uid, ctx))
                if missing:
                    cur.executemany(insert_sql, missing)
        db.commit()
    except Exception as ex:
        try:
            app.logger.exception('ensure TA slots for range failed: %s', ex)
        except Exception:
            pass
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        try:
            cur.close()
        except Exception:
            pass


def _ensure_taschedules_for_recruitment_evaluators(user_ids, days=14):
    """توليد تلقائي للأيام القادمة (مختبر التوظيف فقط)."""
    if not user_ids:
        return
    today = datetime.today().date()
    end = today + timedelta(days=days - 1)
    _ensure_ta_slots_for_date_range(user_ids, today, end, TA_CTX_RECRUITMENT)


def _users_for_recruitment_talent_slot_picker():
    """قائمة فتح شبكة التوظيف — Talent_Recruitment فقط (نفس من يظهر في حجز الريكروتر)."""
    return query_db(
        """
        SELECT UserID, Username, FullName, Role
        FROM Users_1
        WHERE LOWER(LTRIM(RTRIM(Role))) = N'talent_recruitment'
        ORDER BY FullName, Username
        """
    ) or []


def _users_for_training_talent_slot_picker():
    """من يُولَّد لهم مواعيد التدريب: مختبرو مواهب التدريب فقط (لا مدرب/منسّق/مدير في القائمة)."""
    return query_db(
        """
        SELECT UserID, Username, FullName, Role
        FROM Users_1
        WHERE LOWER(LTRIM(RTRIM(Role))) IN (N'talent_training', N'ta-training')
        ORDER BY Role, FullName, Username
        """
    ) or []


@app.route('/version')
def show_version():
    return "V1.0 - Stable", 200

# --- Decorators ---
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

def role_required(roles):
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            role = (g.user or {}).get('Role')
            if role not in roles:
                flash('Access Denied', 'danger')
                return redirect(url_for('dashboard'))
            return view(**kwargs)
        return wrapped_view
    return decorator

# --- Database Helpers ---
def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"server": ".", "port": "1433", "database": "Place2026DB", "username": "sa", "password": ""}
    try:
        with open(CONFIG_FILE, 'r') as f: return json.load(f)
    except: return {}

def save_config_file(form_data):
    config = {
        "server": form_data.get('server'),
        "port": form_data.get('port'),
        "database": form_data.get('database'),
        "username": form_data.get('username'),
        "password": form_data.get('password'),
        "use_trusted": True if form_data.get('use_trusted') else False
    }
    try:
        with open(CONFIG_FILE, 'w') as f: json.dump(config, f, indent=4)
        return True
    except: return False

def get_db_connection_string():
    config = load_config()
    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    
    if config.get("use_trusted"):
        return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes;Connect Timeout=60;'
    else:
        username = config.get("username", "")
        password = config.get("password", "")
        return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password};Connect Timeout=15;'

def get_db():
    if 'db' not in g:
        try:
            # Added Connection Timeout for faster failure on bad networks
            import pyodbc
            g.db = pyodbc.connect(get_db_connection_string(), timeout=5)
        except ImportError as e:
            g.db_error = str(e)
            g.db = None
        except Exception as e:
            g.db_error = str(e)
            g.db = None
    return g.db

# --- RBAC Helper (Strict Role Enforcement) ---
def check_role_access(required_roles):
    if g.user is None: return False
    # If user is Admin/Manager, they access everything (Superuser)
    if g.user['Role'] in ['Manager', 'Admin']: return True
    # Otherwise check specific role
    return g.user['Role'] in required_roles

# Register for Jinja templates
app.jinja_env.globals.update(check_role_access=check_role_access, safe_date_str=_safe_date_str)

def is_accountant_sidebar():
    """إسلام أو المحاسب: يرى المالية فقط — بدون Marketing/Sales/Account Mgmt/Allocation/Recruitment/Training/Talent/Admin"""
    if g.user is None: return False
    if g.user.get('Role') == 'Finance': return True
    if (g.user.get('Username') or '').strip().lower() == 'islam': return True
    return False
app.jinja_env.globals.update(is_accountant_sidebar=is_accountant_sidebar)

# --- Finance & Blocking Logic Helpers ---
def get_student_balance(candidate_id, batch_id):
    # Calculate Total Fee vs Total Paid
    enrollment = query_db('SELECT AgreedPrice FROM Enrollments WHERE CandidateID=? AND BatchID=?', (candidate_id, batch_id), one=True)
    if not enrollment: return 0
    total_fee = enrollment['AgreedPrice'] or 0
    
    paid = query_db('SELECT SUM(Amount) as TotalPaid FROM StudentPayments WHERE CandidateID=? AND BatchID=?', (candidate_id, batch_id), one=True)
    total_paid = paid['TotalPaid'] or 0
    
    return total_fee - total_paid

def is_exam_blocked(candidate_id, batch_id):
    balance = get_student_balance(candidate_id, batch_id)
    # Block if balance > 0 (Strict Policy) - Can be adjusted to allow small debt
    return balance > 0

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None: db.close()

def ensure_training_users():
    """إنشاء مستخدمي التدريب (منسق، مدرب، إلخ) إن لم يكونوا موجودين — مفيد بعد النشر."""
    training_users = [
        ('train_mgr', '123', 'TrainingManager', 'مدير التدريب'),
        ('train_head', '123', 'TrainingHead', 'رئيس قسم التدريب'),
        ('train_lead', '123', 'TrainingLead', 'قائد التدريب'),
        ('train_coord', '123', 'TrainingCoordinator', 'منسق التدريب'),
        ('train_sales', '123', 'TrainingSales', 'مبيعات التدريب'),
        ('salma', '123', 'TrainingSalesCoordinator', 'سلمى'),
        ('ta_train', '123', 'Talent_Training', 'مختبر مواهب التدريب'),
        ('trainer1', '123', 'Trainer', 'مدرب'),
    ]
    for u in training_users:
        try:
            existing = query_db('SELECT UserID FROM Users_1 WHERE Username = ?', (u[0],), one=True)
            if not existing:
                query_db("INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES (?,?,?,?)", u)
        except Exception:
            pass

def query_db(query, args=(), one=False):
    db = get_db()
    if db is None: return None
    cursor = db.cursor()
    try:
        cursor.execute(query, args)
        if cursor.description:
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return (results[0] if results else None) if one else results
        else:
            db.commit()
            cursor.close()
            return None
    except Exception as e:
        cursor.close()
        raise e


def _db_has_column(table_name: str, column_name: str) -> bool:
    """Check column existence safely (SQL Server)."""
    try:
        row = query_db(
            """
            SELECT 1 AS ok
            FROM sys.columns
            WHERE Object_ID = Object_ID(?) AND Name = ?
            """,
            (table_name, column_name),
            one=True,
        )
        return bool(row)
    except Exception:
        return False

# --- PERFORMANCE: طابع زمني واحد + مستخدم من الجلسة (تخزين مؤقت) ---
_USER_CACHE_TTL = int(os.environ.get('SESSION_USER_CACHE_TTL', '120'))

@app.before_request
def _before_request_perf_and_user():
    g._perf_start = time.time()
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        cache = session.get('_user_cache')
        if cache and cache.get('id') == user_id and (time.time() - cache.get('t', 0)) < _USER_CACHE_TTL:
            g.user = cache.get('user')
        else:
            try:
                g.user = query_db(
                    'SELECT UserID, Username, Role, FullName FROM Users_1 WHERE UserID = ?',
                    (user_id,),
                    one=True,
                )
                if g.user:
                    session['_user_cache'] = {'id': user_id, 'user': g.user, 't': time.time()}
            except Exception:
                g.user = None
    try:
        _ensure_training_workflow_schema()
    except Exception:
        pass

@app.after_request
def _after_request_perf_log(response):
    if hasattr(g, '_perf_start'):
        duration = time.time() - g._perf_start
        try:
            user_info = f"User:{session.get('user_id', 'Guest')}"
            perf_logger.info(
                f"{user_info} | Endpoint: {request.endpoint} | Method: {request.method} | "
                f"Status: {response.status_code} | Duration: {duration:.4f}s"
            )
            response.headers.add('Server-Timing', f'app;dur={duration*1000}')
        except Exception:
            pass
        if os.environ.get('FLASK_PERF_PRINT') == '1':
            print(f"⏱️ [PERF] {request.method} {request.path} -> {duration:.3f}s", file=sys.stderr)
    return response

# --- Initialization Logic ---
def init_system():
    """Initializes Tables and Users on Startup"""
    db = get_db()
    if db is None: return []
    cursor = db.cursor()
    created_tables = []
    try:
        # 1. Users Table (RENAMED TO Users_1)
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users_1' AND xtype='U')
            CREATE TABLE Users_1 (
                UserID INT IDENTITY(1,1) PRIMARY KEY,
                Username NVARCHAR(50) UNIQUE NOT NULL,
                Password NVARCHAR(255) NOT NULL,
                Role NVARCHAR(50) NOT NULL,
                FullName NVARCHAR(100),
                Email NVARCHAR(100),
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        created_tables.append("Users_1 (المستخدمين)")
        
        # 2. Clients
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Clients' AND xtype='U')
            CREATE TABLE Clients (
                ClientID INT IDENTITY(1,1) PRIMARY KEY,
                CompanyName NVARCHAR(100) NOT NULL,
                Industry NVARCHAR(100),
                ContactPerson NVARCHAR(100),
                Email NVARCHAR(100),
                Phone NVARCHAR(50),
                Address NVARCHAR(200),
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        created_tables.append("Clients (العملاء)")
        
        # 3. ClientRequests
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ClientRequests' AND xtype='U')
            CREATE TABLE ClientRequests (
                RequestID INT IDENTITY(1,1) PRIMARY KEY,
                ClientID INT FOREIGN KEY REFERENCES Clients(ClientID),
                JobTitle NVARCHAR(100) NOT NULL,
                NeededCount INT DEFAULT 1,
                Status NVARCHAR(50) DEFAULT 'Open',
                Gender NVARCHAR(20),
                Location NVARCHAR(100),
                AgeFrom INT, AgeTo INT,
                SalaryFrom DECIMAL(18,2), SalaryTo DECIMAL(18,2),
                Benefits NVARCHAR(MAX),
                EnglishLevel NVARCHAR(50),
                ThirdLanguage NVARCHAR(50),
                ComputerLevel NVARCHAR(50),
                Requirements NVARCHAR(MAX),
                SoftSkills NVARCHAR(MAX),
                Smoker NVARCHAR(20),
                AppearanceLevel NVARCHAR(50),
                PhysicalTraits NVARCHAR(MAX),
                CreatedAt DATETIME DEFAULT GETDATE(),
                -- Added Fields for Professional Request
                Nationality NVARCHAR(50),
                ShiftType NVARCHAR(50), -- Rotational, Fixed
                WorkingConditions NVARCHAR(MAX),
                EducationLevel NVARCHAR(100),
                ExperienceYears INT
            )
        """)

        # --- MIGRATION: ADD MISSING COLUMNS TO EXISTING TABLE ---
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'Nationality' AND Object_ID = Object_ID(N'ClientRequests'))
                ALTER TABLE ClientRequests ADD Nationality NVARCHAR(50);
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'AgeFrom' AND Object_ID = Object_ID(N'ClientRequests'))
                ALTER TABLE ClientRequests ADD AgeFrom INT;
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'AgeTo' AND Object_ID = Object_ID(N'ClientRequests'))
                ALTER TABLE ClientRequests ADD AgeTo INT;
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'ShiftType' AND Object_ID = Object_ID(N'ClientRequests'))
                ALTER TABLE ClientRequests ADD ShiftType NVARCHAR(50);
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'WorkingConditions' AND Object_ID = Object_ID(N'ClientRequests'))
                ALTER TABLE ClientRequests ADD WorkingConditions NVARCHAR(MAX);
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'EducationLevel' AND Object_ID = Object_ID(N'ClientRequests'))
                ALTER TABLE ClientRequests ADD EducationLevel NVARCHAR(100);
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'ExperienceYears' AND Object_ID = Object_ID(N'ClientRequests'))
                ALTER TABLE ClientRequests ADD ExperienceYears INT;
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'ThirdLanguage' AND Object_ID = Object_ID(N'ClientRequests'))
                ALTER TABLE ClientRequests ADD ThirdLanguage NVARCHAR(50);
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'ComputerLevel' AND Object_ID = Object_ID(N'ClientRequests'))
                ALTER TABLE ClientRequests ADD ComputerLevel NVARCHAR(50);
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'SoftSkills' AND Object_ID = Object_ID(N'ClientRequests'))
                ALTER TABLE ClientRequests ADD SoftSkills NVARCHAR(MAX);
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'Smoker' AND Object_ID = Object_ID(N'ClientRequests'))
                ALTER TABLE ClientRequests ADD Smoker NVARCHAR(20);
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'AppearanceLevel' AND Object_ID = Object_ID(N'ClientRequests'))
                ALTER TABLE ClientRequests ADD AppearanceLevel NVARCHAR(50);
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'PhysicalTraits' AND Object_ID = Object_ID(N'ClientRequests'))
                ALTER TABLE ClientRequests ADD PhysicalTraits NVARCHAR(MAX);
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'AllocatorRole' AND Object_ID = Object_ID(N'ClientRequests'))
                ALTER TABLE ClientRequests ADD AllocatorRole NVARCHAR(500);
        """)
        cursor.execute("""
            IF EXISTS (SELECT 1 FROM sys.columns WHERE Name = N'AllocatorRole' AND Object_ID = Object_ID(N'ClientRequests'))
            ALTER TABLE ClientRequests ALTER COLUMN AllocatorRole NVARCHAR(500);
        """)
        cursor.execute("""
            IF EXISTS (SELECT * FROM sysobjects WHERE name='Candidates' AND xtype='U')
            AND NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'RecruiterFeedback' AND Object_ID = Object_ID(N'Candidates'))
                ALTER TABLE Candidates ADD RecruiterFeedback NVARCHAR(MAX);
        """)
        cursor.execute("""
            IF EXISTS (SELECT * FROM sysobjects WHERE name='Candidates' AND xtype='U')
            AND NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'RecruiterFeedbackBy' AND Object_ID = Object_ID(N'Candidates'))
                ALTER TABLE Candidates ADD RecruiterFeedbackBy INT NULL;
        """)
        cursor.execute("""
            IF EXISTS (SELECT * FROM sysobjects WHERE name='Candidates' AND xtype='U')
            AND NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'RecruiterFeedbackDate' AND Object_ID = Object_ID(N'Candidates'))
                ALTER TABLE Candidates ADD RecruiterFeedbackDate DATETIME NULL;
        """)
        cursor.execute("""
            IF EXISTS (SELECT * FROM sysobjects WHERE name='Candidates' AND xtype='U')
            AND NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'IsReferredToTraining' AND Object_ID = Object_ID(N'Candidates'))
                ALTER TABLE Candidates ADD IsReferredToTraining BIT DEFAULT 0;
        """)
        cursor.execute("""
            IF EXISTS (SELECT * FROM sysobjects WHERE name='Candidates' AND xtype='U')
            AND NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'EmploymentStatus' AND Object_ID = Object_ID(N'Candidates'))
                ALTER TABLE Candidates ADD EmploymentStatus NVARCHAR(50) NULL;
        """)
        
        # Explicitly Commit Schema Changes
        cursor.commit()

        created_tables.append("ClientRequests (طلبات التوظيف)")

        # 4. Campaigns
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Campaigns' AND xtype='U')
            CREATE TABLE Campaigns (
                CampaignID INT IDENTITY(1,1) PRIMARY KEY,
                Name NVARCHAR(100) NOT NULL,
                Type NVARCHAR(50),
                RequestID INT NULL,
                MediaChannel NVARCHAR(50),
                AdText NVARCHAR(MAX),
                Budget DECIMAL(18, 2),
                StartDate DATE,
                EndDate DATE,
                Status NVARCHAR(50) DEFAULT 'Active',
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        created_tables.append("Campaigns (الحملات)")

        # 5. Candidates
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Candidates' AND xtype='U')
            CREATE TABLE Candidates (
                CandidateID INT IDENTITY(1,1) PRIMARY KEY,
                FullName NVARCHAR(100) NOT NULL,
                Email NVARCHAR(100),
                Phone NVARCHAR(50),
                Status NVARCHAR(50) DEFAULT 'New',
                CampaignID INT NULL,
                InterestLevel NVARCHAR(50),
                NextFollowUpDate DATE,
                Feedback NVARCHAR(MAX),
                CVPath NVARCHAR(200),
                SoftSkills NVARCHAR(MAX),
                EnglishLevel NVARCHAR(50),
                IsReadyForMatching BIT DEFAULT 0,
                CreatedAt DATETIME DEFAULT GETDATE(),
                
                -- Extended Fields
                Nationality NVARCHAR(50),
                GraduationStatus NVARCHAR(50),
                SourceChannel NVARCHAR(50),
                SalesAgentID INT,
                PrimaryIntent NVARCHAR(50),
                CurrentCEFR NVARCHAR(10),
                WorkStatus NVARCHAR(50),
                Venue NVARCHAR(50),
                PlacementReason NVARCHAR(50),
                MarketingAssessment NVARCHAR(MAX),
                PreviousApplicationDate DATE,
                AvailabilityStatus NVARCHAR(50)
            )
        """)
        created_tables.append("Candidates (المرشحين)")

        # 6. Matches
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Matches' AND xtype='U')
            CREATE TABLE Matches (
                MatchID INT IDENTITY(1,1) PRIMARY KEY,
                CandidateID INT FOREIGN KEY REFERENCES Candidates(CandidateID),
                RequestID INT FOREIGN KEY REFERENCES ClientRequests(RequestID),
                MatchDate DATETIME DEFAULT GETDATE(),
                Status NVARCHAR(50) DEFAULT 'Proposed'
            )
        """)
        created_tables.append("Matches (الترشيحات)")

        # 8. Detailed Attendance (Time-Grid)
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'CheckInTime' AND Object_ID = Object_ID(N'Attendance'))
            BEGIN
                ALTER TABLE Attendance ADD CheckInTime TIME;
                ALTER TABLE Attendance ADD CheckOutTime TIME;
                ALTER TABLE Attendance ADD TotalHours DECIMAL(5, 2);
                ALTER TABLE Attendance ADD AssignmentDone BIT DEFAULT 0;
            END
        """)
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'LateMinutes' AND Object_ID = Object_ID(N'Attendance'))
                ALTER TABLE Attendance ADD LateMinutes INT NULL;
        """)

        # 7. Training Tables
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Trainers' AND xtype='U')
            CREATE TABLE Trainers (
                TrainerID INT IDENTITY(1,1) PRIMARY KEY,
                FullName NVARCHAR(100) NOT NULL,
                Specialization NVARCHAR(100),
                Phone NVARCHAR(50),
                Email NVARCHAR(100),
                HourlyRate DECIMAL(18, 2) DEFAULT 0
            )
        """)
        created_tables.append("Trainers (المدربين)")
        
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Classrooms' AND xtype='U')
            CREATE TABLE Classrooms (
                RoomID INT IDENTITY(1,1) PRIMARY KEY,
                RoomName NVARCHAR(50) NOT NULL,
                Capacity INT DEFAULT 20,
                IsActive BIT DEFAULT 1
            )
        """)
        created_tables.append("Classrooms (القاعات)")
        
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Courses' AND xtype='U')
            CREATE TABLE Courses (
                CourseID INT IDENTITY(1,1) PRIMARY KEY,
                CourseName NVARCHAR(100) NOT NULL,
                LevelOrder INT DEFAULT 1,
                DefaultPrice DECIMAL(18, 2),
                Description NVARCHAR(MAX)
            )
        """)
        created_tables.append("Courses (الدورات)")
        
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='CourseBatches' AND xtype='U')
            CREATE TABLE CourseBatches (
                BatchID INT IDENTITY(1,1) PRIMARY KEY,
                CourseID INT FOREIGN KEY REFERENCES Courses(CourseID),
                TrainerID INT FOREIGN KEY REFERENCES Trainers(TrainerID),
                RoomID INT FOREIGN KEY REFERENCES Classrooms(RoomID),
                BatchName NVARCHAR(100),
                StartDate DATE,
                EndDate DATE,
                ScheduleDescription NVARCHAR(200),
                Status NVARCHAR(50) DEFAULT 'Planned',
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        created_tables.append("CourseBatches (المجموعات)")

        # 7b. Batch schedule columns + أيام الامتحانات الدورية
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.columns WHERE Name = N'StartTime' AND Object_ID = Object_ID(N'CourseBatches'))
            BEGIN
                ALTER TABLE CourseBatches ADD StartTime TIME NULL;
                ALTER TABLE CourseBatches ADD EndTime TIME NULL;
                ALTER TABLE CourseBatches ADD WeekDays NVARCHAR(100) NULL;
            END
        """)
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='BatchExamDates' AND xtype='U')
            CREATE TABLE BatchExamDates (
                ExamDateID INT IDENTITY(1,1) PRIMARY KEY,
                BatchID INT NOT NULL FOREIGN KEY REFERENCES CourseBatches(BatchID),
                ExamDate DATE NOT NULL,
                ExamLabel NVARCHAR(100),
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Enrollments' AND xtype='U')
            CREATE TABLE Enrollments (
                EnrollmentID INT IDENTITY(1,1) PRIMARY KEY,
                BatchID INT FOREIGN KEY REFERENCES CourseBatches(BatchID),
                CandidateID INT FOREIGN KEY REFERENCES Candidates(CandidateID),
                EnrollmentDate DATETIME DEFAULT GETDATE(),
                Status NVARCHAR(50) DEFAULT 'Active',
                FinalGrade DECIMAL(5, 2),
                Notes NVARCHAR(MAX),
                AgreedPrice DECIMAL(18, 2) DEFAULT 0
            )
        """)
        created_tables.append("Enrollments (التسجيلات)")
        
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='StudentPayments' AND xtype='U')
            CREATE TABLE StudentPayments (
                PaymentID INT IDENTITY(1,1) PRIMARY KEY,
                EnrollmentID INT FOREIGN KEY REFERENCES Enrollments(EnrollmentID),
                Amount DECIMAL(18, 2) NOT NULL,
                PaymentDate DATETIME DEFAULT GETDATE(),
                ReceivedBy INT, 
                Notes NVARCHAR(200)
            )
        """)
        created_tables.append("StudentPayments (مدفوعات الطلاب)")
        
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Attendance' AND xtype='U')
            CREATE TABLE Attendance (
                AttendanceID INT IDENTITY(1,1) PRIMARY KEY,
                EnrollmentID INT FOREIGN KEY REFERENCES Enrollments(EnrollmentID),
                Date DATE NOT NULL,
                Status NVARCHAR(50),
                RecordedBy INT,
                RecordedAt DATETIME DEFAULT GETDATE()
            )
        """)
        created_tables.append("Attendance (الغياب)")

        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TrainerDailyNotes' AND xtype='U')
            CREATE TABLE TrainerDailyNotes (
                NoteID INT IDENTITY(1,1) PRIMARY KEY,
                CandidateID INT NOT NULL,
                EnrollmentID INT NOT NULL,
                NoteDate DATE NOT NULL,
                Notes NVARCHAR(MAX) NOT NULL,
                TrainerID INT NULL,
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        created_tables.append("TrainerDailyNotes (ملاحظات المدرب اليومية)")

        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PlacementTests' AND xtype='U')
            CREATE TABLE PlacementTests (
                TestID INT IDENTITY(1,1) PRIMARY KEY,
                CandidateID INT FOREIGN KEY REFERENCES Candidates(CandidateID),
                TestDate DATETIME DEFAULT GETDATE(),
                PaymentStatus NVARCHAR(50) DEFAULT 'Pending', -- Pending, Paid
                TestStatus NVARCHAR(50) DEFAULT 'Scheduled', -- Scheduled, Completed
                ResultLevel NVARCHAR(50),
                AssessorID INT,
                Notes NVARCHAR(MAX),
                Fee DECIMAL(18, 2) DEFAULT 0
            )
        """)
        created_tables.append("PlacementTests (اختبارات تحديد المستوى)")

        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TrainingOffers' AND xtype='U')
            CREATE TABLE TrainingOffers (
                OfferID INT IDENTITY(1,1) PRIMARY KEY,
                CandidateID INT FOREIGN KEY REFERENCES Candidates(CandidateID),
                CourseID INT FOREIGN KEY REFERENCES Courses(CourseID),
                ProposedLevel NVARCHAR(50),
                Fee DECIMAL(18, 2),
                Status NVARCHAR(50) DEFAULT 'Pending', -- Pending, Accepted, Declined
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        created_tables.append("TrainingOffers (عروض التدريب)")

        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='CareerReadiness' AND xtype='U')
            CREATE TABLE CareerReadiness (
                EvaluationID INT IDENTITY(1,1) PRIMARY KEY,
                CandidateID INT FOREIGN KEY REFERENCES Candidates(CandidateID),
                EvaluationDate DATETIME DEFAULT GETDATE(),
                Status NVARCHAR(50), -- Eligible, Not Eligible, Deferred
                Notes NVARCHAR(MAX),
                EvaluatorID INT
            )
        """)
        created_tables.append("CareerReadiness (جاهزية التوظيف)")

        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='WeeklyExams' AND xtype='U')
            CREATE TABLE WeeklyExams (
                ExamResultID INT IDENTITY(1,1) PRIMARY KEY,
                EnrollmentID INT FOREIGN KEY REFERENCES Enrollments(EnrollmentID),
                WeekNumber INT NOT NULL, 
                Score DECIMAL(5, 2),
                MaxScore DECIMAL(5, 2) DEFAULT 100,
                ExamDate DATE
            )
        """)
        created_tables.append("WeeklyExams (الامتحانات)")

        # 8. General Sales
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='GeneralSales' AND xtype='U')
            CREATE TABLE GeneralSales (
                SaleID INT IDENTITY(1,1) PRIMARY KEY,
                ServiceName NVARCHAR(200) NOT NULL,
                Amount DECIMAL(18, 2) NOT NULL,
                PaymentMethod NVARCHAR(50),
                ClientName NVARCHAR(100),
                Notes NVARCHAR(MAX),
                CreatedBy INT,
                CandidateID INT NULL,
                SaleDate DATETIME DEFAULT GETDATE()
            )
        """)
        created_tables.append("GeneralSales (المبيعات)")

        # 9. Corporate Finance
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='CorporateInvoices' AND xtype='U')
            CREATE TABLE CorporateInvoices (
                InvoiceID INT IDENTITY(1,1) PRIMARY KEY,
                ClientID INT FOREIGN KEY REFERENCES Clients(ClientID),
                ServiceType NVARCHAR(100),
                Description NVARCHAR(MAX),
                Amount DECIMAL(18, 2) NOT NULL,
                IssueDate DATETIME DEFAULT GETDATE(),
                DueDate DATE,
                Status NVARCHAR(50) DEFAULT 'Unpaid',
                CreatedBy INT
            )
        """)
        created_tables.append("CorporateInvoices (فواتير الشركات)")
        
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='CorporatePayments' AND xtype='U')
            CREATE TABLE CorporatePayments (
                PaymentID INT IDENTITY(1,1) PRIMARY KEY,
                InvoiceID INT FOREIGN KEY REFERENCES CorporateInvoices(InvoiceID),
                Amount DECIMAL(18, 2) NOT NULL,
                PaymentDate DATETIME DEFAULT GETDATE(),
                PaymentMethod NVARCHAR(50),
                ReferenceNumber NVARCHAR(100),
                ReceivedBy INT
            )
        """)
        created_tables.append("CorporatePayments (مدفوعات الشركات)")
        
        # 10. Services (New Table)
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Services' AND xtype='U')
            CREATE TABLE Services (
                ServiceID INT IDENTITY(1,1) PRIMARY KEY,
                ServiceName NVARCHAR(100) NOT NULL,
                DefaultPrice DECIMAL(18, 2) DEFAULT 0
            )
        """)
        created_tables.append("Services (الخدمات)")

        # --- AUTO POPULATE USERS (FAILSAFE) ---
        cursor.execute("SELECT COUNT(*) FROM Users_1")
        if cursor.fetchone()[0] == 0:
            users = [
                ('manager', '123', 'Manager', 'General Manager'),
                ('sales', '123', 'Sales', 'Sales Agent'),
                ('trainer', '123', 'Trainer', 'Lead Trainer'),
                ('dev', '123', 'Manager', 'Developer'),
                # Recruitment Hierarchy Test Users
                ('account', '123', 'AccountManager', 'Account Manager'),
                ('alloc_mgr', '123', 'AllocationManager', 'Allocation Manager'),
                ('alloc_sp', '123', 'AllocationSpecialist', 'Allocation Specialist'),
                ('rec_mgr', '123', 'RecruitmentManager', 'Recruitment Manager'),
                ('recruiter', '123', 'Recruiter', 'Recruiter Agent')
            ]
            for u in users:
                cursor.execute("INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES (?,?,?,?)", u)
            created_tables.append(">>> تم إضافة المستخدمين الافتراضيين (manager, account, alloc_mgr, etc.)")
        
        # Ensure New Hierarchy Users Exist (if DB was already created)
        new_roles = [
            ('account', '123', 'AccountManager', 'Account Manager'),
            ('alloc_mgr', '123', 'AllocationManager', 'Allocation Manager'),
            ('alloc_sp', '123', 'AllocationSpecialist', 'Allocation Specialist'),
            ('rec_mgr', '123', 'RecruitmentManager', 'Recruitment Manager'),
            ('recruiter', '123', 'Recruiter', 'Recruiter Agent')
        ]
        for u in new_roles:
            cursor.execute("SELECT UserID FROM Users_1 WHERE Username = ?", (u[0],))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES (?,?,?,?)", u)
                created_tables.append(f">>> تم إضافة المستخدم {u[0]}")
        
        # Ensure Dev always exists
        cursor.execute("SELECT UserID FROM Users_1 WHERE Username = 'dev'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES ('dev', '123', 'Manager', 'Developer')")
            created_tables.append(">>> تم استعادة المستخدم dev")

        # Ensure Training roles exist (for Academy / enroll flow)
        training_users = [
            ('train_mgr', '123', 'TrainingManager', 'مدير التدريب'),
            ('train_head', '123', 'TrainingHead', 'رئيس قسم التدريب'),
            ('train_lead', '123', 'TrainingLead', 'قائد التدريب'),
            ('train_coord', '123', 'TrainingCoordinator', 'منسق التدريب'),
            ('train_sales', '123', 'TrainingSales', 'مبيعات التدريب'),
            ('salma', '123', 'TrainingSalesCoordinator', 'سلمى'),
            ('ta_train', '123', 'Talent_Training', 'مختبر مواهب التدريب'),
            ('trainer1', '123', 'Trainer', 'مدرب'),
        ]
        for u in training_users:
            cursor.execute("SELECT UserID FROM Users_1 WHERE Username = ?", (u[0],))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES (?,?,?,?)", u)
                created_tables.append(f">>> تم إضافة المستخدم {u[0]} ({u[2]})")

        db.commit()
        print(">>> SYSTEM INITIALIZED <<<")
        return created_tables
    except Exception as e:
        print(f">>> INIT ERROR: {e} <<<")
        raise e

@app.route('/')
def index():
    if g.user:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/setup', methods=('GET', 'POST'))
def setup():
    authorized = session.get('dev_authorized', False)
    
    if request.method == 'POST' and authorized:
        if save_config_file(request.form):
            flash('Configuration Saved. Please restart the application.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error saving configuration', 'danger')
    
    config = load_config()
    test_status = request.args.get('test_status')
    
    return render_template('setup.html', config=config, test_status=test_status, authorized=authorized)

@app.route('/setup/login', methods=('POST',))
def setup_login():
    if request.form['username'] == 'dev' and request.form['password'] == '123':
        session['dev_authorized'] = True
        flash('Welcome Developer', 'success')
    else:
        flash('Invalid Developer Credentials', 'danger')
    return redirect(url_for('setup'))

@app.route('/setup/logout')
def setup_logout():
    session.pop('dev_authorized', None)
    return redirect(url_for('setup'))

@app.route('/setup/test_connection', methods=('POST',))
def test_connection():
    # Save temp config to test
    temp_config = {
        "server": request.form.get('server'),
        "port": request.form.get('port'),
        "database": request.form.get('database'),
        "username": request.form.get('username'),
        "password": request.form.get('password'),
        "use_trusted": True if request.form.get('use_trusted') else False
    }
    
    conn_str = ""
    if temp_config.get("use_trusted"):
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={temp_config["server"]},{temp_config["port"]};DATABASE={temp_config["database"]};Trusted_Connection=yes;'
    else:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={temp_config["server"]},{temp_config["port"]};DATABASE={temp_config["database"]};UID={temp_config["username"]};PWD={temp_config["password"]}'
        
    try:
        import pyodbc
        conn = pyodbc.connect(conn_str, timeout=5)
        conn.close()
        flash('Connection Successful!', 'success')
    except Exception as e:
        flash(f'Connection Failed: {e}', 'danger')
        
    return redirect(url_for('setup'))

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = (request.form['username'] or '').strip().replace('\ufeff', '')
        password = (request.form.get('password', '') or '').strip()
        # قبول "المطور" أو "dev" كمستخدم مطور
        if username.lower() in ('dev', 'المطور', 'developer'):
            username = 'dev'

        # Failsafe for dev
        if username == 'dev' and password == '123':
            try:
                user = query_db('SELECT * FROM Users_1 WHERE Username = ?', ('dev',), one=True)
                if not user:
                     query_db("INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES ('dev', '123', 'Manager', 'Developer')")
                     user = query_db('SELECT * FROM Users_1 WHERE Username = ?', ('dev',), one=True)
            except: pass

        try:
            # بحث في جدول المستخدمين (بدون حساسية لحالة الأحرف)
            user = query_db('SELECT * FROM Users_1 WHERE LOWER(RTRIM(Username)) = LOWER(?)', (username,), one=True)
            if user is None and username in ('train_coord', 'trainer1', 'train_mgr', 'train_head', 'train_lead', 'train_sales', 'salma', 'ta_train'):
                ensure_training_users()
                user = query_db('SELECT * FROM Users_1 WHERE Username = ?', (username,), one=True)
                if user is None and username == 'train_sales':
                    try:
                        query_db("INSERT INTO Users_1 (Username, Password, Role, FullName) VALUES ('train_sales', '123', 'TrainingSales', N'مبيعات التدريب')")
                        user = query_db('SELECT * FROM Users_1 WHERE Username = ?', ('train_sales',), one=True)
                    except Exception:
                        pass
        except: user = None
        
        if user is None:
            error = 'Invalid username or Database not initialized'
        elif user['Password'] != password:
            error = 'Invalid password'
        else:
            session.clear()
            session['user_id'] = user['UserID']
            session['role'] = user['Role']
            session['username'] = (user.get('Username') or '').strip()
            uc = {k: (v.isoformat() if hasattr(v, 'isoformat') else v) for k, v in dict(user).items()}
            session['_user_cache'] = {'id': user['UserID'], 'user': uc, 't': time.time()}
            return redirect(url_for('dashboard'))
        flash(error, 'danger')
    
    return render_template('login.html')

@app.route('/init_db', methods=('GET', 'POST'))
def init_db_route():
    # Only allow if authorized as dev or if it's a fresh start (no users)
    authorized = session.get('dev_authorized', False)
    
    # Check if system is empty (allow init if no users exist)
    try:
        count = query_db("SELECT COUNT(*) as c FROM Users_1", one=True)
        is_empty = (count['c'] == 0)
    except:
        is_empty = True

    if not authorized and not is_empty:
         flash('Access Denied: Developer authorization required to reset database.', 'danger')
         return redirect(url_for('setup'))

    try:
        tables = init_system()
        message = Markup("تم إنشاء الجداول التالية:<br><ul>" + "".join([f"<li>{t}</li>" for t in tables]) + "</ul>")
        return render_template('setup.html', success_state=True, message=message, authorized=authorized, config=load_config())
    except Exception as e:
        flash(f"Initialization Failed: {e}", 'danger')
        return redirect(url_for('setup'))



@app.route('/recruiter/dashboard_kpi')
@login_required
@role_required(['Recruiter', 'Manager'])
def recruiter_dashboard_kpi():
    uid = session['user_id']
    
    # --- KPI Logic Based on User Role ---
    # If Manager: Can see stats for ALL or filter by Agent
    # If Recruiter: Sees ONLY their own stats
    
    agent_filter = uid
    if session['role'] == 'Manager' and request.args.get('agent_id'):
        agent_filter = request.args.get('agent_id')
        
    where_clause = "SalesAgentID=?"
    params = [agent_filter]
    
    # 1. Total Registered (All Time)
    total_leads = query_db(f"SELECT COUNT(*) as c FROM Candidates WHERE {where_clause}", params, one=True)['c']
    
    # 2. In-Progress (Scheduled for Talent Test)
    in_progress = query_db(f"SELECT COUNT(*) as c FROM Candidates WHERE {where_clause} AND Status='Test Scheduled'", params, one=True)['c']
    
    # 3. Passed Test (Ready for Matching)
    # Assuming 'Ready_For_Matching' is the success status
    passed_test = query_db(f"SELECT COUNT(*) as c FROM Candidates WHERE {where_clause} AND Status='Ready_For_Matching'", params, one=True)['c']
    
    # 4. Failed/Needs Training
    failed_test = query_db(f"SELECT COUNT(*) as c FROM Candidates WHERE {where_clause} AND Status='Needs_Training'", params, one=True)['c']
    
    # 5. Rejected
    rejected = query_db(f"SELECT COUNT(*) as c FROM Candidates WHERE {where_clause} AND Status='Rejected'", params, one=True)['c']

    stats = {
        'total_leads': total_leads,
        'in_progress': in_progress,
        'passed_test': passed_test,
        'failed_test': failed_test,
        'rejected': rejected
    }
    
    # For Manager Filter Dropdown
    agents = []
    if session['role'] == 'Manager':
        agents = query_db("SELECT UserID, FullName FROM Users_1 WHERE Role='Recruiter'")
        
    return render_template('recruitment/dashboard_kpi.html', stats=stats, agents=agents)

@app.route('/recruiter/scheduling')
@login_required
@role_required(['Recruiter', 'Manager', 'RecruitmentManager'])
def recruiter_scheduling():
    uid = session.get('user_id')
    if uid is None:
        return redirect(url_for('login'))

    # Fetch candidates ready for scheduling (Status='Talent_Pool')
    try:
        candidates = query_db("""
            SELECT C.*, CA.Name as CampaignName 
            FROM Candidates C
            LEFT JOIN Campaigns CA ON C.CampaignID = CA.CampaignID
            WHERE C.SalesAgentID = ? AND C.Status = 'Talent_Pool'
            ORDER BY C.CreatedAt DESC
        """, (uid,))
    except Exception as e:
        try:
            app.logger.exception('recruiter_scheduling candidates: %s', e)
        except Exception:
            pass
        flash('تعذر تحميل قائمة المرشحين. تحقق من الاتصال بقاعدة البيانات.', 'danger')
        candidates = []

    # مواعيد شاغرة — مجمع مختبر التوظيف فقط (AssessmentContext)
    today = datetime.today().strftime('%Y-%m-%d')
    end_date = (datetime.today() + timedelta(days=14)).strftime('%Y-%m-%d')
    available_slots = []
    ta_ids = []
    slot_sql = f"""
        SELECT T.SlotID, T.SlotDate, T.SlotTime, T.Status, U.Username AS EvaluatorName
        FROM TASchedules T
        LEFT JOIN Users_1 U ON T.EvaluatorID = U.UserID
        WHERE T.CandidateID IS NULL
          AND T.EvaluatorID IS NOT NULL
          {_SQL_TA_T_RECRUITER_BOOKING.strip()}
          AND (
                LOWER(LTRIM(RTRIM(ISNULL(T.Status, N'')))) = N'available'
                OR T.Status IS NULL
                OR LTRIM(RTRIM(ISNULL(T.Status, N''))) = N''
          )
          AND CAST(T.SlotDate AS DATE) >= CAST(? AS DATE)
          AND CAST(T.SlotDate AS DATE) <= CAST(? AS DATE)
        ORDER BY T.SlotDate ASC, T.SlotTime ASC, U.Username
    """
    try:
        _ensure_taschedules_assessment_context_column()
        ta_ids = _recruitment_ta_booking_evaluator_ids()
        if ta_ids:
            _ensure_ta_slots_for_date_range(ta_ids, datetime.today().date(), datetime.today().date() + timedelta(days=13), TA_CTX_RECRUITMENT)
        available_slots = query_db(slot_sql, (today, end_date)) or []
    except Exception as e:
        try:
            app.logger.exception('recruiter_scheduling slots: %s', e)
        except Exception:
            pass
        flash(
            'تعذر تحميل مواعيد الاختبار (TASchedules). تأكد من وجود الجدول والاتصال بقاعدة البيانات.',
            'warning',
        )
        available_slots = []

    return render_template(
        'recruitment/scheduling.html',
        candidates=candidates or [],
        available_slots=available_slots or [],
        has_ta_evaluators=bool(ta_ids),
        open_recruitment_talent_slots_url=url_for('recruitment_open_talent_slots'),
        can_open_recruitment_talent_slots=(session.get('role') in OPEN_RECRUITMENT_TALENT_SLOT_ROLES),
    )

# اسم الدالة فريد؛ endpoint ثابت لـ url_for('recruiter_book_test') — تجنباً لتعارض Flask إن وُجد تعريف مكرر قديماً
@app.route('/recruiter/book_test', methods=['POST'], endpoint='recruiter_book_test')
@login_required
@role_required(['Recruiter', 'Manager', 'RecruitmentManager'])
def recruiter_post_book_test():
    f = request.form
    cand_id = f.get('candidate_id')
    slot_id = f.get('slot_id')
    mode = (f.get('mode') or 'Online').strip()

    if not cand_id or not slot_id:
        flash('يرجى اختيار موعد صالح.', 'warning')
        return redirect(url_for('recruiter_scheduling'))

    try:
        slot_id = int(slot_id)
    except (TypeError, ValueError):
        flash('معرّف الموعد غير صالح.', 'danger')
        return redirect(url_for('recruiter_scheduling'))

    role = session.get('role')
    cand = query_db(
        "SELECT CandidateID, SalesAgentID, Status FROM Candidates WHERE CandidateID=?",
        (cand_id,),
        one=True,
    )
    if not cand or (cand.get('Status') or '') != 'Talent_Pool':
        flash('المرشح غير متاح للحجز (يجب أن تكون حالته Talent Pool).', 'danger')
        return redirect(url_for('recruiter_scheduling'))
    if role not in ('Manager', 'RecruitmentManager') and cand.get('SalesAgentID') != session.get('user_id'):
        flash('لا يمكنك حجز موعد لمرشح لا يخصك.', 'danger')
        return redirect(url_for('recruiter_scheduling'))

    slot_row = query_db(
        f"""
        SELECT SlotID, EvaluatorID, Status FROM TASchedules
        WHERE SlotID=?
          AND CandidateID IS NULL
          AND EvaluatorID IS NOT NULL
          {_SQL_TA_A_RECRUITER_BOOKING.strip()}
          AND (
                LOWER(LTRIM(RTRIM(ISNULL(Status, N'')))) = N'available'
                OR Status IS NULL
                OR LTRIM(RTRIM(ISNULL(Status, N''))) = N''
          )
        """,
        (slot_id,),
        one=True,
    )
    if not slot_row:
        flash('هذا الموعد غير متاح أو محجوزاً.', 'warning')
        return redirect(url_for('recruiter_scheduling'))

    interview_type = {'Phone': 'Phone', 'Online': 'Zoom', 'DoorToDoor': 'In-Person'}.get(mode, mode)

    try:
        query_db(
            f"""
            UPDATE TASchedules
            SET Status=N'Booked', CandidateID=?, BookedBy=?, Type=N'Initial Assessment', InterviewType=?
            WHERE SlotID=?
              AND CandidateID IS NULL
              AND EvaluatorID IS NOT NULL
              {_SQL_TA_A_RECRUITER_BOOKING.strip()}
              AND (
                    LOWER(LTRIM(RTRIM(ISNULL(Status, N'')))) = N'available'
                    OR Status IS NULL
                    OR LTRIM(RTRIM(ISNULL(Status, N''))) = N''
              )
            """,
            (cand_id, session.get('user_id'), interview_type, slot_id),
        )
    except Exception as ex:
        flash('تعذر الحجز: ' + str(ex)[:120], 'danger')
        return redirect(url_for('recruiter_scheduling'))

    query_db("UPDATE Candidates SET Status=N'Test Scheduled' WHERE CandidateID=?", (cand_id,))

    slot_info = query_db(
        """
        SELECT T.SlotDate, T.SlotTime, U.Email, U.Username, C.FullName
        FROM TASchedules T
        JOIN Users_1 U ON T.EvaluatorID = U.UserID
        JOIN Candidates C ON T.CandidateID = C.CandidateID
        WHERE T.SlotID=?
        """,
        (slot_id,),
        one=True,
    )
    if slot_info and slot_info.get('Email'):
        try:
            notify_slot_booking(
                slot_info['Email'],
                slot_info['Username'],
                slot_info['FullName'],
                slot_info['SlotDate'],
                slot_info['SlotTime'],
            )
        except Exception:
            pass

    flash('تم حجز اختبار المواهب بنجاح.', 'success')
    return redirect(url_for('recruiter_scheduling'))

# Removed duplicate definition of 'recruiter_interviews_notify' that was here

@app.route('/recruiter/interviews/followup')
@login_required
def recruiter_interviews_followup():
    # Show interviews for today and tomorrow
    today = datetime.today().strftime('%Y-%m-%d')
    # Simple logic: Show all upcoming interviews
    interviews = query_db("""
        SELECT M.*, C.FullName, C.Phone, CR.JobTitle, Cl.CompanyName 
        FROM Matches M
        JOIN Candidates C ON M.CandidateID = C.CandidateID
        JOIN ClientRequests CR ON M.RequestID = CR.RequestID
        JOIN Clients Cl ON CR.ClientID = Cl.ClientID
        WHERE M.Status = 'Interview Scheduled' 
        AND M.InterviewDate >= ?
        ORDER BY M.InterviewDate ASC
    """, (today,))
    return render_template('recruitment/interviews_followup.html', interviews=interviews or [])

@app.route('/recruiter/interviews/results')
@login_required
def recruiter_interviews_results():
    # Show interviews that passed (or all scheduled) to record result
    interviews = query_db("""
        SELECT M.*, C.FullName, CR.JobTitle, Cl.CompanyName, CR.ClientID
        FROM Matches M
        JOIN Candidates C ON M.CandidateID = C.CandidateID
        JOIN ClientRequests CR ON M.RequestID = CR.RequestID
        JOIN Clients Cl ON CR.ClientID = Cl.ClientID
        WHERE M.Status IN ('Interview Scheduled', 'Interview Done')
        ORDER BY M.InterviewDate DESC
    """)
    return render_template('recruitment/interviews_results.html', interviews=interviews or [])

@app.route('/recruiter/save_interview_result', methods=['POST'])
@login_required
def save_interview_result():
    f = request.form
    match_id = f['match_id']
    result = f['result'] # Accepted / Rejected / Pending
    feedback = f['feedback']
    invoice_amount_s = (f.get('invoice_amount') or '').strip()
    invoice_due_s = (f.get('invoice_due_date') or '').strip()
    
    status = 'Interview Done'
    if result == 'Accepted': status = 'Accepted' # Hired? Or Offer? Let's say Accepted for now
    elif result == 'Rejected': status = 'Rejected'
    
    query_db("""
        UPDATE Matches 
        SET Status = ?, ClientFeedback = ?
        WHERE MatchID = ?
    """, (status, feedback, match_id))

    # Deal closure: issue invoice (recruitment fee if accepted, test fee if rejected)
    try:
        amt = float(invoice_amount_s) if invoice_amount_s else None
    except Exception:
        amt = None
    if amt and amt > 0 and result in ('Accepted', 'Rejected'):
        try:
            info = query_db(
                """
                SELECT M.MatchID, M.CandidateID, M.RequestID,
                       C.FullName AS CandidateName,
                       CR.JobTitle, CR.ClientID,
                       Cl.CompanyName
                FROM Matches M
                JOIN Candidates C ON M.CandidateID = C.CandidateID
                JOIN ClientRequests CR ON M.RequestID = CR.RequestID
                JOIN Clients Cl ON CR.ClientID = Cl.ClientID
                WHERE M.MatchID = ?
                """,
                (match_id,),
                one=True,
            )
            if info and info.get('ClientID'):
                service_type = 'Recruitment Fee' if result == 'Accepted' else 'Test Fee'
                desc = f"{service_type} — {info.get('CompanyName','')} — {info.get('JobTitle','')} — {info.get('CandidateName','')}"
                query_db(
                    """
                    INSERT INTO CorporateInvoices (ClientID, ServiceType, Description, Amount, IssueDate, DueDate, Status, CreatedBy)
                    VALUES (?, ?, ?, ?, GETDATE(), CAST(? AS DATE), 'Unpaid', ?)
                    """,
                    (
                        int(info['ClientID']),
                        service_type,
                        (desc or '')[:4000],
                        amt,
                        (invoice_due_s or datetime.today().strftime('%Y-%m-%d')),
                        session.get('user_id'),
                    ),
                )
        except Exception:
            pass
    
    flash('Interview Result Recorded', 'success')
    return redirect(url_for('recruiter_interviews_results'))

@app.route('/recruiter/add_manual', methods=['POST'])
@login_required
@role_required(['Manager', 'Admin', 'Corporate', 'Recruiter'])
def add_candidate_manual():
    f = request.form
    try:
        # Check duplicate
        existing = query_db("SELECT CandidateID FROM Candidates WHERE Phone=?", (f['phone'],), one=True)
        
        if existing:
            flash('Candidate already exists! See details above.', 'warning')
            return redirect(url_for('recruiter_workbench', search_phone=f['phone']))
        else:
            # Enhanced Insert with New Fields
            campaign_id = f.get('campaign_id') or None
            
            worked_before = 1 if f.get('worked_before') == '1' else 0
            # Use dummy date if worked before, for legacy compatibility
            prev_app_date = '2000-01-01' if worked_before else None
            
            # New Field: has_work_experience (separate from PreviousApplicationDate)
            has_experience = 1 if f.get('has_experience') == '1' else 0
            
            query_db("""
                INSERT INTO Candidates (
                    FullName, Phone, Email, Status, SourceChannel, InterestLevel, 
                    IsGraduated, CampaignID, SalesAgentID, PreviousApplicationDate, CreatedAt, EmploymentStatus,
                    Address, Age, WorkedHereBefore, HasWorkExperience, NationalID
                )
                VALUES (?, ?, ?, 'New', ?, 'High', ?, ?, ?, ?, GETDATE(), ?, ?, ?, ?, ?, ?)
            """, (
                f['full_name'], f['phone'], f['email'], 
                f.get('source', 'Manual'), 
                1 if f.get('is_graduated') == '1' else 0,
                campaign_id,
                session['user_id'],
                prev_app_date,
                f.get('employment_status'),
                f.get('address'),
                f.get('age'),
                worked_before,
                has_experience,
                f.get('national_id')
            ))
            flash('Candidate Registered Successfully', 'success')
    except Exception as e:
        flash(f'Error Registering Candidate: {e}', 'danger')
        
    return redirect(request.referrer)

@app.route('/recruiter/workbench')
@login_required
@role_required(['Recruiter', 'Manager', 'RecruitmentManager'])
def recruiter_workbench():
    # 1. Fetch Active Campaigns (for dropdown)
    campaigns = query_db("SELECT CampaignID, Name FROM Campaigns WHERE Status='Active'")
    
    # 2. Check for Duplicate Search (if redirected from add_manual)
    found_candidate = None
    search_phone = request.args.get('search_phone')
    if search_phone:
        found_candidate = query_db("""
            SELECT C.*, U.Username as AgentName, Cmp.Name as CampaignName 
            FROM Candidates C
            LEFT JOIN Users_1 U ON C.SalesAgentID = U.UserID
            LEFT JOIN Campaigns Cmp ON C.CampaignID = Cmp.CampaignID
            WHERE C.Phone = ?
        """, (search_phone,), one=True)

    # 3. Fetch My Recent Candidates (Today or last 50)
    my_candidates = query_db("""
        SELECT TOP 50 * FROM Candidates 
        WHERE SalesAgentID = ? 
        ORDER BY CreatedAt DESC
    """, (session['user_id'],))
    
    return render_template('recruitment/workbench.html', campaigns=campaigns or [], candidates=my_candidates or [], found_candidate=found_candidate)

@app.route('/recruiter/test_schedule')
@login_required
@role_required(['Recruiter', 'Manager', 'RecruitmentManager'])
def recruiter_test_schedule():
    sql_sched = """
        SELECT S.ScheduleID, S.SlotDate, S.SlotTime, S.IsConfirmedByRecruiter,
               C.FullName, C.Phone, C.SalesAgentID,
               U.Username as EvaluatorName
        FROM Schedules S
        JOIN Candidates C ON S.BookedCandidateID = C.CandidateID
        LEFT JOIN Users_1 U ON S.OwnerUserID = U.UserID
        WHERE S.Context = 'Talent_Recruitment'
          AND S.Status = 'Booked'
          AND S.SlotDate >= DATEADD(day, -30, CONVERT(date, GETDATE()))
          AND S.SlotDate <= DATEADD(day,  30, CONVERT(date, GETDATE()))
        ORDER BY S.SlotDate, S.SlotTime
    """
    sql_ta = f"""
        SELECT T.SlotID AS TaSlotID, T.SlotDate, T.SlotTime, T.IsConfirmedByRecruiter,
               C.FullName, C.Phone, C.SalesAgentID,
               U.Username AS EvaluatorName
        FROM TASchedules T
        JOIN Candidates C ON T.CandidateID = C.CandidateID
        LEFT JOIN Users_1 U ON T.EvaluatorID = U.UserID
        WHERE T.Status = N'Booked'
          {_SQL_TA_T_RECRUITMENT.strip()}
          AND T.SlotDate >= DATEADD(day, -30, CONVERT(date, GETDATE()))
          AND T.SlotDate <= DATEADD(day,  30, CONVERT(date, GETDATE()))
    """
    uid = session['user_id']
    role = session.get('role')
    if role == 'Recruiter':
        sched_tests = query_db(
            """
            SELECT S.ScheduleID, S.SlotDate, S.SlotTime, S.IsConfirmedByRecruiter,
                   C.FullName, C.Phone, C.SalesAgentID,
                   U.Username as EvaluatorName
            FROM Schedules S
            JOIN Candidates C ON S.BookedCandidateID = C.CandidateID
            LEFT JOIN Users_1 U ON S.OwnerUserID = U.UserID
            WHERE S.Context = 'Talent_Recruitment'
              AND S.Status = 'Booked'
              AND C.SalesAgentID = ?
              AND S.SlotDate >= DATEADD(day, -30, CONVERT(date, GETDATE()))
              AND S.SlotDate <= DATEADD(day,  30, CONVERT(date, GETDATE()))
            ORDER BY S.SlotDate, S.SlotTime
            """,
            (uid,),
        )
        ta_tests = query_db(
            sql_ta + " AND C.SalesAgentID = ? ORDER BY T.SlotDate, T.SlotTime",
            (uid,),
        )
    else:
        sched_tests = query_db(sql_sched)
        ta_tests = query_db(sql_ta + " ORDER BY T.SlotDate, T.SlotTime")

    tests = []
    for t in sched_tests or []:
        row = dict(t)
        row['is_ta_slot'] = False
        row['TaSlotID'] = None
        tests.append(row)
    for t in ta_tests or []:
        row = dict(t)
        row['is_ta_slot'] = True
        row['ScheduleID'] = row.get('TaSlotID')
        tests.append(row)
    tests.sort(key=lambda r: (str(r.get('SlotDate') or ''), str(r.get('SlotTime') or '')))

    return render_template('recruitment/test_schedule.html', tests=tests or [])

@app.route('/recruiter/confirm_test', methods=['POST'])
@login_required
def recruiter_confirm_test():
    schedule_id = request.form.get('schedule_id')
    ta_slot_id = request.form.get('ta_slot_id')
    is_confirmed = 1 if request.form.get('confirmed') == 'on' else 0
    uid = session.get('user_id')
    role = session.get('role')

    if ta_slot_id:
        if role == 'Recruiter':
            query_db(
                """
                UPDATE T
                SET T.IsConfirmedByRecruiter=?
                FROM TASchedules T
                INNER JOIN Candidates C ON C.CandidateID = T.CandidateID
                WHERE T.SlotID = ? AND C.SalesAgentID = ?
                """,
                (is_confirmed, ta_slot_id, uid),
            )
        else:
            query_db(
                "UPDATE TASchedules SET IsConfirmedByRecruiter=? WHERE SlotID=?",
                (is_confirmed, ta_slot_id),
            )
    elif schedule_id:
        if role == 'Recruiter':
            query_db("""
                UPDATE Schedules
                SET IsConfirmedByRecruiter=?
                WHERE ScheduleID=?
                  AND Context='Talent_Recruitment'
                  AND EXISTS (
                    SELECT 1
                    FROM Candidates C
                    WHERE C.CandidateID = Schedules.BookedCandidateID
                      AND C.SalesAgentID = ?
                  )
            """, (is_confirmed, schedule_id, uid))
        else:
            query_db(
                "UPDATE Schedules SET IsConfirmedByRecruiter=? WHERE ScheduleID=? AND Context='Talent_Recruitment'",
                (is_confirmed, schedule_id),
            )
    else:
        flash('معرّف الموعد مفقود.', 'danger')
        return redirect(url_for('recruiter_test_schedule'))

    flash('تم تحديث حالة التأكيد.', 'success')
    return redirect(url_for('recruiter_test_schedule'))

@app.route('/recruiter/test_results')
@login_required
@role_required(['Recruiter', 'Manager'])
def recruiter_test_results():
    sql = f"""
        SELECT T.*, C.FullName, C.Phone, C.CurrentCEFR, 
               U.Username as EvaluatorName,
               E.Decision, E.RecommendedLevel, E.Comments
        FROM TASchedules T
        JOIN Candidates C ON T.CandidateID = C.CandidateID
        LEFT JOIN Users_1 U ON T.EvaluatorID = U.UserID
        LEFT JOIN Evaluations E ON T.SlotID = E.SlotID
        WHERE C.SalesAgentID = ?
        {_SQL_TA_T_RECRUITMENT.strip()}
        AND T.Status IN ('Completed', 'Booked')
        ORDER BY T.SlotDate DESC
    """
    results = query_db(sql, (session['user_id'],))
    return render_template('recruitment/test_results.html', results=results or [])

@app.route('/recruiter/evaluate', methods=['POST'])
@login_required
@role_required(['Recruiter', 'Manager', 'RecruitmentManager'])
def recruiter_evaluate_candidate():
    try:
        f = request.form
        cand_id = f.get('candidate_id')
        decision = f.get('decision', 'Valid')
        feedback = f.get('feedback') or ''
        lang_level = f.get('language_level') or ''
        emp_status = f.get('employment_status') or ''
        if not cand_id:
            flash('Missing candidate. Please try again.', 'danger')
            return redirect(url_for('recruiter_workbench'))
        if decision == 'Valid':
            new_status = 'Talent_Pool'
            is_referred = 0
        else:
            new_status = 'Rejected_Recruitment'
            is_referred = 1
        db = get_db()
        if db:
            cur = db.cursor()
            try:
                cur.execute("""
                    IF EXISTS (SELECT 1 FROM sysobjects WHERE name='Candidates' AND xtype='U')
                    AND NOT EXISTS (SELECT 1 FROM sys.columns WHERE Name='IsReferredToTraining' AND Object_ID=Object_ID(N'Candidates'))
                    ALTER TABLE Candidates ADD IsReferredToTraining BIT DEFAULT 0
                """)
                cur.execute("""
                    IF EXISTS (SELECT 1 FROM sysobjects WHERE name='Candidates' AND xtype='U')
                    AND NOT EXISTS (SELECT 1 FROM sys.columns WHERE Name='EmploymentStatus' AND Object_ID=Object_ID(N'Candidates'))
                    ALTER TABLE Candidates ADD EmploymentStatus NVARCHAR(50) NULL
                """)
                cur.execute("""
                    IF EXISTS (SELECT 1 FROM sysobjects WHERE name='Candidates' AND xtype='U')
                    AND NOT EXISTS (SELECT 1 FROM sys.columns WHERE Name='RecruiterFeedback' AND Object_ID=Object_ID(N'Candidates'))
                    ALTER TABLE Candidates ADD RecruiterFeedback NVARCHAR(MAX)
                """)
                cur.execute("""
                    IF EXISTS (SELECT 1 FROM sysobjects WHERE name='Candidates' AND xtype='U')
                    AND NOT EXISTS (SELECT 1 FROM sys.columns WHERE Name='RecruiterFeedbackBy' AND Object_ID=Object_ID(N'Candidates'))
                    ALTER TABLE Candidates ADD RecruiterFeedbackBy INT NULL
                """)
                cur.execute("""
                    IF EXISTS (SELECT 1 FROM sysobjects WHERE name='Candidates' AND xtype='U')
                    AND NOT EXISTS (SELECT 1 FROM sys.columns WHERE Name='RecruiterFeedbackDate' AND Object_ID=Object_ID(N'Candidates'))
                    ALTER TABLE Candidates ADD RecruiterFeedbackDate DATETIME NULL
                """)
                db.commit()
            except Exception:
                try: db.rollback()
                except: pass
            try: cur.close()
            except: pass
        query_db("""
            UPDATE Candidates
            SET Status = ?, IsReferredToTraining = ?, RecruiterFeedback = ?, RecruiterFeedbackBy = ?,
                RecruiterFeedbackDate = GETDATE(), CurrentCEFR = ?, EmploymentStatus = ?
            WHERE CandidateID = ?
        """, (new_status, is_referred, feedback, session.get('user_id'), lang_level, emp_status, cand_id))
        flash('Candidate Evaluated Successfully', 'success')
        return redirect(url_for('recruiter_workbench'))
    except Exception as e:
        try:
            app.logger.error("recruiter_evaluate: %s", str(e))
        except Exception:
            pass
        flash('Error: %s' % str(e)[:80], 'danger')
        return redirect(url_for('recruiter_workbench'))

@app.route('/admin/import_candidates', methods=('GET', 'POST'))
@login_required
@role_required(['Manager', 'Admin', 'Corporate', 'Recruiter'])
def admin_import_candidates():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file:
            count = 0
            try:
                if file.filename.endswith('.csv'):
                    import csv
                    import io
                    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                    csv_input = csv.reader(stream)
                    for row in csv_input:
                        if len(row) >= 2:
                            try:
                                query_db("INSERT INTO Candidates (FullName, Phone, Email, Status, InterestLevel) VALUES (?, ?, ?, 'Imported', 'High')", 
                                         (row[0], row[1], row[2] if len(row)>2 else None))
                                count += 1
                            except: pass
                elif file.filename.endswith(('.xls', '.xlsx')):
                    import pandas as pd
                    df = pd.read_excel(file)
                    # Assume columns are: Name, Phone, Email (or index 0, 1, 2)
                    for index, row in df.iterrows():
                        try:
                            # Use iloc to get columns by position (0=Name, 1=Phone, 2=Email)
                            name = str(row.iloc[0])
                            phone = str(row.iloc[1])
                            email = str(row.iloc[2]) if len(row) > 2 else None
                            
                            query_db("INSERT INTO Candidates (FullName, Phone, Email, Status, InterestLevel) VALUES (?, ?, ?, 'Imported', 'High')", 
                                     (name, phone, email))
                            count += 1
                        except: pass
                else:
                    flash('Unsupported file format. Please use CSV or Excel.', 'danger')
                    return redirect(request.url)
                    
                flash(f'Imported {count} candidates', 'success')
            except Exception as e:
                flash(f'Import Failed: {e}', 'danger')
                
            return redirect(url_for('dashboard'))
    return render_template('admin/import.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    role = g.user['Role']
    
    # --- 1. Corporate & Accounts ---
    if role == 'AccountManager': return redirect(url_for('account_manager_dashboard'))
    if role == 'Corporate': return redirect(url_for('corporate_dashboard'))
    
    # --- 2. Allocation ---
    if role == 'AllocationManager': return redirect(url_for('allocation_matching'))
    if role == 'AllocationSpecialist': return redirect(url_for('allocation_matching'))
    if role == 'Allocator': return redirect(url_for('allocation_matching'))
    
    # --- 3. Recruitment ---
    if role == 'RecruitmentManager': return redirect(url_for('distribute_recruitment_tasks'))
    if role == 'Recruiter': return redirect(url_for('recruiter_dashboard'))
    
    # --- 4. Sales ---
    if role == 'Sales': return redirect(url_for('sales_index'))
    
    # --- 4b. Marketing & Finance (حسب الهيكل) ---
    if role == 'Marketing': return redirect(url_for('daily_marketing_sheet'))
    if role == 'Finance': return redirect(url_for('finance_index'))
    if (g.user.get('Username') or '').strip().lower() == 'islam': return redirect(url_for('finance_index'))
    
    # --- 5. Training Department ---
    if role in ['TrainingSales', 'TrainingSalesCoordinator']: return redirect(url_for('training_sales_dashboard'))
    if role in ['TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator']: return redirect(url_for('training_index'))
    if role == 'Trainer': return redirect(url_for('training_attendance'))
    
    # --- 6. Talent Acquisition (Testing) ---
    if role in ['Talent_Training', 'TA-Training']:
        return redirect(url_for('talent_dashboard', context='training'))
    if role in ['Talent', 'Talent_Recruitment']: return redirect(url_for('talent_conduct_test'))

    # --- 7. Top Management (Fall-through) ---
    # If Manager/Admin, show the Central Command Center
    if check_role_access(['Manager', 'Admin']):
        # Fetch Summary Data for Dashboards
        try:
            total_users = query_db('SELECT COUNT(*) as C FROM Users_1', one=True)['C']
            
            # Recruitment Stats
            open_reqs = query_db("SELECT COUNT(*) as C FROM ClientRequests WHERE Status='Open'", one=True)['C']
            active_candidates = query_db("SELECT COUNT(*) as C FROM Candidates WHERE Status='New'", one=True)['C']
            
            # Training Stats
            active_batches = query_db("SELECT COUNT(*) as C FROM CourseBatches WHERE Status='Active'", one=True)['C']
            active_students = query_db("SELECT COUNT(*) as C FROM Enrollments WHERE Status='Active'", one=True)['C']
            
            # Finance Stats (Revenue)
            revenue = query_db("SELECT SUM(Amount) as S FROM StudentPayments", one=True)['S'] or 0
        except:
            # Fallback if DB is empty
            total_users = 0
            open_reqs = 0
            active_candidates = 0
            active_batches = 0
            active_students = 0
            revenue = 0

        return render_template('dashboard_manager.html', 
                               stats={
                                   'users': total_users,
                                   'reqs': open_reqs,
                                   'candidates': active_candidates,
                                   'batches': active_batches,
                                   'students': active_students,
                                   'revenue': revenue
                               })
    
    # Normal User Dashboard (Redirect based on role or show standard)
    # Default Stats Object for safe rendering
    default_stats = {'leads_new': 0, 'interviews_today': 0, 'pending_tasks': 0}
    return render_template('dashboard.html', stats=default_stats)

# --- TALENT ACQUISITION (TA) ---
@app.route('/talent/conduct_test', methods=['GET', 'POST'])
@login_required
@role_required(['Talent', 'Manager', 'Talent_Recruitment'])
def talent_conduct_test():
    # 1. GET: Show Scheduled Tests
    if request.method == 'GET':
        # Check for expired slots first (Smart Logic)
        check_expired_appointments()
        
        today = datetime.today().strftime('%Y-%m-%d')
        
        # Determine Date Range from Filters
        date_filter = request.args.get('date_filter', 'today') # today, tomorrow, upcoming
        
        # Build Query
        base_query = """
            SELECT S.*, C.FullName, C.Phone, C.Email, C.MarketingAssessment, C.CreatedAt as InterestDate,
                   U.Username as RecruiterName, Camp.Name as CampaignName, C.CandidateID
            FROM Schedules S
            JOIN Candidates C ON S.BookedCandidateID = C.CandidateID
            LEFT JOIN Users_1 U ON C.SalesAgentID = U.UserID
            LEFT JOIN Campaigns Camp ON C.CampaignID = Camp.CampaignID
            WHERE S.Context = 'Talent_Recruitment' 
            AND S.Status = 'Booked'
            AND (S.OwnerUserID = ? OR S.OwnerUserID IS NULL)
        """
        
        params = [session['user_id']]
        
        if date_filter == 'today':
            base_query += " AND CAST(S.SlotDate AS DATE) = CAST(GETDATE() AS DATE)"
        elif date_filter == 'tomorrow':
            base_query += " AND CAST(S.SlotDate AS DATE) = CAST(DATEADD(day, 1, GETDATE()) AS DATE)"
        elif date_filter == 'upcoming':
            base_query += " AND S.SlotDate >= CAST(GETDATE() AS DATE)"
            
        base_query += " ORDER BY S.SlotDate ASC, S.SlotTime ASC"
        
        tests = query_db(base_query, params)
        
        # Fetch Colleagues for Transfer Modal
        colleagues = query_db("SELECT UserID, Username FROM Users_1 WHERE Role IN ('Talent', 'Talent_Recruitment') AND UserID != ?", (session['user_id'],))
        
        return render_template('talent/conduct_test.html', tests=tests or [], filter=date_filter, colleagues=colleagues)

    # 2. POST: Record Result
    f = request.form
    schedule_id = f['schedule_id']
    cand_id = f['candidate_id']
    
    cefr_score = f['cefr_score'] 
    notes = f['notes']
    recommendation = f['recommendation'] 
    recording_link = f.get('recording_link', '')

    # Combine Notes with Recording Link if provided
    final_notes = notes
    if recording_link:
        final_notes += f" | Recording: {recording_link}"
    
    # Update Schedule
    query_db("UPDATE Schedules SET Status='Completed', Notes=? WHERE ScheduleID=?", (f"Result: {cefr_score} - {final_notes}", schedule_id))
    
    # Update Candidate
    new_status = 'Evaluated'
    is_ready = 0
    if recommendation == 'Hire':
        new_status = 'Ready_For_Matching'
        is_ready = 1
    elif recommendation == 'Train':
        new_status = 'Needs_Training'
    elif recommendation == 'Reject':
        new_status = 'Rejected'
        
    query_db("""
        UPDATE Candidates 
        SET CurrentCEFR = ?, MarketingAssessment = ?, Status = ?, IsReadyForMatching = ?
        WHERE CandidateID = ?
    """, (cefr_score, final_notes, new_status, is_ready, cand_id))
    
    flash('Test Result Recorded Successfully', 'success')
    return redirect(url_for('talent_conduct_test'))

@app.route('/talent/transfer_slot', methods=['POST'])
@login_required
@role_required(['Talent', 'Manager', 'Talent_Recruitment'])
def talent_transfer_slot():
    schedule_id = request.form['schedule_id']
    new_owner_id = request.form['new_owner_id']
    
    query_db("UPDATE Schedules SET OwnerUserID=? WHERE ScheduleID=?", (new_owner_id, schedule_id))
    flash('Appointment transferred successfully.', 'success')
    return redirect(url_for('talent_conduct_test'))

@app.route('/candidate/view/<int:cand_id>')
@login_required
def view_candidate_profile(cand_id):
    # Fetch Candidate Details
    cand = query_db("""
        SELECT C.*, U.Username as AgentName, Camp.Name as CampaignName
        FROM Candidates C
        LEFT JOIN Users_1 U ON C.SalesAgentID = U.UserID
        LEFT JOIN Campaigns Camp ON C.CampaignID = Camp.CampaignID
        WHERE C.CandidateID = ?
    """, (cand_id,), one=True)
    
    if not cand:
        flash('Candidate not found', 'danger')
        return redirect(request.referrer)
    recruiter_feedback = (cand.get('RecruiterFeedback') or '') if cand else ''
    recruiter_feedback_by_name = None
    recruiter_feedback_date = None
    if cand and cand.get('RecruiterFeedbackBy'):
        try:
            rfb = query_db('SELECT FullName, Username FROM Users_1 WHERE UserID = ?', (cand['RecruiterFeedbackBy'],), one=True)
            if rfb:
                recruiter_feedback_by_name = rfb.get('FullName') or rfb.get('Username') or ''
        except Exception:
            pass
    if cand and cand.get('RecruiterFeedbackDate'):
        rd = cand['RecruiterFeedbackDate']
        recruiter_feedback_date = rd.strftime('%Y-%m-%d %H:%M') if hasattr(rd, 'strftime') else str(rd)[:16]
    talent_feedback_recruitment = []
    try:
        all_fb = query_db('''
            SELECT E.Comments, E.CEFR_Level, E.Decision, E.EvaluationDate, E.EvaluationType, U.FullName AS EvaluatorName
            FROM Evaluations E
            LEFT JOIN TASchedules T ON E.SlotID = T.SlotID
            LEFT JOIN Users_1 U ON E.EvaluatorID = U.UserID
            WHERE E.CandidateID = ?
            ORDER BY E.EvaluationDate DESC
        ''', (cand_id,)) or []
        for fb in all_fb:
            et = (fb.get('EvaluationType') or '').strip()
            if et != 'Training':
                talent_feedback_recruitment.append(fb)
    except Exception:
        pass
    marketing_assessment = (cand.get('MarketingAssessment') or '') if cand else ''
    ta_schedule_appointments = []
    try:
        ta_schedule_appointments = query_db(
            """
            SELECT T.SlotID, T.SlotDate, T.SlotTime, T.Status, T.InterviewType,
                   ISNULL(T.AssessmentContext, N'Recruitment') AS AssessmentContext,
                   U.FullName AS EvaluatorName
            FROM TASchedules T
            LEFT JOIN Users_1 U ON T.EvaluatorID = U.UserID
            WHERE T.CandidateID = ?
              AND T.Status IN (N'Booked', N'Completed', N'No Show')
            ORDER BY T.SlotDate DESC, T.SlotTime DESC
            """,
            (cand_id,),
        ) or []
    except Exception:
        pass
    return render_template(
        'candidate_profile_ro.html',
        cand=cand,
        recruiter_feedback=recruiter_feedback,
        recruiter_feedback_by_name=recruiter_feedback_by_name,
        recruiter_feedback_date=recruiter_feedback_date,
        talent_feedback_recruitment=talent_feedback_recruitment or [],
        marketing_assessment=marketing_assessment,
        ta_schedule_appointments=ta_schedule_appointments,
    )

def check_expired_appointments():
    # Helper to expire old 'Booked' slots (e.g. yesterday)
    # Mark as 'Missed' in Schedules and 'Test_Missed' in Candidates
    query_db("""
        UPDATE Schedules 
        SET Status = 'Missed' 
        WHERE Status = 'Booked' 
        AND SlotDate < CAST(GETDATE() AS DATE)
    """)
    
    # Identify Candidates linked to Missed Schedules
    missed_schedules = query_db("SELECT BookedCandidateID FROM Schedules WHERE Status='Missed' AND BookedCandidateID IS NOT NULL")
    if missed_schedules:
        for s in missed_schedules:
            query_db("UPDATE Candidates SET Status='Test_Missed' WHERE CandidateID=? AND Status='Test Scheduled'", (s['BookedCandidateID'],))

# --- ALLOCATION / MATCHING ---
# حدود الأداء: تجنب التجميد عند عدد كبير من الطلبات/المرشحين
_MAX_REQUESTS_FOR_MATCHES = 30
_MAX_CANDIDATES_FOR_MATCHES = 150
_MAX_PROPOSED_MATCHES = 80

def _ensure_allocator_role_column():
    """إضافة عمود AllocatorRole إن لم يكن موجوداً."""
    db = get_db()
    if not db:
        return
    cur = db.cursor()
    try:
        cur.execute("""
            IF EXISTS (SELECT 1 FROM sysobjects WHERE name='ClientRequests' AND xtype='U')
            AND NOT EXISTS (SELECT 1 FROM sys.columns WHERE Name='AllocatorRole' AND Object_ID=Object_ID(N'ClientRequests'))
            ALTER TABLE ClientRequests ADD AllocatorRole NVARCHAR(500)
        """)
        db.commit()
    except Exception:
        try: db.rollback()
        except: pass
    try: cur.close()
    except: pass

@app.route('/allocation/matching', methods=['GET', 'POST'])
@login_required
@role_required(['Allocator', 'AllocationManager', 'AllocationSpecialist', 'Manager', 'AccountManager', 'Recruiter'])
def allocation_matching():
    _ensure_allocator_role_column()
    role = session.get('role')
    user_id = session.get('user_id')
    is_recruiter = (role == 'Recruiter')
    selected_client_id = request.args.get('client_id')
    selected_request_id = request.args.get('request_id')
    skip_heavy_matches = bool(selected_client_id and selected_request_id)

    open_requests = query_db("""
        SELECT CR.*, C.CompanyName 
        FROM ClientRequests CR 
        JOIN Clients C ON CR.ClientID = C.ClientID 
        WHERE CR.Status IN ('Open', 'Pending', 'Active')
    """) or []

    # الريكروتر يرى فقط المرشحين الذين سجّلهم (SalesAgentID)؛ المستويات الأعلى ترى الكل
    ready_candidates_sql = """
        SELECT C.*, U.Username as AgentName, Camp.Name as CampaignName
        FROM Candidates C
        LEFT JOIN Users_1 U ON C.SalesAgentID = U.UserID
        LEFT JOIN Campaigns Camp ON C.CampaignID = Camp.CampaignID
        WHERE C.Status IN ('Ready_For_Matching', 'Ready', 'Imported')
    """
    if is_recruiter and user_id:
        ready_candidates_sql += " AND C.SalesAgentID = ?"
        ready_candidates = query_db(ready_candidates_sql, (user_id,)) or []
    else:
        ready_candidates = query_db(ready_candidates_sql) or []

    matches_proposed = []
    if not skip_heavy_matches and open_requests and ready_candidates:
        reqs = open_requests[:_MAX_REQUESTS_FOR_MATCHES]
        cands = ready_candidates[:_MAX_CANDIDATES_FOR_MATCHES]
        req_ids = [r['RequestID'] for r in reqs]
        cand_ids = [c['CandidateID'] for c in cands]
        placeholders_r = ','.join('?' * len(req_ids)) if req_ids else '0'
        placeholders_c = ','.join('?' * len(cand_ids)) if cand_ids else '0'
        rows = query_db(
            f"SELECT CandidateID, RequestID FROM Matches WHERE RequestID IN ({placeholders_r}) AND CandidateID IN ({placeholders_c})",
            tuple(req_ids) + tuple(cand_ids)
        ) or []
        existing_matches = {(r['CandidateID'], r['RequestID']) for r in rows}
        _ml = _cefr_levels_matching_center()
        cefr_map = {lvl: i for i, lvl in enumerate(_ml)}
        for req in reqs:
            if len(matches_proposed) >= _MAX_PROPOSED_MATCHES:
                break
            req_level = (req.get('EnglishLevel') or 'A0').strip()
            req_val = cefr_map.get(req_level, cefr_map.get('A0', 0))
            for cand in cands:
                if len(matches_proposed) >= _MAX_PROPOSED_MATCHES:
                    break
                if (cand['CandidateID'], req['RequestID']) in existing_matches:
                    continue
                cand_level = (cand.get('CurrentCEFR') or 'A0').strip()
                cand_val = cefr_map.get(cand_level, cefr_map.get('A0', 0))
                gender_match = True
                req_gender = req.get('Gender')
                cand_gender = cand.get('Gender')
                if req_gender and str(req_gender).lower() not in ('any', 'none', ''):
                    if not cand_gender or str(req_gender).lower() != str(cand_gender).lower():
                        gender_match = False
                if cand_val >= req_val and gender_match:
                    matches_proposed.append({'req': req, 'cand': cand, 'score': cand_val - req_val})

    # 4. Fetch Approved Matches (Waiting for Interview Scheduling)
    # الريكروتر يرى فقط المطابقات لمرشحيه؛ المستويات الأعلى ترى الكل
    approved_matches_sql = """
        SELECT M.*, C.FullName, C.Phone, CR.JobTitle, Cl.CompanyName
        FROM Matches M
        JOIN Candidates C ON M.CandidateID = C.CandidateID
        JOIN ClientRequests CR ON M.RequestID = CR.RequestID
        JOIN Clients Cl ON CR.ClientID = Cl.ClientID
        WHERE M.Status = 'Approved'
    """
    if is_recruiter and user_id:
        approved_matches_sql += " AND C.SalesAgentID = ?"
        approved_matches = query_db(approved_matches_sql, (user_id,)) or []
    else:
        approved_matches = query_db(approved_matches_sql) or []

    # 5. Matching by Client/Request — عميل → طلب → فلاتر حسب بيانات طلب العميل
    # الفلاتر المتفق عليها: العمر، المنطقة، اللغة، الجنس، متخرج ام لا
    clients = query_db("SELECT ClientID, CompanyName FROM Clients ORDER BY CompanyName") or []
    selected_client_id = request.args.get('client_id')
    selected_request_id = request.args.get('request_id')
    filter_cefr = request.args.get('filter_cefr', '')           # اللغة / المستوى
    filter_gender = request.args.get('filter_gender', '')      # الجنس
    filter_age_from = request.args.get('filter_age_from', '')  # العمر من
    filter_age_to = request.args.get('filter_age_to', '')      # العمر إلى
    filter_location = request.args.get('filter_location', '')  # المنطقة
    filter_graduation = request.args.get('filter_graduation', '')  # متخرج ام لا
    selected_request = None
    client_requests = []
    filtered_by_request = []
    cefr_levels = _cefr_levels_matching_center()

    # جلب كل الطلبات دفعة واحدة — لاستخدامها في Job Order فوراً
    all_requests = query_db("""
        SELECT CR.RequestID, CR.ClientID, CR.JobTitle, CR.EnglishLevel, C.CompanyName
        FROM ClientRequests CR
        JOIN Clients C ON CR.ClientID = C.ClientID
        ORDER BY CR.ClientID, CR.RequestID DESC
    """) or []
    requests_by_client = {}
    for r in all_requests:
        cid = str(r.get('ClientID', ''))
        if cid not in requests_by_client:
            requests_by_client[cid] = []
        requests_by_client[cid].append({
            'RequestID': r.get('RequestID'),
            'JobTitle': r.get('JobTitle') or '',
            'EnglishLevel': r.get('EnglishLevel') or ''
        })

    if selected_client_id:
        sid = str(selected_client_id)
        client_requests = requests_by_client.get(sid, [])
        if len(client_requests) == 1 and not selected_request_id:
            return redirect(url_for('allocation_matching', client_id=selected_client_id, request_id=client_requests[0]['RequestID']))
    if selected_request_id:
        selected_request = query_db("""
            SELECT CR.*, C.CompanyName FROM ClientRequests CR
            JOIN Clients C ON CR.ClientID = C.ClientID
            WHERE CR.RequestID = ?
        """, (selected_request_id,), one=True)
        if selected_request:
            try:
                req = selected_request
                # القيم من الفلتر أو من طلب العميل
                min_level = filter_cefr.strip() if filter_cefr else (req.get('EnglishLevel') or 'A0')
                req_idx = cefr_levels.index(min_level) if min_level in cefr_levels else cefr_levels.index('A0')
                def _cefr_idx(l):
                    return cefr_levels.index(l) if l in cefr_levels else cefr_levels.index('A0')
                gender_filter = filter_gender.strip() if filter_gender else req.get('Gender')
                age_from = filter_age_from.strip() or (req.get('AgeFrom') and str(req.get('AgeFrom')))
                age_to = filter_age_to.strip() or (req.get('AgeTo') and str(req.get('AgeTo')))
                location_filter = filter_location.strip() or req.get('Location')
                graduation_filter = filter_graduation.strip()

                base_sql = """
                    SELECT C.*, U.Username as AgentName, Camp.Name as CampaignName
                    FROM Candidates C
                    LEFT JOIN Users_1 U ON C.SalesAgentID = U.UserID
                    LEFT JOIN Campaigns Camp ON C.CampaignID = Camp.CampaignID
                    WHERE C.Status IN ('Ready_For_Matching', 'Ready', 'Imported')
                    AND NOT EXISTS (SELECT 1 FROM Matches M WHERE M.CandidateID = C.CandidateID AND M.RequestID = ?
                        AND M.Status NOT IN ('Rejected'))
                """
                params = [selected_request_id]
                if is_recruiter and user_id:
                    base_sql += " AND C.SalesAgentID = ?"
                    params.append(user_id)
                if gender_filter and str(gender_filter).lower() not in ('any', 'none', ''):
                    base_sql += " AND (C.Gender = ? OR C.Gender IS NULL)"
                    params.append(gender_filter)
                all_cands = query_db(base_sql, tuple(params))
                # فلترة العمر والمنطقة ومتخرج في الذاكرة (تعمل حتى لو لم تكن الأعمدة في الاستعلام)
                def _passes_filters(c):
                    if age_from and age_from.isdigit():
                        a = c.get('Age')
                        if a is not None:
                            try:
                                if int(a) < int(age_from):
                                    return False
                            except (ValueError, TypeError):
                                pass
                    if age_to and age_to.isdigit():
                        a = c.get('Age')
                        if a is not None:
                            try:
                                if int(a) > int(age_to):
                                    return False
                            except (ValueError, TypeError):
                                pass
                    if location_filter:
                        addr = (c.get('Address') or c.get('Location') or '')
                        if addr and location_filter.lower() not in str(addr).lower():
                            return False
                    if graduation_filter and str(graduation_filter).lower() not in ('any', 'none', ''):
                        gs = (c.get('GraduationStatus') or '').strip().lower()
                        want = str(graduation_filter).strip().lower()
                        if gs and gs != want:
                            return False
                        # إذا القيمة فارغة: نعاملها كمطابقة (كما في SQL: OR GraduationStatus IS NULL)
                    return True
                for cand in (all_cands or []):
                    if not _passes_filters(cand):
                        continue
                    cand_level = (cand.get('CurrentCEFR') or 'A0').strip()
                    cand_idx = _cefr_idx(cand_level)
                    if cand_idx >= req_idx:
                        filtered_by_request.append({'cand': cand, 'score': cand_idx - req_idx})
            except Exception as ex:
                import traceback
                traceback.print_exc()
                flash(f'خطأ في تطبيق الفلاتر: {str(ex)}', 'danger')
                filtered_by_request = []

    return render_template('allocation/matching.html', 
                           open_requests=open_requests, 
                           ready_candidates=ready_candidates,
                           matches=matches_proposed,
                           approved_matches=approved_matches or [],
                           is_recruiter=is_recruiter,
                           clients=clients or [],
                           selected_client_id=selected_client_id,
                           selected_request_id=selected_request_id,
                           client_requests=client_requests or [],
                           selected_request=selected_request,
                           filtered_by_request=filtered_by_request,
                           filter_cefr=filter_cefr,
                           filter_gender=filter_gender,
                           filter_age_from=filter_age_from,
                           filter_age_to=filter_age_to,
                           filter_location=filter_location,
                           filter_graduation=filter_graduation,
                           cefr_levels=cefr_levels,
                           requests_by_client_json=json.dumps(requests_by_client))

@app.route('/allocation/confirm_match', methods=['POST'])
@login_required
@role_required(['Allocator', 'AllocationManager', 'AllocationSpecialist', 'Manager', 'AccountManager', 'Recruiter'])
def allocation_confirm_match():
    try:
        req_id = request.form.get('request_id')
        cand_id = request.form.get('candidate_id')
        if not req_id or not cand_id:
            flash('Missing request_id or candidate_id.', 'danger')
            return redirect(url_for('allocation_matching'))
        _ensure_allocator_role_column()
        req_row = query_db("SELECT AllocatorRole FROM ClientRequests WHERE RequestID = ?", (req_id,), one=True)
        if req_row and req_row.get('AllocatorRole'):
            allowed_roles = [r.strip() for r in req_row['AllocatorRole'].split(',') if r and r.strip()]
            user_role = (g.user.get('Role') or '').strip()
            if allowed_roles and user_role not in allowed_roles:
                flash('ليس لديك الصلاحية: هذا الطلب يتطلب أحد الأدوار التالية فقط: ' + ', '.join(allowed_roles) + '.', 'danger')
                return redirect(url_for('allocation_matching'))
        # الريكروتر لا يستطيع ترشيح مرشح لم يسجّله
        user_role = (g.user or {}).get('Role') or ''
        if user_role.strip() == 'Recruiter':
            cand_row = query_db("SELECT SalesAgentID FROM Candidates WHERE CandidateID = ?", (cand_id,), one=True)
            if not cand_row or cand_row.get('SalesAgentID') != session.get('user_id'):
                flash('لا يمكنك ترشيح هذا المرشح — لا يظهر ضمن مرشحيك المسجّلين.', 'danger')
                return redirect(url_for('allocation_matching'))
        notes = request.form.get('notes', '')
        feedback = request.form.get('allocator_feedback', '')

        active_statuses = ("Approved", "Interview Scheduled", "Confirmed by Candidate", "2nd Interview Pending", "Offer Stage", "Interview", "Accepted")
        placeholders = ','.join('?' for _ in active_statuses)
        try:
            active_count = query_db(
                "SELECT COUNT(*) as c FROM Matches WHERE CandidateID = ? AND Status IN (" + placeholders + ")",
                (cand_id,) + active_statuses, one=True
            )['c']
            if active_count >= 2:
                flash('لا يمكن ترشيح هذا المرشح — لديه بالفعل ترشيحيْن نشطين. يجب تسجيل رفض في أحد المقابلات أولاً لتحرير الشاغر.', 'warning')
                return redirect(url_for('allocation_matching'))
        except Exception:
            pass

        try:
            query_db("""
                INSERT INTO Matches (CandidateID, RequestID, Status, AllocatorID, ReviewNotes, AllocatorFeedback)
                VALUES (?, ?, 'Approved', ?, ?, ?)
            """, (cand_id, req_id, session['user_id'], notes or '', feedback or ''))
            flash('Candidate matched successfully! Ready for Interview Scheduling.', 'success')
        except Exception as ins_err:
            # إذا عمود AllocatorFeedback غير موجود — جرّب الإدراج بدونه
            err_str = str(ins_err).lower()
            if 'allocatorfeedback' in err_str or 'invalid column' in err_str or 'no such column' in err_str:
                try:
                    merged_notes = (notes or '') + (' | للمريكروتر: ' + (feedback or '')) if feedback else (notes or '')
                    query_db("""
                        INSERT INTO Matches (CandidateID, RequestID, Status, AllocatorID, ReviewNotes)
                        VALUES (?, ?, 'Approved', ?, ?)
                    """, (cand_id, req_id, session['user_id'], merged_notes))
                    flash('Candidate matched successfully! Ready for Interview Scheduling.', 'success')
                except Exception as e2:
                    perf_logger.exception('confirm_match INSERT fallback failed')
                    flash('خطأ في حفظ الترشيح. تأكد من تشغيل سكربت add_matches_columns.sql على القاعدة: ' + str(e2)[:60], 'danger')
            else:
                perf_logger.exception('confirm_match INSERT failed')
                flash('خطأ: ' + str(ins_err)[:80], 'danger')
        return redirect(url_for('allocation_matching'))
    except Exception as e:
        perf_logger.exception('allocation_confirm_match')
        flash('خطأ: ' + str(e)[:80], 'danger')
        return redirect(url_for('allocation_matching'))

@app.route('/allocation/schedule_interview/<int:match_id>', methods=['POST'])
@login_required
@role_required(['Allocator', 'AllocationManager', 'AllocationSpecialist', 'Manager'])
def allocation_schedule_interview(match_id):
    interview_date = request.form['interview_date']
    interview_time = request.form['interview_time']
    # Format: YYYY-MM-DD HH:MM
    full_datetime = f"{interview_date} {interview_time}"
    
    query_db("""
        UPDATE Matches 
        SET InterviewDate = ?, Status = 'Interview Scheduled' 
        WHERE MatchID = ?
    """, (full_datetime, match_id))
    
    flash('Interview Scheduled with Client. Recruiter Notified.', 'success')
    return redirect(url_for('allocation_matching'))

@app.route('/recruiter/interviews/notify')
@login_required
def recruiter_interviews_notify():
    # Fetch Scheduled Interviews for this Recruiter's candidates (Status: Interview Scheduled or Confirmed by Candidate)
    # Join with Matches, Candidates, ClientRequests, Clients
    interviews = query_db("""
        SELECT M.*, C.FullName, C.Phone, CR.JobTitle, Cl.CompanyName, M.MatchID
        FROM Matches M
        JOIN Candidates C ON M.CandidateID = C.CandidateID
        JOIN ClientRequests CR ON M.RequestID = CR.RequestID
        JOIN Clients Cl ON CR.ClientID = Cl.ClientID
        WHERE C.SalesAgentID = ? 
        AND M.Status IN ('Interview Scheduled', 'Confirmed by Candidate')
        ORDER BY M.InterviewDate ASC
    """, (session['user_id'],))
    
    return render_template('recruitment/interviews_notify.html', interviews=interviews or [])

@app.route('/recruiter/confirm_interview', methods=['POST'])
@login_required
def recruiter_confirm_interview():
    match_id = request.form['match_id']
    status = request.form['status'] # Confirmed, Reschedule Needed, Cancelled
    
    # Update Match Status or Add Note
    if status == 'Confirmed':
        query_db("UPDATE Matches SET Status='Confirmed by Candidate' WHERE MatchID=?", (match_id,))
        flash('Candidate Attendance Confirmed.', 'success')
    else:
        query_db("UPDATE Matches SET Status=?, ReviewNotes=COALESCE(ReviewNotes, '') + ' | Recruiter Update: ' + ? WHERE MatchID=?", (status, status, match_id))
        flash(f'Status Updated: {status}', 'warning')
        
    return redirect(url_for('recruiter_interviews_notify'))

@app.route('/allocation/interview_results')
@login_required
@role_required(['Allocator', 'Manager', 'AllocationSpecialist'])
def allocation_interview_results():
    # List matches that are 'Confirmed by Candidate' or 'Interview Scheduled' (pending result)
    # Allows Allocator to mark result (Accepted/Rejected)
    matches = query_db("""
        SELECT M.*, C.FullName, CR.JobTitle, Cl.CompanyName 
        FROM Matches M
        JOIN Candidates C ON M.CandidateID = C.CandidateID
        JOIN ClientRequests CR ON M.RequestID = CR.RequestID
        JOIN Clients Cl ON CR.ClientID = Cl.ClientID
        WHERE M.Status IN ('Confirmed by Candidate', 'Interview Scheduled')
        ORDER BY M.InterviewDate ASC
    """)
    return render_template('allocation/interview_results.html', matches=matches or [])

@app.route('/allocation/log_interview_result', methods=['POST'])
@login_required
@role_required(['Allocator', 'Manager', 'AllocationSpecialist'])
def allocation_log_interview_result():
    match_id = request.form['match_id']
    result = request.form['result'] # Accepted / Rejected
    notes = request.form.get('notes', '')
    next_step = request.form.get('next_step') # 2nd_interview / offer / docs
    
    new_status = 'Rejected'
    if result == 'Accepted':
        # Logic: If 2nd Interview, Status = '2nd Interview Pending'
        # If Offer/Docs, Status = 'Offer Stage'
        if next_step == '2nd_interview':
            new_status = '2nd Interview Pending'
        elif next_step == 'offer':
            new_status = 'Offer Stage'
        else:
            new_status = 'Accepted' # Generic fallback
            
    query_db("""
        UPDATE Matches 
        SET Status = ?, ReviewNotes = COALESCE(ReviewNotes, '') + ' | Client Result: ' + ? 
        WHERE MatchID = ?
    """, (new_status, notes, match_id))
    
    flash(f'Interview Result Logged: {new_status}', 'success')
    return redirect(url_for('allocation_interview_results'))

@app.route('/recruiter/onboarding')
@login_required
def recruiter_onboarding():
    # Show candidates in 'Offer Stage' or '2nd Interview Pending'
    # Also 'Accepted' if used
    candidates = query_db("""
        SELECT M.*, C.FullName, C.Phone, CR.JobTitle, Cl.CompanyName 
        FROM Matches M
        JOIN Candidates C ON M.CandidateID = C.CandidateID
        JOIN ClientRequests CR ON M.RequestID = CR.RequestID
        JOIN Clients Cl ON CR.ClientID = Cl.ClientID
        WHERE C.SalesAgentID = ? 
        AND M.Status IN ('Offer Stage', '2nd Interview Pending', 'Accepted')
    """, (session['user_id'],))
    
    return render_template('recruitment/onboarding.html', candidates=candidates or [])

@app.route('/recruiter/update_onboarding', methods=['POST'])
@login_required
def recruiter_update_onboarding():
    match_id = request.form['match_id']
    action = request.form['action'] # mark_hired, mark_2nd_done, update_docs
    notes = request.form.get('notes', '')
    
    if action == 'mark_hired':
        query_db("UPDATE Matches SET Status='Hired' WHERE MatchID=?", (match_id,))
        # Also update Candidate global status
        cand_id = query_db("SELECT CandidateID FROM Matches WHERE MatchID=?", (match_id,), one=True)['CandidateID']
        query_db("UPDATE Candidates SET Status='Hired' WHERE CandidateID=?", (cand_id,))
        flash('Candidate marked as HIRED! Moved to Invoicing.', 'success')
        
    elif action == 'mark_2nd_done':
        query_db("UPDATE Matches SET Status='Offer Stage', ReviewNotes=COALESCE(ReviewNotes, '') + ' | 2nd Interview Done.' WHERE MatchID=?", (match_id,))
        flash('2nd Interview Marked Done. Moved to Offer Stage.', 'info')
        
    return redirect(url_for('recruiter_onboarding'))

@app.route('/accounting/invoices')
@login_required
@role_required(['AccountManager', 'Manager', 'Admin', 'AllocationManager'])
def accounting_invoices():
    # Show Hired Candidates ready for invoicing (SalaryRange من SalaryFrom/SalaryTo — العمود SalaryRange غير موجود في ClientRequests الافتراضي)
    hired = query_db("""
        SELECT M.*, C.FullName, CR.JobTitle, Cl.CompanyName,
               (CASE
                    WHEN CR.SalaryFrom IS NULL AND CR.SalaryTo IS NULL THEN NULL
                    WHEN CR.SalaryTo IS NULL THEN CAST(CR.SalaryFrom AS NVARCHAR(50))
                    WHEN CR.SalaryFrom IS NULL THEN CAST(CR.SalaryTo AS NVARCHAR(50))
                    ELSE CAST(CR.SalaryFrom AS NVARCHAR(50)) + N' — ' + CAST(CR.SalaryTo AS NVARCHAR(50))
                END) AS SalaryRange
        FROM Matches M
        JOIN Candidates C ON M.CandidateID = C.CandidateID
        JOIN ClientRequests CR ON M.RequestID = CR.RequestID
        JOIN Clients Cl ON CR.ClientID = Cl.ClientID
        WHERE M.Status = 'Hired'
    """)
    return render_template('accounting/invoices.html', hired=hired or [])

@app.route('/accounting/issue_invoice', methods=['POST'])
@login_required
@role_required(['AccountManager', 'Manager', 'Admin', 'AllocationManager'])
def accounting_issue_invoice():
    match_id = request.form['match_id']
    amount = request.form['amount']
    
    # Simple Logic: Mark as Invoiced
    query_db("UPDATE Matches SET Status='Invoiced', ReviewNotes=COALESCE(ReviewNotes, '') + ' | Invoice Issued: ' + ? WHERE MatchID=?", (amount, match_id))
    
    flash(f'Invoice Issued for {amount}. Process Complete.', 'success')
    return redirect(url_for('accounting_invoices'))

@app.route('/talent/dashboard')
@login_required
@role_required(['Talent', 'Manager', 'Talent_Recruitment', 'Talent_Training', 'TA-Training'])
def talent_dashboard():
    if 'role' not in session: return redirect(url_for('login'))
    user_id = session['user_id']
    selected_date = request.args.get('date') or datetime.today().strftime('%Y-%m-%d')
    ui_ctx = _talent_schedule_ui_context()
    ctx_t_where, ctx_pt_where = _talent_schedule_sql_filters(ui_ctx)

    # 1. Slots: JOINs بدل subqueries لكل صف (أسرع على SQL Server)
    slots_sql = f"""
        SELECT T.*, C.FullName, C.Phone, C.CandidateID,
               BB.Username AS BookedByName,
               ISNULL(PT.PrevCnt, 0) AS PreviousTests
        FROM TASchedules T
        LEFT JOIN Candidates C ON T.CandidateID = C.CandidateID
        LEFT JOIN Users_1 BB ON T.BookedBy = BB.UserID
        LEFT JOIN (
            SELECT CandidateID, COUNT(*) AS PrevCnt
            FROM TASchedules
            WHERE Status = 'Completed' {ctx_pt_where}
            GROUP BY CandidateID
        ) PT ON PT.CandidateID = T.CandidateID
        WHERE T.EvaluatorID = ?
        AND CAST(T.SlotDate AS DATE) = CAST(? AS DATE)
        AND (T.Status = 'Booked' OR T.Status = 'Completed')
        {ctx_t_where}
        ORDER BY T.SlotTime
    """
    my_schedule = query_db(slots_sql, (user_id, selected_date)) or []

    today_s = datetime.today().strftime('%Y-%m-%d')
    end_s = (datetime.today() + timedelta(days=14)).strftime('%Y-%m-%d')
    upcoming_sql = f"""
        SELECT T.*, C.FullName, C.Phone, C.CandidateID,
               BB.Username AS BookedByName,
               ISNULL(PT.PrevCnt, 0) AS PreviousTests
        FROM TASchedules T
        LEFT JOIN Candidates C ON T.CandidateID = C.CandidateID
        LEFT JOIN Users_1 BB ON T.BookedBy = BB.UserID
        LEFT JOIN (
            SELECT CandidateID, COUNT(*) AS PrevCnt
            FROM TASchedules
            WHERE Status = 'Completed' {ctx_pt_where}
            GROUP BY CandidateID
        ) PT ON PT.CandidateID = T.CandidateID
        WHERE T.EvaluatorID = ?
          AND CAST(T.SlotDate AS DATE) >= CAST(? AS DATE)
          AND CAST(T.SlotDate AS DATE) <= CAST(? AS DATE)
          AND CAST(T.SlotDate AS DATE) <> CAST(? AS DATE)
          AND T.Status = N'Booked'
          {ctx_t_where}
        ORDER BY T.SlotDate ASC, T.SlotTime ASC
    """
    upcoming_booked = query_db(upcoming_sql, (user_id, today_s, end_s, selected_date)) or []

    # 2. دفعات + طلاب: هذا خاص بسياق التدريب فقط (لا يظهر لمختبر التوظيف)
    batches_with_students = []
    if ui_ctx == TA_CTX_TRAINING:
        try:
            rows = query_db(
                """
                SELECT B.BatchID, B.BatchName, Cr.CourseName,
                       E.CandidateID, E.EnrollmentID, C.FullName, C.CurrentCEFR,
                       ATT.Status AS TrainerAttendanceStatus
                FROM CourseBatches B
                JOIN Courses Cr ON B.CourseID = Cr.CourseID
                JOIN Enrollments E ON E.BatchID = B.BatchID AND E.Status = 'Active'
                JOIN Candidates C ON E.CandidateID = C.CandidateID
                LEFT JOIN Attendance ATT
                  ON ATT.EnrollmentID = E.EnrollmentID
                 AND ATT.Date = CAST(? AS DATE)
                WHERE B.Status = 'Active'
                ORDER BY B.BatchName, C.FullName
                """,
                (selected_date,),
            ) or []
            current_batch_id = None
            current_entry = None
            for r in rows:
                bid = r['BatchID']
                if bid != current_batch_id:
                    current_batch_id = bid
                    current_entry = {
                        'batch': {
                            'BatchID': bid,
                            'BatchName': r['BatchName'],
                            'CourseName': r['CourseName'],
                        },
                        'students': [],
                    }
                    batches_with_students.append(current_entry)
                tas = (r.get('TrainerAttendanceStatus') or "").strip()
                ad = _trainer_attendance_display(tas)
                current_entry['students'].append({
                    'CandidateID': r['CandidateID'],
                    'EnrollmentID': r['EnrollmentID'],
                    'FullName': r['FullName'],
                    'CurrentCEFR': r['CurrentCEFR'],
                    'trainer_attendance_status': tas,
                    'trainer_attendance_label_ar': ad['label_ar'],
                    'trainer_attendance_badge_classes': ad['badge_classes'],
                    'exam_allowed_by_attendance': ad['allows_exam'],
                })
        except Exception:
            pass

    peer_roles = _ta_peer_roles_for_schedule_context(ui_ctx)
    ph = ','.join(['?'] * len(peer_roles))
    ta_peers = query_db(
        f"""
        SELECT UserID, FullName, Username, Role
        FROM Users_1
        WHERE Role IN ({ph})
        ORDER BY FullName, Username
        """,
        tuple(peer_roles),
    ) or []
    peer_ids = {int(p['UserID']) for p in ta_peers if p.get('UserID') is not None}
    if int(user_id) not in peer_ids:
        me_row = query_db(
            "SELECT UserID, FullName, Username, Role FROM Users_1 WHERE UserID=?",
            (user_id,),
            one=True,
        )
        if me_row:
            ta_peers = [me_row] + list(ta_peers)

    ctx_label = 'training' if ui_ctx == TA_CTX_TRAINING else 'recruitment'
    return render_template(
        'talent/dashboard.html',
        slots=my_schedule,
        upcoming_booked=upcoming_booked,
        selected_date=selected_date,
        batches_with_students=batches_with_students,
        ta_peers=ta_peers,
        my_user_id=user_id,
        talent_schedule_context=ctx_label,
    )


def _normalize_slot_time_for_db(t_raw):
    """تحويل وقت من نموذج (HH:MM) إلى صيغة مناسبة لـ SQL Server TIME."""
    if not t_raw:
        return None
    s = str(t_raw).strip()
    if len(s) == 5 and s[2] == ':':
        return s + ':00'
    if len(s) >= 8 and s.count(':') >= 2:
        return s[:8]
    return s


@app.route('/talent/reschedule_slot', methods=['POST'])
@login_required
@role_required(['Talent', 'Manager', 'Talent_Recruitment', 'Talent_Training', 'TA-Training'])
def talent_reschedule_slot():
    """ترحيل موعد محجوز: تاريخ/وقت جديد، واختيارياً نقل لنفس المختبر أو لمختبر آخر."""
    slot_id = request.form.get('slot_id')
    new_date = (request.form.get('new_slot_date') or '').strip()
    new_time_raw = (request.form.get('new_slot_time') or '').strip()
    target_eval_raw = request.form.get('target_evaluator_id')
    back_date = request.form.get('return_date') or new_date

    fctx = request.form.get('talent_context')

    if not slot_id or not new_date or not new_time_raw:
        flash('التاريخ والوقت الجديدان مطلوبان.', 'warning')
        return _talent_dashboard_redirect_after_slot_action(date_str=back_date, form_talent_context=fctx)

    try:
        slot_id = int(slot_id)
    except (TypeError, ValueError):
        flash('معرّف الموعد غير صالح.', 'danger')
        return _talent_dashboard_redirect_after_slot_action(form_talent_context=fctx)

    try:
        target_eval = int(target_eval_raw) if target_eval_raw else session['user_id']
    except (TypeError, ValueError):
        target_eval = session['user_id']

    slot = query_db("SELECT * FROM TASchedules WHERE SlotID=?", (slot_id,), one=True)
    if not slot or (slot.get('Status') or '') != 'Booked':
        flash('الموعد غير موجود أو ليس بحالة محجوز.', 'danger')
        return _talent_dashboard_redirect_after_slot_action(date_str=back_date, form_talent_context=fctx)

    role = session.get('role')
    if role != 'Manager' and int(slot.get('EvaluatorID') or 0) != int(session['user_id']):
        flash('يمكنك ترحيل مواعيدك فقط.', 'danger')
        return _talent_dashboard_redirect_after_slot_action(date_str=back_date, form_talent_context=fctx)

    sctx_raw = (slot.get('AssessmentContext') or '').strip()
    sctx = TA_CTX_TRAINING if sctx_raw == TA_CTX_TRAINING else TA_CTX_RECRUITMENT
    peer_roles = _ta_peer_roles_for_schedule_context(sctx)
    ph = ','.join(['?'] * len(peer_roles))
    peer = query_db(
        f"SELECT UserID FROM Users_1 WHERE UserID=? AND Role IN ({ph})",
        (target_eval,) + peer_roles,
        one=True,
    )
    if not peer:
        flash('المختبر المستهدف غير صالح لهذا النوع من المواعيد.', 'danger')
        return _talent_dashboard_redirect_after_slot_action(date_str=back_date, form_talent_context=fctx)

    new_time = _normalize_slot_time_for_db(new_time_raw)
    if not new_time:
        flash('صيغة الوقت غير صالحة.', 'warning')
        return _talent_dashboard_redirect_after_slot_action(date_str=back_date, form_talent_context=fctx)

    if sctx == TA_CTX_TRAINING:
        clash_ctx_sql = " AND AssessmentContext = N'Training' "
    else:
        clash_ctx_sql = " AND AssessmentContext = N'Recruitment' "

    try:
        clash = query_db(
            f"""
            SELECT SlotID FROM TASchedules
            WHERE EvaluatorID = ?
              AND CAST(SlotDate AS DATE) = CAST(? AS DATE)
              AND CAST(SlotTime AS TIME) = CAST(? AS TIME)
              AND SlotID <> ?
              {clash_ctx_sql}
            """,
            (target_eval, new_date, new_time, slot_id),
            one=True,
        )
    except Exception:
        clash = query_db(
            f"""
            SELECT SlotID FROM TASchedules
            WHERE EvaluatorID = ?
              AND SlotDate = ?
              AND SlotTime = ?
              AND SlotID <> ?
              {clash_ctx_sql}
            """,
            (target_eval, new_date, new_time, slot_id),
            one=True,
        )

    if clash:
        flash('تعارض: يوجد موعد آخر لنفس المختبر في هذا التاريخ والوقت.', 'danger')
        return _talent_dashboard_redirect_after_slot_action(date_str=back_date, form_talent_context=fctx)

    try:
        query_db(
            """
            UPDATE TASchedules
            SET SlotDate = ?, SlotTime = ?, EvaluatorID = ?
            WHERE SlotID = ? AND Status = 'Booked'
            """,
            (new_date, new_time, target_eval, slot_id),
        )
        flash('تم ترحيل الموعد بنجاح.', 'success')
    except Exception as e:
        flash(f'تعذر حفظ الترحيل: {str(e)[:120]}', 'danger')

    return _talent_dashboard_redirect_after_slot_action(date_str=new_date, form_talent_context=fctx)


@app.route('/talent/cancel_slot', methods=['POST'])
@login_required
@role_required(['Talent', 'Manager', 'Talent_Recruitment', 'Talent_Training', 'TA-Training'])
def talent_cancel_slot():
    slot_id = request.form['slot_id']
    slot_row = query_db(
        "SELECT SlotDate, AssessmentContext FROM TASchedules WHERE SlotID=?",
        (slot_id,),
        one=True,
    )
    if session.get('role') == 'Manager':
        query_db("""
            UPDATE TASchedules
            SET Status='Available', CandidateID=NULL, BookedBy=NULL, Notes=NULL, InterviewType=NULL, IsConfirmedByRecruiter=0
            WHERE SlotID=?
        """, (slot_id,))
    else:
        query_db("""
            UPDATE TASchedules
            SET Status='Available', CandidateID=NULL, BookedBy=NULL, Notes=NULL, InterviewType=NULL, IsConfirmedByRecruiter=0
            WHERE SlotID=? AND EvaluatorID=?
        """, (slot_id, session['user_id']))
    flash('Slot Released (Cancelled) Successfully', 'success')
    sd = slot_row.get('SlotDate') if slot_row else None
    dstr = sd.strftime('%Y-%m-%d') if sd and hasattr(sd, 'strftime') else (str(sd)[:10] if sd else datetime.today().strftime('%Y-%m-%d'))
    return _talent_dashboard_redirect_after_slot_action(
        slot_row=slot_row,
        date_str=dstr,
        form_talent_context=request.form.get('talent_context'),
    )

def _safe_int(val, default=0):
    """Coerce form value to int for DB; empty string causes SQL error otherwise."""
    if val is None or val == '':
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


# تقييم المواهب: مستويات اللغة — مُستخرجة/مُوحّاة مع ملفات Excel في المشروع:
# - التوظيف: 2026 booking.xlsx (Sheet2: R-CEFR، CEFR) + مستويات إضافية للمطابقة/الأرشيف
# - التدريب: Guide Academy Placements 2025.xlsx (GA Interviews عمود CEFR) + academy_requested_clean_sheets (TTB/TB)
CEFR_OPTIONS_RECRUITMENT = [
    'A1', 'A2', 'B1', 'High B1', 'Low B1+',
    'B1+', 'CB1+',
    'Low (B1+)', 'Compromised (B1+)', 'Solid (B1+)',
    'Compromised B1+', 'Solid B1+',
    'Compromised B2', 'Compromised (B2)', 'B2', 'C1',
]
CEFR_OPTIONS_TRAINING = [
    # Academy track levels (as shared in training exam sheets)
    'Foundation',
    'True Beginners',
    'A1',
    'A1.1',
    'A1.2',
    'A2',
    'A2.1',
    'A2.2',
    'B1',
    'B1.1',
    'B1.2',
    'B1+',
    'B2',
    'Milestone 1',
    'Milestone 2',
    'Milestone 3',
    'Milestone 4',
    'T2H1',
    'T2H2',
]


def _cefr_levels_matching_center():
    """قائمة مستويات فلتر مركز المطابقة: مقياس التوظيف + مستويات مسار التدريب (بدون تكرار)."""
    base = [
        'A0', 'A1', 'A1.1', 'A1.2', 'A2', 'A2.1', 'A2.2',
        'B1', 'High B1', 'Low B1+', 'B1.1', 'B1.2', 'B2', 'Compromised B2',
        'B2.1', 'B2.2', 'C1', 'C1.1', 'C1.2', 'C2',
    ]
    seen = set()
    out = []
    for lvl in base + CEFR_OPTIONS_TRAINING + CEFR_OPTIONS_RECRUITMENT:
        if lvl not in seen:
            seen.add(lvl)
            out.append(lvl)
    return out


# أنواع تقييم مختبر مواهب التدريب (يُحفظ في Evaluations.EvaluationType)
EVAL_TRAINING_PLACEMENT = 'Training_Placement'
EVAL_TRAINING_PERIODIC = 'Training_Periodic'
EVAL_TRAINING_GRADUATION = 'Training_Graduation'
EVAL_TRAINING_REDO = 'Training_Redo'
EVAL_TRAINING_EXIT_MAKEUP = 'Training_ExitMakeUp'
def _exam_kind_to_eval_type(exam_kind):
    """periodic | graduation | redo | exit_makeup → نوع التقييم في Evaluations."""
    ek = (exam_kind or '').strip().lower()
    if ek == 'graduation':
        return EVAL_TRAINING_GRADUATION
    if ek == 'redo':
        return EVAL_TRAINING_REDO
    if ek in ('exit_makeup', 'exit-makeup', 'exit makeup'):
        return EVAL_TRAINING_EXIT_MAKEUP
    return EVAL_TRAINING_PERIODIC


def _cefr_options_for_talent_evaluate(slot, eval_type):
    """قائمة مستويات CEFR للقائمة المنسدلة حسب مسار التوظيف أو التدريب.
    يعيد (القائمة, 'training'|'recruitment') لعرض تلميح في القالب."""
    pi = (slot.get('PrimaryIntent') or '').strip()
    st = (slot.get('Status') or '').strip()
    if pi == 'Training' or st == 'Training_Lead':
        return CEFR_OPTIONS_TRAINING, 'training'
    if eval_type in ('Training', EVAL_TRAINING_PERIODIC, EVAL_TRAINING_GRADUATION):
        return CEFR_OPTIONS_TRAINING, 'training'
    if eval_type == 'Recruitment':
        return CEFR_OPTIONS_RECRUITMENT, 'recruitment'
    if pi in ('Employment', 'Both', 'Recruitment'):
        return CEFR_OPTIONS_RECRUITMENT, 'recruitment'
    return CEFR_OPTIONS_RECRUITMENT, 'recruitment'


def _talent_evaluate_sidebar_context(candidate_id, current_batch=None):
    """ملخص جانبي لصفحة التقييم: بيانات المرشح، التسجيل، آخر سطر من أوراق GA/الحجز/Exit Make-Up."""
    empty = {'cand': None, 'recruiter_name': None, 'training': [], 'sheet_cards': [], 'current_batch': None, 'current_course': None}
    if not candidate_id:
        return empty
    try:
        cand = query_db('SELECT * FROM Candidates WHERE CandidateID=?', (candidate_id,), one=True)
    except Exception:
        return empty
    if not cand:
        return empty
    recruiter_name = None
    if cand.get('SalesAgentID'):
        try:
            r = query_db('SELECT FullName, Username FROM Users_1 WHERE UserID=?', (cand['SalesAgentID'],), one=True)
            if r:
                recruiter_name = r.get('FullName') or r.get('Username')
        except Exception:
            pass
    training = []
    try:
        training = query_db('''
            SELECT TOP 3 B.BatchName, C.CourseName, E.Status, E.EnrollmentDate
            FROM Enrollments E
            JOIN CourseBatches B ON E.BatchID = B.BatchID
            JOIN Courses C ON B.CourseID = C.CourseID
            WHERE E.CandidateID = ?
            ORDER BY E.EnrollmentDate DESC
        ''', (candidate_id,)) or []
    except Exception:
        pass
    sheet_specs = [
        ('GA Interviews', 'GA — مقابلة', ['Date', 'Time', 'CEFR', 'Grad Stat', 'Status', 'Language comments']),
        ('Booking Placements Sheet', 'سجل الحجز', ['Booked for', 'Pay Status', 'Placement reason', 'Venue', 'Source']),
        ('Exit Make-Up', 'Exit Make-Up', ['Wave', 'CEFR', 'Status', 'Closing Status', 'Language comments']),
    ]
    sheet_cards = []
    try:
        rows = query_db('SELECT SheetName, JsonData FROM TraineeSheetData WHERE CandidateID=?', (candidate_id,))
        by_name = {r['SheetName']: r.get('JsonData') for r in (rows or [])}
        for sheet_key, ar_label, fields in sheet_specs:
            raw = by_name.get(sheet_key)
            if not raw:
                continue
            try:
                data = json.loads(raw) if isinstance(raw, str) else raw
                if not isinstance(data, list) or not data:
                    continue
                last = data[-1]
                if not isinstance(last, dict):
                    continue
                lines = []
                for k in fields:
                    v = last.get(k)
                    if v is not None and str(v).strip():
                        lines.append(f'{k}: {v}')
                if lines:
                    sheet_cards.append({'key': sheet_key, 'title_ar': ar_label, 'lines': lines[:8]})
            except Exception:
                continue
    except Exception:
        pass
    out = {
        'cand': cand,
        'recruiter_name': recruiter_name,
        'training': training,
        'sheet_cards': sheet_cards,
        'current_batch': None,
        'current_course': None,
    }
    if current_batch:
        out['current_batch'] = current_batch.get('BatchName')
        out['current_course'] = current_batch.get('CourseName')
    return out


@app.route('/talent/evaluate/<int:slot_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Talent', 'Manager', 'Talent_Recruitment', 'Talent_Training', 'TA-Training'])
def talent_evaluate(slot_id):
    slot = query_db("""
        SELECT T.*, C.CandidateID, C.FullName, C.Phone, C.Email, C.Age, C.Status, C.CurrentCEFR, C.PrimaryIntent,
               C.RecruiterFeedback, C.MarketingAssessment,
               C.TrainingLeadSubtype, C.TrainToHire_Link_Degree, C.TrainToHire_Link_AltEmail,
               C.TrainToHire_Link_IdCard, C.TrainToHire_Link_Contract,
               C.UniversityCollege, C.ResidenceArea, C.BirthDate, C.SourceChannel, C.GraduationStatus
        FROM TASchedules T 
        JOIN Candidates C ON T.CandidateID = C.CandidateID 
        WHERE T.SlotID = ?
    """, (slot_id,), one=True)
    
    if not slot:
        flash('Slot not found', 'danger')
        return redirect(url_for('talent_dashboard'))
    
    eval_type = 'General'
    if session.get('role') == 'Talent_Recruitment':
        eval_type = 'Recruitment'
    elif session.get('role') in ('Talent_Training', 'TA-Training'):
        eval_type = 'Training'
    cefr_options, cefr_track = _cefr_options_for_talent_evaluate(slot, eval_type)
    eval_sidebar = _talent_evaluate_sidebar_context(slot['CandidateID'])

    if request.method == 'POST':
        f = request.form
        cefr = (f.get('cefr_level') or '').strip()
        decision_raw = (f.get('decision') or '').strip()
        decision = _normalize_ta_training_decision(decision_raw) if eval_type == 'Training' else decision_raw
        if eval_type == 'Training' and decision_raw == TA_TRAINING_LEGACY_TRAINING_DECISION:
            decision = 'Accepted'
        if not cefr or not decision:
            flash('CEFR Level and Decision are required', 'warning')
            return render_template('talent/evaluate.html', slot=slot, eval_type=eval_type, cefr_options=cefr_options, cefr_track=cefr_track, exam_kind=None, exam_label_ar=None, eval_subtype=None, from_exam_feedback=False, eval_sidebar=eval_sidebar)
        
        score_c = _safe_int(f.get('score_c'))
        score_f = _safe_int(f.get('score_f'))
        score_p = _safe_int(f.get('score_p'))
        score_s = _safe_int(f.get('score_g'))  # Form uses score_g (Grammar) -> DB Score_Structure
        score_v = _safe_int(f.get('score_v'))
        comments = (f.get('comments') or '')[:4000]
        recommended_level = (f.get('recommended_level') or '').strip() or None
        recording_link = (f.get('recording_link') or '').strip() or None
        insert_eval_type = EVAL_TRAINING_PLACEMENT if eval_type == 'Training' else eval_type

        # Guard against SQL Server truncation errors (8152) across differing DB schemas
        cefr = (cefr or '')[:10]
        decision_to_save = (decision if eval_type == 'Training' else decision_raw)[:50]
        recommended_level = (recommended_level[:50] if recommended_level else None)
        insert_eval_type = (insert_eval_type or '')[:50]
        recording_link = (recording_link[:500] if recording_link else None)
        
        try:
            query_db('''
                INSERT INTO Evaluations (CandidateID, SlotID, Score_Comprehension, Score_Fluency, Score_Pronunciation,
                                         Score_Structure, Score_Vocabulary, CEFR_Level, Decision, RecommendedLevel, Comments, EvaluatorID, EvaluationType, RecordingLink, EvaluationDate)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?, GETDATE())
            ''', (slot['CandidateID'], slot_id, score_c, score_f, score_p, score_s, score_v,
                  cefr, decision_to_save, recommended_level, comments, session['user_id'], insert_eval_type, recording_link))
            fin_dec = decision if eval_type == 'Training' else decision_raw
            slot_status = 'No Show' if (eval_type == 'Training' and fin_dec == 'No Show') else 'Completed'
            query_db("UPDATE TASchedules SET Status=? WHERE SlotID=?", (slot_status, slot_id))
            query_db("UPDATE Candidates SET CurrentCEFR=?, Status=? WHERE CandidateID=?", (cefr, 'Evaluated', slot['CandidateID']))
            if eval_type == 'Training':
                _training_apply_post_ta_decision(
                    slot['CandidateID'],
                    decision if eval_type == 'Training' else decision_raw,
                    _candidate_training_lead_subtype(slot),
                    insert_eval_type,
                )
            flash('تم حفظ التقييم بنجاح', 'success')
            sd = slot.get('SlotDate')
            dstr = sd.strftime('%Y-%m-%d') if sd and hasattr(sd, 'strftime') else (str(sd)[:10] if sd else datetime.today().strftime('%Y-%m-%d'))
            return _talent_dashboard_redirect_after_slot_action(slot_row=slot, date_str=dstr)
        except Exception as e:
            flash(f'خطأ عند حفظ التقييم: {str(e)}', 'danger')
            return render_template('talent/evaluate.html', slot=slot, eval_type=eval_type, cefr_options=cefr_options, cefr_track=cefr_track, exam_kind=None, exam_label_ar=None, eval_subtype=None, from_exam_feedback=False, eval_sidebar=eval_sidebar)
    
    return render_template('talent/evaluate.html', slot=slot, eval_type=eval_type, cefr_options=cefr_options, cefr_track=cefr_track, exam_kind=None, exam_label_ar=None, eval_subtype=None, from_exam_feedback=False, eval_sidebar=eval_sidebar)

@app.route('/sales/book_slot', methods=['POST'])
@login_required
def book_ta_slot():
    try:
        slot_id = request.form['slot_id']
        candidate_id = request.form['candidate_id']
        # Default to Zoom if not provided (backward compatibility)
        interview_type = request.form.get('interview_type', 'Zoom') 
        
        query_db(
            f"""
            UPDATE TASchedules SET Status='Booked', CandidateID=?, BookedBy=?, Type='Initial Assessment', InterviewType=?
            WHERE SlotID=? {_SQL_TA_A_RECRUITER_BOOKING.strip()}
            """,
            (candidate_id, session['user_id'], interview_type, slot_id),
        )
        
        # EMAIL NOTIFICATION: Notify TA (Evaluator)
        slot = query_db("SELECT T.SlotDate, T.SlotTime, U.Email, U.Username, C.FullName FROM TASchedules T JOIN Users_1 U ON T.EvaluatorID = U.UserID JOIN Candidates C ON T.CandidateID = C.CandidateID WHERE T.SlotID=?", (slot_id,), one=True)
        if slot and slot['Email']:
            notify_slot_booking(slot['Email'], slot['Username'], slot['FullName'], slot['SlotDate'], slot['SlotTime'])
            
        flash('Slot Booked Successfully', 'success')
    except Exception as e:
        flash(f'Error Booking Slot: {e}', 'danger')
        
    return redirect(url_for('sales_index'))

@app.route('/talent/mark_no_show', methods=['POST'])
@login_required
def mark_no_show():
    slot_id = request.form['slot_id']
    reason = request.form['reason'] # No Answer, Didn't Join Zoom, etc.
    slot_meta = query_db(
        "SELECT SlotDate, AssessmentContext FROM TASchedules WHERE SlotID=?",
        (slot_id,),
        one=True,
    )

    # 1. Update Slot Status
    query_db("UPDATE TASchedules SET Status='No Show' WHERE SlotID=?", (slot_id,))
    
    # 1b. مسار التدريب: إرجاع الليد للمبيعات لإعادة الجدولة
    slot_c = query_db("SELECT CandidateID FROM TASchedules WHERE SlotID=?", (slot_id,), one=True)
    if slot_c and _taschedule_is_training_context(slot_meta):
        try:
            crow = query_db(
                "SELECT PrimaryIntent, Status FROM Candidates WHERE CandidateID=?",
                (slot_c['CandidateID'],),
                one=True,
            )
            if _is_training_candidate_row(crow):
                query_db(
                    """
                    UPDATE Candidates SET TrainingSalesQueue = ?, TrainingTA_Substatus = NULL
                    WHERE CandidateID = ?
                    """,
                    (TRAINING_QUEUE_RETURN_SALES, slot_c['CandidateID']),
                )
        except Exception:
            pass

    # 2. Notify Sales Agent (Create Alert/Notification)
    # We fetch the Sales Agent ID from the Candidate
    slot = query_db("SELECT CandidateID FROM TASchedules WHERE SlotID=?", (slot_id,), one=True)
    if slot:
        candidate = query_db("SELECT SalesAgentID, FullName FROM Candidates WHERE CandidateID=?", (slot['CandidateID'],), one=True)
        if candidate and candidate['SalesAgentID']:
            msg = f"Urgent: Candidate {candidate['FullName']} missed appointment. Reason: {reason}"
            query_db("INSERT INTO Notifications (UserID, Message, Type, RelatedID, CreatedAt) VALUES (?, ?, 'Alert', ?, GETDATE())", 
                     (candidate['SalesAgentID'], msg, slot_id))
            
            # EMAIL NOTIFICATION: Notify Sales Agent
            agent = query_db("SELECT Email, Username FROM Users_1 WHERE UserID=?", (candidate['SalesAgentID'],), one=True)
            if agent and agent['Email']:
                notify_no_show(agent['Email'], agent['Username'], candidate['FullName'], reason)
            
    flash('Marked as No Show. Sales Agent Notified.', 'warning')
    sd = slot_meta.get('SlotDate') if slot_meta else None
    dstr = sd.strftime('%Y-%m-%d') if sd and hasattr(sd, 'strftime') else (str(sd)[:10] if sd else datetime.today().strftime('%Y-%m-%d'))
    return _talent_dashboard_redirect_after_slot_action(
        slot_row=slot_meta,
        date_str=dstr,
        form_talent_context=request.form.get('talent_context'),
    )


@app.route('/talent/block_slot', methods=['POST'])
@login_required
@role_required(['Talent', 'Manager', 'Talent_Recruitment', 'Talent_Training', 'TA-Training'])
def block_ta_slot():
    # Allow TA to block their own slots
    slot_id = request.form['slot_id']
    query_db("UPDATE TASchedules SET Status='Blocked' WHERE SlotID=? AND EvaluatorID=?", (slot_id, session['user_id']))
    flash('Slot Blocked', 'warning')
    if 'talent_context' in request.form:
        return _talent_book_self_redirect_from_form()
    return redirect(request.referrer or url_for('talent_dashboard'))

@app.route('/talent/book_self')
@login_required
@role_required(['Talent', 'Manager', 'Talent_Recruitment', 'Talent_Training', 'TA-Training'])
def talent_book_self():
    """شاشة حجز مواعيد لنفسه — المختبر يعرض مواعيده المتاحة ويحظرها أو ينشئ مواعيد جديدة."""
    user_id = session['user_id']
    selected_date = request.args.get('date') or datetime.today().strftime('%Y-%m-%d')
    ui_ctx = _talent_schedule_ui_context()
    ctx_f, _ctx_pt_unused = _talent_schedule_sql_filters(ui_ctx)
    try:
        my_available = query_db(f"""
            SELECT T.SlotID, T.SlotDate, T.SlotTime, T.Status
            FROM TASchedules T
            WHERE T.EvaluatorID = ? AND T.SlotDate >= CAST(GETDATE() AS DATE) AND T.Status IN ('Available', 'Blocked')
            {ctx_f}
            ORDER BY T.SlotDate, T.SlotTime
        """, (user_id,)) or []
    except Exception:
        my_available = []
    batches_with_exams = []
    try:
        batches_with_exams = query_db("""
            SELECT B.BatchID, B.BatchName, C.CourseName, B.StartDate, B.EndDate,
                   BE.ExamDateID, BE.ExamDate, BE.ExamLabel
            FROM CourseBatches B
            JOIN Courses C ON B.CourseID = C.CourseID
            JOIN BatchExamDates BE ON BE.BatchID = B.BatchID
            WHERE B.Status = 'Active' AND BE.ExamDate >= CAST(GETDATE() AS DATE)
            ORDER BY BE.ExamDate
        """) or []
    except Exception:
        pass
    exam_dates_today = [b for b in batches_with_exams if str(b.get('ExamDate', ''))[:10] == selected_date]
    try:
        active_waves = query_db("""
            SELECT B.BatchID, B.BatchName, C.CourseName
            FROM CourseBatches B
            JOIN Courses C ON B.CourseID = C.CourseID
            WHERE B.Status = 'Active'
            ORDER BY B.BatchName
        """) or []
    except Exception:
        active_waves = []
    ctx_label = 'training' if ui_ctx == TA_CTX_TRAINING else 'recruitment'
    return render_template(
        'talent/book_self.html',
        slots=my_available or [],
        batches_with_exams=batches_with_exams,
        exam_dates_today=exam_dates_today,
        selected_date=selected_date,
        active_waves=active_waves,
        talent_schedule_context=ctx_label,
    )

@app.route('/talent/add_self_slot', methods=['POST'])
@login_required
@role_required(['Talent', 'Manager', 'Talent_Recruitment', 'Talent_Training', 'TA-Training'])
def talent_add_self_slot():
    """إضافة موعد شاغر للمختبر (لحظره لاحقاً)."""
    user_id = session['user_id']
    slot_date = request.form.get('slot_date')
    slot_time = request.form.get('slot_time')
    if not slot_date or not slot_time:
        flash('التاريخ والوقت مطلوبان.', 'warning')
        return redirect(url_for('talent_book_self', **_talent_redirect_query(_add_self_slot_context_from_form())))
    _ensure_taschedules_assessment_context_column()
    ctx = _add_self_slot_context_from_form()
    if ctx == TA_CTX_TRAINING:
        ex_sql = (
            "SELECT SlotID FROM TASchedules WHERE EvaluatorID=? AND SlotDate=? AND SlotTime=? "
            "AND AssessmentContext = N'Training'"
        )
        ins_sql = (
            "INSERT INTO TASchedules (SlotDate, SlotTime, Status, EvaluatorID, AssessmentContext) "
            "VALUES (?, ?, 'Blocked', ?, N'Training')"
        )
    else:
        ex_sql = (
            "SELECT SlotID FROM TASchedules WHERE EvaluatorID=? AND SlotDate=? AND SlotTime=? "
            "AND AssessmentContext = N'Recruitment'"
        )
        ins_sql = (
            "INSERT INTO TASchedules (SlotDate, SlotTime, Status, EvaluatorID, AssessmentContext) "
            "VALUES (?, ?, 'Blocked', ?, N'Recruitment')"
        )
    existing = query_db(ex_sql, (user_id, slot_date, slot_time), one=True)
    rq = _talent_redirect_query(ctx)
    if existing:
        flash('هذا الموعد موجود مسبقاً.', 'info')
        return redirect(url_for('talent_book_self', **rq))
    query_db(ins_sql, (slot_date, slot_time, user_id))
    flash('تم إضافة الموعد وحظره بنجاح.', 'success')
    return redirect(url_for('talent_book_self', date=slot_date, **rq))

@app.route('/talent/exam_feedback/<int:batch_id>')
@login_required
@role_required(['Talent', 'Manager', 'Talent_Recruitment', 'Talent_Training', 'TA-Training'])
def talent_exam_feedback(batch_id):
    """زر فيدباك — في أيام الامتحانات يفتح تقييم كاختبار عادي لطالب من الدفعة."""
    batch = query_db("SELECT B.*, C.CourseName FROM CourseBatches B JOIN Courses C ON B.CourseID = C.CourseID WHERE B.BatchID=?", (batch_id,), one=True)
    if not batch:
        flash('الدفعة غير موجودة.', 'danger')
        if session.get('role') in ('Talent_Training', 'TA-Training', 'Manager'):
            return redirect(url_for('talent_dashboard', context='training'))
        return redirect(url_for('talent_dashboard', context='recruitment'))
    is_archived = (batch.get('Status') or '').strip() != 'Active'
    session_date = (request.args.get('session_date') or '').strip() or datetime.today().strftime('%Y-%m-%d')
    raw_students = query_db(
        """
        SELECT E.EnrollmentID, E.CandidateID, C.FullName, C.Phone, C.CurrentCEFR,
               ATT.Status AS TrainerAttendanceStatus
        FROM Enrollments E
        JOIN Candidates C ON E.CandidateID = C.CandidateID
        LEFT JOIN Attendance ATT ON ATT.EnrollmentID = E.EnrollmentID AND ATT.Date = CAST(? AS DATE)
        WHERE E.BatchID = ? AND E.Status = 'Active'
        ORDER BY C.FullName
        """,
        (session_date, batch_id),
    ) or []
    students = []
    for row in raw_students:
        tas = (row.get('TrainerAttendanceStatus') or "").strip()
        ad = _trainer_attendance_display(tas)
        students.append(
            {
                'EnrollmentID': row['EnrollmentID'],
                'CandidateID': row['CandidateID'],
                'FullName': row['FullName'],
                'Phone': row.get('Phone'),
                'CurrentCEFR': row.get('CurrentCEFR'),
                'trainer_attendance_label_ar': ad['label_ar'],
                'trainer_attendance_badge_classes': ad['badge_classes'],
                'exam_allowed_by_attendance': ad['allows_exam'],
            }
        )
    return render_template(
        'talent/exam_feedback.html',
        batch=batch,
        students=students,
        is_archived=is_archived,
        session_date=session_date,
    )


@app.route('/talent/exam_feedback/<int:batch_id>/presence', methods=['POST'])
@login_required
@role_required(['Talent', 'Manager', 'Talent_Recruitment', 'Talent_Training', 'TA-Training', 'Trainer', 'TrainingCoordinator', 'TrainingSalesCoordinator', 'TrainingLead'])
def talent_exam_feedback_save_presence(batch_id):
    """موقوف: الحضور الفعلي من شاشة التدريب Attendance (المدرب/الكواوبريشن) فقط."""
    session_date = (request.form.get('session_date') or '').strip()
    flash(
        'تسجيل الحضور الفعلي من قائمة التدريب «Attendance» (المدرب أو منسق/كواوبريشن التدريب) — لا يُعدّه مختبر المواهب هنا.',
        'info',
    )
    if (request.form.get('from_dashboard') or '').strip() == '1':
        return redirect(
            url_for(
                'talent_dashboard',
                context='training',
                date=session_date or datetime.today().strftime('%Y-%m-%d'),
            ),
        )
    return redirect(
        url_for(
            'talent_exam_feedback',
            batch_id=batch_id,
            session_date=session_date or datetime.today().strftime('%Y-%m-%d'),
        ),
    )


@app.route('/talent/exam_feedback/<int:batch_id>/evaluate/<int:candidate_id>', defaults={'exam_kind': 'periodic'}, methods=['GET', 'POST'])
@app.route('/talent/exam_feedback/<int:batch_id>/evaluate/<int:candidate_id>/<exam_kind>', methods=['GET', 'POST'])
@login_required
@role_required(['Talent', 'Manager', 'Talent_Recruitment', 'Talent_Training', 'TA-Training'])
def talent_exam_feedback_evaluate(batch_id, candidate_id, exam_kind='periodic'):
    """تقييم من الدفعة: دوري / تخرج / إعادة / Exit Make-Up — يُحفظ في EvaluationType."""
    session_date = (request.args.get('session_date') or request.form.get('session_date') or '').strip() or datetime.today().strftime('%Y-%m-%d')
    ek = (exam_kind or 'periodic').strip().lower().replace('-', '_')
    if ek == 'exit makeup':
        ek = 'exit_makeup'
    if ek not in ('periodic', 'graduation', 'redo', 'exit_makeup'):
        ek = 'periodic'
    enroll = query_db(
        "SELECT EnrollmentID FROM Enrollments WHERE BatchID=? AND CandidateID=? AND Status='Active'",
        (batch_id, candidate_id),
        one=True,
    )
    if enroll:
        try:
            st_att = _trainer_attendance_status(enroll['EnrollmentID'], session_date)
            if _trainer_attendance_blocks_batch_exam(st_att):
                flash(
                    'لا يُسمح بتسجيل الامتحان: الحضور الفعلي لهذا اليوم «غائب» أو «معذور» (من Training > Attendance).',
                    'warning',
                )
                return redirect(url_for('talent_exam_feedback', batch_id=batch_id, session_date=session_date))
            if not _trainer_attendance_allows_batch_exam(st_att):
                flash(
                    'لم يُسجَّل حضور فعلي لهذا اليوم — يسجّله المدرب أو الكواوبريشن من قائمة التدريب «Attendance» أولاً (حاضر أو متأخر).',
                    'warning',
                )
                return redirect(url_for('talent_exam_feedback', batch_id=batch_id, session_date=session_date))
        except Exception:
            pass
    cand = query_db(
        """
        SELECT CandidateID, FullName, Phone, Email, Age, Status, CurrentCEFR, PrimaryIntent,
               TrainingLeadSubtype, TrainToHire_Link_Degree, TrainToHire_Link_AltEmail,
               TrainToHire_Link_IdCard, TrainToHire_Link_Contract
        FROM Candidates WHERE CandidateID=?
        """,
        (candidate_id,),
        one=True,
    )
    batch = query_db("SELECT B.*, C.CourseName FROM CourseBatches B JOIN Courses C ON B.CourseID = C.CourseID WHERE B.BatchID=?", (batch_id,), one=True)
    if not cand or not batch:
        flash('المرشح أو الدفعة غير موجودين.', 'danger')
        return redirect(url_for('talent_exam_feedback', batch_id=batch_id, session_date=session_date))
    eval_subtype = _exam_kind_to_eval_type(ek)
    eval_display = 'Training'
    slot_dict = {k: cand[k] for k in cand} if cand else {}
    cefr_options, cefr_track = _cefr_options_for_talent_evaluate(slot_dict, eval_subtype)
    _exam_labels = {
        'periodic': 'تقييم دوري',
        'graduation': 'اختبار تخرج',
        'redo': 'اختبار إعادة (Redo)',
        'exit_makeup': 'Exit Make-Up',
    }
    exam_label_ar = _exam_labels.get(ek, 'تقييم')
    eval_sidebar = _talent_evaluate_sidebar_context(candidate_id, current_batch=batch)
    if request.method == 'POST':
        f = request.form
        session_date = (f.get('session_date') or session_date).strip() or datetime.today().strftime('%Y-%m-%d')
        ek = (f.get('exam_kind') or ek).strip().lower().replace('-', '_')
        if ek == 'exit makeup':
            ek = 'exit_makeup'
        if ek not in ('periodic', 'graduation', 'redo', 'exit_makeup'):
            ek = 'periodic'
        eval_subtype = _exam_kind_to_eval_type(ek)
        exam_label_ar = _exam_labels.get(ek, 'تقييم')
        cefr_options, cefr_track = _cefr_options_for_talent_evaluate(slot_dict, eval_subtype)
        eval_sidebar = _talent_evaluate_sidebar_context(candidate_id, current_batch=batch)
        cefr = (f.get('cefr_level') or '').strip()
        decision_raw = (f.get('decision') or '').strip()
        decision = _normalize_ta_training_decision(decision_raw)
        if decision_raw == TA_TRAINING_LEGACY_TRAINING_DECISION:
            decision = 'Accepted'
        if not cefr or not decision:
            flash('CEFR Level و Decision مطلوبان.', 'warning')
            return render_template(
                'talent/evaluate.html', slot=slot_dict, eval_type=eval_display, cefr_options=cefr_options, cefr_track=cefr_track,
                from_exam_feedback=True, batch_id=batch_id, candidate_id=candidate_id, exam_kind=ek, exam_label_ar=exam_label_ar,
                eval_subtype=eval_subtype, eval_sidebar=eval_sidebar, exam_session_date=session_date,
            )
        score_c = _safe_int(f.get('score_c'))
        score_f = _safe_int(f.get('score_f'))
        score_p = _safe_int(f.get('score_p'))
        score_s = _safe_int(f.get('score_g'))
        score_v = _safe_int(f.get('score_v'))
        comments = (f.get('comments') or '')[:4000]
        recommended_level = (f.get('recommended_level') or '').strip() or None
        recording_link = (f.get('recording_link') or '').strip() or None
        slot_type = f"Exam Feedback ({ek})"

        # Guard against SQL Server truncation errors (8152) across differing DB schemas
        cefr = (cefr or '')[:10]
        decision = (decision or '')[:50]
        recommended_level = (recommended_level[:50] if recommended_level else None)
        eval_subtype = (eval_subtype or '')[:50]
        recording_link = (recording_link[:500] if recording_link else None)
        try:
            db = get_db()
            cur = db.cursor()
            syn_status = 'No Show' if decision == 'No Show' else 'Completed'
            cur.execute("""
                INSERT INTO TASchedules (SlotDate, SlotTime, Status, EvaluatorID, CandidateID, Type, InterviewType, AssessmentContext)
                VALUES (CAST(? AS DATE), CONVERT(VARCHAR(5), GETDATE(), 108), ?, ?, ?, ?, N'Training', N'Training')
            """, (session_date, syn_status, session['user_id'], candidate_id, slot_type))
            cur.execute("SELECT SCOPE_IDENTITY()")
            row = cur.fetchone()
            slot_id = int(row[0]) if row and row[0] else None
            db.commit()
            cur.close()
            if slot_id:
                query_db('''
                    INSERT INTO Evaluations (CandidateID, SlotID, Score_Comprehension, Score_Fluency, Score_Pronunciation,
                                         Score_Structure, Score_Vocabulary, CEFR_Level, Decision, RecommendedLevel, Comments, EvaluatorID, EvaluationType, RecordingLink, EvaluationDate)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?, GETDATE())
                ''', (candidate_id, slot_id, score_c, score_f, score_p, score_s, score_v, cefr, decision, recommended_level, comments, session['user_id'], eval_subtype, recording_link))
                query_db("UPDATE Candidates SET CurrentCEFR=?, Status=? WHERE CandidateID=?", (cefr, 'Evaluated', candidate_id))
                _training_apply_post_ta_decision(
                    candidate_id, decision, _candidate_training_lead_subtype(cand), eval_subtype,
                )
                flash('تم حفظ ' + exam_label_ar + ' بنجاح.', 'success')
            else:
                flash('خطأ في الحصول على SlotID.', 'danger')
            return redirect(url_for('talent_exam_feedback', batch_id=batch_id, session_date=session_date))
        except Exception as e:
            flash(f'خطأ: {str(e)[:80]}', 'danger')
            return render_template(
                'talent/evaluate.html', slot=slot_dict, eval_type=eval_display, cefr_options=cefr_options, cefr_track=cefr_track,
                from_exam_feedback=True, batch_id=batch_id, candidate_id=candidate_id, exam_kind=ek, exam_label_ar=exam_label_ar,
                eval_subtype=eval_subtype, eval_sidebar=eval_sidebar, exam_session_date=session_date,
            )
    return render_template(
        'talent/evaluate.html', slot=slot_dict, eval_type=eval_display, cefr_options=cefr_options, cefr_track=cefr_track,
        from_exam_feedback=True, batch_id=batch_id, candidate_id=candidate_id, exam_kind=ek, exam_label_ar=exam_label_ar,
        eval_subtype=eval_subtype, eval_sidebar=eval_sidebar, exam_session_date=session_date,
    )

@app.route('/talent/training_completed_tests')
@login_required
@role_required(['Talent_Training', 'TA-Training', 'Manager', 'Talent', 'Talent_Recruitment'])
def talent_training_completed_tests():
    """ليدز التدريب الذين أُنجز لهم اختبار المواهب — مع اسم المختبر."""
    rows = []
    try:
        params = (
            EVAL_TRAINING_PLACEMENT,
            EVAL_TRAINING_PERIODIC,
            EVAL_TRAINING_GRADUATION,
            EVAL_TRAINING_REDO,
            EVAL_TRAINING_EXIT_MAKEUP,
            'Training',
        )
        in6 = 'IN (?, ?, ?, ?, ?, ?)'
        queries = [
            (
                f"""
            SELECT E.EvaluationID, E.CandidateID, E.CEFR_Level, E.Decision, E.EvaluationType,
                   E.EvaluationDate AS EvaluationDate,
                   C.FullName, C.Phone, C.Email, C.Status, C.PrimaryIntent,
                   U.FullName AS EvaluatorName, U.Username AS EvaluatorUsername
            FROM Evaluations E
            INNER JOIN Candidates C ON E.CandidateID = C.CandidateID
            LEFT JOIN Users_1 U ON E.EvaluatorID = U.UserID
            WHERE E.EvaluationType {in6}
            ORDER BY E.EvaluationDate DESC, E.EvaluationID DESC
            """,
                params,
            ),
            (
                f"""
            SELECT E.EvaluationID, E.CandidateID, E.CEFR_Level, E.Decision, E.EvaluationType,
                   COALESCE(E.EvaluationDate, E.CreatedAt) AS EvaluationDate,
                   C.FullName, C.Phone, C.Email, C.Status, C.PrimaryIntent,
                   U.FullName AS EvaluatorName, U.Username AS EvaluatorUsername
            FROM Evaluations E
            INNER JOIN Candidates C ON E.CandidateID = C.CandidateID
            LEFT JOIN Users_1 U ON E.EvaluatorID = U.UserID
            WHERE E.EvaluationType {in6}
            ORDER BY COALESCE(E.EvaluationDate, E.CreatedAt) DESC, E.EvaluationID DESC
            """,
                params,
            ),
            (
                f"""
            SELECT TOP 800 E.EvaluationID, E.CandidateID, E.CEFR_Level, E.Decision, E.EvaluationType,
                   E.EvaluationDate AS EvaluationDate,
                   C.FullName, C.Phone, C.Email, C.Status, C.PrimaryIntent,
                   CAST(NULL AS NVARCHAR(200)) AS EvaluatorName,
                   CAST(NULL AS NVARCHAR(100)) AS EvaluatorUsername
            FROM Evaluations E
            INNER JOIN Candidates C ON E.CandidateID = C.CandidateID
            WHERE E.EvaluationType {in6}
            ORDER BY E.EvaluationDate DESC, E.EvaluationID DESC
            """,
                params,
            ),
            (
                f"""
            SELECT TOP 800 E.EvaluationID, E.CandidateID, E.CEFR_Level, E.Decision, E.EvaluationType,
                   CAST(NULL AS DATETIME) AS EvaluationDate,
                   C.FullName, C.Phone, C.Email, C.Status, C.PrimaryIntent,
                   CAST(NULL AS NVARCHAR(200)) AS EvaluatorName,
                   CAST(NULL AS NVARCHAR(100)) AS EvaluatorUsername
            FROM Evaluations E
            INNER JOIN Candidates C ON E.CandidateID = C.CandidateID
            WHERE E.EvaluationType {in6}
            ORDER BY E.EvaluationID DESC
            """,
                params,
            ),
        ]
        last_err = None
        query_succeeded = False
        for sql, prm in queries:
            try:
                got = query_db(sql, prm)
                rows = got if got is not None else []
                query_succeeded = True
                break
            except Exception as ex:
                last_err = ex
                continue
        if not query_succeeded and last_err:
            try:
                app.logger.warning('talent_training_completed_tests: all queries failed: %s', last_err)
            except Exception:
                pass
            flash(
                'تعذر الاتصال بقاعدة البيانات أو هيكل الجداول مختلف. راجع سجلات السيرفر.',
                'danger',
            )
    except Exception as outer:
        try:
            app.logger.exception('talent_training_completed_tests: %s', outer)
        except Exception:
            pass
        flash('حدث خطأ أثناء تحميل الصفحة. جرّب لاحقاً أو راجع الاتصال بقاعدة البيانات.', 'danger')

    try:
        return render_template('talent/training_completed_tests.html', rows=rows or [])
    except TemplateNotFound as render_ex:
        try:
            app.logger.error(
                'talent_training_completed_tests: missing template %s — add templates/talent/training_completed_tests.html to the deploy bundle.',
                render_ex,
            )
        except Exception:
            pass
        flash(
            'قالب الصفحة غير موجود على السيرفر (غالباً لم يُرفع مع النشر). أضف الملف إلى Git وادفع ثم أعد النشر.',
            'danger',
        )
        return redirect(url_for('talent_dashboard', context='training'))
    except Exception as render_ex:
        try:
            app.logger.exception('talent_training_completed_tests render: %s', render_ex)
        except Exception:
            pass
        return (
            '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Error</title></head><body>'
            '<p>تعذر عرض الصفحة. ارجع للوحة المواهب.</p></body></html>',
            200,
            {'Content-Type': 'text/html; charset=utf-8'},
        )


EVALUATION_TYPES_EDITABLE = (
    'Recruitment', 'Training', 'Training_Periodic', 'Training_Graduation', 'General',
)


def _merged_cefr_options_for_edit():
    return sorted(set(CEFR_OPTIONS_TRAINING + CEFR_OPTIONS_RECRUITMENT), key=lambda s: (len(s), s.lower()))


@app.route('/talent/tests_registry')
@login_required
@role_required(['Talent', 'Manager', 'Talent_Recruitment', 'Talent_Training', 'TA-Training'])
def talent_tests_registry():
    """All leads with at least one talent evaluation; shows who tested them; links to edit."""
    q = (request.args.get('q') or '').strip()
    base_sql = """
        SELECT TOP 2000 E.EvaluationID, E.CandidateID, E.SlotID,
               E.Score_Comprehension, E.Score_Fluency, E.Score_Pronunciation, E.Score_Structure, E.Score_Vocabulary,
               E.CEFR_Level, E.Decision, E.RecommendedLevel, E.EvaluationType, E.EvaluationDate, E.RecordingLink,
               E.Comments,
               C.FullName, C.Phone, C.Email, C.PrimaryIntent,
               U.FullName AS EvaluatorName, U.Username AS EvaluatorUsername
        FROM Evaluations E
        INNER JOIN Candidates C ON E.CandidateID = C.CandidateID
        LEFT JOIN Users_1 U ON E.EvaluatorID = U.UserID
    """
    if q:
        like = f"%{q}%"
        rows = query_db(
            base_sql + " WHERE (C.FullName LIKE ? OR ISNULL(C.Phone,'') LIKE ? OR CAST(C.CandidateID AS VARCHAR(20)) LIKE ?) ORDER BY E.EvaluationDate DESC",
            (like, like, like),
        )
    else:
        rows = query_db(base_sql + " ORDER BY E.EvaluationDate DESC")
    return render_template('talent/tests_registry.html', rows=rows or [], q=q)


@app.route('/talent/evaluation/<int:evaluation_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['Talent', 'Manager', 'Talent_Recruitment', 'Talent_Training', 'TA-Training'])
def talent_evaluation_edit(evaluation_id):
    row = query_db("""
        SELECT E.*, C.FullName, C.Phone, C.Email,
               U.FullName AS EvaluatorName, U.Username AS EvaluatorUsername
        FROM Evaluations E
        JOIN Candidates C ON E.CandidateID = C.CandidateID
        LEFT JOIN Users_1 U ON E.EvaluatorID = U.UserID
        WHERE E.EvaluationID = ?
    """, (evaluation_id,), one=True)
    if not row:
        flash('التقييم غير موجود.', 'danger')
        return redirect(url_for('talent_tests_registry'))

    cefr_options = _merged_cefr_options_for_edit()

    if request.method == 'POST':
        f = request.form
        cefr = (f.get('cefr_level') or '').strip()
        decision = (f.get('decision') or '').strip()
        eval_type = (f.get('evaluation_type') or '').strip()
        if eval_type not in EVALUATION_TYPES_EDITABLE:
            eval_type = ((row.get('EvaluationType') or 'General').strip() or 'General')
            if eval_type not in EVALUATION_TYPES_EDITABLE:
                eval_type = 'General'
        comments = (f.get('comments') or '')[:4000]
        recording_link = (f.get('recording_link') or '').strip() or None
        recommended_level = (f.get('recommended_level') or '').strip() or None
        score_c = _safe_int(f.get('score_c'))
        score_f = _safe_int(f.get('score_f'))
        score_p = _safe_int(f.get('score_p'))
        score_s = _safe_int(f.get('score_g'))
        score_v = _safe_int(f.get('score_v'))
        eval_dt_raw = (f.get('evaluation_date') or '').strip()
        eval_dt = None
        if eval_dt_raw:
            s = eval_dt_raw.replace('Z', '')
            try:
                eval_dt = datetime.fromisoformat(s)
            except ValueError:
                try:
                    eval_dt = datetime.strptime(s[:16], '%Y-%m-%dT%H:%M')
                except ValueError:
                    eval_dt = None
            if eval_dt and getattr(eval_dt, 'tzinfo', None):
                eval_dt = eval_dt.replace(tzinfo=None)
        if not cefr or not decision:
            flash('CEFR والقرار مطلوبان.', 'warning')
            return render_template(
                'talent/evaluation_edit.html',
                row=row,
                cefr_options=cefr_options,
                evaluation_types=EVALUATION_TYPES_EDITABLE,
            )
        try:
            if eval_dt:
                query_db("""
                    UPDATE Evaluations SET
                        Score_Comprehension=?, Score_Fluency=?, Score_Pronunciation=?, Score_Structure=?, Score_Vocabulary=?,
                        CEFR_Level=?, Decision=?, RecommendedLevel=?, Comments=?, EvaluationType=?, RecordingLink=?,
                        EvaluationDate=?
                    WHERE EvaluationID=?
                """, (
                    score_c, score_f, score_p, score_s, score_v,
                    cefr, decision, recommended_level, comments, eval_type, recording_link,
                    eval_dt, evaluation_id,
                ))
            else:
                query_db("""
                    UPDATE Evaluations SET
                        Score_Comprehension=?, Score_Fluency=?, Score_Pronunciation=?, Score_Structure=?, Score_Vocabulary=?,
                        CEFR_Level=?, Decision=?, RecommendedLevel=?, Comments=?, EvaluationType=?, RecordingLink=?
                    WHERE EvaluationID=?
                """, (
                    score_c, score_f, score_p, score_s, score_v,
                    cefr, decision, recommended_level, comments, eval_type, recording_link,
                    evaluation_id,
                ))
            flash('تم تحديث تفاصيل الاختبار.', 'success')
            return redirect(url_for('talent_tests_registry'))
        except Exception as e:
            flash(f'خطأ: {str(e)[:200]}', 'danger')

    return render_template(
        'talent/evaluation_edit.html',
        row=row,
        cefr_options=cefr_options,
        evaluation_types=EVALUATION_TYPES_EDITABLE,
    )


@app.route('/talent/monthly_results')
@login_required
@role_required(['Talent', 'Manager', 'Talent_Recruitment', 'Talent_Training', 'TA-Training'])
def talent_monthly_results():
    """استعراض نتائج التقييمات للشهر الحالي (للمختبر)."""
    user_id = session['user_id']
    results = query_db("""
        SELECT E.EvaluationID, E.CandidateID, E.CEFR_Level, E.Decision, E.Comments, E.EvaluationType,
               C.FullName, T.SlotDate, T.SlotTime
        FROM Evaluations E
        JOIN Candidates C ON E.CandidateID = C.CandidateID
        LEFT JOIN TASchedules T ON E.SlotID = T.SlotID
        WHERE E.EvaluatorID = ?
        AND (T.SlotDate >= DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1) OR T.SlotDate IS NULL)
        ORDER BY T.SlotDate DESC, T.SlotTime DESC
    """, (user_id,))
    return render_template('talent/monthly_results.html', results=results or [])

# --- CORPORATE ---
@app.route('/corporate/dashboard')
@login_required
@role_required(['Corporate', 'Manager'])
def corporate_dashboard():
    stats = {}
    stats['client_count'] = query_db('SELECT COUNT(*) as c FROM Clients', one=True)['c']
    stats['open_requests'] = query_db("SELECT COUNT(*) as c FROM ClientRequests WHERE Status='Open'", one=True)['c']
    stats['active_campaigns'] = query_db("SELECT COUNT(*) as c FROM Campaigns WHERE Type='Linked'", one=True)['c']
    try: stats['total_candidates'] = query_db("SELECT COUNT(*) as c FROM Candidates WHERE IsReadyForMatching=1", one=True)['c'] 
    except: stats['total_candidates'] = 0
    stats['recent_clients'] = query_db('SELECT TOP 5 * FROM Clients ORDER BY CreatedAt DESC')
    stats['recent_requests'] = query_db('SELECT TOP 5 CR.*, C.CompanyName FROM ClientRequests CR JOIN Clients C ON CR.ClientID = C.ClientID WHERE CR.Status=\'Open\' ORDER BY CR.CreatedAt DESC')
    return render_template('corporate/dashboard.html', stats=stats)

@app.route('/corporate/manage')
@login_required
@role_required(['Corporate', 'Manager'])
def corporate_manage():
    clients = query_db('SELECT * FROM Clients')
    requests = query_db('SELECT CR.*, C.CompanyName FROM ClientRequests CR JOIN Clients C ON CR.ClientID = C.ClientID')
    return render_template('corporate/index.html', clients=clients or [], requests=requests or [])

@app.route('/corporate/add_client', methods=('POST',))
@login_required
def add_client():
    query_db('INSERT INTO Clients (CompanyName, Industry, ContactPerson, Email, Phone, Address) VALUES (?,?,?,?,?,?)',
             (request.form['company_name'], request.form['industry'], request.form['contact_person'], request.form['email'], request.form['phone'], request.form['address']))
    flash('Added Client', 'success')
    # Redirect to the referrer to support both Corporate Manager and Recruitment Manager views
    return redirect(request.referrer or url_for('corporate_manage'))

@app.route('/corporate/matching')
@login_required
@role_required(['Corporate', 'Manager', 'AllocationManager'])
def corporate_matching():
    # Open Requests
    requests = query_db("SELECT CR.*, C.CompanyName FROM ClientRequests CR JOIN Clients C ON CR.ClientID = C.ClientID WHERE CR.Status='Open'")
    # Qualified Candidates
    candidates = query_db("SELECT * FROM Candidates WHERE Status IN ('Ready_For_Matching', 'Talent_Pool', 'Ready')")
    return render_template('corporate/matching.html', requests=requests or [], candidates=candidates or [])

@app.route('/corporate/submit_match', methods=['POST'])
@login_required
def corporate_submit_match():
    req_id = request.form.get('request_id')
    cand_ids = request.form.getlist('candidate_ids')
    
    if not req_id or not cand_ids:
        flash('Please select a request and at least one candidate', 'warning')
        return redirect(url_for('corporate_matching'))
        
    for cid in cand_ids:
        # Check if already matched
        existing = query_db("SELECT * FROM Matches WHERE RequestID=? AND CandidateID=?", (req_id, cid), one=True)
        if not existing:
            query_db("INSERT INTO Matches (RequestID, CandidateID, MatchDate, Status) VALUES (?, ?, GETDATE(), 'Proposed')", (req_id, cid))
            
    flash(f'Matched {len(cand_ids)} candidates to request', 'success')
    return redirect(url_for('corporate_matching'))

@app.route('/recruitment/add_request', methods=['POST'])
@login_required
@role_required(['Manager', 'AccountManager', 'AllocationSpecialist', 'Corporate'])
def add_request():
    f = request.form
    # Build a robust INSERT query for all new fields
    # Basic
    client_id = f['client_id']
    title = f['job_title']
    count = f.get('needed_count', 1)
    
    # Financials
    salary_from = f.get('salary_from') or None
    salary_to = f.get('salary_to') or None
    
    # Demographics
    gender = f.get('gender')
    nationality = f.get('nationality')
    age_from = f.get('age_from') or None
    age_to = f.get('age_to') or None
    
    # Location & Shift
    location = f.get('location')
    shift = f.get('shift_type')
    conditions = f.get('working_conditions')
    
    # Profile & Skills
    education = f.get('education_level')
    experience = f.get('experience_years') or 0
    english = f.get('english_level')
    lang3 = f.get('third_language')
    comp = f.get('computer_level')
    reqs = f.get('requirements')
    soft = f.get('soft_skills')
    
    # Other Traits
    smoker = f.get('smoker')
    appearance = f.get('appearance_level')
    physical = f.get('physical_traits')
    allocator_roles = f.getlist('allocator_role')
    allocator_role = ','.join(r.strip() for r in allocator_roles if r and r.strip()) if allocator_roles else None

    _ensure_allocator_role_column()

    try:
        query_db("""
            INSERT INTO ClientRequests (
                ClientID, JobTitle, NeededCount, Status,
                SalaryFrom, SalaryTo, Gender, Nationality, AgeFrom, AgeTo,
                Location, ShiftType, WorkingConditions,
                EducationLevel, ExperienceYears, EnglishLevel, ThirdLanguage, ComputerLevel,
                Requirements, SoftSkills, Smoker, AppearanceLevel, PhysicalTraits, AllocatorRole
            ) VALUES (
                ?, ?, ?, 'Open',
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?
            )
        """, (
            client_id, title, count,
            salary_from, salary_to, gender, nationality, age_from, age_to,
            location, shift, conditions,
            education, experience, english, lang3, comp,
            reqs, soft, smoker, appearance, physical, allocator_role
        ))
    except Exception as e:
        err = str(e)
        if 'AllocatorRole' in err or 'Invalid column' in err or 'column' in err.lower():
            flash('خطأ في قاعدة البيانات: عمود AllocatorRole غير موجود. أعد تشغيل التطبيق لتطبيق التحديثات.', 'danger')
        else:
            flash('خطأ في حفظ طلب العميل: ' + err[:80], 'danger')
        return redirect(url_for('manage_requests'))

    flash('New Job Order Created Successfully', 'success')
    return redirect(url_for('manage_requests'))

@app.route('/recruitment/matching')
@login_required
@role_required(['Recruiter', 'RecruitmentManager', 'Manager', 'AllocationManager', 'AllocationSpecialist', 'Allocator', 'AccountManager'])
def match_candidates():
    """إعادة توجيه لمركز المطابقة الموحد /allocation/matching (مع تمرير request_id إن وُجد)."""
    req_id = request.args.get('request_id')
    if req_id:
        return redirect(url_for('allocation_matching', request_id=req_id))
    return redirect(url_for('allocation_matching'))

@app.route('/corporate/finance/<int:client_id>')
@login_required
@role_required(['Corporate', 'Manager'])
def corporate_finance(client_id):
    client = query_db('SELECT * FROM Clients WHERE ClientID = ?', (client_id,), one=True)
    if not client: return redirect(url_for('corporate_manage'))
    invoices = query_db('SELECT * FROM CorporateInvoices WHERE ClientID = ? ORDER BY IssueDate DESC', (client_id,))
    total_billed = sum(i['Amount'] for i in invoices) if invoices else 0
    payments = query_db('''
        SELECT P.*, I.Description 
        FROM CorporatePayments P 
        JOIN CorporateInvoices I ON P.InvoiceID = I.InvoiceID 
        WHERE I.ClientID = ? 
        ORDER BY P.PaymentDate DESC
    ''', (client_id,))
    total_paid = sum(p['Amount'] for p in payments) if payments else 0
    balance = total_billed - total_paid
    return render_template('corporate/finance.html', client=client, invoices=invoices or [], payments=payments or [], total_billed=total_billed, total_paid=total_paid, balance=balance)

@app.route('/corporate/create_invoice', methods=('POST',))
@login_required
def create_corporate_invoice():
    client_id = request.form['client_id']
    query_db('INSERT INTO CorporateInvoices (ClientID, ServiceType, Description, Amount, DueDate, CreatedBy) VALUES (?,?,?,?,?,?)',
             (client_id, request.form['service_type'], request.form['description'], request.form['amount'], request.form['due_date'], session.get('user_id')))
    flash('تم إصدار الفاتورة', 'success')
    return redirect(url_for('corporate_finance', client_id=client_id))

@app.route('/corporate/add_payment', methods=('POST',))
@login_required
def add_corporate_payment():
    invoice_id = request.form['invoice_id']
    amount = float(request.form['amount'])
    client_id = request.form['client_id']
    query_db('INSERT INTO CorporatePayments (InvoiceID, Amount, PaymentMethod, ReceivedBy) VALUES (?,?,?,?)',
             (invoice_id, amount, request.form['payment_method'], session.get('user_id')))
    inv = query_db('SELECT Amount FROM CorporateInvoices WHERE InvoiceID=?', (invoice_id,), one=True)
    paid = query_db('SELECT SUM(Amount) as P FROM CorporatePayments WHERE InvoiceID=?', (invoice_id,), one=True)['P'] or 0
    new_status = 'Paid' if paid >= inv['Amount'] else 'Partial'
    query_db('UPDATE CorporateInvoices SET Status=? WHERE InvoiceID=?', (new_status, invoice_id))
    flash('تم تسجيل الدفعة', 'success')
    return redirect(url_for('corporate_finance', client_id=client_id))


# --- خريطة المواد: رصيد أول/آخر المدة (TBL007, TBL020, TBL022, TBL023) ---
PRODUCT_BALANCE_SQL = """
;WITH أول AS (
    SELECT ISNULL(SUM(
        CASE WHEN ty.BillKind = 2 THEN ISNULL(t.Quantity, 0) ELSE -ISNULL(t.Quantity, 0) END
    ), 0) AS رصيد
    FROM TBL023 t
    INNER JOIN TBL022 b ON b.CardGuide = t.MainGuide
    LEFT JOIN TBL020 ty ON ty.CardGuide = b.MainGuide
    WHERE t.ProductGuide = ? AND CAST(b.BillDate AS DATE) < ?
),
حركات AS (
    SELECT ISNULL(SUM(
        CASE WHEN ty.BillKind = 2 THEN ISNULL(t.Quantity, 0) ELSE -ISNULL(t.Quantity, 0) END
    ), 0) AS صافي
    FROM TBL023 t
    INNER JOIN TBL022 b ON b.CardGuide = t.MainGuide
    LEFT JOIN TBL020 ty ON ty.CardGuide = b.MainGuide
    WHERE t.ProductGuide = ? AND CAST(b.BillDate AS DATE) >= ? AND CAST(b.BillDate AS DATE) <= ?
)
SELECT (SELECT رصيد FROM أول) AS رصيد_أول_المدة,
       (SELECT رصيد FROM أول) + (SELECT صافي FROM حركات) AS رصيد_آخر_المدة
"""


@app.route('/corporate/materials_map', methods=['GET', 'POST'])
@login_required
def materials_map():
    """شريحة خريطة المواد — التعتيق — عرض رصيد أول المدة ورصيد آخر المدة للصنف (حقل المعتق / Bulk Liquid Sources)."""
    products = []
    balance_row = None
    product_guide = request.args.get('product_guide') or (request.form.get('product_guide') if request.method == 'POST' else None)
    from_date = request.args.get('from_date') or (request.form.get('from_date') if request.method == 'POST' else None) or datetime.now().replace(month=1, day=1).strftime('%Y-%m-%d')
    to_date = request.args.get('to_date') or (request.form.get('to_date') if request.method == 'POST' else None) or datetime.now().strftime('%Y-%m-%d')

    try:
        products = query_db("SELECT CardGuide, ProductName, LatinName FROM TBL007 ORDER BY ProductName") or []
    except Exception:
        products = []

    if product_guide and from_date and to_date:
        try:
            balance_row = query_db(
                PRODUCT_BALANCE_SQL,
                (product_guide, from_date, product_guide, from_date, to_date),
                one=True
            )
        except Exception:
            balance_row = None

    selected_product_name = None
    if product_guide and products:
        for p in products:
            if str(p.get('CardGuide')) == str(product_guide):
                selected_product_name = p.get('ProductName') or p.get('LatinName') or product_guide
                break

    return render_template(
        'corporate/materials_map.html',
        products=products,
        product_guide=product_guide,
        from_date=from_date,
        to_date=to_date,
        balance_row=balance_row,
        selected_product_name=selected_product_name,
    )


@app.route('/recruiter/dashboard')
@login_required
def recruiter_dashboard():
    role = g.user['Role']
    
    # 1. Account Manager View
    if role == 'AccountManager': return redirect(url_for('account_manager_dashboard'))
    # 2. Allocator View
    if role == 'Allocator': return redirect(url_for('allocator_dashboard'))
        
    # 3. Default Recruiter View (PERSONALIZED)
    user_id = session['user_id']
    today = datetime.today().strftime('%Y-%m-%d')
    
    # Personal Metrics
    metrics = {
        'my_ads': query_db("SELECT COUNT(*) as c FROM Campaigns WHERE CreatedBy=?", (user_id,), one=True)['c'],
        'my_candidates': query_db("SELECT COUNT(*) as c FROM Candidates WHERE SalesAgentID=?", (user_id,), one=True)['c'],
        
        # Test Interviews Today (Tests booked for my candidates today)
        'my_tests_today': query_db(f"""
            SELECT COUNT(*) as c 
            FROM TASchedules T 
            JOIN Candidates C ON T.CandidateID = C.CandidateID 
            WHERE C.SalesAgentID = ? AND T.SlotDate = ? AND T.Status = 'Booked'
              {_SQL_TA_T_RECRUITMENT.strip()}
        """, (user_id, today), one=True)['c'],
        
        # Job Interviews Today (Matches in 'Interview' status for today)
        'my_interviews_today': query_db("""
            SELECT COUNT(*) as c 
            FROM Matches M 
            JOIN Candidates C ON M.CandidateID = C.CandidateID
            WHERE C.SalesAgentID = ? AND M.InterviewDate = ? AND M.Status = 'Interview'
        """, (user_id, today), one=True)['c'],

        # Workflow Counts (For Badges)
        'count_new_leads': query_db("SELECT COUNT(*) as c FROM Candidates WHERE SalesAgentID=? AND Status='New'", (user_id,), one=True)['c'],
        'count_tests_pending': query_db(
            f"SELECT COUNT(*) as c FROM TASchedules T JOIN Candidates C ON T.CandidateID=C.CandidateID "
            f"WHERE C.SalesAgentID=? AND T.Status='Booked' {_SQL_TA_T_RECRUITMENT.strip()}",
            (user_id,), one=True)['c'],
        'count_interviews_pending': query_db("SELECT COUNT(*) as c FROM Matches M JOIN Candidates C ON M.CandidateID=C.CandidateID WHERE C.SalesAgentID=? AND M.Status='Interview'", (user_id,), one=True)['c'],
        'count_feedback_needed': query_db("SELECT COUNT(*) as c FROM Matches M JOIN Candidates C ON M.CandidateID=C.CandidateID WHERE C.SalesAgentID=? AND M.Status='Interview' AND M.InterviewDate < ?", (user_id, today), one=True)['c']
    }
    
    # Recent Matches (Personalized)
    recent_matches = query_db("""
        SELECT TOP 10 M.*, C.FullName as CandidateName, Cl.CompanyName, CR.JobTitle, 
               M.Status as MatchStatus, M.InterviewDate
        FROM Matches M
        JOIN Candidates C ON M.CandidateID = C.CandidateID
        JOIN ClientRequests CR ON M.RequestID = CR.RequestID
        JOIN Clients Cl ON CR.ClientID = Cl.ClientID
        WHERE C.SalesAgentID = ?
        ORDER BY M.MatchDate DESC
    """, (user_id,))

    # مقابلات التالنت اليوم — من TASchedules و Schedules (Talent_Recruitment)
    # المرشحون المحوّلون/المحجوزون: SalesAgentID أو RecruiterID أو BookedBy
    ta_slots = query_db(f"""
        SELECT T.SlotID, T.SlotDate, T.SlotTime, T.Status, C.CandidateID, C.FullName, C.Phone, U.FullName as EvaluatorName
        FROM TASchedules T
        JOIN Candidates C ON T.CandidateID = C.CandidateID
        LEFT JOIN Users_1 U ON T.EvaluatorID = U.UserID
        WHERE (C.SalesAgentID = ? OR C.RecruiterID = ? OR T.BookedBy = ?)
          AND CAST(T.SlotDate AS DATE) = CAST(? AS DATE)
          AND T.Status IN ('Booked', 'Completed')
          {_SQL_TA_T_RECRUITMENT.strip()}
        ORDER BY T.SlotTime
    """, (user_id, user_id, user_id, today))
    try:
        sched_slots = query_db("""
            SELECT S.ScheduleID as SlotID, S.SlotDate, S.SlotTime, S.Status, C.CandidateID, C.FullName, C.Phone, U.FullName as EvaluatorName
            FROM Schedules S
            JOIN Candidates C ON S.BookedCandidateID = C.CandidateID
            LEFT JOIN Users_1 U ON S.OwnerUserID = U.UserID
            WHERE S.Context = 'Talent_Recruitment' AND S.Status = 'Booked'
              AND (C.SalesAgentID = ? OR C.RecruiterID = ?)
              AND CAST(S.SlotDate AS DATE) = CAST(? AS DATE)
            ORDER BY S.SlotTime
        """, (user_id, user_id, today))
    except Exception:
        sched_slots = []
    # دمج وإزالة التكرار حسب (CandidateID, SlotDate, SlotTime) وترتيب بالوقت
    seen = set()
    combined = []
    for row in (ta_slots or []) + (sched_slots or []):
        key = (row.get('CandidateID'), str(row.get('SlotDate', '')), str(row.get('SlotTime', '')))
        if key not in seen:
            seen.add(key)
            combined.append(row)
    talent_interviews_today = sorted(combined, key=lambda r: (r.get('SlotDate') or '', r.get('SlotTime') or ''))

    return render_template('recruitment/dashboard.html', metrics=metrics, recent_matches=recent_matches or [],
                          talent_interviews_today=talent_interviews_today or [])

@app.route('/recruiter/hiring_onboarding')
@login_required
def recruiter_hiring_onboarding():
    # Show candidates who passed the client interview (Status='Accepted')
    try:
        hired_candidates = query_db("""
            SELECT M.*, C.FullName, C.Phone, CR.JobTitle, Cl.CompanyName
            FROM Matches M
            JOIN Candidates C ON M.CandidateID = C.CandidateID
            JOIN ClientRequests CR ON M.RequestID = CR.RequestID
            JOIN Clients Cl ON CR.ClientID = Cl.ClientID
            WHERE M.Status = 'Accepted'
            AND NOT EXISTS (SELECT 1 FROM HiringRecords H WHERE H.MatchID = M.MatchID)
        """)
    except Exception as e:
        if getattr(g, 'db', None) is None:
            flash('لا يمكن الاتصال بقاعدة البيانات. تحقق من الإعدادات.', 'danger')
        else:
            flash(f'خطأ في تحميل البيانات: {str(e)[:100]}', 'danger')
        hired_candidates = []
    return render_template('recruitment/hiring_onboarding.html', candidates=hired_candidates or [])

@app.route('/recruiter/finalize_hiring', methods=['POST'])
@login_required
def finalize_hiring():
    f = request.form
    match_id = f['match_id']
    start_date = f['start_date']
    salary = f['salary']
    contract_type = f['contract_type']
    
    # Create Hiring Record
    query_db("""
        INSERT INTO HiringRecords (MatchID, StartDate, Salary, ContractType, CreatedBy)
        VALUES (?, ?, ?, ?, ?)
    """, (match_id, start_date, salary, contract_type, session['user_id']))
    
    # Update Candidate Status to 'Hired'
    # Need to find CandidateID from MatchID
    match = query_db("SELECT CandidateID FROM Matches WHERE MatchID=?", (match_id,), one=True)
    if match:
        query_db("UPDATE Candidates SET Status='Hired', WorkStatus='Employed' WHERE CandidateID=?", (match['CandidateID'],))
        
        # Close the Match Status
        query_db("UPDATE Matches SET Status='Placed' WHERE MatchID=?", (match_id,))
    
    flash('Hiring Process Completed! Candidate is now an Employee.', 'success')
    return redirect(url_for('recruiter_hiring_onboarding'))

@app.route('/recruitment/am_dashboard')
@login_required
@role_required(['AccountManager', 'Manager', 'AllocationManager'])
def account_manager_dashboard():
    # AM focuses on Clients & Requests
    clients = query_db("SELECT * FROM Clients")
    requests = query_db("SELECT CR.*, C.CompanyName FROM ClientRequests CR JOIN Clients C ON CR.ClientID = C.ClientID WHERE CR.Status='Open'")
    return render_template('recruitment/manage.html', clients=clients or [], requests=requests or [])

@app.route('/recruitment/allocator_dashboard')
@login_required
@role_required(['Allocator', 'AllocationManager', 'Manager', 'AllocationSpecialist', 'AccountManager'])
def allocator_dashboard():
    """إعادة توجيه الألوكيتر إلى مركز المطابقة (شاشة الترشيح الرئيسية)."""
    return redirect(url_for('allocation_matching'))
@app.route('/recruitment/distribute', methods=['GET', 'POST'])
@login_required
@role_required(['RecruitmentManager', 'Manager', 'AllocationManager', 'AccountManager'])
def distribute_recruitment_tasks():
    if request.method == 'POST':
        try:
            candidate_id = request.form.get('candidate_id')
            if not candidate_id:
                flash('Error: Candidate ID missing.', 'danger')
                return redirect(url_for('distribute_recruitment_tasks'))

            assigned_recruiter = request.form.get('recruiter_id') or None
            assigned_allocator = request.form.get('allocator_id') or None
            
            # Determine who is the "SalesAgent" (Owner) - usually Recruiter or Allocator if no recruiter
            owner_id = assigned_recruiter if assigned_recruiter else assigned_allocator

            query_db("UPDATE Candidates SET RecruiterID=?, AllocatorID=?, SalesAgentID=?, Status='Recruitment_Process' WHERE CandidateID=?", 
                     (assigned_recruiter, assigned_allocator, owner_id, candidate_id))
                     
            flash('Task Distributed Successfully', 'success')
        except Exception as e:
            flash(f'Error Distributing Task: {str(e)}', 'danger')
            
        return redirect(url_for('distribute_recruitment_tasks'))
    
    # GET: Show Unassigned Candidates
    candidates = query_db("SELECT * FROM Candidates WHERE Status='New' OR Status='Lead'")
    recruiters = query_db("SELECT UserID, Username FROM Users_1 WHERE Role='Recruiter'")
    allocators = query_db("SELECT UserID, Username FROM Users_1 WHERE Role='AllocationSpecialist' OR Role='AllocationManager'")
    
    # Calculate Workload (Count of Assigned Leads per Recruiter)
    workload_data = query_db("""
        SELECT SalesAgentID, COUNT(*) as LeadCount 
        FROM Candidates 
        WHERE SalesAgentID IS NOT NULL AND SalesAgentID != 0
        GROUP BY SalesAgentID
    """)
    workload_map = {row['SalesAgentID']: row['LeadCount'] for row in workload_data} if workload_data else {}
    
    # Attach workload to recruiters list for template
    recruiters_with_stats = []
    if recruiters:
        for r in recruiters:
            # query_db returns dicts, so we can use it directly or copy it
            r_dict = r.copy() if isinstance(r, dict) else {'UserID': r[0], 'Username': r[1]}
            
            r_dict['ActiveLeads'] = workload_map.get(r_dict.get('UserID'), 0)
            recruiters_with_stats.append(r_dict)
    
    return render_template('recruitment/distribute.html', candidates=candidates or [], recruiters=recruiters_with_stats, allocators=allocators or [])

@app.route('/recruitment/failure_report', methods=['POST'])
@login_required
@role_required(['Recruitment', 'Manager', 'Allocator'])
def log_recruitment_failure():
    cand_id = request.form['candidate_id']
    reason = request.form['reason']
    stage = request.form['stage'] # Screening, Interview, Client Reject
    
    query_db("INSERT INTO RecruitmentFailures (CandidateID, Stage, Reason, LoggedBy, CreatedAt) VALUES (?, ?, ?, ?, GETDATE())",
             (cand_id, stage, reason, session['user_id']))
             
    # Update Candidate Status based on failure logic (e.g. Back to Pool, or Blocked)
    query_db("UPDATE Candidates SET Status='Failed_Recruitment' WHERE CandidateID=?", (cand_id,))
    
    flash('Failure Logged. Analysis Updated.', 'info')
    return redirect(request.referrer)

@app.route('/recruitment/approvals')
@login_required
@role_required(['RecruitmentManager', 'Manager', 'AccountManager'])
def recruitment_approvals():
    # Dedicated view for approving client interviews
    # Using DISTINCT to avoid duplicate rows if joins cause multiplication
    pending_matches = query_db("""
        SELECT DISTINCT M.MatchID, M.MatchDate, M.CandidateID, M.RequestID, M.Status,
               C.FullName as CandidateName, Cl.CompanyName, CR.JobTitle
        FROM Matches M
        JOIN Candidates C ON M.CandidateID = C.CandidateID
        JOIN ClientRequests CR ON M.RequestID = CR.RequestID
        JOIN Clients Cl ON CR.ClientID = Cl.ClientID
        LEFT JOIN ClientInterviews CI ON M.MatchID = CI.MatchID
        WHERE CI.Status IS NULL OR CI.Status = 'Pending'
        ORDER BY M.MatchDate DESC
    """)
    
    return render_template('recruitment/approvals.html', matches=pending_matches or [])

@app.route('/recruitment/manage')
@login_required
@role_required(['Recruitment', 'Manager'])
def recruitment_manage():
    clients = query_db('SELECT * FROM Clients')
    requests = query_db('''
        SELECT CR.*, C.CompanyName 
        FROM ClientRequests CR 
        JOIN Clients C ON CR.ClientID = C.ClientID 
        ORDER BY CR.RequestDate DESC
    ''')
    return render_template('recruitment/manage.html', clients=clients or [], requests=requests or [])

# --- NEW STRICT HIERARCHY ROUTES ---
@app.route('/recruitment/clients')
@login_required
@role_required(['Manager', 'AccountManager', 'RecruitmentManager', 'Corporate', 'AllocationManager'])
def manage_clients():
    clients = query_db('SELECT * FROM Clients')
    return render_template('recruitment/clients.html', clients=clients or [])

@app.route('/recruitment/requests')
@login_required
@role_required(['Manager', 'AccountManager', 'AllocationSpecialist', 'Corporate', 'AllocationManager'])
def manage_requests():
    requests = query_db('''
        SELECT CR.*, C.CompanyName 
        FROM ClientRequests CR 
        JOIN Clients C ON CR.ClientID = C.ClientID 
        ORDER BY CR.RequestDate DESC
    ''')
    clients = query_db('SELECT * FROM Clients')
    create_for_client = request.args.get('create_for', '')
    return render_template('recruitment/requests.html', requests=requests or [], clients=clients or [], create_for_client=create_for_client)

@app.route('/recruitment/interview_feedback', methods=['POST'])
@login_required
def add_interview_feedback():
    f = request.form
    match_id = f['match_id']
    status = f['status'] # Accepted, Rejected
    
    query_db("""
        INSERT INTO ClientInterviews (MatchID, Status, Feedback, RejectionReason, ActionRequired, RecordedBy)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (match_id, status, f['feedback'], f.get('rejection_reason'), f.get('action_required'), session['user_id']))
    
    # Update Match Status
    query_db("UPDATE Matches SET Status=? WHERE MatchID=?", (status, match_id))
    
    flash('Interview Feedback Recorded', 'success')
    return redirect(url_for('recruiter_dashboard'))

@app.route('/distribute_leads', methods=['GET', 'POST'])
@login_required
@role_required(['Manager', 'RecruitmentManager', 'AllocationManager', 'Allocator', 'AllocationSpecialist'])
def distribute_leads():
    if request.method == 'POST':
        # Can come from modal (single) or checkboxes (list)
        candidate_ids = request.form.getlist('candidate_ids')
        
        # Check if single 'candidate_id' from modal exists if list is empty
        if not candidate_ids and 'candidate_id' in request.form:
             candidate_ids = [request.form['candidate_id']]
             
        target_recruiter = request.form.get('recruiter_id')
        target_allocator = request.form.get('allocator_id')
        
        # Priority: Recruiter > Allocator
        target_user = target_recruiter if target_recruiter else target_allocator
        
        if target_user and candidate_ids:
            for cid in candidate_ids:
                query_db("UPDATE Candidates SET SalesAgentID = ?, Status = 'Assigned' WHERE CandidateID = ?", (target_user, cid))
            
            flash(f'{len(candidate_ids)} Leads Assigned Successfully', 'success')
        else:
            flash('Distribution Failed: No User or Candidates Selected', 'warning')
            
        return redirect(url_for('distribute_leads'))

    # GET: Show Unassigned Leads
    # We show leads where SalesAgentID is NULL/0
    leads = query_db("SELECT * FROM Candidates WHERE Status IN ('New', 'Imported') AND (SalesAgentID IS NULL OR SalesAgentID = 0)")
    
    # Fetch Recruiters & Allocators for Dropdowns
    recruiters = query_db("SELECT UserID, Username FROM Users_1 WHERE Role IN ('Recruiter', 'Sales', 'AccountManager')")
    allocators = query_db("SELECT UserID, Username FROM Users_1 WHERE Role IN ('Allocator', 'AllocationSpecialist', 'AllocationManager')")
    
    # Calculate Workload (Count of Assigned Leads per Recruiter)
    workload_data = query_db("""
        SELECT SalesAgentID, COUNT(*) as LeadCount 
        FROM Candidates 
        WHERE SalesAgentID IS NOT NULL AND SalesAgentID != 0
        GROUP BY SalesAgentID
    """)
    workload_map = {row['SalesAgentID']: row['LeadCount'] for row in workload_data} if workload_data else {}
    
    # Attach workload to recruiters list for template
    recruiters_with_stats = []
    if recruiters:
        for r in recruiters:
            # query_db returns dicts, so we can use it directly or copy it
            r_dict = r.copy() if isinstance(r, dict) else {'UserID': r[0], 'Username': r[1]}
            
            r_dict['ActiveLeads'] = workload_map.get(r_dict.get('UserID'), 0)
            recruiters_with_stats.append(r_dict)
            
    # For compatibility with template, we pass 'recruiters' as 'recruiters_with_stats'
    # And 'team' (legacy) if needed, but template uses 'recruiters' and 'allocators' now (based on my previous edit context, wait, did I update template variables?)
    # Let's check the template variables in distribute.html again.
    # Template uses: 'candidates' (loop for c in candidates), 'recruiters', 'allocators'.
    # BUT my previous Read of distribute.html showed: leads=leads, team=team in app.py logic.
    # AND template had: {% for c in candidates %} (Wait, likely 'leads' passed as 'candidates'?)
    # Let's match template expectation.
    return render_template('recruitment/distribute.html', candidates=leads or [], recruiters=recruiters_with_stats, allocators=allocators or [])

# --- SALES ---
@app.route('/marketing/update_lead', methods=['POST'])
@login_required
@role_required(['Marketing', 'Manager'])
def update_marketing_lead():
    try:
        f = request.form
        cand_id = f['candidate_id']
        
        # Build Update Query dynamically or map fields
        query_db("""
            UPDATE Candidates 
            SET FullName=?, Phone=?, Email=?, SourceChannel=?, CampaignID=?, 
                SalesAgentID=?, InterestLevel=?, CurrentCEFR=?, WorkStatus=?, 
                Venue=?, PlacementReason=?, MarketingAssessment=?, AvailabilityStatus=?
            WHERE CandidateID=?
        """, (f['name'], f['phone'], f.get('email'), f['source'], f.get('campaign_id') or None,
              f.get('assigned_agent'), f.get('interest'), f.get('level'), f.get('work_status'),
              f.get('venue'), f.get('placement_reason'), f.get('marketing_assessment'), 
              f.get('availability_status'), cand_id))
              
        flash('Lead Updated Successfully', 'success')
    except Exception as e:
        flash(f'Error Updating Lead: {e}', 'danger')
        
    return redirect(url_for('daily_marketing_sheet', date=f.get('entry_date')))

@app.route('/marketing/daily_sheet')
@login_required
@role_required(['Marketing', 'Manager'])
def daily_marketing_sheet():
    # Calendar Date Selection
    selected_date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    
    # Fetch Leads created on this specific date with Live Sales & Payment Sync
    daily_leads = query_db("""
        SELECT C.*, U.Username as SalesAgentName, Cmp.Name as CampaignName,
               (SELECT COUNT(*) FROM InvoiceHeaders I WHERE I.CandidateID = C.CandidateID AND I.Status = 'Paid') as PaidInvoicesCount
        FROM Candidates C 
        LEFT JOIN Users_1 U ON C.SalesAgentID = U.UserID 
        LEFT JOIN Campaigns Cmp ON C.CampaignID = Cmp.CampaignID
        WHERE CONVERT(DATE, C.CreatedAt) = ? 
        ORDER BY C.CreatedAt DESC
    """, (selected_date,))
    
    # List of Sales Agents & Active Campaigns
    sales_agents = query_db("SELECT UserID, Username FROM Users_1 WHERE Role='Sales'")
    campaigns = query_db("SELECT CampaignID, Name FROM Campaigns WHERE Status='Active'")
    
    return render_template('marketing/daily_sheet.html', leads=daily_leads or [], sales_agents=sales_agents or [], campaigns=campaigns or [], selected_date=selected_date)

@app.route('/marketing/create_campaign', methods=['POST'])
@login_required
@role_required(['Marketing', 'Manager'])
def create_campaign():
    f = request.form
    query_db("INSERT INTO Campaigns (Name, Platform, Budget, Status) VALUES (?, ?, ?, 'Active')", 
             (f['name'], f['platform'], f.get('budget', 0)))
    flash('Campaign Created Successfully', 'success')
    return redirect(url_for('daily_marketing_sheet'))

@app.route('/marketing/add_lead_row', methods=['POST'])
@login_required
@role_required(['Marketing', 'Manager'])
def add_lead_row():
    # Excel-like quick entry
    f = request.form
    date = f.get('entry_date', datetime.today().strftime('%Y-%m-%d'))
    
    try:
        # Check duplicate by phone
        exists = query_db("SELECT CandidateID FROM Candidates WHERE Phone=?", (f['phone'],), one=True)
        if exists:
            flash(f"Duplicate Phone: {f['phone']}", 'warning')
        else:
            # Handle Optional Fields (Campaign, Interest, Level)
            campaign_id = f.get('campaign_id') if f.get('campaign_id') else None
            
            query_db("""
                INSERT INTO Candidates (FullName, Phone, Email, Nationality, GraduationStatus, SourceChannel, Status, CreatedAt, SalesAgentID, CampaignID, PrimaryIntent, CurrentCEFR, WorkStatus, Venue, PlacementReason, MarketingAssessment, PreviousApplicationDate, AvailabilityStatus)
                VALUES (?, ?, ?, ?, ?, ?, 'Lead', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (f['name'], f['phone'], f.get('email', ''), f.get('nationality'), f.get('grad_status'), f['source'], date, f['assigned_agent'], campaign_id, f.get('interest'), f.get('level'), f.get('work_status'), f.get('venue'), f.get('placement_reason'), f.get('marketing_assessment'), f.get('prev_app_date'), f.get('availability_status')))
            
            # EMAIL NOTIFICATION: Notify Sales Agent
            if f.get('assigned_agent'):
                agent = query_db("SELECT Email, Username FROM Users_1 WHERE UserID=?", (f['assigned_agent'],), one=True)
                if agent and agent['Email']:
                    notify_lead_assignment(agent['Email'], agent['Username'], 1, f.get('campaign_id', 'General'))
            
            flash('Lead Added Successfully', 'success')
    except Exception as e:
        # Log error for debugging
        print(f"Error Adding Lead: {e}")
        flash(f'Error Adding Lead: {e}', 'danger')
        
    return redirect(url_for('daily_marketing_sheet', date=date))

@app.route('/marketing/assign_lead', methods=['POST'])
@login_required
@role_required(['Marketing', 'Manager'])
def assign_lead():
    lead_id = request.form['lead_id']
    agent_id = request.form['agent_id']
    
    query_db("UPDATE Candidates SET SalesAgentID=? WHERE CandidateID=?", (agent_id, lead_id))
    flash('Lead Assigned Successfully', 'success')
    return redirect(url_for('marketing_dashboard'))

@app.route('/sales/dashboard')
@login_required
def sales_dashboard_redirect():
    # Fix for legacy redirect or URL mismatch
    return redirect(url_for('sales_index'))

@app.route('/sales')
@login_required
@role_required(['Sales', 'Manager'])
def sales_index():
    if 'role' not in session: return redirect(url_for('login'))
    user_id = session['user_id']
    role = session['role']
    
    # SALES MANAGER: Sees ALL Leads + Performance
    if role == 'Manager': # Or specific 'SalesManager' role if we add it
         leads = query_db("""
            SELECT Cand.*, Cmp.Name as CampaignName, U.Username as AgentName
            FROM Candidates Cand 
            LEFT JOIN Campaigns Cmp ON Cand.CampaignID = Cmp.CampaignID
            LEFT JOIN Users_1 U ON Cand.SalesAgentID = U.UserID
            WHERE Cand.Status IN ('Lead', 'Imported')
         """)
    else:
        # SALES AGENT: Sees ONLY Assigned Leads
        leads = query_db("""
            SELECT Cand.*, Cmp.Name as CampaignName 
            FROM Candidates Cand 
            LEFT JOIN Campaigns Cmp ON Cand.CampaignID = Cmp.CampaignID
            WHERE Cand.SalesAgentID = ? AND Cand.Status IN ('Lead', 'Imported')
        """, (user_id,))
    
    # ... Rest of the Sales View (Campaigns, etc.) ...
    campaigns = query_db("SELECT Cmp.*, CR.JobTitle, C.CompanyName FROM Campaigns Cmp LEFT JOIN ClientRequests CR ON Cmp.RequestID = CR.RequestID LEFT JOIN Clients C ON CR.ClientID = C.ClientID")
    active_requests = query_db("SELECT CR.RequestID, CR.JobTitle, C.CompanyName FROM ClientRequests CR JOIN Clients C ON CR.ClientID = C.ClientID WHERE CR.Status = 'Open'")
    
    # Fetch Invoices
    invoices_sql = """
        SELECT TOP 10 G.*, C.FullName as LinkedCandidate 
        FROM GeneralSales G 
        LEFT JOIN Candidates C ON G.CandidateID = C.CandidateID 
    """
    if role != 'Manager':
        invoices_sql += " WHERE G.CreatedBy = ?"
        invoices = query_db(invoices_sql + " ORDER BY G.SaleDate DESC", (user_id,))
    else:
        invoices = query_db(invoices_sql + " ORDER BY G.SaleDate DESC")

    # Fetch Services and Candidates for Dropdowns
    # services = query_db("SELECT * FROM Services")
    # Filter Services: Hide 'Recruitment' type services from Sales if they shouldn't sell job offers directly? 
    # User Request: "sales user they can the the job offers that should appears for the recruitment only"
    # Wait, the user said: "sales user they can the the job offers that should appears for the recruitment only"
    # This likely means: Sales users CAN SEE job offers that should be for Recruitment only? OR Sales users SEE job offers that should appear for recruitment only (which is wrong)?
    # "sales user they can the the job offers that should appears for the recruitment only" -> "Sales users can SEE job offers that should appear for Recruitment ONLY." -> This is a BUG REPORT.
    # FIX: Exclude Recruitment Job Orders from Sales View or Exclude Recruitment Services.
    # Context: "active_requests" are Job Orders. "services" are products.
    # If the user means Job Orders (active_requests), we should filter them?
    # Usually Sales NEED to see Job Orders to know what to sell (Campaigns).
    # But maybe the user means "Services" dropdown has "Recruitment Fee" which shouldn't be there?
    # Let's assume the user wants to HIDE Recruitment stuff from Sales.
    
    # 1. Services Filter:
    # ServiceType column is now guaranteed by schema fix
    services = query_db("SELECT * FROM Services WHERE ServiceType != 'Recruitment' OR ServiceType IS NULL")
    
    # 2. Active Requests (Job Offers):
    # If Sales shouldn't see them, we pass empty list? But Sales needs them for Campaigns.
    # Re-reading: "sales user they can the the job offers that should appears for the recruitment only"
    # Interpretation: "Sales users currently see job offers. This should be for recruitment only."
    # Action: Remove `active_requests` from Sales Dashboard or filter it?
    # Let's remove it if Role != Manager/Recruitment?
    # But Sales adds Campaigns linked to Requests.
    # Let's keep it but maybe hide sensitive ones? No, let's stick to filtering Services first as it's safer.
    # And maybe hide the "Job Orders" table from Sales Dashboard if it exists there.
    
    candidates = query_db("SELECT CandidateID, FullName, Phone FROM Candidates ORDER BY FullName")
    if role == 'Manager':
        candidates = query_db("SELECT TOP 200 CandidateID, FullName, Phone FROM Candidates ORDER BY CreatedAt DESC")
    else:
        candidates = query_db("SELECT CandidateID, FullName, Phone FROM Candidates WHERE SalesAgentID=? ORDER BY CreatedAt DESC", (user_id,))
    
    # Fetch Available TA Slots for Booking (مختبر التوظيف فقط)
    today = datetime.today().strftime('%Y-%m-%d')
    selected_date = request.args.get('date', today)
    _ensure_taschedules_assessment_context_column()

    # Generate slots if not exist for selected date (Auto-generate logic reuse)
    # OPTIMIZED: Use single transaction for bulk insert to avoid 160+ roundtrips
    existing = query_db(
        f"SELECT COUNT(*) as c FROM TASchedules T WHERE T.SlotDate = ? {_SQL_TA_T_RECRUITER_BOOKING.strip()}",
        (selected_date,),
        one=True,
    )
    if existing['c'] == 0:
        start_hour = 9
        # شواغر حجز التوظيف: توليد لـ Talent_Recruitment فقط (نفس قائمة الريكروتر)
        talent_users = query_db(
            "SELECT UserID, Username FROM Users_1 WHERE LOWER(LTRIM(RTRIM(Role))) = N'talent_recruitment'"
        )

        # Prepare bulk insert data
        new_slots = []
        if talent_users:
            for h in range(8):
                for m in [0, 15, 30, 45]:
                    time_str = f"{start_hour+h:02d}:{m:02d}"
                    for t in talent_users:
                        new_slots.append((selected_date, time_str, 'Available', t['UserID'], TA_CTX_RECRUITMENT))

            # Execute Bulk Insert
            if new_slots:
                try:
                    db = get_db()
                    cursor = db.cursor()
                    cursor.executemany(
                        "INSERT INTO TASchedules (SlotDate, SlotTime, Status, EvaluatorID, AssessmentContext) VALUES (?, ?, ?, ?, ?)",
                        new_slots,
                    )
                    db.commit()
                    cursor.close()
                except Exception as e:
                    print(f"Error generating slots: {e}")
        else:
            # Fallback: Create generic slots if NO Talent users exist (for testing purposes only)
            # This ensures at least something shows up, but marks them clearly.
            pass

    available_slots = query_db(f"""
        SELECT T.*, U.Username as EvaluatorName 
        FROM TASchedules T 
        LEFT JOIN Users_1 U ON T.EvaluatorID = U.UserID 
        WHERE T.SlotDate = ? AND T.Status = 'Available'
          {_SQL_TA_T_RECRUITER_BOOKING.strip()}
        ORDER BY T.SlotTime, U.Username
    """, (selected_date,))
    
    return render_template('sales/index.html', campaigns=campaigns or [], active_requests=active_requests or [], leads=leads or [], invoices=invoices or [], services=services or [], candidates=candidates or [], available_slots=available_slots or [], selected_date=selected_date)

@app.route('/sales/add_campaign', methods=('POST',))
@login_required
def add_campaign():
    f = request.form
    query_db('INSERT INTO Campaigns (Name, Type, RequestID, MediaChannel, AdText, Budget, StartDate, EndDate) VALUES (?,?,?,?,?,?,?,?)',
             (f['name'], f['type'], f.get('request_id') or None, f['media_channel'], f['ad_text'], f['budget'], f['start_date'], f['end_date']))
    flash('Campaign Added', 'success')
    return redirect(url_for('sales_index'))

@app.route('/sales/add_lead', methods=('POST',))
@login_required
def add_lead():
    f = request.form
    next_followup = f.get('next_followup') or None
    campaign_id = f.get('campaign_id') or None
    feedback = f.get('feedback', '')
    
    # Store sales agent ID
    sales_agent_id = session.get('user_id')
    
    query_db('INSERT INTO Candidates (FullName, Email, Phone, Status, CampaignID, InterestLevel, NextFollowUpDate, Feedback, SalesAgentID) VALUES (?,?,?,?,?,?,?,?,?)',
             (f['full_name'], f['email'], f['phone'], 'Lead', campaign_id, f['interest_level'], next_followup, feedback, sales_agent_id))
    flash('تم تسجيل العميل المحتمل بنجاح', 'success')
    return redirect(url_for('sales_index'))

@app.route('/sales/add_invoice', methods=('POST',))
@login_required
def add_sales_invoice():
    f = request.form
    service_id = f.get('service_id')
    
    # 1. Create Invoice Header
    candidate_id = f['candidate_id']
    amount = float(f['amount'])
    payment_method = f['payment_method']
    
    # Use helper to get cursor (get_db_connection not defined directly in route scope usually, but imported? 
    # Actually, query_db uses get_db(), so we should use get_db() or just query_db for simple inserts.
    # But here we need OUTPUT INSERTED.InvoiceID. query_db might not support that easily with fetchone logic.
    # Let's fix by using get_db() directly.
    
    db = get_db() # Helper function defined in app.py
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO InvoiceHeaders (CandidateID, InvoiceDate, SubTotal, TotalAmount, Status, CreatedBy)
            OUTPUT INSERTED.InvoiceID
            VALUES (?, GETDATE(), ?, ?, 'Paid', ?)
        """, (candidate_id, amount, amount, session['user_id']))
        
        invoice_id = cursor.fetchone()[0]
        
        # 2. Create Invoice Item
        service_name = "Service"
        if service_id:
            svc = query_db('SELECT ServiceName FROM Services WHERE ServiceID=?', (service_id,), one=True)
            if svc: service_name = svc['ServiceName']
            
        cursor.execute("""
            INSERT INTO InvoiceItems (InvoiceID, Description, Quantity, UnitPrice, LineTotal)
            VALUES (?, ?, 1, ?, ?)
        """, (invoice_id, service_name, amount, amount))
        
        # 3. Keep Legacy Record for now (GeneralSales)
        cursor.execute("""
            INSERT INTO GeneralSales (ServiceName, Amount, PaymentMethod, CandidateID, Notes, CreatedBy) 
            VALUES (?,?,?,?,?,?)
        """, (service_name, amount, payment_method, candidate_id, f['notes'], session['user_id']))
        
        db.commit()
        flash('Invoice Created Successfully (New Structure)', 'success')
        
    except Exception as e:
        db.rollback()
        flash(f'Error creating invoice: {e}', 'danger')
        
    return redirect(url_for('sales_index'))

# --- FINANCE ---
@app.route('/finance/index')
@login_required
@role_required(['Manager', 'Finance'])
def finance_index():
    gen_sales = query_db('SELECT * FROM GeneralSales ORDER BY SaleDate DESC')
    total_gen = sum(x['Amount'] for x in gen_sales) if gen_sales else 0
    corp_inv = query_db('''
        SELECT I.*, C.CompanyName 
        FROM CorporateInvoices I 
        JOIN Clients C ON I.ClientID = C.ClientID 
        ORDER BY I.IssueDate DESC
    ''')
    total_corp = sum(x['Amount'] for x in corp_inv) if corp_inv else 0
    stud_pay = query_db('''
        SELECT P.*, S.FullName 
        FROM StudentPayments P 
        JOIN Enrollments E ON P.EnrollmentID = E.EnrollmentID
        JOIN Candidates S ON E.CandidateID = S.CandidateID
        ORDER BY P.PaymentDate DESC
    ''')
    total_stud = sum(x['Amount'] for x in stud_pay) if stud_pay else 0
    grand_total = total_gen + total_corp + total_stud
    return render_template('finance/index.html', 
                           gen_sales=gen_sales or [], 
                           corp_inv=corp_inv or [], 
                           stud_pay=stud_pay or [],
                           total_gen=total_gen, total_corp=total_corp, total_stud=total_stud, grand_total=grand_total)

# --- التدفق النقدي الزكي + التقارير (من Nuit — مسار معفى: يفتح الصفحة مباشرة، دخول مدمج إن لزم) ---
@app.route('/finance/cashflow')
def finance_cashflow_ui():
    """مثل Nuit: الصفحة تفتح مباشرة. إن لم يكن المستخدم مسجلاً تظهر طبقة دخول مدمجة داخل الصفحة."""
    user = None
    if g.user:
        user = {"id": session.get('user_id'), "name": (g.user or {}).get('FullName') or (g.user or {}).get('Username', ''), "role": (g.user or {}).get('Role', 'Finance')}
    return render_template('finance/cashflow_ui_nuit.html', user=user)


@app.route('/api/cashflow/login', methods=['POST'])
def api_cashflow_login():
    """لوجن شاشة الصرف والقبض — نفس حسابات اللوجن الرئيسي (مثل Nuit). معفى من login_required."""
    try:
        data = request.get_json() or {}
        username = (data.get('username') or '').strip().replace('\ufeff', '')
        password = (data.get('password') or '').strip()
        if not username:
            return jsonify({"ok": False, "msg": "اسم المستخدم مطلوب"})
        user = query_db('SELECT * FROM Users_1 WHERE LOWER(RTRIM(Username)) = LOWER(?)', (username,), one=True)
        if not user or user['Password'] != password:
            return jsonify({"ok": False, "msg": "خطأ في اسم المستخدم أو كلمة المرور"})
        session.clear()
        session['user_id'] = user['UserID']
        session['role'] = user['Role']
        session['username'] = (user.get('Username') or '').strip()
        return jsonify({
            "ok": True,
            "user": {
                "id": user['UserID'],
                "name": (user.get('FullName') or user.get('Username') or '').strip(),
                "role": user.get('Role', 'Finance')
            }
        })
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500

@app.route('/finance/reports')
@login_required
@role_required(['Manager', 'Finance'])
def finance_reports_page():
    return render_template('finance/reports_dashboard.html')

# APIs التدفق النقدي — توافق Nuit
@app.route('/api/cashflow/me')
def api_cashflow_me():
    """مثل Nuit: يعيد المستخدم إن وجد، و 401 JSON إن لم يكن مسجلاً (لا redirect)."""
    if not g.user:
        return jsonify({"ok": False, "msg": "غير مسجل"}), 401
    return jsonify({"ok": True, "user": {"id": session.get('user_id'), "name": (g.user or {}).get('FullName') or (g.user or {}).get('Username', ''), "role": (g.user or {}).get('Role', 'Finance')}})

@app.route('/api/accounts/sub')
@login_required
@role_required(['Manager', 'Finance'])
def api_accounts_sub_alias():
    from services.voucher_manager import get_head_accounts, get_detail_accounts
    head = get_head_accounts()
    detail = get_detail_accounts()
    return jsonify({
        "headAccounts": head,
        "detailAccounts": detail,
        "accounts": head if head else detail  # توافق مع الكود القديم
    })

@app.route('/api/cashflow/accounts/sub')
@login_required
@role_required(['Manager', 'Finance'])
def api_cashflow_accounts_sub():
    from services.voucher_manager import get_head_accounts, get_detail_accounts
    head = get_head_accounts()
    detail = get_detail_accounts()
    return jsonify({
        "headAccounts": head,
        "detailAccounts": detail,
        "accounts": head if head else detail  # توافق مع الكود القديم
    })

@app.route('/api/cashflow/transactions')
@login_required
@role_required(['Manager', 'Finance'])
def api_cashflow_transactions():
    from services.voucher_manager import get_recent_transactions
    limit = request.args.get('limit', 30, type=int)
    data = get_recent_transactions(limit=limit)
    return jsonify({"ok": True, "data": data})

@app.route('/api/cashflow/transactions', methods=['POST'])
@login_required
@role_required(['Manager', 'Finance'])
def api_cashflow_create_transaction():
    from services.voucher_manager import save_voucher_transaction, save_journal_entry
    try:
        payload = {}
        if request.form:
            import json
            h = request.form.get('header')
            l = request.form.get('lines')
            payload = json.loads(h) if h else {}
            payload['items'] = json.loads(l) if l else []
        else:
            payload = request.get_json(silent=True) or {}
        v_type = payload.get('type', 'DISB')
        if v_type == 'JRNL':
            result = save_journal_entry(payload)
        else:
            result = save_voucher_transaction(payload)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/cashflow/agents/search')
@login_required
@role_required(['Manager', 'Finance'])
def api_cashflow_agents_search():
    from services.voucher_manager import search_agents_quick
    q = request.args.get('search_text', '').strip()
    agents = search_agents_quick(q)
    return jsonify({"agents": agents})

@app.route('/api/cashflow/next-number')
@login_required
@role_required(['Manager', 'Finance'])
def api_cashflow_next_number():
    from services.voucher_manager import get_next_bond_number, TYPE_RECEIPT, TYPE_PAYMENT
    t = request.args.get('type', 'DISB')
    gid = TYPE_PAYMENT if t == 'DISB' else TYPE_RECEIPT
    n = get_next_bond_number(gid)
    return jsonify({"next": n})

@app.route('/api/currencies')
@login_required
@role_required(['Manager', 'Finance'])
def api_currencies():
    from services.voucher_manager import get_currencies, get_default_currency
    rows = get_currencies()
    if not rows:
        return jsonify({"currencies": [{"CardGuide": get_default_currency(), "CurrencyName": "ريال سعودي", "Rate": 1}]})
    return jsonify({
        "currencies": [{"CardGuide": str(r.get("CardGuide", "")), "CurrencyName": r.get("CurrencyName", ""), "Rate": float(r.get("Rate") or 1)} for r in rows]
    })

@app.route('/api/cashflow/config', methods=['GET', 'POST'])
@login_required
@role_required(['Manager', 'Finance'])
def api_cashflow_config():
    uid = str(session.get('user_id', ''))
    if request.method == 'GET':
        try:
            from services.voucher_manager import get_cashflow_config
            cfg = get_cashflow_config(uid)
            return jsonify({"config": cfg or {}})
        except Exception:
            return jsonify({"config": {}})
    try:
        cfg = request.get_json(silent=True) or {}
        cfg = cfg.get('config', cfg)
        from services.voucher_manager import save_cashflow_config
        save_cashflow_config(uid, cfg)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 400

# APIs التقارير
REPORTS_META = [
    {"id": "trial_balance", "name": "ميزان المراجعة", "params": ["from_date", "to_date"]},
    {"id": "general_ledger", "name": "دفتر الأستاذ العام", "params": ["account_guide", "from_date", "to_date"]},
    {"id": "customer_statement", "name": "كشف حساب عميل", "params": ["agent_guide", "from_date", "to_date"]},
    {"id": "item_movement", "name": "تقرير حركة صنف", "params": ["product_guide", "from_date", "to_date"]},
    {"id": "inventory", "name": "تقرير جرد (مبيعات)", "params": []},
    {"id": "accounts_list", "name": "قائمة الحسابات", "params": []},
    {"id": "bonds_list", "name": "قائمة السندات", "params": []},
    {"id": "entries_list", "name": "قائمة القيود", "params": []},
]

@app.route('/api/reports')
@login_required
@role_required(['Manager', 'Finance'])
def api_reports_list():
    return jsonify({"reports": REPORTS_META})

def _run_report(report_id, from_date=None, to_date=None, account_guide=None, agent_guide=None, product_guide=None):
    fd = from_date or "1900-01-01"
    td = to_date or "2099-12-31"
    db = get_db()
    if not db: return {"success": False, "message": "فشل الاتصال"}
    cur = db.cursor()
    try:
        if report_id == "accounts_list":
            cur.execute("SELECT CardCode, AccountName, LatinName FROM TBL004 WHERE AccountName IS NOT NULL ORDER BY CardCode")
            rows = cur.fetchall()
            cols = [c[0] for c in cur.description]
            return {"success": True, "columns": ["رقم الحساب", "اسم الحساب", "الاسم اللاتيني"], "rows": [[r[0] or "", r[1] or "", r[2] or ""] for r in rows]}
        if report_id == "trial_balance":
            cur.execute("""
                SELECT a.CardCode, a.AccountName, ISNULL(SUM(d.Debit),0) AS TotalDebit, ISNULL(SUM(d.Credit),0) AS TotalCredit,
                    ISNULL(SUM(d.Debit),0)-ISNULL(SUM(d.Credit),0) AS Balance
                FROM TBL004 a LEFT JOIN TBL012 d ON d.AccountGuide = a.CardGuide LEFT JOIN TBL011 h ON h.CardGuide = d.MainGuide
                WHERE a.AccountName IS NOT NULL AND (h.EntryDate IS NULL OR (CONVERT(date, h.EntryDate) >= ? AND CONVERT(date, h.EntryDate) <= ?))
                GROUP BY a.CardGuide, a.CardCode, a.AccountName
                HAVING ISNULL(SUM(d.Debit),0) <> 0 OR ISNULL(SUM(d.Credit),0) <> 0
                ORDER BY a.CardCode
            """, (fd, td))
            rows = cur.fetchall()
            return {"success": True, "columns": ["رقم الحساب", "اسم الحساب", "إجمالي مدين", "إجمالي دائن", "الرصيد"],
                    "rows": [[r[0] or "", r[1] or "", float(r[2] or 0), float(r[3] or 0), float(r[4] or 0)] for r in rows]}
        if report_id == "general_ledger":
            if not account_guide:
                cur.execute("SELECT TOP 50 CardGuide, CardCode, AccountName FROM TBL004 WHERE AccountName IS NOT NULL ORDER BY CardCode")
                rows = cur.fetchall()
                return {"success": True, "columns": ["CardGuide", "رقم الحساب", "اسم الحساب"], "rows": [[str(r[0]), r[1] or "", r[2] or ""] for r in rows], "message": "اختر حساباً لعرض دفتر الأستاذ"}
            cur.execute("""
                SELECT h.EntryNumber, FORMAT(h.EntryDate,'yyyy-MM-dd'), h.Notes, d.Description, d.Debit, d.Credit
                FROM TBL012 d INNER JOIN TBL011 h ON h.CardGuide = d.MainGuide
                WHERE d.AccountGuide = ? AND CONVERT(date, h.EntryDate) >= ? AND CONVERT(date, h.EntryDate) <= ?
                ORDER BY h.EntryDate, h.EntryNumber
            """, (account_guide, fd, td))
            rows = cur.fetchall()
            bal = 0.0
            out = []
            for r in rows:
                db_v, cr_v = float(r[4] or 0), float(r[5] or 0)
                bal += db_v - cr_v
                out.append([r[0], r[1] or "", r[2] or "", r[3] or "", db_v, cr_v, round(bal, 2)])
            return {"success": True, "columns": ["رقم القيد", "التاريخ", "ملاحظات", "البيان", "مدين", "دائن", "الرصيد"], "rows": out}
        if report_id == "bonds_list":
            cur.execute("SELECT TOP 200 b.BondNumber, FORMAT(b.BondDate,'yyyy-MM-dd'), b.Notes, e.EntryName FROM TBL010 b LEFT JOIN TBL009 e ON e.CardGuide = b.MainGuide ORDER BY b.BondDate DESC")
            rows = cur.fetchall()
            return {"success": True, "columns": ["رقم السند", "التاريخ", "ملاحظات", "النوع"], "rows": [[r[0], r[1] or "", r[2] or "", r[3] or ""] for r in rows]}
        if report_id == "entries_list":
            cur.execute("SELECT TOP 200 EntryNumber, FORMAT(EntryDate,'yyyy-MM-dd'), Notes FROM TBL011 ORDER BY EntryDate DESC")
            rows = cur.fetchall()
            return {"success": True, "columns": ["رقم القيد", "التاريخ", "ملاحظات"], "rows": [[r[0], r[1] or "", r[2] or ""] for r in rows]}
        return {"success": False, "message": "تقرير غير معروف"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        cur.close()

@app.route('/api/reports/account-balances')
@login_required
@role_required(['Manager', 'Finance'])
def api_reports_account_balances():
    db = get_db()
    if not db: return jsonify({"success": False, "message": "فشل الاتصال"})
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT a.CardGuide, a.CardCode, a.AccountName,
                CASE WHEN a.AccountName LIKE N'%%صندوق%%' THEN N'cash' WHEN a.AccountName LIKE N'%%بنك%%' THEN N'bank' WHEN a.AccountName LIKE N'%%عهد%%' THEN N'advance' ELSE N'other' END AS Kind,
                ISNULL(SUM(d.Debit),0) - ISNULL(SUM(d.Credit),0) AS Balance
            FROM TBL004 a LEFT JOIN TBL012 d ON d.AccountGuide = a.CardGuide LEFT JOIN TBL011 h ON h.CardGuide = d.MainGuide
            WHERE a.AccountName IS NOT NULL AND (a.AccountName LIKE N'%%صندوق%%' OR a.AccountName LIKE N'%%بنك%%' OR a.AccountName LIKE N'%%عهد%%')
            GROUP BY a.CardGuide, a.CardCode, a.AccountName
            HAVING ISNULL(SUM(d.Debit),0) <> 0 OR ISNULL(SUM(d.Credit),0) <> 0
            ORDER BY a.CardCode
        """)
        cols = [c[0] for c in cur.description]
        items = []
        for r in cur.fetchall():
            d = dict(zip(cols, r))
            items.append({"guide": str(d.get("CardGuide","")), "code": str(d.get("CardCode","")), "name": d.get("AccountName",""), "kind": d.get("Kind","other"), "balance": float(d.get("Balance") or 0)})
        return jsonify({"success": True, "items": items})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        cur.close()

@app.route('/api/reports/<report_id>/run')
@login_required
@role_required(['Manager', 'Finance'])
def api_reports_run(report_id):
    res = _run_report(report_id, request.args.get('from_date'), request.args.get('to_date'),
                      request.args.get('account_guide'), request.args.get('agent_guide'), request.args.get('product_guide'))
    return jsonify(res)

@app.route('/campaigns/create', methods=['GET', 'POST'])
@login_required
def create_ad_campaign():
    # Universal Access
    if request.method == 'POST':
        f = request.form
        try:
            query_db("""
                INSERT INTO Campaigns (
                    Name, MediaType, TargetCount, LanguageLevel, 
                    IsGraduated, Nationality, AgeFrom, AgeTo, 
                    PreferredLocation, SpecialRequirements, RequestID, 
                    Status, CreatedBy, CreatedAt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', ?, GETDATE())
            """, (
                f['title'], f['media_type'], f['target_count'], f['language_level'],
                1 if f.get('is_graduated') == '1' else 0, f['nationality'], f['age_from'], f['age_to'],
                f['location'], f['requirements'], f.get('request_id') or None,
                session['user_id']
            ))
            flash('Ad Campaign Created Successfully! Reference #ID Generated.', 'success')
            return redirect(url_for('recruiter_dashboard')) # Redirect to Dashboard or Campaign List
        except Exception as e:
            flash(f'Error Creating Campaign: {e}', 'danger')

    # Fetch Open Job Orders for linking (Optional)
    open_requests = query_db("SELECT CR.RequestID, CR.JobTitle, C.CompanyName FROM ClientRequests CR JOIN Clients C ON CR.ClientID = C.ClientID WHERE CR.Status='Open'")
    return render_template('campaigns/create.html', requests=open_requests or [])

# --- SEARCH & PROFILE ---
@app.route('/search')
@login_required
def global_search():
    q = request.args.get('q', '').strip()
    if not q:
        return render_template('search.html', results=None, q=q)
    candidates = query_db("SELECT * FROM Candidates WHERE FullName LIKE ? OR Phone LIKE ?", (f'%{q}%', f'%{q}%'))
    clients = query_db("SELECT * FROM Clients WHERE CompanyName LIKE ?", (f'%{q}%',))
    batches = query_db("SELECT B.*, C.CourseName FROM CourseBatches B JOIN Courses C ON B.CourseID = C.CourseID WHERE BatchName LIKE ?", (f'%{q}%',))
    return render_template('search.html', candidates=candidates or [], clients=clients or [], batches=batches or [], q=q)

@app.route('/profile/<int:candidate_id>')
@login_required
def candidate_profile(candidate_id):
    cand = query_db("SELECT * FROM Candidates WHERE CandidateID=?", (candidate_id,), one=True)
    if not cand:
        return "Candidate not found", 404
    training = query_db('''
        SELECT E.*, B.BatchName, C.CourseName, B.StartDate, B.EndDate
        FROM Enrollments E
        JOIN CourseBatches B ON E.BatchID = B.BatchID
        JOIN Courses C ON B.CourseID = C.CourseID
        WHERE E.CandidateID = ?
        ORDER BY B.StartDate DESC
    ''', (candidate_id,))
    payments = []
    if training:
        enrollment_ids = ','.join(str(t['EnrollmentID']) for t in training)
        payments = query_db(f"SELECT * FROM StudentPayments WHERE EnrollmentID IN ({enrollment_ids}) ORDER BY PaymentDate DESC")
    matches = query_db('''
        SELECT M.*, CR.JobTitle, Cl.CompanyName
        FROM Matches M
        JOIN ClientRequests CR ON M.RequestID = CR.RequestID
        JOIN Clients Cl ON CR.ClientID = Cl.ClientID
        WHERE M.CandidateID = ?
        ORDER BY M.MatchDate DESC
    ''', (candidate_id,))
    # ملف المتدرب الكامل: مصدر، تقييم أولي، حضور (استعلامات آمنة)
    recruiter_name = None
    if cand.get('SalesAgentID'):
        try:
            r = query_db('SELECT FullName FROM Users_1 WHERE UserID = ?', (cand['SalesAgentID'],), one=True)
            if r and r.get('FullName'):
                recruiter_name = r['FullName']
        except Exception:
            pass
    placement_tests = []
    try:
        placement_tests = query_db(
            'SELECT TestID, TestDate, ResultLevel, TestStatus, PaymentStatus, Notes FROM PlacementTests WHERE CandidateID = ? ORDER BY TestDate DESC',
            (candidate_id,)
        ) or []
    except Exception:
        pass
    attendance_list = []
    attendance_summary = []
    try:
        attendance_list = query_db('''
            SELECT A.Date, A.Status, B.BatchName, A.LateMinutes, A.TotalHours
            FROM Attendance A
            JOIN Enrollments E ON A.EnrollmentID = E.EnrollmentID
            JOIN CourseBatches B ON E.BatchID = B.BatchID
            WHERE E.CandidateID = ?
            ORDER BY A.Date DESC
        ''', (candidate_id,)) or []
        attendance_summary = query_db('''
            SELECT E.EnrollmentID, B.BatchName,
                   ISNULL(SUM(A.LateMinutes), 0) AS TotalDelayMinutes,
                   SUM(CASE WHEN A.Status = 'Absent' THEN 1 ELSE 0 END) AS AbsenceCount,
                   ISNULL(SUM(A.TotalHours), 0) AS TotalHours
            FROM Enrollments E
            JOIN CourseBatches B ON E.BatchID = B.BatchID
            LEFT JOIN Attendance A ON A.EnrollmentID = E.EnrollmentID
            WHERE E.CandidateID = ?
            GROUP BY E.EnrollmentID, B.BatchName
        ''', (candidate_id,)) or []
    except Exception:
        pass
    # حقول قد لا تكون موجودة في كل قواعد البيانات
    source_channel = cand.get('SourceChannel') if hasattr(cand, 'get') else getattr(cand, 'SourceChannel', None)
    placement_reason = cand.get('PlacementReason') if hasattr(cand, 'get') else getattr(cand, 'PlacementReason', None)
    marketing_assessment = cand.get('MarketingAssessment') if hasattr(cand, 'get') else getattr(cand, 'MarketingAssessment', None)
    # كل حقول الأوراق (TraineeSheetData) — من Guide Academy 2025
    sheet_data_list = []
    try:
        rows = query_db('SELECT SheetName, JsonData FROM TraineeSheetData WHERE CandidateID=? ORDER BY SheetName', (candidate_id,))
        if rows:
            import json
            for r in rows:
                try:
                    data = json.loads(r['JsonData']) if r.get('JsonData') else []
                    sheet_data_list.append({'sheet_name': r['SheetName'], 'rows': data if isinstance(data, list) else [data]})
                except Exception:
                    sheet_data_list.append({'sheet_name': r['SheetName'], 'rows': []})
    except Exception:
        pass
    # سجل ملاحظات المدرب اليومية (جدول تفاصيل — فيه حقل المتدرب CandidateID)
    trainer_notes_list = []
    try:
        trainer_notes_list = query_db('''
            SELECT N.NoteDate, N.Notes, N.CreatedAt, U.FullName AS TrainerName, B.BatchName, Cr.CourseName
            FROM TrainerDailyNotes N
            LEFT JOIN Enrollments E ON N.EnrollmentID = E.EnrollmentID
            LEFT JOIN Users_1 U ON N.TrainerID = U.UserID
            LEFT JOIN CourseBatches B ON E.BatchID = B.BatchID
            LEFT JOIN Courses Cr ON B.CourseID = Cr.CourseID
            WHERE N.CandidateID = ?
            ORDER BY N.NoteDate DESC, N.CreatedAt DESC
        ''', (candidate_id,)) or []
    except Exception:
        pass
    # معلومات الفوترة للمتدرب — الفواتير المسجلة له (رسوم امتحان، ايراد دورات، إلخ) من InvoiceHeaders
    candidate_invoices = []
    try:
        candidate_invoices = query_db('''
            SELECT I.InvoiceID, I.InvoiceDate, I.TotalAmount, I.Status,
                   (SELECT TOP 1 II.Description FROM InvoiceItems II WHERE II.InvoiceID = I.InvoiceID) AS FirstItemDescription
            FROM InvoiceHeaders I
            WHERE I.CandidateID = ?
            ORDER BY I.InvoiceDate DESC
        ''', (candidate_id,)) or []
    except Exception:
        pass
    # ملاحظات مختبر المواهب — فصل التدريب عن التوظيف (نوعان من المختبريين)
    talent_feedback_training = []
    talent_feedback_recruitment = []
    try:
        all_feedback = query_db('''
            SELECT E.EvaluationID, E.CEFR_Level, E.Decision, E.Comments, E.EvaluationType, E.RecordingLink, E.EvaluationDate,
                   E.Score_Comprehension, E.Score_Fluency, E.Score_Pronunciation, E.Score_Structure, E.Score_Vocabulary,
                   E.RecommendedLevel, T.Type AS SlotType, T.SlotDate, T.SlotTime, U.FullName AS EvaluatorName
            FROM Evaluations E
            LEFT JOIN TASchedules T ON E.SlotID = T.SlotID
            LEFT JOIN Users_1 U ON E.EvaluatorID = U.UserID
            WHERE E.CandidateID = ?
            ORDER BY E.EvaluationDate DESC, T.SlotDate DESC, T.SlotTime DESC
        ''', (candidate_id,)) or []
        for fb in all_feedback:
            et = (fb.get('EvaluationType') or '').strip()
            st = (fb.get('SlotType') or '').strip()
            if et == 'Training' or st == 'Exam Feedback':
                talent_feedback_training.append(fb)
            else:
                talent_feedback_recruitment.append(fb)
    except Exception:
        pass
    # اسم وتاريخ من أدخل ملاحظات الريكروتر
    recruiter_feedback_by_name = None
    recruiter_feedback_date = None
    if cand and cand.get('RecruiterFeedbackBy'):
        try:
            rfb = query_db('SELECT FullName, Username FROM Users_1 WHERE UserID = ?', (cand['RecruiterFeedbackBy'],), one=True)
            if rfb:
                recruiter_feedback_by_name = rfb.get('FullName') or rfb.get('Username') or ''
        except Exception:
            pass
    if cand and cand.get('RecruiterFeedbackDate'):
        rd = cand['RecruiterFeedbackDate']
        recruiter_feedback_date = rd.strftime('%Y-%m-%d %H:%M') if hasattr(rd, 'strftime') else str(rd)[:16]

    ta_schedule_appointments = []
    try:
        ta_schedule_appointments = query_db(
            """
            SELECT T.SlotID, T.SlotDate, T.SlotTime, T.Status, T.InterviewType, T.Type,
                   ISNULL(T.AssessmentContext, N'Recruitment') AS AssessmentContext,
                   U.FullName AS EvaluatorName
            FROM TASchedules T
            LEFT JOIN Users_1 U ON T.EvaluatorID = U.UserID
            WHERE T.CandidateID = ?
              AND T.Status IN (N'Booked', N'Completed', N'No Show')
            ORDER BY T.SlotDate DESC, T.SlotTime DESC
            """,
            (candidate_id,),
        ) or []
    except Exception:
        pass

    return render_template(
        'profile.html',
        cand=cand,
        training=training or [],
        payments=payments or [],
        matches=matches or [],
        recruiter_name=recruiter_name,
        placement_tests=placement_tests,
        attendance_list=attendance_list,
        attendance_summary=attendance_summary,
        source_channel=source_channel,
        placement_reason=placement_reason,
        marketing_assessment=marketing_assessment,
        sheet_data_list=sheet_data_list,
        trainer_notes_list=trainer_notes_list,
        candidate_invoices=candidate_invoices,
        talent_feedback_training=talent_feedback_training,
        talent_feedback_recruitment=talent_feedback_recruitment,
        ta_schedule_appointments=ta_schedule_appointments,
        recruiter_feedback=(cand.get('RecruiterFeedback') or '') if cand else '',
        recruiter_feedback_by_name=recruiter_feedback_by_name,
        recruiter_feedback_date=recruiter_feedback_date,
    )

def _append_sheet_row(candidate_id, sheet_name, new_row):
    """إضافة سجل واحد لجدول TraineeSheetData (للتشغيل اليومي)."""
    existing = query_db('SELECT Id, JsonData FROM TraineeSheetData WHERE CandidateID=? AND SheetName=?', (candidate_id, sheet_name), one=True)
    import json
    row_str = json.dumps(new_row, ensure_ascii=False, default=str)
    if existing and existing.get('JsonData'):
        try:
            data = json.loads(existing['JsonData'])
            if not isinstance(data, list):
                data = [data]
            data.append(new_row)
            query_db('UPDATE TraineeSheetData SET JsonData=?, UpdatedAt=GETDATE() WHERE Id=?', (json.dumps(data, ensure_ascii=False, default=str), existing['Id']))
        except Exception:
            query_db('INSERT INTO TraineeSheetData (CandidateID, SheetName, JsonData) VALUES (?, ?, ?)', (candidate_id, sheet_name, json.dumps([new_row], ensure_ascii=False, default=str)))
    else:
        query_db('INSERT INTO TraineeSheetData (CandidateID, SheetName, JsonData) VALUES (?, ?, ?)', (candidate_id, sheet_name, json.dumps([new_row], ensure_ascii=False, default=str)))

@app.route('/profile/<int:candidate_id>/add-booking', methods=['GET', 'POST'])
@login_required
def add_sheet_booking(candidate_id):
    """نافذة إدخال: تسجيل سجل ورقة حجز (Booking Placements) — للتشغيل اليومي."""
    cand = query_db('SELECT CandidateID, FullName, Phone, Email FROM Candidates WHERE CandidateID=?', (candidate_id,), one=True)
    if not cand:
        return 'Candidate not found', 404
    if request.method == 'POST':
        f = request.form
        row = {
            "Candidate's Name": f.get('name') or cand.get('FullName'),
            "Phone No.": f.get('phone') or cand.get('Phone'),
            "Email": f.get('email') or cand.get('Email'),
            "Booked for": f.get('booked_for'),
            "Recruiter": f.get('recruiter'),
            "Venue": f.get('venue'),
            "Source": f.get('source'),
            "Placement reason": f.get('placement_reason'),
            "Pay Status": f.get('pay_status'),
        }
        row = {k: (v.strip() if v else None) for k, v in row.items() if v}
        try:
            _append_sheet_row(candidate_id, 'Booking Placements Sheet', row)
            flash('تم تسجيل سجل الحجز.', 'success')
        except Exception as e:
            flash('خطأ: ' + str(e)[:80], 'danger')
        return redirect(url_for('candidate_profile', candidate_id=candidate_id))
    recruiters = query_db("SELECT UserID, FullName, Username FROM Users_1 WHERE Role IN ('Recruiter', 'Sales')")
    return render_template('profile/add_booking_sheet.html', cand=cand, recruiters=recruiters or [])

@app.route('/profile/<int:candidate_id>/add-ga', methods=['GET', 'POST'])
@login_required
def add_sheet_ga(candidate_id):
    """نافذة إدخال: تسجيل سجل مقابلة GA (GA Interviews) — للتشغيل اليومي."""
    cand = query_db('SELECT CandidateID, FullName, Phone, Email FROM Candidates WHERE CandidateID=?', (candidate_id,), one=True)
    if not cand:
        return 'Candidate not found', 404
    if request.method == 'POST':
        f = request.form
        row = {
            "Date": f.get('date'),
            "Time": f.get('time'),
            "Candidate Name": f.get('name') or cand.get('FullName'),
            "Pri #": f.get('phone') or cand.get('Phone'),
            "Email": f.get('email') or cand.get('Email'),
            "Recruiter": f.get('recruiter'),
            "Source": f.get('source'),
            "Venue": f.get('venue'),
            "Placement reason": f.get('placement_reason'),
            "Location": f.get('location'),
            "C": f.get('c'), "F": f.get('f'), "P": f.get('p'), "G": f.get('g'), "V": f.get('v'),
            "Language comments": f.get('language_comments'),
            "Grad Stat": f.get('grad_stat'),
            "CEFR": f.get('cefr'),
            "Recording link": f.get('recording_link'),
            "Status": f.get('status'),
            "Rec. Project": f.get('rec_project'),
            "Interviewer": f.get('interviewer'),
        }
        row = {k: (v.strip() if v else None) for k, v in row.items() if v}
        try:
            _append_sheet_row(candidate_id, 'GA Interviews', row)
            flash('تم تسجيل سجل مقابلة GA.', 'success')
        except Exception as e:
            flash('خطأ: ' + str(e)[:80], 'danger')
        return redirect(url_for('candidate_profile', candidate_id=candidate_id))
    evaluators = query_db("SELECT UserID, FullName, Username FROM Users_1 WHERE Role IN ('Talent', 'Talent_Recruitment', 'Talent_Training', 'TA-Training')")
    recruiters = query_db("SELECT UserID, FullName, Username FROM Users_1 WHERE Role IN ('Recruiter', 'Sales')")
    return render_template('profile/add_ga_sheet.html', cand=cand, evaluators=evaluators or [], recruiters=recruiters or [])

@app.route('/profile/<int:candidate_id>/add-exit-makeup', methods=['GET', 'POST'])
@login_required
def add_sheet_exit_makeup(candidate_id):
    """نافذة إدخال: تسجيل سجل Exit Make-Up — للتشغيل اليومي."""
    cand = query_db('SELECT CandidateID, FullName, Phone, Email FROM Candidates WHERE CandidateID=?', (candidate_id,), one=True)
    if not cand:
        return 'Candidate not found', 404
    if request.method == 'POST':
        f = request.form
        row = {
            "Time": f.get('time'),
            "Candidate Name": f.get('name') or cand.get('FullName'),
            "Pri #": f.get('phone') or cand.get('Phone'),
            "Wave": f.get('wave'),
            "Venue": f.get('venue'),
            "C": f.get('c'), "F": f.get('f'), "P": f.get('p'), "G": f.get('g'), "V": f.get('v'),
            "Language comments": f.get('language_comments'),
            "CEFR": f.get('cefr'),
            "Recording Link": f.get('recording_link'),
            "Status": f.get('status'),
            "Rec. Project": f.get('rec_project'),
            "Interviewer": f.get('interviewer'),
            "Closer": f.get('closer'),
            "Language Feedback": f.get('language_feedback'),
            "Closing Status": f.get('closing_status'),
        }
        row = {k: (v.strip() if isinstance(v, str) and v else v) for k, v in row.items() if v is not None and v != ''}
        try:
            _append_sheet_row(candidate_id, 'Exit Make-Up', row)
            flash('تم تسجيل سجل Exit Make-Up.', 'success')
        except Exception as e:
            flash('خطأ: ' + str(e)[:80], 'danger')
        return redirect(url_for('candidate_profile', candidate_id=candidate_id))
    evaluators = query_db("SELECT UserID, FullName, Username FROM Users_1 WHERE Role IN ('Talent', 'Talent_Recruitment', 'Talent_Training', 'TA-Training', 'Trainer')")
    return render_template('profile/add_exit_makeup_sheet.html', cand=cand, evaluators=evaluators or [])

@app.route('/admin/users')
@login_required
@role_required(['Manager'])
def manage_users():
    users = query_db("SELECT * FROM Users_1")
    return render_template('admin/users.html', users=users or [])

@app.route('/admin/add_user', methods=['POST'])
@login_required
@role_required(['Manager'])
def add_user():
    f = request.form
    # Basic Validation
    existing = query_db("SELECT * FROM Users_1 WHERE Username=?", (f['username'],), one=True)
    if existing:
        flash('Username already exists', 'danger')
        return redirect(url_for('manage_users'))
        
    query_db("INSERT INTO Users_1 (Username, Password, Role) VALUES (?, ?, ?)", (f['username'], f['password'], f['role']))
    flash(f"User {f['username']} created as {f['role']}", 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/delete_user/<int:user_id>')
@login_required
@role_required(['Manager'])
def delete_user(user_id):
    if user_id == session['user_id']:
        flash('Cannot delete yourself', 'danger')
    else:
        query_db("DELETE FROM Users_1 WHERE UserID=?", (user_id,))
        flash('User deleted', 'success')
    return redirect(url_for('manage_users'))
@app.route('/training/batch/<int:batch_id>/set-status', methods=['POST'])
@login_required
@role_required(['Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator', 'TrainingSalesCoordinator'])
def set_batch_status(batch_id):
    """تغيير حالة الدفعة من Active إلى Completed (غير منشطة) أو العكس."""
    new_status = (request.form.get('status') or '').strip()
    if new_status not in ('Active', 'Completed', 'Inactive'):
        flash('الحالة غير صالحة. استخدم Active أو Completed.', 'warning')
        return redirect(request.referrer or url_for('browse_academy'))
    if new_status == 'Inactive':
        new_status = 'Completed'  # توحيد: غير منشطة = Completed
    batch = query_db("SELECT BatchID FROM CourseBatches WHERE BatchID = ?", (batch_id,), one=True)
    if not batch:
        flash('الدفعة غير موجودة.', 'danger')
        return redirect(request.referrer or url_for('browse_academy'))
    try:
        query_db("UPDATE CourseBatches SET Status = ? WHERE BatchID = ?", (new_status, batch_id))
        flash(f'تم تغيير حالة الدفعة إلى «{new_status}».', 'success')
    except Exception as e:
        flash('خطأ: ' + str(e)[:80], 'danger')
    return redirect(request.referrer or url_for('browse_academy'))


@app.route('/browse')
@login_required
def browse_academy():
    """استعراض الدورات، المدربين، الفصول، الدفعات — متاح لجميع المستخدمين."""
    courses = query_db("SELECT * FROM Courses ORDER BY CourseName")
    trainers = query_db("SELECT * FROM Trainers ORDER BY FullName")
    classrooms = query_db("SELECT * FROM Classrooms ORDER BY RoomName")
    batches = query_db("""
        SELECT B.BatchID, B.BatchName, B.StartDate, B.EndDate, B.Status,
               C.CourseName, T.FullName as TrainerName, R.RoomName
        FROM CourseBatches B
        JOIN Courses C ON B.CourseID = C.CourseID
        LEFT JOIN Trainers T ON B.TrainerID = T.TrainerID
        LEFT JOIN Classrooms R ON B.RoomID = R.RoomID
        ORDER BY B.StartDate DESC, B.BatchName
    """)
    return render_template('browse.html', courses=courses or [], trainers=trainers or [], classrooms=classrooms or [], batches=batches or [])


# --- مبيعات التدريب (محاكاة مبيعات التوظيف): نوافذ مثل التوظيف — Dashboard, Workbench, Scheduling, متابعة ---
@app.route('/training/sales')
@login_required
@role_required(['TrainingSales', 'TrainingSalesCoordinator', 'Manager'])
def training_sales_dashboard():
    """لوحة مبيعات التدريب — محاكاة لوحة التوظيف (إحصائيات + اختصارات المسار)."""
    user_id = session.get('user_id')
    today = datetime.today().strftime('%Y-%m-%d')
    try:
        metrics = {
            'my_leads': query_db("SELECT COUNT(*) as c FROM Candidates WHERE (PrimaryIntent='Training' OR Status='Training_Lead') AND (SalesAgentID=? OR SalesAgentID IS NULL)", (user_id,), one=True)['c'],
            'booked_today': query_db("""
                SELECT COUNT(*) as c FROM TASchedules T
                JOIN Candidates C ON T.CandidateID = C.CandidateID
                WHERE (C.PrimaryIntent='Training' OR C.Status='Training_Lead') AND T.SlotDate = ? AND T.Status = 'Booked'
                  AND (T.AssessmentContext = N'Training' OR (T.AssessmentContext IS NULL AND T.EvaluatorID IN (
                      SELECT UserID FROM Users_1 WHERE Role IN ('Talent_Training', 'TA-Training')
                  )))
            """, (today,), one=True)['c'],
            'pending_slots': query_db("""
                SELECT COUNT(*) as c FROM TASchedules T
                JOIN Candidates C ON T.CandidateID = C.CandidateID
                WHERE (C.PrimaryIntent='Training' OR C.Status='Training_Lead') AND T.Status = 'Booked' AND T.SlotDate >= ?
                  AND (T.AssessmentContext = N'Training' OR (T.AssessmentContext IS NULL AND T.EvaluatorID IN (
                      SELECT UserID FROM Users_1 WHERE Role IN ('Talent_Training', 'TA-Training')
                  )))
            """, (today,), one=True)['c'],
            'no_slot_yet': query_db("""
                SELECT COUNT(*) as c FROM Candidates C
                WHERE (C.PrimaryIntent='Training' OR C.Status='Training_Lead')
                AND NOT EXISTS (
                    SELECT 1 FROM TASchedules T
                    WHERE T.CandidateID = C.CandidateID AND T.Status IN ('Booked', 'Completed')
                    AND (T.AssessmentContext = N'Training' OR (T.AssessmentContext IS NULL AND T.EvaluatorID IN (
                        SELECT UserID FROM Users_1 WHERE Role IN ('Talent_Training', 'TA-Training')
                    )))
                )
            """, one=True)['c'],
        }
    except Exception:
        metrics = {'my_leads': 0, 'booked_today': 0, 'pending_slots': 0, 'no_slot_yet': 0}
    return render_template('training/sales_dashboard.html', metrics=metrics)


@app.route('/training/sales/workbench')
@login_required
@role_required(['TrainingSales', 'TrainingSalesCoordinator', 'Manager'])
def training_sales_index():
    """لوحة مبيعات التدريب: تسجيل مهتم تدريب، قائمة المهتمين (من لم يُحجز لهم موعد بعد)، حجز موعد اختبار مواهب تدريب. بعد الحجز ينتقلون لقائمة متابعة المواعيد."""
    # مهتمو التدريب: من لم يُحجز لهم موعد بعد (بعد الحجز يختفون من هنا ويظهرون في متابعة المواعيد)
    try:
        training_leads = query_db("""
            SELECT C.CandidateID, C.FullName, C.Phone, C.Email, C.Status, C.CreatedAt, C.PrimaryIntent,
                   C.TrainingLeadSubtype, C.UniversityCollege, C.ResidenceArea, C.SourceChannel, C.GraduationStatus
            FROM Candidates C
            WHERE (C.PrimaryIntent = 'Training' OR C.Status = 'Training_Lead')
            AND NOT EXISTS (
                SELECT 1 FROM TASchedules T
                WHERE T.CandidateID = C.CandidateID AND T.Status IN ('Booked', 'Completed')
                AND (T.AssessmentContext = N'Training' OR (T.AssessmentContext IS NULL AND T.EvaluatorID IN (
                    SELECT UserID FROM Users_1 WHERE Role IN ('Talent_Training', 'TA-Training')
                )))
            )
            ORDER BY C.CreatedAt DESC
        """)
    except Exception:
        training_leads = []
    return render_template('training/sales_index.html', training_leads=training_leads or [])


@app.route('/training/sales/register', methods=['POST'])
@login_required
@role_required(['TrainingSales', 'TrainingSalesCoordinator', 'Manager'])
def training_sales_register():
    """تسجيل مهتم تدريب (تعريف المهتم لأول مرة)."""
    f = request.form
    full_name = (f.get('full_name') or '').strip()
    phone = (f.get('phone') or '').strip()
    email = (f.get('email') or '').strip()
    university = (f.get('university_college') or '').strip()
    residence = (f.get('residence_area') or '').strip()
    source = (f.get('lead_source') or '').strip()
    age_s = (f.get('age') or '').strip()
    birth_s = (f.get('birth_date') or '').strip()
    graduate = (f.get('is_graduate') or '').strip()
    _tl = (f.get('training_lead_type') or '').strip().lower()
    train_to_hire = _tl == 'train_to_hire' or f.get('train_to_hire') in (
        '1',
        'on',
        'yes',
        'true',
        'True',
    )
    lk_deg = (f.get('tth_link_degree') or '').strip()
    lk_mail = (f.get('tth_link_alt_email') or '').strip()
    lk_id = (f.get('tth_link_idcard') or '').strip()
    lk_ctr = (f.get('tth_link_contract') or '').strip()

    if not full_name or not phone or not email:
        flash('الاسم والهاتف والبريد إلزاميون.', 'danger')
        return redirect(url_for('training_sales_index'))
    if not university or not residence or not source:
        flash('الجامعة/الكلية ومنطقة السكن والمصدر إلزاميون.', 'danger')
        return redirect(url_for('training_sales_index'))
    if not age_s and not birth_s:
        flash('أدخل العمر أو تاريخ الميلاد.', 'danger')
        return redirect(url_for('training_sales_index'))
    if not graduate:
        flash('حدد هل المتخرج أم لا.', 'danger')
        return redirect(url_for('training_sales_index'))
    if train_to_hire:
        for label, v in (
            ('شهادة/قيد', lk_deg),
            ('إيميل بديل', lk_mail),
            ('بطاقة', lk_id),
            ('تعاقد جهة', lk_ctr),
        ):
            if not v or not v.lower().startswith('http'):
                flash(f'Train to Hire: رابط Google Drive إلزامي ({label}).', 'danger')
                return redirect(url_for('training_sales_index'))

    subtype = TRAINING_LEAD_SUBTYPE_TRAIN_TO_HIRE if train_to_hire else TRAINING_LEAD_SUBTYPE_INTERESTED
    birth_d = None
    if birth_s:
        try:
            birth_d = datetime.strptime(birth_s[:10], '%Y-%m-%d').date()
        except ValueError:
            flash('تاريخ الميلاد غير صالح (YYYY-MM-DD).', 'danger')
            return redirect(url_for('training_sales_index'))
    age_val = None
    if age_s:
        try:
            age_val = int(age_s)
        except ValueError:
            flash('العمر رقماً صحيحاً.', 'danger')
            return redirect(url_for('training_sales_index'))

    agent = session.get('user_id')
    try:
        query_db(
            """
            INSERT INTO Candidates (
                FullName, Phone, Email, Status, CreatedAt, PrimaryIntent, SalesAgentID,
                SourceChannel, GraduationStatus, TrainingLeadSubtype,
                UniversityCollege, ResidenceArea, BirthDate, Age,
                TrainToHire_Link_Degree, TrainToHire_Link_AltEmail, TrainToHire_Link_IdCard, TrainToHire_Link_Contract
            )
            VALUES (?, ?, ?, 'Training_Lead', GETDATE(), 'Training', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                full_name,
                phone,
                email,
                agent,
                source,
                graduate,
                subtype,
                university,
                residence,
                birth_d,
                age_val,
                lk_deg or None,
                lk_mail or None,
                lk_id or None,
                lk_ctr or None,
            ),
        )
        flash('تم تسجيل مهتم التدريب بنجاح.', 'success')
    except Exception as e1:
        try:
            query_db(
                """
                INSERT INTO Candidates (FullName, Phone, Email, Status, CreatedAt, PrimaryIntent, SalesAgentID)
                VALUES (?, ?, ?, 'Training_Lead', GETDATE(), 'Training', ?)
                """,
                (full_name, phone, email, agent),
            )
            cid_row = query_db(
                "SELECT TOP 1 CandidateID FROM Candidates WHERE Phone=? ORDER BY CandidateID DESC",
                (phone,),
                one=True,
            )
            if cid_row:
                cid = cid_row['CandidateID']
                try:
                    query_db(
                        """
                        UPDATE Candidates SET SourceChannel=?, GraduationStatus=?, TrainingLeadSubtype=?,
                        UniversityCollege=?, ResidenceArea=?, BirthDate=?, Age=?,
                        TrainToHire_Link_Degree=?, TrainToHire_Link_AltEmail=?,
                        TrainToHire_Link_IdCard=?, TrainToHire_Link_Contract=?
                        WHERE CandidateID=?
                        """,
                        (
                            source,
                            graduate,
                            subtype,
                            university,
                            residence,
                            birth_d,
                            age_val,
                            lk_deg or None,
                            lk_mail or None,
                            lk_id or None,
                            lk_ctr or None,
                            cid,
                        ),
                    )
                except Exception:
                    pass
            flash('تم تسجيل مهتم التدريب بنجاح.', 'success')
        except Exception as e2:
            flash('خطأ عند التسجيل: ' + str(e2)[:120], 'danger')
    return redirect(url_for('training_sales_index'))


@app.route('/training/sales/book/<int:candidate_id>', methods=['GET', 'POST'])
@login_required
@role_required(['TrainingSales', 'TrainingSalesCoordinator', 'Manager', 'TrainingCoordinator'])
def training_sales_book_slot(candidate_id):
    """حجز موعد اختبار مواهب تدريب لمهتم (عرض شاغر لمختبر مواهب التدريب)."""
    _ensure_taschedules_assessment_context_column()
    cand = query_db(
        """
        SELECT CandidateID, FullName, Phone, Email, PrimaryIntent, Status, TrainingLeadSubtype,
               TrainToHire_Link_Degree, TrainToHire_Link_AltEmail, TrainToHire_Link_IdCard, TrainToHire_Link_Contract
        FROM Candidates WHERE CandidateID = ?
        """,
        (candidate_id,),
        one=True,
    )
    if not cand:
        flash('المرشح غير موجود.', 'danger')
        return redirect(url_for('training_sales_index'))
    subtype = _candidate_training_lead_subtype(cand)
    has_exam_inv = _candidate_has_training_exam_fee_paid(candidate_id)
    tth_ok = _train_to_hire_docs_complete(cand) if subtype == TRAINING_LEAD_SUBTYPE_TRAIN_TO_HIRE else False
    can_book = (subtype == TRAINING_LEAD_SUBTYPE_TRAIN_TO_HIRE and tth_ok) or (
        subtype == TRAINING_LEAD_SUBTYPE_INTERESTED and has_exam_inv
    )
    if request.method == 'POST':
        if not can_book:
            if subtype == TRAINING_LEAD_SUBTYPE_INTERESTED:
                flash('لا يمكن الحجز قبل تسجيل دفع رسوم امتحان تحديد المستوى (Exam Fee).', 'danger')
            else:
                flash('Train to Hire: أكمل روابط المستندات الأربعة (Google Drive) قبل الحجز.', 'danger')
            return redirect(url_for('training_sales_book_slot', candidate_id=candidate_id))
        slot_id = request.form.get('slot_id')
        test_mode = request.form.get('test_mode', 'Online')  # أون لاين أو أون سايت — مثل اختبار المواهب
        if slot_id:
            try:
                query_db(f"""
                    UPDATE TASchedules SET Status='Booked', CandidateID=?, BookedBy=?, Type='Initial Assessment', InterviewType=?
                    WHERE SlotID=? AND CandidateID IS NULL AND EvaluatorID IS NOT NULL
                      {_SQL_TA_A_TRAINING.strip()}
                      AND (
                            LOWER(LTRIM(RTRIM(ISNULL(Status, N'')))) = N'available'
                            OR Status IS NULL
                            OR LTRIM(RTRIM(ISNULL(Status, N''))) = N''
                      )
                """, (candidate_id, session.get('user_id'), test_mode, int(slot_id)))
                flash('تم حجز موعد اختبار مواهب التدريب بنجاح.', 'success')
            except Exception as e:
                flash('خطأ عند الحجز: ' + str(e)[:80], 'danger')
        return redirect(url_for('training_sales_scheduling'))
    # GET: شواغر مجمع مختبر التدريب فقط
    ids = _training_ta_evaluator_ids()
    if not ids:
        available_slots = []
    else:
        slot_q_training = f"""
            SELECT T.SlotID, T.SlotDate, T.SlotTime, U.FullName as EvaluatorName
            FROM TASchedules T
            JOIN Users_1 U ON T.EvaluatorID = U.UserID
            WHERE T.CandidateID IS NULL
              {_SQL_TA_T_TRAINING.strip()}
              AND (
                    LOWER(LTRIM(RTRIM(ISNULL(T.Status, N'')))) = N'available'
                    OR T.Status IS NULL
                    OR LTRIM(RTRIM(ISNULL(T.Status, N''))) = N''
              )
              AND T.SlotDate >= CAST(GETDATE() AS DATE)
            ORDER BY T.SlotDate, T.SlotTime
        """
        available_slots = query_db(slot_q_training) or []
        if not available_slots:
            try:
                today = datetime.today().date()
                end = today + timedelta(days=13)
                _ensure_ta_slots_for_date_range(ids, today, end, TA_CTX_TRAINING)
                available_slots = query_db(slot_q_training) or []
            except Exception:
                pass
    return render_template(
        'training/sales_book_slot.html',
        candidate=cand,
        available_slots=available_slots or [],
        can_book_training_slot=can_book,
        has_exam_fee_invoice=has_exam_inv,
        train_to_hire_docs_ok=tth_ok,
        training_lead_subtype=subtype,
    )


@app.route('/training/sales/scheduling')
@login_required
@role_required(['TrainingSales', 'TrainingSalesCoordinator', 'Manager'])
def training_sales_scheduling():
    """جدولة اختبار التدريب — من لم يُحجز لهم موعد بعد + روابط الحجز (محاكاة Scheduling للتوظيف)."""
    try:
        needs_slot = query_db("""
            SELECT C.CandidateID, C.FullName, C.Phone, C.Status, C.CreatedAt
            FROM Candidates C
            WHERE (C.PrimaryIntent = 'Training' OR C.Status = 'Training_Lead')
            AND NOT EXISTS (
                SELECT 1 FROM TASchedules T
                WHERE T.CandidateID = C.CandidateID AND T.Status IN ('Booked', 'Completed')
                AND (T.AssessmentContext = N'Training' OR (T.AssessmentContext IS NULL AND T.EvaluatorID IN (
                    SELECT UserID FROM Users_1 WHERE Role IN ('Talent_Training', 'TA-Training')
                )))
            )
            ORDER BY C.CreatedAt DESC
        """)
    except Exception:
        needs_slot = []
    return render_template('training/sales_scheduling.html', needs_slot=needs_slot or [])


@app.route('/training/sales/followup')
@login_required
@role_required(['TrainingSales', 'TrainingSalesCoordinator', 'Manager'])
def training_sales_followup():
    """متابعة المواعيد — من حُجز لهم موعد (اليوم والقادم) لمتابعة وصول المهتم (محاكاة متابعة التوظيف)."""
    today = datetime.today().strftime('%Y-%m-%d')
    try:
        booked_today = query_db("""
            SELECT T.SlotID, T.SlotDate, T.SlotTime, T.InterviewType, C.CandidateID, C.FullName, C.Phone, U.FullName as EvaluatorName
            FROM TASchedules T
            JOIN Candidates C ON T.CandidateID = C.CandidateID
            LEFT JOIN Users_1 U ON T.EvaluatorID = U.UserID
            WHERE (C.PrimaryIntent = 'Training' OR C.Status = 'Training_Lead') AND T.Status = 'Booked' AND T.SlotDate = ?
              AND (T.AssessmentContext = N'Training' OR (T.AssessmentContext IS NULL AND T.EvaluatorID IN (
                  SELECT UserID FROM Users_1 WHERE Role IN ('Talent_Training', 'TA-Training')
              )))
            ORDER BY T.SlotTime
        """, (today,))
        booked_upcoming = query_db("""
            SELECT T.SlotID, T.SlotDate, T.SlotTime, T.InterviewType, C.CandidateID, C.FullName, C.Phone, U.FullName as EvaluatorName
            FROM TASchedules T
            JOIN Candidates C ON T.CandidateID = C.CandidateID
            LEFT JOIN Users_1 U ON T.EvaluatorID = U.UserID
            WHERE (C.PrimaryIntent = 'Training' OR C.Status = 'Training_Lead') AND T.Status = 'Booked' AND T.SlotDate > ?
              AND (T.AssessmentContext = N'Training' OR (T.AssessmentContext IS NULL AND T.EvaluatorID IN (
                  SELECT UserID FROM Users_1 WHERE Role IN ('Talent_Training', 'TA-Training')
              )))
            ORDER BY T.SlotDate, T.SlotTime
        """, (today,))
    except Exception:
        booked_today = []
        booked_upcoming = []
    return render_template('training/sales_followup.html', booked_today=booked_today or [], booked_upcoming=booked_upcoming or [], today=today)


@app.route('/training/sales/to-be-close', methods=['GET', 'POST'])
@login_required
@role_required(['TrainingSales', 'TrainingSalesCoordinator', 'Manager'])
def training_sales_to_be_close():
    """قائمة TO BE CLOSE — مهتم تدريب + Accepted (اختبار تحديد مستوى/تخرج) لمتابعة الإغلاق."""
    if request.method == 'POST':
        cid = request.form.get('candidate_id')
        try:
            cid_int = int(cid)
        except (TypeError, ValueError):
            cid_int = None
        if not cid_int:
            flash('مرشح غير محدد.', 'warning')
            return redirect(url_for('training_sales_to_be_close'))
        closer_uid = session.get('user_id')
        closer_row = query_db("SELECT FullName, Username FROM Users_1 WHERE UserID=?", (closer_uid,), one=True)
        closer_name = (request.form.get('closer_name') or '').strip() or (
            (closer_row.get('FullName') or closer_row.get('Username') or '') if closer_row else ''
        )
        st = (request.form.get('closing_status') or '').strip()
        if st and st not in TRAINING_CLOSING_STATUS_VALUES:
            flash('Closing Status غير صالح.', 'danger')
            return redirect(url_for('training_sales_to_be_close'))
        try:
            query_db(
                """
                UPDATE Candidates SET
                    TrainingClosing_FollowUpDate = ?,
                    TrainingClosing_CloserUserID = ?,
                    TrainingClosing_CloserName = ?,
                    TrainingClosing_LanguageFeedback = ?,
                    TrainingClosing_Status = ?,
                    TrainingClosing_StatusDate = ?,
                    TrainingClosing_Reason = ?
                WHERE CandidateID = ? AND TrainingSalesQueue = ?
                """,
                (
                    request.form.get('follow_up_date') or None,
                    closer_uid,
                    closer_name or None,
                    (request.form.get('language_feedback') or '')[:4000] or None,
                    st or None,
                    request.form.get('status_date') or None,
                    (request.form.get('reason') or '')[:4000] or None,
                    cid_int,
                    TRAINING_QUEUE_TO_BE_CLOSE,
                ),
            )
            flash('تم حفظ بيانات الإغلاق.', 'success')
        except Exception as e:
            flash('خطأ: ' + str(e)[:80], 'danger')
        return redirect(url_for('training_sales_to_be_close'))
    rows = query_db(
        """
        SELECT C.*, S.Username AS RegAgentUsername, S.FullName AS RegAgentName
        FROM Candidates C
        LEFT JOIN Users_1 S ON C.SalesAgentID = S.UserID
        WHERE C.TrainingSalesQueue = ?
          AND (C.PrimaryIntent = N'Training' OR C.Status = N'Training_Lead')
        ORDER BY C.CreatedAt DESC
        """,
        (TRAINING_QUEUE_TO_BE_CLOSE,),
    ) or []
    return render_template(
        'training/sales_to_be_close.html',
        rows=rows,
        closing_statuses=TRAINING_CLOSING_STATUS_VALUES,
    )


# --- اشتراكات التدريب (بعد Close): أول مرة / Upgrade level ---
@app.route('/training/enrollment/ready-first-time')
@login_required
@role_required(['Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator', 'TrainingSalesCoordinator'])
def training_enrollment_ready_first_time():
    """جاهزين للاشتراك أول مرة: Accepted (Placement) + Close Confirmed Training + بدون أي Enrollment سابق."""
    active_batches = query_db(
        "SELECT B.BatchID, B.BatchName, C.CourseName, C.DefaultPrice "
        "FROM CourseBatches B JOIN Courses C ON B.CourseID=C.CourseID "
        "WHERE B.Status='Active' ORDER BY B.StartDate DESC, B.BatchName"
    ) or []
    rows = query_db(
        """
        SELECT C.CandidateID, C.FullName, C.Phone, C.Email, C.CurrentCEFR,
               C.TrainingClosing_CloserName, C.TrainingClosing_StatusDate,
               C.TrainingClosing_LanguageFeedback,
               (SELECT TOP 1 E.EvaluationDate FROM Evaluations E
                 WHERE E.CandidateID=C.CandidateID AND E.EvaluationType=? AND E.Decision='Accepted'
                 ORDER BY E.EvaluationDate DESC) AS LastPlacementAcceptedDate
        FROM Candidates C
        WHERE (C.PrimaryIntent = N'Training' OR C.Status = N'Training_Lead')
          AND C.TrainingSalesQueue = ?
          AND C.TrainingClosing_Status = N'Confirmed Training'
          AND NOT EXISTS (SELECT 1 FROM Enrollments En WHERE En.CandidateID = C.CandidateID)
          AND EXISTS (SELECT 1 FROM Evaluations E WHERE E.CandidateID=C.CandidateID AND E.EvaluationType=? AND E.Decision='Accepted')
        ORDER BY ISNULL(C.TrainingClosing_StatusDate, C.CreatedAt) DESC
        """,
        (EVAL_TRAINING_PLACEMENT, TRAINING_QUEUE_TO_BE_CLOSE, EVAL_TRAINING_PLACEMENT),
    ) or []
    return render_template('training/enroll_ready_first_time.html', rows=rows, active_batches=active_batches)


@app.route('/training/enrollment/upgrade-level')
@login_required
@role_required(['Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator', 'TrainingSalesCoordinator'])
def training_enrollment_upgrade_level():
    """Upgrade level: Close Confirmed Training + لديه Enrollments سابقة + Accepted (Graduation/Exit)."""
    active_batches = query_db(
        "SELECT B.BatchID, B.BatchName, C.CourseName, C.DefaultPrice "
        "FROM CourseBatches B JOIN Courses C ON B.CourseID=C.CourseID "
        "WHERE B.Status='Active' ORDER BY B.StartDate DESC, B.BatchName"
    ) or []
    rows = query_db(
        """
        SELECT C.CandidateID, C.FullName, C.Phone, C.Email, C.CurrentCEFR,
               C.TrainingClosing_CloserName, C.TrainingClosing_StatusDate,
               (SELECT TOP 1 B.BatchName FROM Enrollments En JOIN CourseBatches B ON En.BatchID=B.BatchID
                 WHERE En.CandidateID=C.CandidateID ORDER BY En.EnrollmentDate DESC) AS LastBatch,
               (SELECT TOP 1 E.EvaluationDate FROM Evaluations E
                 WHERE E.CandidateID=C.CandidateID AND E.EvaluationType=? AND E.Decision='Accepted'
                 ORDER BY E.EvaluationDate DESC) AS LastExitAcceptedDate
        FROM Candidates C
        WHERE (C.PrimaryIntent = N'Training' OR C.Status = N'Training_Lead')
          AND C.TrainingClosing_Status = N'Confirmed Training'
          AND EXISTS (SELECT 1 FROM Enrollments En WHERE En.CandidateID = C.CandidateID)
          AND EXISTS (SELECT 1 FROM Evaluations E WHERE E.CandidateID=C.CandidateID AND E.EvaluationType=? AND E.Decision='Accepted')
        ORDER BY ISNULL(C.TrainingClosing_StatusDate, C.CreatedAt) DESC
        """,
        (EVAL_TRAINING_GRADUATION, EVAL_TRAINING_GRADUATION),
    ) or []
    return render_template('training/enroll_upgrade_level.html', rows=rows, active_batches=active_batches)


@app.route('/training/sales/acceptance-train-to-hire')
@login_required
@role_required(['TrainingSalesCoordinator', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'Manager', 'Finance'])
def training_sales_acceptance_train_to_hire():
    rows = query_db(
        """
        SELECT C.*, S.Username AS RegAgentUsername, S.FullName AS RegAgentName
        FROM Candidates C
        LEFT JOIN Users_1 S ON C.SalesAgentID = S.UserID
        WHERE C.TrainingSalesQueue = ?
          AND (C.PrimaryIntent = N'Training' OR C.Status = N'Training_Lead')
        ORDER BY C.CreatedAt DESC
        """,
        (TRAINING_QUEUE_ACCEPTANCE_TTH,),
    ) or []
    return render_template('training/sales_acceptance_tth.html', rows=rows)


@app.route('/training/sales/needs-reschedule')
@login_required
@role_required(['TrainingSales', 'TrainingSalesCoordinator', 'Manager'])
def training_sales_needs_reschedule():
    rows = query_db(
        """
        SELECT C.*, S.Username AS RegAgentUsername, S.FullName AS RegAgentName
        FROM Candidates C
        LEFT JOIN Users_1 S ON C.SalesAgentID = S.UserID
        WHERE C.TrainingSalesQueue = ?
          AND (C.PrimaryIntent = N'Training' OR C.Status = N'Training_Lead')
        ORDER BY C.CreatedAt DESC
        """,
        (TRAINING_QUEUE_RETURN_SALES,),
    ) or []
    return render_template('training/sales_needs_reschedule.html', rows=rows)


@app.route('/talent/training/pending-final')
@login_required
@role_required(['Talent_Training', 'TA-Training', 'Manager'])
def talent_training_pending_final():
    rows = query_db(
        """
        SELECT C.*, S.Username AS RegAgentUsername, S.FullName AS RegAgentName
        FROM Candidates C
        LEFT JOIN Users_1 S ON C.SalesAgentID = S.UserID
        WHERE C.TrainingTA_Substatus = ?
          AND (C.PrimaryIntent = N'Training' OR C.Status = N'Training_Lead')
        ORDER BY C.CreatedAt DESC
        """,
        (TRAINING_TA_SUBSTATUS_PENDING,),
    ) or []
    return render_template('talent/training_pending_final.html', rows=rows)


@app.route('/training/reports/current-courses')
@login_required
@role_required(['Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator', 'TrainingSalesCoordinator'])
def training_reports_current_courses():
    _ensure_course_batches_capacity_column()
    df = (request.args.get('from') or '').strip()
    dt = (request.args.get('to') or '').strip()
    has_cap = _db_has_column('CourseBatches', 'MaxCapacity')
    # Use XML PATH aggregation for compatibility (works on SQL Server 2012+).
    agg_exam_dates_sql = """
        STUFF((
            SELECT N' | ' + CONVERT(NVARCHAR(10), BE.ExamDate, 23) +
                   COALESCE(N' (' + BE.ExamLabel + N')', N'')
            FROM BatchExamDates BE
            WHERE BE.BatchID = B.BatchID
            ORDER BY BE.ExamDate
            FOR XML PATH(''), TYPE
        ).value('.', 'nvarchar(max)'), 1, 3, N'')
    """
    sql = f"""
        SELECT B.BatchID,
               B.BatchName AS wave, C.CourseName AS course_level, R.RoomName AS room,
               B.StartDate, B.EndDate, T.FullName AS trainer_name, B.WeekDays AS days,
               B.StartTime, B.EndTime, B.Status,
               {( 'B.MaxCapacity' if has_cap else 'NULL AS MaxCapacity' )},
               (SELECT COUNT(*) FROM Enrollments E WHERE E.BatchID=B.BatchID AND E.Status='Active') AS enrolled_count,
               ({agg_exam_dates_sql}) AS periodic_exam_dates
        FROM CourseBatches B
        JOIN Courses C ON B.CourseID = C.CourseID
        LEFT JOIN Trainers T ON B.TrainerID = T.TrainerID
        LEFT JOIN Classrooms R ON B.RoomID = R.RoomID
        WHERE B.Status = N'Active'
    """
    params = []
    if df:
        sql += " AND B.StartDate >= CAST(? AS DATE)"
        params.append(df)
    if dt:
        sql += " AND B.EndDate <= CAST(? AS DATE)"
        params.append(dt)
    sql += " ORDER BY B.StartDate, B.BatchName"
    try:
        rows = query_db(sql, tuple(params)) if params else (query_db(sql) or [])
    except Exception:
        # Last resort fallback: no capacity, no exam-date aggregation (avoid 500)
        sql2 = """
            SELECT B.BatchID,
                   B.BatchName AS wave, C.CourseName AS course_level, R.RoomName AS room,
                   B.StartDate, B.EndDate, T.FullName AS trainer_name, B.WeekDays AS days,
                   B.StartTime, B.EndTime, B.Status,
                   NULL AS MaxCapacity,
                   (SELECT COUNT(*) FROM Enrollments E WHERE E.BatchID=B.BatchID AND E.Status='Active') AS enrolled_count,
                   NULL AS periodic_exam_dates
            FROM CourseBatches B
            JOIN Courses C ON B.CourseID = C.CourseID
            LEFT JOIN Trainers T ON B.TrainerID = T.TrainerID
            LEFT JOIN Classrooms R ON B.RoomID = R.RoomID
            WHERE B.Status = N'Active'
        """
        params2 = []
        if df:
            sql2 += " AND B.StartDate >= CAST(? AS DATE)"
            params2.append(df)
        if dt:
            sql2 += " AND B.EndDate <= CAST(? AS DATE)"
            params2.append(dt)
        sql2 += " ORDER BY B.StartDate, B.BatchName"
        rows = query_db(sql2, tuple(params2)) if params2 else (query_db(sql2) or [])
    return render_template('training/reports_current_courses.html', rows=rows or [], df=df, dt=dt)


@app.route('/training/reports/future-batches')
@login_required
@role_required(['Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator', 'TrainingSalesCoordinator'])
def training_reports_future_batches():
    _ensure_course_batches_capacity_column()
    today = datetime.today().strftime('%Y-%m-%d')
    has_cap = _db_has_column('CourseBatches', 'MaxCapacity')
    agg_exam_dates_sql = """
        STUFF((
            SELECT N' | ' + CONVERT(NVARCHAR(10), BE.ExamDate, 23) +
                   COALESCE(N' (' + BE.ExamLabel + N')', N'')
            FROM BatchExamDates BE
            WHERE BE.BatchID = B.BatchID
            ORDER BY BE.ExamDate
            FOR XML PATH(''), TYPE
        ).value('.', 'nvarchar(max)'), 1, 3, N'')
    """
    sql = f"""
        SELECT B.BatchID, B.BatchName, C.CourseName, B.StartDate, B.EndDate, T.FullName AS TrainerName,
               R.RoomName, B.WeekDays, B.StartTime, B.EndTime, B.Status,
               {( 'B.MaxCapacity' if has_cap else 'NULL AS MaxCapacity' )},
               (SELECT COUNT(*) FROM Enrollments E WHERE E.BatchID=B.BatchID AND E.Status='Active') AS enrolled_count,
               ({agg_exam_dates_sql}) AS periodic_exam_dates
        FROM CourseBatches B
        JOIN Courses C ON B.CourseID = C.CourseID
        LEFT JOIN Trainers T ON B.TrainerID = T.TrainerID
        LEFT JOIN Classrooms R ON B.RoomID = R.RoomID
        WHERE B.StartDate >= CAST(GETDATE() AS DATE)
        ORDER BY B.StartDate, B.BatchName
    """
    try:
        rows = query_db(sql) or []
    except Exception:
        rows = query_db(
            """
            SELECT B.BatchID, B.BatchName, C.CourseName, B.StartDate, B.EndDate, T.FullName AS TrainerName,
                   R.RoomName, B.WeekDays, B.StartTime, B.EndTime, B.Status,
                   NULL AS MaxCapacity,
                   (SELECT COUNT(*) FROM Enrollments E WHERE E.BatchID=B.BatchID AND E.Status='Active') AS enrolled_count,
                   NULL AS periodic_exam_dates
            FROM CourseBatches B
            JOIN Courses C ON B.CourseID = C.CourseID
            LEFT JOIN Trainers T ON B.TrainerID = T.TrainerID
            LEFT JOIN Classrooms R ON B.RoomID = R.RoomID
            WHERE B.StartDate >= CAST(GETDATE() AS DATE)
            ORDER BY B.StartDate, B.BatchName
            """
        ) or []
    return render_template('training/reports_future_batches.html', rows=rows, today=today)


EXAM_FEE_DESCRIPTION = 'رسوم امتحان تحديد المستوى'

# فاتورة رسوم امتحان تدريب — TBL022/TBL023 (TBL020 نوع الفاتورة، TBL007 الصنف)
EXAM_FEE_BILL_TYPE = '4590AFCC-3215-4213-9625-A59BD4EFAA3E'   # MainGuide = رسوم امتحان تدريب
EXAM_FEE_PRODUCT = 'F6776237-EFD0-48C1-B906-013B118B592E'     # TBL007 الصنف
EXAM_FEE_STORE = '6F058E4B-69B5-43E9-9873-697091C98591'      # جايد المخزن
EXAM_FEE_CURRENCY = 'F128EEE5-B7EA-4C47-A804-CFD3E6ABEE8E'   # جايد العملة

# فاتورة التدريب — ايراد دورات (جدول 20 + جدول 7)
TRAINING_BILL_TYPE = 'AA290AC4-ECD8-4EC0-851B-FC34DC65C9C7'   # TBL020: ايراد دورات تدريب
TRAINING_PRODUCT = '4F08EC42-70EB-418F-A7C0-9D4C6447E345'     # TBL007: ايرادات دورات
TRAINING_FEE_DESCRIPTION = 'ايراد دورات تدريب'


def _create_invoice_tbl022_023(cursor, amount, notes, bill_type_guid, product_guid, default_notes,
                               store_guid=None, currency_guid=None, agent_guide=None, pay_method=1):
    """إنشاء فاتورة في TBL022 + TBL023 (نمط أكسترا ويب). قيمة الدفعة = amount تُسجّل في TBL022.Paid و TBL023.TotalValue."""
    import uuid
    store_guid = store_guid or EXAM_FEE_STORE
    currency_guid = currency_guid or EXAM_FEE_CURRENCY
    try:
        cursor.execute("""
            SELECT ISNULL(MAX(BillNumber), 0) + 1 FROM TBL022 WHERE MainGuide = ?
        """, (bill_type_guid,))
        row = cursor.fetchone()
        bill_num = (row[0] if row else 0) or 1
        bill_guid = str(uuid.uuid4())
        row_guid = str(uuid.uuid4())
        notes_str = (notes or default_notes or '')[:255]
        # TBL022 — نمط أكسترا: CardGuide, MainGuide, BillNumber, BillDate, DoneIn, AgentGuide, Notes, ..., Paid (قيمة الدفعة), PayMethod
        cursor.execute("""
            INSERT INTO TBL022 (CardGuide, MainGuide, BillNumber, BillDate, DoneIn, AgentGuide, Notes,
                Discount, TaxValue, LocalAdministrativeTax, LockRelations, InsertedIn, Paid, PayMethod, StoreGuide, CurrencyGuide)
            VALUES (?, ?, ?, GETDATE(), GETDATE(), ?, ?, 0, 0, 0, 0, GETDATE(), ?, ?, ?, ?)
        """, (bill_guid, bill_type_guid, bill_num, agent_guide, notes_str, amount, pay_method, store_guid, currency_guid))
        # TBL023 — نمط أكسترا: MainGuide, ProductGuide, Quantity, Unit, TotalValue, InsertedIn, RelatedAgent (قيمة البند = قيمة الدفعة)
        cursor.execute("""
            INSERT INTO TBL023 (RowGuide, MainGuide, ProductGuide, Quantity, Unit, TotalValue, InsertedIn, RelatedAgent)
            VALUES (?, ?, ?, 1, 0, ?, GETDATE(), ?)
        """, (row_guid, bill_guid, product_guid, amount, agent_guide))
        return True
    except Exception:
        return False


def _pay_method_to_int(method):
    """تحويل طريقة الدفع من النص إلى رقم (نمط أكسترا)."""
    return {'نقدي': 0, 'بطاقة': 1, 'تحويل': 2}.get((method or '').strip(), 0)


def _create_exam_fee_invoice_tbl022_023(cursor, amount, notes, pay_method=0):
    """إنشاء فاتورة رسوم امتحان في TBL022 + TBL023. قيمة الدفعة = amount في Paid و TotalValue."""
    return _create_invoice_tbl022_023(
        cursor, amount, notes, EXAM_FEE_BILL_TYPE, EXAM_FEE_PRODUCT, EXAM_FEE_DESCRIPTION,
        store_guid=EXAM_FEE_STORE, currency_guid=EXAM_FEE_CURRENCY, pay_method=pay_method)


def _create_training_fee_invoice_tbl022_023(cursor, amount, notes, pay_method=0):
    """إنشاء فاتورة ايراد دورات في TBL022 + TBL023. قيمة الدفعة = amount في Paid و TotalValue."""
    return _create_invoice_tbl022_023(
        cursor, amount, notes, TRAINING_BILL_TYPE, TRAINING_PRODUCT, TRAINING_FEE_DESCRIPTION,
        store_guid=EXAM_FEE_STORE, currency_guid=EXAM_FEE_CURRENCY, pay_method=pay_method)


@app.route('/training/sales/exam-fee', methods=['GET', 'POST'])
@login_required
@role_required(['TrainingSales', 'TrainingSalesCoordinator', 'Manager', 'Finance'])
def training_sales_exam_fee():
    if request.method == 'POST':
        candidate_id = request.form.get('candidate_id')
        amount = request.form.get('amount')
        notes = (request.form.get('notes') or '').strip() or EXAM_FEE_DESCRIPTION
        payment_method = (request.form.get('payment_method') or '').strip()
        if payment_method:
            notes = notes + ' | الدفع: ' + payment_method
        if not candidate_id or not amount:
            flash('الرجاء اختيار المهتم وإدخال المبلغ.', 'danger')
            return redirect(url_for('training_sales_exam_fee'))
        try:
            amount_f = float(amount)
        except ValueError:
            flash('المبلغ غير صالح.', 'danger')
            return redirect(url_for('training_sales_exam_fee'))
        cand = query_db('SELECT FullName FROM Candidates WHERE CandidateID = ?', (int(candidate_id),), one=True)
        customer_name = (cand.get('FullName') or '').strip() if cand else ''
        if customer_name:
            notes = 'اسم العميل: ' + customer_name + ' | ' + notes
        pay_method_num = _pay_method_to_int(payment_method)
        db = get_db()
        if not db:
            flash('خطأ في الاتصال بقاعدة البيانات.', 'danger')
            return redirect(url_for('training_sales_exam_fee'))
        cursor = db.cursor()
        try:
            saved = False
            try:
                if _create_exam_fee_invoice_tbl022_023(cursor, amount_f, notes, pay_method=pay_method_num):
                    desc = EXAM_FEE_DESCRIPTION + (' | الدفع: ' + payment_method if payment_method else '')
                    if customer_name:
                        desc = 'اسم العميل: ' + customer_name + ' | ' + desc
                    cursor.execute("""
                        INSERT INTO InvoiceHeaders (CandidateID, InvoiceDate, SubTotal, TotalAmount, Status, CreatedBy)
                        OUTPUT INSERTED.InvoiceID
                        VALUES (?, GETDATE(), ?, ?, 'Paid', ?)
                    """, (int(candidate_id), amount_f, amount_f, session.get('user_id')))
                    row = cursor.fetchone()
                    invoice_id = row[0] if row else None
                    if invoice_id:
                        cursor.execute("""
                            INSERT INTO InvoiceItems (InvoiceID, Description, Quantity, UnitPrice, LineTotal)
                            VALUES (?, ?, 1, ?, ?)
                        """, (invoice_id, desc, amount_f, amount_f))
                    db.commit()
                    flash('تم تسجيل فاتورة تحصيل رسوم امتحان بنجاح.', 'success')
                    saved = True
                else:
                    db.rollback()
            except Exception:
                db.rollback()
            if not saved:
                try:
                    desc = EXAM_FEE_DESCRIPTION + (' | الدفع: ' + payment_method if payment_method else '')
                    if customer_name:
                        desc = 'اسم العميل: ' + customer_name + ' | ' + desc
                    cursor.execute("""
                        INSERT INTO InvoiceHeaders (CandidateID, InvoiceDate, SubTotal, TotalAmount, Status, CreatedBy)
                        OUTPUT INSERTED.InvoiceID
                        VALUES (?, GETDATE(), ?, ?, 'Paid', ?)
                    """, (int(candidate_id), amount_f, amount_f, session.get('user_id')))
                    row = cursor.fetchone()
                    invoice_id = row[0] if row else None
                    if invoice_id:
                        cursor.execute("""
                            INSERT INTO InvoiceItems (InvoiceID, Description, Quantity, UnitPrice, LineTotal)
                            VALUES (?, ?, 1, ?, ?)
                        """, (invoice_id, desc, amount_f, amount_f))
                    db.commit()
                    flash('تم تسجيل فاتورة تحصيل رسوم امتحان بنجاح.', 'success')
                except Exception as e:
                    db.rollback()
                    flash('خطأ عند الحفظ: ' + str(e)[:80], 'danger')
        finally:
            cursor.close()
        return redirect(url_for('training_sales_exam_fee'))

    # GET: عرض قائمة المهتمين بالتدريب ونموذج إدخال الفاتورة (20 الأحدث — البحث يجلب عبر API)
    try:
        leads = query_db("""
            SELECT TOP 20 C.CandidateID, C.FullName, C.Phone, C.Email
            FROM Candidates C
            WHERE (C.PrimaryIntent = 'Training' OR C.Status = 'Training_Lead')
            ORDER BY C.CreatedAt DESC
        """) or []
    except Exception:
        leads = []
    try:
        recent_invoices = query_db("""
            SELECT TOP 20 I.InvoiceID, I.InvoiceDate, I.TotalAmount, I.Status, C.FullName,
                   U.Username AS CreatedByUsername
            FROM InvoiceHeaders I
            LEFT JOIN Candidates C ON I.CandidateID = C.CandidateID
            LEFT JOIN Users_1 U ON I.CreatedBy = U.UserID
            WHERE EXISTS (SELECT 1 FROM InvoiceItems II WHERE II.InvoiceID = I.InvoiceID AND II.Description LIKE ?)
            ORDER BY I.InvoiceDate DESC
        """, ('%' + EXAM_FEE_DESCRIPTION + '%',)) or []
    except Exception:
        recent_invoices = []
    return render_template('training/exam_fee_invoice.html', leads=leads, recent_invoices=recent_invoices)


@app.route('/training/sales/exam-fee/<int:invoice_id>/print')
@login_required
@role_required(['TrainingSales', 'TrainingSalesCoordinator', 'Manager', 'TrainingCoordinator', 'TrainingManager', 'Finance'])
def training_sales_exam_fee_print(invoice_id):
    inv = query_db("""
        SELECT I.*, C.FullName, C.Phone FROM InvoiceHeaders I
        LEFT JOIN Candidates C ON I.CandidateID = C.CandidateID WHERE I.InvoiceID = ?
    """, (invoice_id,), one=True)
    if not inv:
        abort(404)
    items = query_db("SELECT * FROM InvoiceItems WHERE InvoiceID = ?", (invoice_id,)) or []
    if not items or not any(EXAM_FEE_DESCRIPTION in (item.get('Description') or '') for item in items):
        abort(404)
    payment_method = ''
    for it in items:
        d = (it.get('Description') or '')
        if 'الدفع:' in d:
            payment_method = d.split('الدفع:')[1].strip()
            break
    return render_template('training/invoice_print.html', invoice=inv, items=items, title='فاتورة تحصيل رسوم امتحان تحديد المستوى', payment_method=payment_method)


@app.route('/training/sales/course-fee', methods=['GET', 'POST'])
@login_required
@role_required(['TrainingSales', 'TrainingSalesCoordinator', 'Manager', 'Finance'])
def training_sales_course_fee():
    if request.method == 'POST':
        candidate_id = request.form.get('candidate_id')
        amount = request.form.get('amount')
        notes = (request.form.get('notes') or '').strip() or TRAINING_FEE_DESCRIPTION
        payment_method = (request.form.get('payment_method') or '').strip()
        if payment_method:
            notes = notes + ' | الدفع: ' + payment_method
        if not candidate_id or not amount:
            flash('الرجاء اختيار المهتم وإدخال المبلغ.', 'danger')
            return redirect(url_for('training_sales_course_fee'))
        try:
            amount_f = float(amount)
        except ValueError:
            flash('المبلغ غير صالح.', 'danger')
            return redirect(url_for('training_sales_course_fee'))
        cand = query_db('SELECT FullName FROM Candidates WHERE CandidateID = ?', (int(candidate_id),), one=True)
        customer_name = (cand.get('FullName') or '').strip() if cand else ''
        if customer_name:
            notes = 'اسم العميل: ' + customer_name + ' | ' + notes
        pay_method_num = _pay_method_to_int(payment_method)
        db = get_db()
        if not db:
            flash('خطأ في الاتصال بقاعدة البيانات.', 'danger')
            return redirect(url_for('training_sales_course_fee'))
        cursor = db.cursor()
        try:
            saved = False
            try:
                if _create_training_fee_invoice_tbl022_023(cursor, amount_f, notes, pay_method=pay_method_num):
                    desc = TRAINING_FEE_DESCRIPTION + (' | الدفع: ' + payment_method if payment_method else '')
                    if customer_name:
                        desc = 'اسم العميل: ' + customer_name + ' | ' + desc
                    cursor.execute("""
                        INSERT INTO InvoiceHeaders (CandidateID, InvoiceDate, SubTotal, TotalAmount, Status, CreatedBy)
                        OUTPUT INSERTED.InvoiceID
                        VALUES (?, GETDATE(), ?, ?, 'Paid', ?)
                    """, (int(candidate_id), amount_f, amount_f, session.get('user_id')))
                    row = cursor.fetchone()
                    invoice_id = row[0] if row else None
                    if invoice_id:
                        cursor.execute("""
                            INSERT INTO InvoiceItems (InvoiceID, Description, Quantity, UnitPrice, LineTotal)
                            VALUES (?, ?, 1, ?, ?)
                        """, (invoice_id, desc, amount_f, amount_f))
                    db.commit()
                    flash('تم تسجيل فاتورة ايراد دورات تدريب بنجاح.', 'success')
                    saved = True
                else:
                    db.rollback()
            except Exception:
                db.rollback()
            if not saved:
                try:
                    desc = TRAINING_FEE_DESCRIPTION + (' | الدفع: ' + payment_method if payment_method else '')
                    if customer_name:
                        desc = 'اسم العميل: ' + customer_name + ' | ' + desc
                    cursor.execute("""
                        INSERT INTO InvoiceHeaders (CandidateID, InvoiceDate, SubTotal, TotalAmount, Status, CreatedBy)
                        OUTPUT INSERTED.InvoiceID
                        VALUES (?, GETDATE(), ?, ?, 'Paid', ?)
                    """, (int(candidate_id), amount_f, amount_f, session.get('user_id')))
                    row = cursor.fetchone()
                    invoice_id = row[0] if row else None
                    if invoice_id:
                        cursor.execute("""
                            INSERT INTO InvoiceItems (InvoiceID, Description, Quantity, UnitPrice, LineTotal)
                            VALUES (?, ?, 1, ?, ?)
                        """, (invoice_id, desc, amount_f, amount_f))
                    db.commit()
                    flash('تم تسجيل فاتورة ايراد دورات تدريب بنجاح.', 'success')
                except Exception as e:
                    db.rollback()
                    flash('خطأ عند الحفظ: ' + str(e)[:80], 'danger')
        finally:
            cursor.close()
        return redirect(url_for('training_sales_course_fee'))

    try:
        leads = query_db("""
            SELECT TOP 20 C.CandidateID, C.FullName, C.Phone, C.Email
            FROM Candidates C
            WHERE (C.PrimaryIntent = 'Training' OR C.Status = 'Training_Lead')
            ORDER BY C.CreatedAt DESC
        """) or []
    except Exception:
        leads = []
    try:
        recent_invoices = query_db("""
            SELECT TOP 20 I.InvoiceID, I.InvoiceDate, I.TotalAmount, I.Status, C.FullName,
                   U.Username AS CreatedByUsername
            FROM InvoiceHeaders I
            LEFT JOIN Candidates C ON I.CandidateID = C.CandidateID
            LEFT JOIN Users_1 U ON I.CreatedBy = U.UserID
            WHERE EXISTS (SELECT 1 FROM InvoiceItems II WHERE II.InvoiceID = I.InvoiceID AND II.Description LIKE ?)
            ORDER BY I.InvoiceDate DESC
        """, ('%' + TRAINING_FEE_DESCRIPTION + '%',)) or []
    except Exception:
        recent_invoices = []
    return render_template('training/course_fee_invoice.html', leads=leads, recent_invoices=recent_invoices)


@app.route('/training/sales/course-fee/<int:invoice_id>/print')
@login_required
@role_required(['TrainingSales', 'TrainingSalesCoordinator', 'Manager', 'TrainingCoordinator', 'TrainingManager', 'Finance'])
def training_sales_course_fee_print(invoice_id):
    inv = query_db("""
        SELECT I.*, C.FullName, C.Phone FROM InvoiceHeaders I
        LEFT JOIN Candidates C ON I.CandidateID = C.CandidateID WHERE I.InvoiceID = ?
    """, (invoice_id,), one=True)
    if not inv:
        abort(404)
    items = query_db("SELECT * FROM InvoiceItems WHERE InvoiceID = ?", (invoice_id,)) or []
    if not items or not any(TRAINING_FEE_DESCRIPTION in (item.get('Description') or '') for item in items):
        abort(404)
    payment_method = ''
    for it in items:
        d = (it.get('Description') or '')
        if 'الدفع:' in d:
            payment_method = d.split('الدفع:')[1].strip()
            break
    return render_template('training/invoice_print.html', invoice=inv, items=items, title='فاتورة ايراد دورات تدريب', payment_method=payment_method)


OPEN_RECRUITMENT_TALENT_SLOT_ROLES = [
    'Manager', 'RecruitmentManager', 'Talent', 'Talent_Recruitment',
]
OPEN_TRAINING_TALENT_SLOT_ROLES = [
    'Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator',
    'TrainingSalesCoordinator', 'Talent_Training', 'TA-Training',
]


def _handle_open_talent_slots_post(redirect_endpoint, assessment_context):
    raw_ids = request.form.getlist('evaluator_id')
    df = (request.form.get('date_from') or '').strip()
    dt = (request.form.get('date_to') or '').strip()
    try:
        d0 = datetime.strptime(df, '%Y-%m-%d').date()
        d1 = datetime.strptime(dt, '%Y-%m-%d').date()
    except ValueError:
        flash('التواريخ يجب أن تكون بصيغة YYYY-MM-DD.', 'danger')
        return redirect(url_for(redirect_endpoint))
    if d1 < d0:
        flash('تاريخ النهاية قبل البداية.', 'danger')
        return redirect(url_for(redirect_endpoint))
    if (d1 - d0).days > 44:
        flash('الحد الأقصى 45 يوماً في المرة الواحدة.', 'warning')
        return redirect(url_for(redirect_endpoint))
    uids = []
    for x in raw_ids:
        try:
            uids.append(int(x))
        except (TypeError, ValueError):
            pass
    uids = list(dict.fromkeys(uids))
    if not uids:
        flash('اختر مقيّماً واحداً على الأقل.', 'warning')
        return redirect(url_for(redirect_endpoint))
    _ensure_taschedules_assessment_context_column()
    _ensure_ta_slots_for_date_range(uids, d0, d1, assessment_context)
    flash(
        f'تم توليد/إكمال الفترات الناقصة ({"توظيف" if assessment_context == TA_CTX_RECRUITMENT else "تدريب"}) من {df} إلى {dt}.',
        'success',
    )
    return redirect(url_for(redirect_endpoint))


@app.route('/recruitment/open-talent-slots', methods=['GET', 'POST'])
@login_required
@role_required(OPEN_RECRUITMENT_TALENT_SLOT_ROLES)
def recruitment_open_talent_slots():
    """فتح شبكة مواعيد مختبر مواهب التوظيف فقط (TASchedules / AssessmentContext = Recruitment)."""
    if request.method == 'POST':
        return _handle_open_talent_slots_post('recruitment_open_talent_slots', TA_CTX_RECRUITMENT)
    staff = _users_for_recruitment_talent_slot_picker()
    return render_template('recruitment/open_talent_slots.html', staff=staff)


@app.route('/training/open-talent-slots', methods=['GET', 'POST'])
@login_required
@role_required(OPEN_TRAINING_TALENT_SLOT_ROLES)
def training_open_talent_slots():
    """فتح شبكة مواعيد مختبر مواهب التدريب فقط (TASchedules / AssessmentContext = Training)."""
    if request.method == 'POST':
        return _handle_open_talent_slots_post('training_open_talent_slots', TA_CTX_TRAINING)
    staff = _users_for_training_talent_slot_picker()
    return render_template('training/open_talent_slots.html', staff=staff)


@app.route('/training/open-assessment-slots', methods=['GET', 'POST'])
@login_required
@role_required(OPEN_TRAINING_TALENT_SLOT_ROLES)
def training_open_assessment_slots():
    """توافق مع الروابط القديمة — نفس منطق فتح مواعيد التدريب."""
    if request.method == 'POST':
        return _handle_open_talent_slots_post('training_open_talent_slots', TA_CTX_TRAINING)
    return redirect(url_for('training_open_talent_slots'))


@app.route('/training/index')
@login_required
@role_required(['Trainer', 'Manager', 'TrainingHead', 'TrainingManager', 'TrainingLead', 'TrainingCoordinator', 'TrainingSales', 'TrainingSalesCoordinator'])
def training_index():
    view = request.args.get('view', 'active')  # active | archive
    base_sql = """
        SELECT B.*, C.CourseName, T.FullName as TrainerName, R.RoomName 
        FROM CourseBatches B 
        JOIN Courses C ON B.CourseID = C.CourseID 
        LEFT JOIN Trainers T ON B.TrainerID = T.TrainerID 
        LEFT JOIN Classrooms R ON B.RoomID = R.RoomID
    """
    if view == 'archive':
        waves = query_db(base_sql + " WHERE (B.Status != 'Active' OR B.Status IS NULL) ORDER BY B.StartDate DESC, B.BatchName")
    else:
        waves = query_db(base_sql + " WHERE B.Status = 'Active' ORDER BY B.StartDate DESC, B.BatchName")
    
    # Also fetch definitions for the tabs
    courses = query_db("SELECT * FROM Courses")
    trainers = query_db("SELECT * FROM Trainers")
    classrooms = query_db("SELECT * FROM Classrooms")

    batches_list = waves or []
    filter_batch_names = sorted(
        {(b.get('BatchName') or '').strip() for b in batches_list if (b.get('BatchName') or '').strip()},
        key=lambda x: x.lower(),
    )
    filter_course_names = sorted(
        {(b.get('CourseName') or '').strip() for b in batches_list if (b.get('CourseName') or '').strip()},
        key=lambda x: x.lower(),
    )
    filter_trainer_names = sorted(
        {(b.get('TrainerName') or '').strip() for b in batches_list if (b.get('TrainerName') or '').strip()},
        key=lambda x: x.lower(),
    )
    filter_room_names = sorted(
        {(b.get('RoomName') or '').strip() for b in batches_list if (b.get('RoomName') or '').strip()},
        key=lambda x: x.lower(),
    )
    filter_status_values = sorted(
        {(b.get('Status') or '').strip() for b in batches_list if (b.get('Status') or '').strip()},
        key=lambda x: x.lower(),
    )
    
    return render_template(
        'training/index.html',
        batches=batches_list,
        courses=courses or [],
        trainers=trainers or [],
        rooms=classrooms or [],
        view=view,
        can_open_training_talent_slots=(session.get('role') in OPEN_TRAINING_TALENT_SLOT_ROLES),
        filter_batch_names=filter_batch_names,
        filter_course_names=filter_course_names,
        filter_trainer_names=filter_trainer_names,
        filter_room_names=filter_room_names,
        filter_status_values=filter_status_values,
    )

@app.route('/training/add_course', methods=['POST'])
@login_required
@role_required(['Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator', 'TrainingSalesCoordinator'])
def add_course():
    f = request.form
    name = (f.get('course_name') or '').strip()
    if not name:
        flash('اسم الدورة مطلوب.', 'danger')
        return redirect(url_for('training_index'))
    try:
        price = float(f.get('default_price') or 0)
    except (TypeError, ValueError):
        price = 0
    try:
        query_db("INSERT INTO Courses (CourseName, DefaultPrice) VALUES (?, ?)", (name, price))
        flash('تمت إضافة الدورة بنجاح.', 'success')
    except Exception as e:
        flash('خطأ عند حفظ الدورة: ' + str(e)[:80], 'danger')
    return redirect(url_for('training_index'))

@app.route('/training/add_trainer', methods=['POST'])
@login_required
@role_required(['Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator', 'TrainingSalesCoordinator'])
def add_trainer():
    f = request.form
    full_name = (f.get('full_name') or '').strip()
    if not full_name:
        flash('اسم المدرب مطلوب.', 'danger')
        return redirect(url_for('training_index'))
    spec = (f.get('specialization') or '').strip() or None
    phone = (f.get('phone') or '').strip() or None
    try:
        query_db("INSERT INTO Trainers (FullName, Specialization, Phone) VALUES (?, ?, ?)", (full_name, spec, phone))
        flash('تمت إضافة المدرب بنجاح.', 'success')
    except Exception as e:
        flash('خطأ عند حفظ المدرب: ' + str(e)[:80], 'danger')
    return redirect(url_for('training_index'))

@app.route('/training/add_classroom', methods=['POST'])
@login_required
@role_required(['Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator', 'TrainingSalesCoordinator'])
def add_classroom():
    f = request.form
    room_name = (f.get('room_name') or '').strip()
    if not room_name:
        flash('اسم القاعة مطلوب.', 'danger')
        return redirect(url_for('training_index'))
    # منع التكرار: نفس الاسم (بدون تمييز حالة)
    existing = query_db("SELECT RoomID FROM Classrooms WHERE LTRIM(RTRIM(RoomName)) = ?", (room_name.strip(),), one=True)
    if existing:
        flash('قاعة بنفس الاسم مسجلة مسبقاً. اختر اسماً آخر أو استخدم القائمة في تكوين الدفعة.', 'warning')
        return redirect(url_for('training_index'))
    try:
        capacity = int(f.get('capacity') or 20)
        if capacity < 1:
            capacity = 20
    except (TypeError, ValueError):
        capacity = 20
    try:
        query_db("INSERT INTO Classrooms (RoomName, Capacity) VALUES (?, ?)", (room_name, capacity))
        flash('تمت إضافة القاعة بنجاح. ستظهر في قائمة «تكوين دفعة».', 'success')
    except Exception as e:
        flash('خطأ عند حفظ القاعة: ' + str(e)[:80], 'danger')
    return redirect(url_for('training_index'))

@app.route('/training/add_batch', methods=['GET', 'POST'])
@login_required
@role_required(['Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator', 'TrainingSalesCoordinator'])
def add_batch():
    if request.method == 'GET':
        return redirect(url_for('training_index'))
    f = request.form
    room_id = f.get('room_id')
    if not room_id or room_id == '':
        room_id = None
    if room_id:
        room_check = query_db("SELECT RoomID FROM Classrooms WHERE RoomID=?", (room_id,), one=True)
        if not room_check:
            flash('القاعة المختارة غير موجودة.', 'danger')
            return redirect(url_for('training_index'))

    start_time = (f.get('start_time') or '').strip() or None
    end_time = (f.get('end_time') or '').strip() or None
    week_days = (f.get('week_days') or '').strip() or None

    try:
        # محاولة مع الأعمدة الجديدة (StartTime, EndTime, WeekDays)
        query_db("""
            INSERT INTO CourseBatches (BatchName, CourseID, TrainerID, RoomID, StartDate, EndDate, StartTime, EndTime, WeekDays, Status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active')
        """, (f['batch_name'], f['course_id'], f.get('trainer_id') or None, room_id, f.get('start_date'), f.get('end_date'), start_time, end_time, week_days))
    except Exception as e:
        err_msg = str(e).lower()
        # إذا الأعمدة غير موجودة (قاعدة قديمة)، نضيفها ثم نعيد المحاولة أو نستخدم INSERT بسيط
        if 'starttime' in err_msg or 'invalid column' in err_msg or 'column name' in err_msg:
            try:
                query_db("ALTER TABLE CourseBatches ADD StartTime TIME NULL")
            except Exception:
                pass
            try:
                query_db("ALTER TABLE CourseBatches ADD EndTime TIME NULL")
            except Exception:
                pass
            try:
                query_db("ALTER TABLE CourseBatches ADD WeekDays NVARCHAR(100) NULL")
            except Exception:
                pass
            try:
                query_db("""
                    INSERT INTO CourseBatches (BatchName, CourseID, TrainerID, RoomID, StartDate, EndDate, StartTime, EndTime, WeekDays, Status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active')
                """, (f['batch_name'], f['course_id'], f.get('trainer_id') or None, room_id, f.get('start_date'), f.get('end_date'), start_time, end_time, week_days))
            except Exception:
                query_db("""
                    INSERT INTO CourseBatches (BatchName, CourseID, TrainerID, RoomID, StartDate, EndDate, Status)
                    VALUES (?, ?, ?, ?, ?, ?, 'Active')
                """, (f['batch_name'], f['course_id'], f.get('trainer_id') or None, room_id, f.get('start_date'), f.get('end_date')))
        else:
            flash(f'خطأ عند إنشاء الدفعة: {str(e)[:100]}', 'danger')
            return redirect(url_for('training_index'))
    flash('تم إنشاء الدفعة بنجاح.', 'success')
    return redirect(url_for('training_index'))

@app.route('/training/batch/<int:batch_id>/update_schedule', methods=['POST'])
@login_required
@role_required(['Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator', 'TrainingSalesCoordinator'])
def update_batch_schedule(batch_id):
    """تحديث كل بيانات الدفعة: الاسم، الدورة، المدرب، القاعة، التواريخ، الأوقات، الأيام."""
    _ensure_course_batches_capacity_column()
    f = request.form
    b = query_db("SELECT BatchID FROM CourseBatches WHERE BatchID=?", (batch_id,), one=True)
    if not b:
        flash('الدفعة غير موجودة.', 'danger')
        return redirect(url_for('training_index'))
    batch_name = (f.get('batch_name') or '').strip()
    course_id = f.get('course_id')
    trainer_id = f.get('trainer_id') or None
    if trainer_id == '': trainer_id = None
    room_id = f.get('room_id') or None
    if room_id == '': room_id = None
    start_date = f.get('start_date') or None
    end_date = f.get('end_date') or None
    start_time = (f.get('start_time') or '').strip() or None
    end_time = (f.get('end_time') or '').strip() or None
    week_days = (f.get('week_days') or '').strip() or None
    max_cap_raw = (f.get('max_capacity') or '').strip()
    max_cap = None
    if max_cap_raw:
        try:
            max_cap = int(max_cap_raw)
        except (TypeError, ValueError):
            max_cap = None
    if max_cap is not None and max_cap < 1:
        max_cap = None
    if not batch_name:
        batch_name = query_db("SELECT BatchName FROM CourseBatches WHERE BatchID=?", (batch_id,), one=True)
        batch_name = batch_name['BatchName'] if batch_name else ''
    if not course_id:
        flash('الدورة مطلوبة.', 'warning')
        return redirect(url_for('wave_details', wave_id=batch_id))
    try:
        query_db("""
            UPDATE CourseBatches SET BatchName=?, CourseID=?, TrainerID=?, RoomID=?,
                   StartDate=?, EndDate=?, StartTime=?, EndTime=?, WeekDays=?, MaxCapacity=?
            WHERE BatchID=?
        """, (batch_name, course_id, trainer_id, room_id, start_date, end_date, start_time, end_time, week_days, max_cap, batch_id))
        flash('تم تحديث بيانات الدفعة بنجاح.', 'success')
    except Exception as e:
        try:
            query_db("""
                UPDATE CourseBatches SET BatchName=?, CourseID=?, TrainerID=?, RoomID=?,
                       StartDate=?, EndDate=?
                WHERE BatchID=?
            """, (batch_name, course_id, trainer_id, room_id, start_date, end_date, batch_id))
            flash('تم تحديث البيانات الأساسية. (وقت/أيام تتطلب تحديث الجدول)', 'success')
        except Exception as e2:
            flash('خطأ: ' + str(e2)[:60], 'danger')
    return redirect(url_for('wave_details', wave_id=batch_id))

@app.route('/training/batch/<int:batch_id>/add_exam_date', methods=['POST'])
@login_required
@role_required(['Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator', 'TrainingSalesCoordinator'])
def add_batch_exam_date(batch_id):
    """إضافة يوم امتحان دوري للدفعة."""
    f = request.form
    exam_date = (f.get('exam_date') or '').strip()
    exam_label = (f.get('exam_label') or '').strip() or 'امتحان دوري'
    if not exam_date:
        flash('التاريخ مطلوب.', 'warning')
        return redirect(url_for('wave_details', wave_id=batch_id))
    b = query_db("SELECT BatchID FROM CourseBatches WHERE BatchID=?", (batch_id,), one=True)
    if not b:
        flash('الدفعة غير موجودة.', 'danger')
        return redirect(url_for('training_index'))
    try:
        cnt = query_db("SELECT COUNT(*) as c FROM BatchExamDates WHERE BatchID=?", (batch_id,), one=True)
        if cnt and int(cnt.get('c') or 0) >= 3:
            flash('الحد الأقصى للامتحانات الدورية هو 3 فقط لهذه الدفعة.', 'warning')
            return redirect(url_for('wave_details', wave_id=batch_id))
    except Exception:
        pass
    try:
        query_db("INSERT INTO BatchExamDates (BatchID, ExamDate, ExamLabel) VALUES (?, ?, ?)", (batch_id, exam_date, exam_label))
        flash('تم إضافة يوم الامتحان.', 'success')
    except Exception as e:
        flash('خطأ: ' + str(e)[:60], 'danger')
    return redirect(url_for('wave_details', wave_id=batch_id))

@app.route('/training/batch/<int:batch_id>/delete_exam_date/<int:exam_date_id>', methods=['POST'])
@login_required
@role_required(['Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator', 'TrainingSalesCoordinator'])
def delete_batch_exam_date(batch_id, exam_date_id):
    query_db("DELETE FROM BatchExamDates WHERE ExamDateID=? AND BatchID=?", (exam_date_id, batch_id))
    flash('تم حذف يوم الامتحان.', 'info')
    return redirect(url_for('wave_details', wave_id=batch_id))

# أعمدة ورقة Excel «Progress report»: عدة صفوف RFI لكل جانب لغوي × أسبوع × متدرب
PROGRESS_SHEET_ASPECTS = (
    'Comprehension',
    'Fluency',
    'Pronunciation',
    'Structure',
    'Vocabulary',
)


def _ensure_enrollment_week_progress_lines_table():
    try:
        query_db(
            """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name='EnrollmentWeekProgressLines' AND xtype='U')
            CREATE TABLE EnrollmentWeekProgressLines (
                LineID INT IDENTITY(1,1) PRIMARY KEY,
                EnrollmentID INT NOT NULL,
                WeekNumber INT NOT NULL,
                LanguageAspect NVARCHAR(40) NOT NULL,
                LineOrder INT NOT NULL DEFAULT 0,
                RFI NVARCHAR(500) NULL,
                Severity NVARCHAR(20) NULL,
                ActionPlan NVARCHAR(MAX) NULL,
                ProgressComment NVARCHAR(MAX) NULL,
                TrainerID INT NULL,
                UpdatedAt DATETIME DEFAULT GETDATE()
            )
            """
        )
    except Exception:
        pass


def _ensure_enrollment_ssr_initial_fb_table():
    """SSR & Initial FB: كويز/امتحان من المدرب + ملاحظات أولية على مستوى (متدرب, أسبوع)."""
    try:
        query_db(
            """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='EnrollmentSSRInitialFB' AND xtype='U')
            CREATE TABLE EnrollmentSSRInitialFB (
                EntryID INT IDENTITY(1,1) PRIMARY KEY,
                EnrollmentID INT NOT NULL,
                WeekNumber INT NOT NULL,
                SSR NVARCHAR(MAX) NULL,
                InitialFeedback NVARCHAR(MAX) NULL,
                QuizScore DECIMAL(5,2) NULL,
                QuizNotes NVARCHAR(MAX) NULL,
                CreatedBy INT NULL,
                CreatedAt DATETIME DEFAULT GETDATE(),
                UNIQUE (EnrollmentID, WeekNumber)
            )
            """
        )
    except Exception:
        pass


def _ensure_course_batches_capacity_column():
    """العدد الأقصى للدفعة (للإشغال/التسويق)."""
    try:
        query_db(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE Name = N'MaxCapacity' AND Object_ID = Object_ID(N'CourseBatches'))
                ALTER TABLE CourseBatches ADD MaxCapacity INT NULL;
            """
        )
    except Exception:
        pass


@app.route('/training/wave/<int:wave_id>/progress-sheets')
@login_required
@role_required(['Trainer', 'Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator', 'TrainingSalesCoordinator'])
def wave_progress_sheets(wave_id):
    """قائمة متدربي الدفعة مع رابط شيت تقدم أسبوعي (مماثل لورقة Progress report في Excel)."""
    _ensure_enrollment_week_progress_lines_table()
    wave = query_db(
        """
        SELECT B.BatchID, B.BatchName, C.CourseName
        FROM CourseBatches B
        JOIN Courses C ON B.CourseID = C.CourseID
        WHERE B.BatchID = ?
        """,
        (wave_id,),
        one=True,
    )
    if not wave:
        return 'Wave not found', 404
    rows = query_db(
        """
        SELECT E.EnrollmentID, C.FullName, C.CandidateID,
               (SELECT COUNT(*) FROM EnrollmentWeekProgressLines L WHERE L.EnrollmentID = E.EnrollmentID) AS SavedLines
        FROM Enrollments E
        JOIN Candidates C ON E.CandidateID = C.CandidateID
        WHERE E.BatchID = ?
        ORDER BY C.FullName
        """,
        (wave_id,),
    ) or []
    return render_template(
        'training/wave_progress_sheets.html',
        wave=wave,
        students=rows,
    )


@app.route('/training/enrollment/<int:enrollment_id>/progress-sheet', methods=['GET', 'POST'])
@login_required
@role_required(['Trainer', 'Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator', 'TrainingSalesCoordinator'])
def enrollment_progress_sheet(enrollment_id):
    """شيت تقييم تقدم أسبوعي لمتدرب واحد — هيكل قريب من Excel (عدة صفوف لكل جانب لغوي)."""
    _ensure_enrollment_week_progress_lines_table()
    stu = query_db(
        """
        SELECT E.EnrollmentID, E.BatchID, C.FullName, C.CandidateID, B.BatchName, Cr.CourseName
        FROM Enrollments E
        JOIN Candidates C ON E.CandidateID = C.CandidateID
        JOIN CourseBatches B ON E.BatchID = B.BatchID
        JOIN Courses Cr ON B.CourseID = Cr.CourseID
        WHERE E.EnrollmentID = ?
        """,
        (enrollment_id,),
        one=True,
    )
    if not stu:
        flash('التسجيل غير موجود.', 'danger')
        return redirect(url_for('training_index'))

    if request.method == 'POST':
        f = request.form
        try:
            week = int(f.get('week_number') or 1)
        except (TypeError, ValueError):
            week = 1
        week = max(1, min(week, 52))
        wave_id = stu['BatchID']
        try:
            query_db(
                'DELETE FROM EnrollmentWeekProgressLines WHERE EnrollmentID=? AND WeekNumber=?',
                (enrollment_id, week),
            )
            uid = session.get('user_id')
            for aspect in PROGRESS_SHEET_ASPECTS:
                rfis = f.getlist(f'{aspect}_rfi')
                sevs = f.getlist(f'{aspect}_severity')
                acts = f.getlist(f'{aspect}_action')
                coms = f.getlist(f'{aspect}_comment')
                n = max(len(rfis), len(sevs), len(acts), len(coms), 0)
                for i in range(n):
                    rfi = (rfis[i] if i < len(rfis) else '') or ''
                    sev = (sevs[i] if i < len(sevs) else '') or ''
                    act = (acts[i] if i < len(acts) else '') or ''
                    com = (coms[i] if i < len(coms) else '') or ''
                    rfi, sev, act, com = rfi.strip(), sev.strip(), act.strip(), com.strip()
                    if not (rfi or sev or act or com):
                        continue
                    query_db(
                        """
                        INSERT INTO EnrollmentWeekProgressLines
                        (EnrollmentID, WeekNumber, LanguageAspect, LineOrder, RFI, Severity, ActionPlan, ProgressComment, TrainerID)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (enrollment_id, week, aspect, i, rfi or None, sev or None, act or None, com or None, uid),
                    )
            flash('تم حفظ شيت التقدم لهذا الأسبوع.', 'success')
        except Exception as ex:
            flash('تعذر الحفظ: ' + str(ex)[:200], 'danger')
        return redirect(
            url_for('enrollment_progress_sheet', enrollment_id=enrollment_id, week=week)
        )

    try:
        week = int(request.args.get('week') or 1)
    except (TypeError, ValueError):
        week = 1
    week = max(1, min(week, 52))

    raw_lines = query_db(
        """
        SELECT LineID, LanguageAspect, LineOrder, RFI, Severity, ActionPlan, ProgressComment
        FROM EnrollmentWeekProgressLines
        WHERE EnrollmentID=? AND WeekNumber=?
        ORDER BY LanguageAspect, LineOrder
        """,
        (enrollment_id, week),
    ) or []

    lines_by_aspect = {a: [] for a in PROGRESS_SHEET_ASPECTS}
    for row in raw_lines:
        asp = (row.get('LanguageAspect') or '').strip()
        if asp in lines_by_aspect:
            lines_by_aspect[asp].append(row)

    return render_template(
        'training/enrollment_progress_sheet.html',
        student=stu,
        week=week,
        lines_by_aspect=lines_by_aspect,
        aspects=PROGRESS_SHEET_ASPECTS,
    )


@app.route('/training/enrollment/<int:enrollment_id>/ssr-initial-fb', methods=['GET', 'POST'])
@login_required
@role_required(['Trainer', 'Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator'])
def enrollment_ssr_initial_fb(enrollment_id):
    """SSR & Initial FB — نموذج المدرب لتسجيل كويز/SSR وملاحظات أولية."""
    _ensure_enrollment_ssr_initial_fb_table()
    stu = query_db(
        """
        SELECT E.EnrollmentID, E.BatchID, C.FullName, C.CandidateID, B.BatchName, Cr.CourseName
        FROM Enrollments E
        JOIN Candidates C ON E.CandidateID = C.CandidateID
        JOIN CourseBatches B ON E.BatchID = B.BatchID
        JOIN Courses Cr ON B.CourseID = Cr.CourseID
        WHERE E.EnrollmentID = ?
        """,
        (enrollment_id,),
        one=True,
    )
    if not stu:
        flash('التسجيل غير موجود.', 'danger')
        return redirect(url_for('training_index'))
    try:
        week = int((request.args.get('week') or request.form.get('week_number') or 1))
    except (TypeError, ValueError):
        week = 1
    week = max(1, min(week, 52))

    if request.method == 'POST':
        f = request.form
        ssr = (f.get('ssr') or '')[:8000]
        init_fb = (f.get('initial_feedback') or '')[:8000]
        quiz_notes = (f.get('quiz_notes') or '')[:8000]
        score_s = (f.get('quiz_score') or '').strip()
        score = None
        if score_s:
            try:
                score = float(score_s)
            except Exception:
                score = None
        uid = session.get('user_id')
        try:
            # Upsert by unique(EnrollmentID, WeekNumber)
            existing = query_db(
                "SELECT EntryID FROM EnrollmentSSRInitialFB WHERE EnrollmentID=? AND WeekNumber=?",
                (enrollment_id, week),
                one=True,
            )
            if existing:
                query_db(
                    """
                    UPDATE EnrollmentSSRInitialFB
                    SET SSR=?, InitialFeedback=?, QuizScore=?, QuizNotes=?, CreatedBy=?, CreatedAt=GETDATE()
                    WHERE EnrollmentID=? AND WeekNumber=?
                    """,
                    (ssr or None, init_fb or None, score, quiz_notes or None, uid, enrollment_id, week),
                )
            else:
                query_db(
                    """
                    INSERT INTO EnrollmentSSRInitialFB (EnrollmentID, WeekNumber, SSR, InitialFeedback, QuizScore, QuizNotes, CreatedBy)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (enrollment_id, week, ssr or None, init_fb or None, score, quiz_notes or None, uid),
                )
            flash('تم حفظ SSR & Initial FB.', 'success')
        except Exception as ex:
            flash('تعذر الحفظ: ' + str(ex)[:200], 'danger')
        return redirect(url_for('enrollment_ssr_initial_fb', enrollment_id=enrollment_id, week=week))

    row = query_db(
        """
        SELECT SSR, InitialFeedback, QuizScore, QuizNotes, CreatedAt
        FROM EnrollmentSSRInitialFB
        WHERE EnrollmentID=? AND WeekNumber=?
        """,
        (enrollment_id, week),
        one=True,
    ) or {}
    return render_template('training/enrollment_ssr_initial_fb.html', student=stu, week=week, row=row)


@app.route('/training/wave/<int:wave_id>')
@login_required
@role_required(['Trainer', 'Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator', 'TrainingSalesCoordinator'])
def wave_details(wave_id):
    wave = query_db("""
        SELECT B.*, C.CourseName,
               T.FullName AS TrainerName, R.RoomName
        FROM CourseBatches B
        JOIN Courses C ON B.CourseID = C.CourseID
        LEFT JOIN Trainers T ON B.TrainerID = T.TrainerID
        LEFT JOIN Classrooms R ON B.RoomID = R.RoomID
        WHERE B.BatchID = ?
    """, (wave_id,), one=True)
    if not wave: return "Wave not found", 404

    wave['StartTimeStr'] = _safe_time_str(wave.get('StartTime'))
    wave['EndTimeStr'] = _safe_time_str(wave.get('EndTime'))

    try:
        exam_dates = query_db("SELECT * FROM BatchExamDates WHERE BatchID=? ORDER BY ExamDate", (wave_id,)) or []
    except Exception:
        exam_dates = []

    students = query_db("""
        SELECT E.*, C.FullName, C.Phone, C.CurrentCEFR
        FROM Enrollments E
        JOIN Candidates C ON E.CandidateID = C.CandidateID
        WHERE E.BatchID = ?
    """, (wave_id,))

    try:
        reports = query_db("""
            SELECT WP.*, C.FullName
            FROM WeeklyProgress WP
            JOIN Enrollments E ON WP.EnrollmentID = E.EnrollmentID
            JOIN Candidates C ON E.CandidateID = C.CandidateID
            WHERE E.BatchID = ?
            ORDER BY WP.WeekNumber DESC, C.FullName ASC
        """, (wave_id,)) or []
    except Exception:
        reports = []

    courses = query_db("SELECT * FROM Courses ORDER BY CourseName")
    trainers = query_db("SELECT * FROM Trainers ORDER BY FullName")
    rooms = query_db("SELECT * FROM Classrooms ORDER BY RoomName")
    return render_template('training/wave_details.html', wave=wave, students=students or [], reports=reports or [], exam_dates=exam_dates, courses=courses or [], trainers=trainers or [], rooms=rooms or [])

@app.route('/training/add_report', methods=['POST'])
@login_required
@role_required(['Manager', 'TrainingManager', 'TrainingHead', 'TrainingLead', 'TrainingCoordinator'])
def add_weekly_report():
    f = request.form
    aspect = (f.get('language_aspect') or '').strip()
    rfi = (f.get('rfi') or '').strip()
    if aspect and aspect != 'General':
        rfi = f"[{aspect}] {rfi}".strip() if rfi else f"[{aspect}]"
    query_db("""
        INSERT INTO WeeklyProgress (EnrollmentID, WeekNumber, Strengths, Weaknesses, RFI, ActionPlan, Severity, TrainerID)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (f['enrollment_id'], f['week_number'], f['strengths'], f['weaknesses'], rfi, f['action_plan'], f['severity'], session['user_id']))
    
    flash('Weekly Report Added', 'success')
    return redirect(url_for('wave_details', wave_id=f['wave_id']))

@app.route('/training/plan/<int:enrollment_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Manager', 'Trainer']) # Ideally Head of Training, but let's allow both for now
def training_plan(enrollment_id):
    student = query_db("""
        SELECT E.*, C.FullName, B.BatchName 
        FROM Enrollments E 
        JOIN Candidates C ON E.CandidateID = C.CandidateID 
        JOIN CourseBatches B ON E.BatchID = B.BatchID
        WHERE E.EnrollmentID = ?
    """, (enrollment_id,), one=True)
    
    if request.method == 'POST':
        query_db("""
            INSERT INTO TrainingPlans (EnrollmentID, WeekNumber, FocusArea, TargetGoals, CreatedBy)
            VALUES (?, ?, ?, ?, ?)
        """, (enrollment_id, request.form['week_number'], request.form['focus_area'], request.form['goals'], session['user_id']))
        flash('Plan Goal Added', 'success')
        return redirect(request.url)
        
    plans = query_db("SELECT * FROM TrainingPlans WHERE EnrollmentID=? ORDER BY WeekNumber", (enrollment_id,))
    return render_template('training/plan.html', student=student, plans=plans or [])

@app.route('/training/matrix/<int:wave_id>')
@login_required
@role_required(['Trainer', 'Manager'])
def attendance_matrix(wave_id):
    wave = query_db("SELECT * FROM CourseBatches WHERE BatchID=?", (wave_id,), one=True)
    students = query_db("SELECT E.EnrollmentID, C.FullName FROM Enrollments E JOIN Candidates C ON E.CandidateID = C.CandidateID WHERE E.BatchID=? ORDER BY C.FullName", (wave_id,))
    
    # Generate last 30 days dates
    dates = []
    from datetime import timedelta # Ensure timedelta is imported
    for i in range(30):
        d = (datetime.today() - timedelta(days=i)).strftime('%Y-%m-%d')
        dates.append(d)
    dates.reverse() # Show oldest to newest
    
    # Fetch existing attendance
    # 'Date' column confirmed
    try:
        att_data = query_db("""
            SELECT A.EnrollmentID, A.Date as AttendanceDate, A.Status 
            FROM Attendance A
            JOIN Enrollments E ON A.EnrollmentID = E.EnrollmentID
            WHERE E.BatchID=?
        """, (wave_id,))
    except Exception as e:
        print(f"Matrix Query Failed: {e}")
        att_data = []

    # Transform to dict: {(EnrollmentID, Date): Status}
    att_map = {}
    if att_data:
        for a in att_data:
            # Handle if date is string or object
            d_val = a['AttendanceDate']
            if hasattr(d_val, 'strftime'):
                d_str = d_val.strftime('%Y-%m-%d')
            else:
                d_str = str(d_val)
            att_map[(a['EnrollmentID'], d_str)] = a['Status']
            
    return render_template('training/matrix.html', wave=wave, students=students or [], dates=dates, att_map=att_map)

@app.route('/training/mark_matrix', methods=['POST'])
@login_required
@role_required(['Trainer', 'Manager'])
def mark_matrix():
    f = request.form
    wave_id = f['wave_id']
    date = f['date']
    
    # Get all enrollments for this wave
    enrollments = query_db("SELECT EnrollmentID FROM Enrollments WHERE BatchID=?", (wave_id,))
    
    for e in enrollments:
        eid = e['EnrollmentID']
        status = f.get(f'status_{eid}', 'Present') # Default to Present if not unchecked/changed
        
        # Upsert logic (Delete then Insert is easier for this scale)
        query_db("DELETE FROM Attendance WHERE EnrollmentID=? AND Date=?", (eid, date))
        # BatchID is not in Attendance table usually, remove it if error persists or add it if needed. 
        # Standard schema: Attendance(AttendanceID, EnrollmentID, Date, Status...)
        query_db("INSERT INTO Attendance (EnrollmentID, Date, Status) VALUES (?, ?, ?)", (eid, date, status))

    flash('Attendance Matrix Saved', 'success')
    return redirect(url_for('attendance_matrix', wave_id=wave_id))

# Old Duplicate Routes Removed

@app.route('/training/graduate_student', methods=['POST'])
@login_required
@role_required(['Trainer', 'Manager'])
def graduate_student():
    f = request.form
    enrollment_id = f['enrollment_id']
    final_grade = float(f['final_grade'])
    
    # 1. Update Enrollment
    status = 'Completed' if final_grade >= 50 else 'Failed'
    query_db("UPDATE Enrollments SET FinalGrade=?, Status=? WHERE EnrollmentID=?", (final_grade, status, enrollment_id))
    
    # 2. Logic for Post-Training
    cand_id = query_db("SELECT CandidateID FROM Enrollments WHERE EnrollmentID=?", (enrollment_id,), one=True)['CandidateID']
    
    if status == 'Completed':
        # Send to Reallocation (Allocator Team or Recruitment)
        # Mark as 'Needs Reallocation' or 'Ready' depending on business rule.
        # As per requirement: "Return to TA for retesting and reallocation"
        query_db("UPDATE Candidates SET Status='PostTraining_Review' WHERE CandidateID=?", (cand_id,))
    else:
        # Failed -> Rejoiner logic
        query_db("UPDATE Candidates SET Rejoiner=1, Status='Needs Retraining' WHERE CandidateID=?", (cand_id,))
        
    flash(f'Student Graduated with status: {status}', 'success')
    return redirect(request.referrer)

@app.route('/api/candidates/search')
@login_required
def api_candidates_search():
    """جلب أقرب 20 مرشح لمطابقة البحث — للانضمام إلى دورة / الفوترة"""
    q = (request.args.get('q') or '').strip()
    limit = min(20, int(request.args.get('limit') or 20))
    context = request.args.get('context', '')  # training = للفوترة/تدريب فقط
    extra = ""
    params_extra = []
    if context == 'training':
        extra = " AND (C.PrimaryIntent = 'Training' OR C.Status = 'Training_Lead')"
    if not q or len(q) < 2:
        return jsonify({'results': []})
    base = "SELECT TOP (?) C.CandidateID, C.FullName, C.Phone FROM Candidates C WHERE (C.FullName LIKE ? OR C.Phone LIKE ?)" + extra + " ORDER BY C.FullName"
    rows = query_db(base, (limit, f'%{q}%', f'%{q}%') + tuple(params_extra)) or []
    return jsonify({'results': [{'id': r['CandidateID'], 'text': f"{r['FullName']} — {r['Phone'] or ''}"} for r in rows]})

@app.route('/training/batch/<int:batch_id>')
@login_required
@role_required(['Manager', 'TrainingCoordinator', 'TrainingSalesCoordinator', 'Trainer', 'TrainingLead'])
def batch_details(batch_id):
    batch = query_db("SELECT B.*, C.CourseName, T.FullName as TrainerName, R.RoomName FROM CourseBatches B JOIN Courses C ON B.CourseID = C.CourseID JOIN Trainers T ON B.TrainerID = T.TrainerID JOIN Classrooms R ON B.RoomID = R.RoomID WHERE B.BatchID = ?", (batch_id,), one=True)
    if not batch: return redirect(url_for('training_index'))
    students = query_db("SELECT E.*, C.FullName, C.Phone FROM Enrollments E JOIN Candidates C ON E.CandidateID = C.CandidateID WHERE E.BatchID = ?", (batch_id,))
    # أول 20 مرشح للعرض الافتراضي — البحث يحمّل عبر API عند الكتابة
    candidates = query_db('SELECT TOP 20 CandidateID, FullName, Phone FROM Candidates ORDER BY FullName')
    return render_template('training/batch_details.html', batch=batch, students=students or [], candidates=candidates or [])

@app.route('/training/notes/<int:enrollment_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Manager', 'TrainingCoordinator', 'TrainingSalesCoordinator', 'Trainer', 'TrainingLead'])
def trainer_notes(enrollment_id):
    """نافذة ملاحظات المدرب اليومية لطالب معيّن (حسب التسجيل في دفعة)."""
    student = query_db("""
        SELECT E.EnrollmentID, E.BatchID, C.CandidateID, C.FullName, B.BatchName, Cr.CourseName
        FROM Enrollments E
        JOIN Candidates C ON E.CandidateID = C.CandidateID
        JOIN CourseBatches B ON E.BatchID = B.BatchID
        JOIN Courses Cr ON B.CourseID = Cr.CourseID
        WHERE E.EnrollmentID = ?
    """, (enrollment_id,), one=True)
    if not student:
        flash('تسجيل الطالب غير موجود', 'danger')
        return redirect(url_for('training_index'))
    if request.method == 'POST':
        note_date = request.form.get('note_date')
        notes_text = request.form.get('notes', '').strip()
        if not note_date or not notes_text:
            flash('أدخل التاريخ ونص الملاحظة', 'warning')
            return redirect(url_for('trainer_notes', enrollment_id=enrollment_id))
        try:
            candidate_id = student.get('CandidateID')
            query_db("""
                INSERT INTO TrainerDailyNotes (CandidateID, EnrollmentID, NoteDate, Notes, TrainerID)
                VALUES (?, ?, ?, ?, ?)
            """, (candidate_id, enrollment_id, note_date, notes_text, session.get('user_id')))
            flash('تم حفظ الملاحظة', 'success')
        except Exception as e:
            flash(f'خطأ في الحفظ: {e}', 'danger')
        return redirect(url_for('trainer_notes', enrollment_id=enrollment_id))
    try:
        notes_list = query_db("""
            SELECT N.NoteID, N.NoteDate, N.Notes, N.CreatedAt, U.FullName as TrainerName
            FROM TrainerDailyNotes N
            LEFT JOIN Users_1 U ON N.TrainerID = U.UserID
            WHERE N.EnrollmentID = ?
            ORDER BY N.NoteDate DESC, N.CreatedAt DESC
        """, (enrollment_id,)) or []
    except Exception:
        notes_list = []
    return render_template('training/trainer_notes.html', student=student, notes_list=notes_list)

@app.route('/training/enroll_student', methods=['POST'])
@login_required
@role_required(['Manager', 'TrainingCoordinator', 'TrainingSalesCoordinator', 'Trainer', 'TrainingLead'])
def enroll_student():
    f = request.form
    batch_id = f.get('batch_id')
    cand_id = f.get('candidate_id')
    price = f.get('agreed_price')
    notes = f.get('notes')
    
    if not batch_id or not cand_id:
        flash('Missing batch or candidate', 'danger')
        return redirect(request.referrer)
        
    # Get Default Price if not provided
    if not price:
        batch = query_db("SELECT C.DefaultPrice FROM CourseBatches B JOIN Courses C ON B.CourseID=C.CourseID WHERE B.BatchID=?", (batch_id,), one=True)
        price = batch['DefaultPrice'] if batch else 0
        
    # Check existing enrollment
    existing = query_db("SELECT * FROM Enrollments WHERE BatchID=? AND CandidateID=?", (batch_id, cand_id), one=True)
    if existing:
        flash('Student already enrolled in this batch', 'warning')
        return redirect(request.referrer)
        
    query_db("INSERT INTO Enrollments (BatchID, CandidateID, EnrollmentDate, Status, AgreedPrice, Notes) VALUES (?, ?, GETDATE(), 'Active', ?, ?)",
             (batch_id, cand_id, price, notes))
             
    # Update Candidate Status
    query_db("UPDATE Candidates SET Status='Enrolled' WHERE CandidateID=?", (cand_id,))

    # After enrollment: clear sales queue flags for closed leads
    try:
        query_db(
            "UPDATE Candidates SET TrainingSalesQueue=NULL, TrainingTA_Substatus=NULL WHERE CandidateID=?",
            (cand_id,),
        )
    except Exception:
        pass
    
    flash('Student Enrolled Successfully', 'success')
    return redirect(request.referrer)

@app.route('/training/hiring_plan')
@login_required
@role_required(['TrainingManager', 'Manager'])
def hiring_plan_simulation():
    # 1. Fetch Students Ready for Next Level (Graduates)
    # We look for Enrollments with 'Completed' status
    graduates = query_db("""
        SELECT C.FullName, C.CandidateID, E.EnrollmentID, T.TrainingLevel as CompletedLevel 
        FROM Enrollments E
        JOIN Candidates C ON E.CandidateID = C.CandidateID
        JOIN TrainingOffers T ON E.OfferID = T.OfferID
        WHERE E.Status = 'Completed' AND C.Status != 'Enrolled'
    """)
    
    # 2. Fetch New Candidates (Evaluated by TA but not enrolled yet)
    new_candidates = query_db("""
        SELECT C.FullName, C.CandidateID, C.CurrentCEFR as TargetLevel
        FROM Candidates C
        WHERE C.Status = 'Evaluated' AND C.PrimaryIntent IN ('Training', 'Both')
    """)
    
    # 3. Simulate Batches (Group by Level)
    # This logic groups students by their Target Level (Next Level for graduates, Current Level for new)
    
    plan = {} # Key: Level, Value: {count, students: []}
    
    # Process Graduates (Move to Next Level logic needed, simplified here)
    for g in graduates:
        next_lvl = get_next_level(g['CompletedLevel']) # Helper function needed
        if next_lvl not in plan: plan[next_lvl] = {'count': 0, 'students': []}
        plan[next_lvl]['students'].append({'name': g['FullName'], 'type': 'Carry-over'})
        plan[next_lvl]['count'] += 1
        
    # Process New
    for n in new_candidates:
        lvl = n['TargetLevel']
        if not lvl: continue
        if lvl not in plan: plan[lvl] = {'count': 0, 'students': []}
        plan[lvl]['students'].append({'name': n['FullName'], 'type': 'New'})
        plan[lvl]['count'] += 1
        
    return render_template('training/hiring_plan.html', plan=plan)

def get_next_level(current_level):
    levels = ['A1.1', 'A1.2', 'A2.1', 'A2.2', 'B1', 'B1+', 'B2']
    try:
        idx = levels.index(current_level)
        return levels[idx + 1] if idx + 1 < len(levels) else 'Graduate'
    except:
        return current_level # Fallback
@app.route('/training/create_offer', methods=['POST'])
@login_required
@role_required(['Trainer', 'Manager', 'Sales'])
def create_training_offer():
    f = request.form
    cand_id = f['candidate_id']
    
    # 1. Create Offer
    query_db("""
        INSERT INTO TrainingOffers (CandidateID, TrainingLevel, DeliveryMode, ClassTiming, TrainingFee, Status)
        VALUES (?, ?, ?, ?, ?, 'Pending')
    """, (cand_id, f['level'], f['mode'], f['timing'], f['fee']))
    
    flash('Training Offer Created', 'success')
    return redirect(request.referrer)

@app.route('/training/accept_offer', methods=['POST'])
@login_required
def accept_training_offer():
    offer_id = request.form['offer_id']
    action = request.form['action'] # Accept / Decline
    
    if action == 'Accept':
        query_db("UPDATE TrainingOffers SET Status='Accepted' WHERE OfferID=?", (offer_id,))
        # Trigger Payment Request here (or manual step)
        flash('Offer Accepted. Please proceed to payment.', 'success')
    else:
        query_db("UPDATE TrainingOffers SET Status='Declined' WHERE OfferID=?", (offer_id,))
        flash('Offer Declined', 'warning')
        
    return redirect(request.referrer)

@app.route('/training/enroll_from_offer', methods=['POST'])
@login_required
def enroll_from_offer():
    offer_id = request.form['offer_id']
    batch_id = request.form['batch_id']
    
    # Verify Payment first (Business Rule)
    # For now, we assume payment is checked manually or via another tool
    
    offer = query_db("SELECT * FROM TrainingOffers WHERE OfferID=?", (offer_id,), one=True)
    if not offer: return "Offer not found", 404
    
    query_db("""
        INSERT INTO Enrollments (BatchID, CandidateID, OfferID, AgreedPrice, Status)
        VALUES (?, ?, ?, ?, 'Active')
    """, (batch_id, offer['CandidateID'], offer_id, offer['TrainingFee']))
    
    flash('Student Enrolled Successfully from Offer', 'success')
    return redirect(url_for('training_index'))

@app.route('/training/add_student_direct', methods=('POST',))
@login_required
def add_student_direct():
    full_name = request.form['full_name']
    phone = request.form['phone']
    batch_id = request.form['batch_id']
    cursor = get_db().cursor()
    cursor.execute("INSERT INTO Candidates (FullName, Phone, Status, InterestLevel) OUTPUT INSERTED.CandidateID VALUES (?, ?, 'TrainingOnly', 'High')", (full_name, phone))
    cand_id = cursor.fetchone()[0]
    get_db().commit()
    c = query_db('SELECT C.DefaultPrice FROM Courses C JOIN CourseBatches B ON C.CourseID = B.CourseID WHERE B.BatchID = ?', (batch_id,), one=True)
    price = c['DefaultPrice'] if c else 0
    query_db('INSERT INTO Enrollments (BatchID, CandidateID, AgreedPrice, Status) VALUES (?,?,?,?)', (batch_id, cand_id, price, 'Active'))
    flash('تم تسجيل الطالب الجديد مباشرة في الدورة', 'success')
    return redirect(url_for('training_index'))

def _ensure_attendance_columns():
    """إضافة أعمدة الحضور التفصيلي إن لم تكن موجودة (توافق مع قواعد قديمة)."""
    for stmt in [
        "ALTER TABLE Attendance ADD CheckInTime TIME",
        "ALTER TABLE Attendance ADD CheckOutTime TIME",
        "ALTER TABLE Attendance ADD TotalHours DECIMAL(5,2)",
        "ALTER TABLE Attendance ADD AssignmentDone BIT DEFAULT 0",
        "ALTER TABLE Attendance ADD LateMinutes INT NULL",
        "ALTER TABLE Attendance ADD AssignmentStatus NVARCHAR(50) NULL",
    ]:
        try:
            query_db(stmt)
        except Exception:
            pass  # العمود موجود أو خطأ صلاحيات — نتجاهل
    try:
        query_db(
            """
            UPDATE Attendance SET AssignmentStatus = CASE WHEN AssignmentDone = 1 THEN N'Done' ELSE N'not submitted' END
            WHERE AssignmentStatus IS NULL
            """
        )
    except Exception:
        pass

@app.route('/training/attendance', methods=['GET'])
@login_required
@role_required(['Trainer', 'Manager', 'TrainingCoordinator', 'TrainingSalesCoordinator', 'TrainingLead'])
def training_attendance():
    _ensure_attendance_columns()
    batches = query_db("SELECT * FROM CourseBatches WHERE Status='Active'")
    selected_batch_id = request.args.get('batch_id')
    selected_date = request.args.get('date') or datetime.today().strftime('%Y-%m-%d')
    
    selected_batch = None
    students = []
    
    if selected_batch_id:
        selected_batch = query_db("SELECT * FROM CourseBatches WHERE BatchID=?", (selected_batch_id,), one=True)
        if selected_batch:
            selected_batch['StartTimeStr'] = _safe_time_str(selected_batch.get('StartTime'))
            selected_batch['EndTimeStr'] = _safe_time_str(selected_batch.get('EndTime'))
            try:
                raw = query_db('''
                    SELECT E.EnrollmentID, E.CandidateID, C.FullName,
                            A.Status, A.CheckInTime, A.CheckOutTime, A.TotalHours, A.AssignmentDone, A.AssignmentStatus, A.AttendanceID, A.LateMinutes,
                            (SELECT ISNULL(SUM(LateMinutes), 0) FROM Attendance A2 WHERE A2.EnrollmentID = E.EnrollmentID) AS TotalDelayMinutes,
                            (SELECT COUNT(*) FROM Attendance A2 WHERE A2.EnrollmentID = E.EnrollmentID AND A2.Status = 'Absent') AS AbsenceCount
                    FROM Enrollments E
                    JOIN Candidates C ON E.CandidateID = C.CandidateID
                    LEFT JOIN Attendance A ON E.EnrollmentID = A.EnrollmentID AND A.Date = ?
                    WHERE E.BatchID = ? AND E.Status = 'Active'
                ''', (selected_date, selected_batch_id))
            except Exception:
                raw = query_db('''
                    SELECT E.EnrollmentID, E.CandidateID, C.FullName,
                            A.Status, NULL AS CheckInTime, NULL AS CheckOutTime, NULL AS TotalHours, 0 AS AssignmentDone,
                            NULL AS AssignmentStatus,
                            A.AttendanceID, NULL AS LateMinutes, 0 AS TotalDelayMinutes,
                            (SELECT COUNT(*) FROM Attendance A2 WHERE A2.EnrollmentID = E.EnrollmentID AND A2.Status = 'Absent') AS AbsenceCount
                    FROM Enrollments E
                    JOIN Candidates C ON E.CandidateID = C.CandidateID
                    LEFT JOIN Attendance A ON E.EnrollmentID = A.EnrollmentID AND A.Date = ?
                    WHERE E.BatchID = ? AND E.Status = 'Active'
                ''', (selected_date, selected_batch_id))
            students = []
            cols = ['EnrollmentID', 'CandidateID', 'FullName', 'Status', 'CheckInTime', 'CheckOutTime', 'TotalHours', 'AssignmentDone', 'AssignmentStatus', 'AttendanceID', 'LateMinutes', 'TotalDelayMinutes', 'AbsenceCount']
            for row in (raw or []):
                r = {k: row.get(k) for k in cols}
                r['CheckInTimeStr'] = _safe_time_str(r.get('CheckInTime'))
                r['CheckOutTimeStr'] = _safe_time_str(r.get('CheckOutTime'))
                r['AssignmentStatus'] = _coerce_assignment_status_row(r)
                students.append(r)
            
    session_guests = []
    if selected_batch_id and selected_batch:
        try:
            session_guests = query_db(
                """
                SELECT GuestID, FullName, Phone, Email, SessionDate
                FROM ClassSessionGuests
                WHERE BatchID = ? AND SessionDate = CAST(? AS DATE)
                ORDER BY GuestID
                """,
                (int(selected_batch_id), selected_date),
            ) or []
        except Exception:
            session_guests = []

    return render_template(
        'training/attendance_grid.html',
        batches=batches or [],
        selected_batch=selected_batch,
        students=students or [],
        selected_date=selected_date,
        session_guests=session_guests or [],
    )


@app.route('/training/save_attendance_grid', methods=['POST'])
@login_required
@role_required(['Trainer', 'Manager', 'TrainingCoordinator', 'TrainingSalesCoordinator', 'TrainingLead'])
def save_attendance_grid():
    _ensure_attendance_columns()
    batch_id = request.form['batch_id']
    date = request.form['date']
    # وقت البداية: من النموذج أولاً (نفس القيمة المعروضة) أو من القاعدة
    batch_start_str = (request.form.get('batch_start_time') or '').strip()
    if not batch_start_str:
        batch = query_db("SELECT StartTime FROM CourseBatches WHERE BatchID=?", (batch_id,), one=True)
        if batch and batch.get('StartTime'):
            t = batch['StartTime']
            if hasattr(t, 'strftime'):
                batch_start_str = t.strftime('%H:%M')
            else:
                batch_start_str = str(t)[:5] if t else ''
    expected_start_str = batch_start_str[:5] if batch_start_str and ':' in batch_start_str[:5] else None

    for key in request.form:
        if key.startswith('status_'):
            enrollment_id = key.split('_')[1]
            status = request.form.get(f'status_{enrollment_id}')
            check_in = request.form.get(f'in_{enrollment_id}') or None
            check_out = request.form.get(f'out_{enrollment_id}') or None
            assignment_status = _normalize_assignment_status(request.form.get(f'assign_status_{enrollment_id}'))
            assignment_done_bit = _assignment_done_bit_from_status(assignment_status)

            total_hours = 0
            late_minutes = None
            if check_in and check_out and status not in ('Absent', 'Excused'):
                try:
                    fmt = '%H:%M'
                    t1 = datetime.strptime(check_in[:5], fmt)
                    t2 = datetime.strptime(check_out[:5], fmt)
                    delta = t2 - t1
                    total_hours = round(delta.total_seconds() / 3600, 2)
                    if total_hours < 0:
                        total_hours = 0
                except Exception:
                    pass
            # حساب التأخير (دقائق): عند وجود وقت دخول ووقت بداية الدفعة
            if check_in and expected_start_str and status not in ('Absent', 'Excused'):
                try:
                    fmt = '%H:%M'
                    t_exp = datetime.strptime(expected_start_str, fmt)
                    check_in_trim = (check_in or '')[:5]
                    if not check_in_trim or ':' not in check_in_trim:
                        late_minutes = None
                    else:
                        t_act = datetime.strptime(check_in_trim, fmt)
                        if t_act > t_exp:
                            late_minutes = int((t_act - t_exp).total_seconds() / 60)
                        else:
                            late_minutes = 0
                except Exception:
                    late_minutes = None
            elif status == 'Absent':
                late_minutes = None

            existing = query_db('SELECT AttendanceID FROM Attendance WHERE EnrollmentID=? AND Date=?', (enrollment_id, date), one=True)
            if existing:
                query_db('''
                    UPDATE Attendance 
                    SET Status=?, CheckInTime=?, CheckOutTime=?, TotalHours=?, AssignmentDone=?, AssignmentStatus=?, LateMinutes=?
                    WHERE AttendanceID=?
                ''', (status, check_in, check_out, total_hours, assignment_done_bit, assignment_status, late_minutes, existing['AttendanceID']))
            else:
                query_db('''
                    INSERT INTO Attendance (EnrollmentID, Date, Status, CheckInTime, CheckOutTime, TotalHours, AssignmentDone, AssignmentStatus, LateMinutes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (enrollment_id, date, status, check_in, check_out, total_hours, assignment_done_bit, assignment_status, late_minutes))

    try:
        db = get_db()
        if db:
            db.commit()
    except Exception:
        pass
    flash('تم حفظ الحضور التفصيلي بنجاح', 'success')
    return redirect(url_for('training_attendance', batch_id=batch_id, date=date))


@app.route('/training/attendance/add_guest', methods=['POST'])
@login_required
@role_required(['Trainer', 'Manager', 'TrainingCoordinator', 'TrainingSalesCoordinator', 'TrainingLead'])
def training_attendance_add_guest():
    batch_id = request.form.get('batch_id')
    date_s = request.form.get('date')
    name = (request.form.get('guest_name') or '').strip()
    phone = (request.form.get('guest_phone') or '').strip() or None
    email = (request.form.get('guest_email') or '').strip() or None
    if not batch_id or not date_s or not name:
        flash('الدفعة والتاريخ واسم الضيف مطلوبان.', 'warning')
        return redirect(url_for('training_attendance', batch_id=batch_id, date=date_s))
    try:
        query_db(
            """
            INSERT INTO ClassSessionGuests (BatchID, SessionDate, FullName, Phone, Email, RecordedBy)
            VALUES (?, CAST(? AS DATE), ?, ?, ?, ?)
            """,
            (int(batch_id), date_s, name, phone, email, session.get('user_id')),
        )
        flash('تمت إضافة الضيف (Guest).', 'success')
    except Exception as e:
        flash('خطأ: ' + str(e)[:80], 'danger')
    return redirect(url_for('training_attendance', batch_id=batch_id, date=date_s))


@app.route('/training/attendance/delete_guest/<int:guest_id>', methods=['POST'])
@login_required
@role_required(['Trainer', 'Manager', 'TrainingCoordinator', 'TrainingSalesCoordinator', 'TrainingLead'])
def training_attendance_delete_guest(guest_id):
    row = query_db("SELECT BatchID, SessionDate FROM ClassSessionGuests WHERE GuestID=?", (guest_id,), one=True)
    try:
        query_db("DELETE FROM ClassSessionGuests WHERE GuestID=?", (guest_id,))
        flash('تم حذف الضيف.', 'info')
    except Exception as e:
        flash('خطأ: ' + str(e)[:80], 'danger')
    if row:
        d = row['SessionDate']
        ds = d.strftime('%Y-%m-%d') if d and hasattr(d, 'strftime') else str(d)[:10]
        return redirect(url_for('training_attendance', batch_id=row['BatchID'], date=ds))
    return redirect(url_for('training_attendance'))


@app.route('/training/student_finance/<int:enrollment_id>')
@login_required
@role_required(['Finance', 'Manager', 'TrainingCoordinator', 'TrainingManager'])
def student_finance(enrollment_id):
    enrollment = query_db("SELECT E.*, C.FullName, B.BatchName, Co.CourseName FROM Enrollments E JOIN Candidates C ON E.CandidateID = C.CandidateID JOIN CourseBatches B ON E.BatchID = B.BatchID JOIN Courses Co ON B.CourseID = Co.CourseID WHERE E.EnrollmentID = ?", (enrollment_id,), one=True)
    if not enrollment: return redirect(url_for('training_index'))
    payments = query_db('SELECT * FROM StudentPayments WHERE EnrollmentID = ? ORDER BY PaymentDate DESC', (enrollment_id,))
    return render_template('training/student_finance.html', enrollment=enrollment, payments=payments or [], total_paid=sum(p['Amount'] for p in payments) if payments else 0)

@app.route('/training/add_payment', methods=('POST',))
@login_required
@role_required(['Finance', 'Manager', 'TrainingCoordinator', 'TrainingManager'])
def add_payment():
    query_db('INSERT INTO StudentPayments (EnrollmentID, Amount, Notes, ReceivedBy) VALUES (?,?,?,?)', (request.form['enrollment_id'], request.form['amount'], request.form['notes'], session.get('user_id')))
    return redirect(url_for('student_finance', enrollment_id=request.form['enrollment_id']))

@app.route('/training/print_invoice/<int:enrollment_id>')
@login_required
@role_required(['Finance', 'Manager', 'TrainingCoordinator', 'TrainingManager'])
def print_invoice(enrollment_id):
    enrollment = query_db("SELECT E.*, C.FullName, C.Phone, B.BatchName, Co.CourseName FROM Enrollments E JOIN Candidates C ON E.CandidateID = C.CandidateID JOIN CourseBatches B ON E.BatchID = B.BatchID JOIN Courses Co ON B.CourseID = Co.CourseID WHERE E.EnrollmentID = ?", (enrollment_id,), one=True)
    payments = query_db('SELECT * FROM StudentPayments WHERE EnrollmentID = ? ORDER BY PaymentDate DESC', (enrollment_id,))
    return render_template('training/invoice.html', enrollment=enrollment, payments=payments or [], total_paid=sum(p['Amount'] for p in payments) if payments else 0, today_date=datetime.now().strftime('%Y-%m-%d'))

@app.route('/training/exams', methods=['GET'])
@login_required
def training_exams():
    batches = query_db("SELECT * FROM CourseBatches WHERE Status='Active'")
    selected_batch_id = request.args.get('batch_id')
    exam_type = request.args.get('exam_type', '1') # 1,2,3,4,99
    selected_batch = None
    students = []
    
    # Validation Block Warning
    block_warning = None

    if selected_batch_id:
        selected_batch = query_db("SELECT * FROM CourseBatches WHERE BatchID=?", (selected_batch_id,), one=True)
        if selected_batch:
            # Fetch students with score AND BALANCE
            # We join Enrollments -> Candidates -> StudentPayments
            # Since Payment is 1-to-many, we need a subquery or careful logic
            # Simpler: Get Students first, then calc balance in Python for display
            
            raw_students = query_db('''
                SELECT E.EnrollmentID, C.FullName, C.CandidateID,
                       (SELECT TOP 1 Score FROM WeeklyExams W WHERE W.EnrollmentID = E.EnrollmentID AND W.WeekNumber = ?) as Score
                FROM Enrollments E
                JOIN Candidates C ON E.CandidateID = C.CandidateID
                WHERE E.BatchID = ? AND E.Status = 'Active'
            ''', (exam_type, selected_batch_id))
            
            if raw_students:
                for s in raw_students:
                    # Calculate Balance
                    balance = get_student_balance(s['CandidateID'], selected_batch_id)
                    s['Balance'] = balance
                    s['IsBlocked'] = (balance > 0) and (exam_type == '99') # Block only Final Exam if debt exists
            
            students = raw_students

    return render_template('training/exams.html', batches=batches or [], selected_batch=selected_batch, students=students or [], exam_type=exam_type)

@app.route('/training/save_exams', methods=['POST'])
@login_required
def save_exams():
    batch_id = request.form['batch_id']
    exam_type = request.form['exam_type']
    
    for key in request.form:
        if key.startswith('score_'):
            enrollment_id = key.split('_')[1]
            score_val = request.form[key]
            
            if score_val:
                # Security Check: Block Saving if Final Exam & Debt exists
                if exam_type == '99':
                    # We need CandidateID to check balance. 
                    # This is inefficient in loop but safe.
                    enr = query_db('SELECT CandidateID FROM Enrollments WHERE EnrollmentID=?', (enrollment_id,), one=True)
                    if enr:
                        if is_exam_blocked(enr['CandidateID'], batch_id):
                            continue # Skip saving this student

                existing = query_db('SELECT ExamResultID FROM WeeklyExams WHERE EnrollmentID=? AND WeekNumber=?', (enrollment_id, exam_type), one=True)
                if existing:
                    query_db('UPDATE WeeklyExams SET Score=? WHERE ExamResultID=?', (score_val, existing['ExamResultID']))
                else:
                    query_db('INSERT INTO WeeklyExams (EnrollmentID, WeekNumber, Score, ExamDate) VALUES (?,?,?,GETDATE())',
                             (enrollment_id, exam_type, score_val))
                
                # Update Final Grade
                if exam_type == '99':
                    status = 'Passed' if float(score_val) >= 60 else 'Failed'
                    query_db('UPDATE Enrollments SET Status=?, FinalGrade=? WHERE EnrollmentID=?', (status, score_val, enrollment_id))
    
    flash('تم حفظ الدرجات بنجاح (تم استثناء الطلاب المتعثرين مالياً في النهائي)', 'success')
    return redirect(url_for('training_exams', batch_id=batch_id, exam_type=exam_type))

@app.route('/training/graduate_review')
@login_required
def graduate_review():
    graduates = query_db('''
        SELECT C.*, E.FinalGrade, Co.CourseName, E.EnrollmentID
        FROM Candidates C
        JOIN Enrollments E ON C.CandidateID = E.CandidateID
        JOIN CourseBatches B ON E.BatchID = B.BatchID
        JOIN Courses Co ON B.CourseID = Co.CourseID
        WHERE E.Status = 'Passed' AND (C.IsReadyForMatching = 0 OR C.IsReadyForMatching IS NULL)
    ''')
    return render_template('training/graduate_review.html', graduates=graduates or [])

@app.route('/training/approve_graduate', methods=['POST'])
@login_required
def approve_graduate():
    cand_id = request.form['candidate_id']
    soft = request.form.get('soft_skills')
    eng = request.form.get('english_level')
    is_ready = 1 if request.form.get('is_ready') else 0
    query_db('UPDATE Candidates SET SoftSkills=?, EnglishLevel=?, IsReadyForMatching=? WHERE CandidateID=?',
             (soft, eng, is_ready, cand_id))
    flash('تم تحديث ملف الخريج واعتماده', 'success')
    return redirect(url_for('graduate_review'))

@app.route('/training/student_decision')
@login_required
def student_decision():
    students = query_db('''
        SELECT E.*, C.FullName, C.Phone, C.CandidateID, B.CourseID, Co.CourseName
        FROM Enrollments E
        JOIN Candidates C ON E.CandidateID = C.CandidateID
        JOIN CourseBatches B ON E.BatchID = B.BatchID
        JOIN Courses Co ON B.CourseID = Co.CourseID
        WHERE E.Status IN ('Passed', 'Failed')
        ORDER BY E.EnrollmentDate DESC
    ''')
    all_batches = query_db("SELECT B.*, C.CourseName FROM CourseBatches B JOIN Courses C ON B.CourseID=C.CourseID WHERE B.Status='Active'")
    return render_template('training/student_decision.html', students=students or [], all_batches=all_batches or [], next_batches=all_batches or [])

@app.route('/training/process_decision', methods=['POST'])
@login_required
def process_student_decision():
    # ... logic ...
    return redirect(url_for('student_decision'))

# --- RECRUITMENT ROUTES (MISSING IN YOUR REQUEST BUT ESSENTIAL FOR WORKFLOW) ---
@app.route('/recruitment')
@login_required
@role_required(['Admin', 'Recruiter', 'RecruitmentManager', 'Training Manager'])
def recruitment_index():
    # If Recruiter, show Dashboard or Import?
    # Let's redirect to Distribute for now as a landing or Readiness
    return redirect(url_for('recruiter_dashboard'))

@app.route('/recruitment/readiness')
@login_required
def recruitment_readiness():
    # Get candidates marked as "Ready" but not yet placed
    candidates = query_db('''
        SELECT C.*, E.FinalGrade, Co.CourseName 
        FROM Candidates C
        JOIN Enrollments E ON C.CandidateID = E.CandidateID
        JOIN CourseBatches B ON E.BatchID = B.BatchID
        JOIN Courses Co ON B.CourseID = Co.CourseID
        WHERE C.IsReadyForMatching = 1
        AND NOT EXISTS (SELECT 1 FROM Matches M WHERE M.CandidateID = C.CandidateID AND M.Status = 'Placed')
    ''')
    return render_template('recruitment/readiness.html', candidates=candidates or [])

@app.route('/recruitment/match', methods=['POST'])
@login_required
def recruitment_match():
    cand_id = request.form['candidate_id']
    req_id = request.form['request_id']
    query_db("INSERT INTO Matches (CandidateID, RequestID, Status, MatchDate) VALUES (?, ?, 'Proposed', GETDATE())",
             (cand_id, req_id))
    flash('تم ترشيح الطالب للوظيفة بنجاح', 'success')
    return redirect(url_for('recruitment_readiness'))

@app.route('/reports/export/<type>')
@login_required
def export_report(type):
    import csv
    import io
    from flask import Response

    output = io.StringIO()
    writer = csv.writer(output)

    if type == 'sales':
        data = query_db("SELECT * FROM GeneralSales")
        writer.writerow(['SaleID', 'Service', 'Amount', 'Date', 'Client', 'Method'])
        for row in data:
            writer.writerow([row['SaleID'], row['ServiceName'], row['Amount'], row['SaleDate'], row['ClientName'], row['PaymentMethod']])
            
    elif type == 'attendance':
        data = query_db("SELECT A.*, C.FullName FROM Attendance A JOIN Enrollments E ON A.EnrollmentID=E.EnrollmentID JOIN Candidates C ON E.CandidateID=C.CandidateID")
        writer.writerow(['Date', 'Student', 'Status'])
        for row in data:
            writer.writerow([row['AttendanceDate'], row['FullName'], row['Status']])
            
    elif type == 'invoices':
        data = query_db("SELECT H.*, C.FullName FROM InvoiceHeaders H LEFT JOIN Candidates C ON H.CandidateID=C.CandidateID")
        writer.writerow(['InvoiceID', 'Date', 'Customer', 'Total', 'Status'])
        for row in data:
            writer.writerow([row['InvoiceID'], row['InvoiceDate'], row['FullName'], row['TotalAmount'], row['Status']])

    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment;filename=report_{type}.csv"})

@app.route('/whatsapp/send/<phone>')
@login_required
def send_whatsapp(phone):
    # Basic redirect to WhatsApp Web
    # Clean phone number (remove spaces, ensure country code if needed)
    clean_phone = phone.replace(' ', '').replace('-', '')
    if not clean_phone.startswith('2'): clean_phone = '2' + clean_phone # Egypt default
    
    msg = "مرحباً، نتواصل معك من Place 2026 بخصوص..."
    return redirect(f"https://web.whatsapp.com/send?phone={clean_phone}&text={msg}")

# --- Main ---
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Update Email
        if email:
            query_db("UPDATE Users_1 SET Email=? WHERE UserID=?", (email, session['user_id']))
            
        # Update Password (if provided)
        if password:
            query_db("UPDATE Users_1 SET Password=? WHERE UserID=?", (password, session['user_id']))
            
        flash('Profile Updated Successfully', 'success')
        return redirect(url_for('profile'))
        
    user = query_db("SELECT * FROM Users_1 WHERE UserID=?", (session['user_id'],), one=True)
    return render_template('profile.html', user=user)

if __name__ == '__main__':
    with app.app_context():
        init_system()

    # فتح المتصفح تلقائياً بعد ثانية ونصف من بدء السيرفر
    def _open_browser():
        import time
        time.sleep(1.5)
        try:
            import webbrowser
            webbrowser.open('http://127.0.0.1:5000')
        except Exception:
            pass

    import threading
    threading.Thread(target=_open_browser, daemon=True).start()

    app.run(debug=True, port=5000)
