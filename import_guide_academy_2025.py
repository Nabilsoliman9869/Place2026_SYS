# -*- coding: utf-8 -*-
"""
استيراد من ملف Guide Academy Placements 2025.xlsx
- دمج البيانات حسب رقم الهاتف (Pri #) وتجنّب التكرار
- عينة: طباعة ملف متدرب واحد للتأكد قبل الاستيراد الكامل
شغّل: python import_guide_academy_2025.py
      python import_guide_academy_2025.py --sample   لعرض عينة لمتدرب واحد فقط (بدون استيراد)
"""
import os
import sys
import json
import re
from datetime import datetime

try:
    import openpyxl
except ImportError:
    print("ثبّت openpyxl: pip install openpyxl")
    sys.exit(1)
try:
    import pyodbc
except ImportError:
    pyodbc = None

# مسار الملف
BASE = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE, "Guide Academy Placements 2025.xlsx")


def safe_str(val, max_len=500):
    if val is None:
        return None
    s = str(val).strip()
    if not s or s.lower() in ("none", "nan", "#n/a"):
        return None
    return s[:max_len] if len(s) > max_len else s


def safe_phone(val):
    if val is None:
        return None
    s = str(val).strip().replace(" ", "").replace("-", "")
    if re.match(r"^\d+$", s) and len(s) >= 8:
        return s
    return None


def row_to_dict(header, row):
    d = {}
    for i, h in enumerate(header):
        if h and i < len(row):
            key = str(h).strip()
            if key and key != "@dropdown":
                d[key] = row[i]
    return d


def load_sheet(wb, sheet_name, key_col="Pri #", name_col=None):
    """يرجع قائمة سجلات مع الهيدر، والمفتاح للربط: Pri # أو Phone No."""
    if sheet_name not in wb.sheetnames:
        return [], []
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return [], []
    header = [x for x in rows[0] if x is not None]
    # تحديد عمود المفتاح
    key_name = key_col
    if key_col == "Pri #" and "Pri #" not in header and "Phone No." in header:
        key_name = "Phone No."
    data = []
    for r in rows[1:]:
        if not r or (len(r) <= 1 and r[0] is None):
            continue
        d = row_to_dict(rows[0], r)
        if not d:
            continue
        key = safe_phone(d.get(key_name)) or safe_phone(d.get("Phone No.")) or safe_phone(d.get("Sec #"))
        if not key:
            name = safe_str(d.get("Candidate Name") or d.get("Candidate's Name"))
            if name:
                data.append((None, d))
            continue
        data.append((key, d))
    return header, data


def build_trainee_index(wb):
    """
    يبني فهرس: رقم_الهاتف -> { 'name', 'phone', 'email', 'booking': [], 'ga_interviews': [], 'exit_makeup': [], 'foundation': [], 'train_to_hire': [] }
    """
    index = {}
    sheets_config = [
        ("Booking Placements Sheet", "Phone No.", "Candidate's Name"),
        ("GA Interviews", "Pri #", "Candidate Name"),
        ("Exit Make-Up", "Pri #", "Candidate Name"),
        ("Foundation(certain program)", "Pri #", "Candidate Name"),
        ("train to hire (certain program)", "Pri #", "Candidate Name"),
    ]
    for sheet_name, key_col, name_col in sheets_config:
        header, data = load_sheet(wb, sheet_name, key_col, name_col)
        short = sheet_name.replace(" ", "_")[:20]
        for key, d in data:
            name = safe_str(d.get("Candidate Name") or d.get("Candidate's Name"), 100)
            phone = key or safe_phone(d.get("Pri #") or d.get("Phone No."))
            email = safe_str(d.get("Email"), 100)
            if not key and (name or phone):
                key = phone or ("name:" + (name or "")[:30])
            if not key:
                continue
            if key not in index:
                # لا نخزن كبريد قيماً لا تحتوي @ (مثل "Redo" في ورقة Exit)
                email_ok = email and "@" in str(email)
                index[key] = {
                    "name": name,
                    "phone": phone,
                    "email": email if email_ok else None,
                    "booking": [],
                    "ga_interviews": [],
                    "exit_makeup": [],
                    "foundation": [],
                    "train_to_hire": [],
                }
            else:
                # دمج: نفضّل الاسم/البريد من GA أو Booking (Exit أحياناً يحوي "Redo" في عمود Email)
                if name and not index[key]["name"]:
                    index[key]["name"] = name
                if email and "@" in str(email) and not index[key]["email"]:
                    index[key]["email"] = email
                elif email and "@" in str(email):
                    index[key]["email"] = index[key]["email"] or email
            if "Booking" in sheet_name:
                index[key]["booking"].append(d)
            elif "GA Interviews" in sheet_name:
                index[key]["ga_interviews"].append(d)
            elif "Exit" in sheet_name:
                index[key]["exit_makeup"].append(d)
            elif "Foundation" in sheet_name:
                index[key]["foundation"].append(d)
            elif "train to hire" in sheet_name:
                index[key]["train_to_hire"].append(d)
    return index


def print_sample_trainee(index, phone_or_name=None):
    """طباعة ملف متدرب واحد (عينة). إذا لم يُحدد phone_or_name نأخذ أول مفتاح له بيانات في أكثر من ورقة."""
    if not index:
        print("لا توجد بيانات في الفهرس.")
        return
    if phone_or_name:
        key = None
        for k, v in index.items():
            if v["phone"] == phone_or_name or (v["name"] and phone_or_name.lower() in (v["name"] or "").lower()):
                key = k
                break
        if not key:
            key = str(phone_or_name)
            if key not in index:
                print("لم يُعثر على متدرب بهذا الرقم أو الاسم. أمثلة مفاتيح:", list(index.keys())[:5])
                return
    else:
        # أول شخص له ظهور في Exit أو GA + Exit
        for k, v in index.items():
            if v["exit_makeup"] or (v["ga_interviews"] and v["exit_makeup"]):
                key = k
                break
        else:
            key = list(index.keys())[0]
    v = index[key]
    print("=" * 60)
    print("ملف متدرب (عينة) — من Guide Academy Placements 2025.xlsx")
    print("=" * 60)
    print("الاسم:", v["name"] or "-")
    print("الهاتف:", v["phone"] or "-")
    email = v["email"]
    if not email or "@" not in str(email):
        email = "-"
    print("البريد:", email)
    print()
    if v["booking"]:
        print("--- حجوزات (Booking) ---")
        for i, r in enumerate(v["booking"][:3], 1):
            print(f"  {i}. تاريخ:", r.get("Date"), "| مجدول ل:", r.get("Booked for"), "| مصدر:", r.get("Source"), "| سبب:", r.get("Placement reason"))
        if len(v["booking"]) > 3:
            print("  ... و", len(v["booking"]) - 3, "سجلات أخرى")
        print()
    if v["ga_interviews"]:
        print("--- مقابلات GA (تقييم أولي) ---")
        for i, r in enumerate(v["ga_interviews"][:3], 1):
            print(f"  {i}. تاريخ:", r.get("Date"), "| CEFR:", r.get("CEFR"), "| مرشّح:", r.get("Recruiter"), "| مصدر:", r.get("Source"))
            if r.get("Language comments"):
                print("     ملاحظات:", (str(r["Language comments"])[:150] + "…") if len(str(r.get("Language comments") or "")) > 150 else r.get("Language comments"))
        if len(v["ga_interviews"]) > 3:
            print("  ... و", len(v["ga_interviews"]) - 3, "سجلات أخرى")
        print()
    if v["exit_makeup"]:
        print("--- خروج / Make-Up (دفعة ونتيجة) ---")
        for i, r in enumerate(v["exit_makeup"][:5], 1):
            print(f"  {i}. Wave:", r.get("Wave"), "| CEFR:", r.get("CEFR"), "| الحالة:", r.get("Status"), "| مقابِل:", r.get("Interviewer"))
            if r.get("Recording Link"):
                print("     تسجيل:", r.get("Recording Link")[:60] + "…")
        if len(v["exit_makeup"]) > 5:
            print("  ... و", len(v["exit_makeup"]) - 5, "سجلات أخرى")
        print()
    if v["foundation"]:
        print("--- Foundation ---")
        for i, r in enumerate(v["foundation"][:3], 1):
            print(f"  {i}. تاريخ:", r.get("Date"), "| CEFR:", r.get("CEFR"), "| تسجيل:", (str(r.get("Recording link") or "")[:50] + "…") if r.get("Recording link") else "-")
        print()
    if v["train_to_hire"]:
        print("--- Train to Hire ---")
        for i, r in enumerate(v["train_to_hire"][:3], 1):
            print(f"  {i}. تاريخ:", r.get("Date"), "| CEFR:", r.get("CEFR"), "| مرشّح:", r.get("Recruiter"))
        print()
    print("=" * 60)
    return key


def get_connection():
    config_path = os.path.join(BASE, "db_config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError("لا يوجد db_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    server = config.get("server", ".")
    port = config.get("port", "1433")
    database = config.get("database", "Place2026DB")
    username = config.get("username", "")
    password = config.get("password", "")
    use_trusted = config.get("use_trusted", False)
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};"
        + ("Trusted_Connection=yes;" if use_trusted else f"UID={username};PWD={password};")
    )
    return pyodbc.connect(conn_str, timeout=15)


def run_import_to_db(index):
    """استيراد الفهرس إلى القاعدة: Candidates, CourseBatches, Enrollments, PlacementTests."""
    conn = get_connection()
    conn.autocommit = False
    cursor = conn.cursor()
    try:
        # دورة واحدة
        cursor.execute("SELECT TOP 1 CourseID FROM Courses")
        row = cursor.fetchone()
        if row:
            course_id = row[0]
        else:
            cursor.execute(
                "INSERT INTO Courses (CourseName, LevelOrder, DefaultPrice) VALUES (N'دورة لغة إنجليزية - أكاديمي', 1, 0)"
            )
            cursor.execute("SELECT SCOPE_IDENTITY()")
            course_id = int(cursor.fetchone()[0])
        # جمع كل Waves من exit_makeup
        waves = set()
        for v in index.values():
            for r in v["exit_makeup"]:
                w = safe_str(r.get("Wave"), 100)
                if w:
                    waves.add(w)
        for v in index.values():
            for r in v["foundation"]:
                w = safe_str(r.get("Wave"), 100)
                if w:
                    waves.add(w)
        batch_name_to_id = {}
        cursor.execute("SELECT BatchID, BatchName FROM CourseBatches")
        for r in cursor.fetchall() or []:
            batch_name_to_id[(r[1] or "").strip().lower()] = r[0]
        for w in waves:
            wnorm = w.strip().lower()
            if wnorm in batch_name_to_id:
                continue
            cursor.execute(
                "INSERT INTO CourseBatches (CourseID, BatchName, Status) VALUES (?, ?, 'Active')",
                (course_id, w.strip()),
            )
            cursor.execute("SELECT SCOPE_IDENTITY()")
            bid = int(cursor.fetchone()[0])
            batch_name_to_id[wnorm] = bid
            batch_name_to_id[w.strip()] = bid
        # إنشاء جدول TraineeSheetData إن لم يكن موجوداً
        try:
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TraineeSheetData' AND xtype='U')
                CREATE TABLE TraineeSheetData (
                    Id INT IDENTITY(1,1) PRIMARY KEY,
                    CandidateID INT NOT NULL,
                    SheetName NVARCHAR(100) NOT NULL,
                    JsonData NVARCHAR(MAX) NULL,
                    UpdatedAt DATETIME DEFAULT GETDATE() NULL
                )
            """)
        except Exception:
            pass
        # مرشحون: لا تكرار بالاسم أو البريد — البحث بالهاتف ثم الاسم/البريد
        phone_to_id = {}
        cursor.execute("SELECT CandidateID, Phone, FullName, Email FROM Candidates")
        for r in cursor.fetchall() or []:
            cid, ph, fn, em = r[0], r[1], r[2], r[3]
            if ph:
                pk = str(ph).strip().replace(" ", "")
                phone_to_id[pk] = cid
        inserted_cand = 0
        inserted_pt = 0
        inserted_enr = 0
        for key, v in index.items():
            phone = v.get("phone") or key
            if isinstance(phone, int):
                phone = str(phone)
            phone_key = str(phone).replace(" ", "").strip()
            name = v.get("name") or "—"
            email = v.get("email")
            if not name or name == "—":
                continue
            cand_id = phone_to_id.get(phone_key)
            if not cand_id:
                # منع تكرار الاسم أو البريد: إن وُجد مرشح بنفس الاسم أو البريد نربط به
                try:
                    cursor.execute(
                        "SELECT CandidateID FROM Candidates WHERE LOWER(RTRIM(FullName))=LOWER(RTRIM(?)) OR (Email IS NOT NULL AND LEN(RTRIM(Email))>0 AND LOWER(RTRIM(Email))=LOWER(RTRIM(?)))",
                        (name, email or ""),
                    )
                    row = cursor.fetchone()
                    if row:
                        cand_id = row[0]
                        phone_to_id[phone_key] = cand_id
                    else:
                        cursor.execute(
                            "INSERT INTO Candidates (FullName, Phone, Email, Status, InterestLevel) VALUES (?, ?, ?, 'TrainingOnly', 'High')",
                            (name, phone_key, email),
                        )
                        cursor.execute("SELECT SCOPE_IDENTITY()")
                        cand_id = int(cursor.fetchone()[0])
                        phone_to_id[phone_key] = cand_id
                        inserted_cand += 1
                except Exception as e:
                    print("تخطي مرشح", name, ":", e)
                    continue
            # PlacementTests من GA + Exit + Foundation
            for rec in v.get("ga_interviews", [])[:1]:
                cefr = safe_str(rec.get("CEFR"), 50)
                notes = rec.get("Language comments")
                if notes and len(str(notes)) > 4000:
                    notes = str(notes)[:4000]
                dt = rec.get("Date")
                try:
                    cursor.execute(
                        "INSERT INTO PlacementTests (CandidateID, ResultLevel, Notes, TestStatus) VALUES (?, ?, ?, 'Completed')",
                        (cand_id, cefr, notes),
                    )
                    inserted_pt += 1
                except Exception:
                    pass
            for rec in v.get("exit_makeup", [])[:1]:
                cefr = safe_str(rec.get("CEFR"), 50)
                notes = rec.get("Language comments") or rec.get("Recording Link")
                if notes and len(str(notes)) > 4000:
                    notes = str(notes)[:4000]
                try:
                    cursor.execute(
                        "INSERT INTO PlacementTests (CandidateID, ResultLevel, Notes, TestStatus) VALUES (?, ?, ?, 'Completed')",
                        (cand_id, cefr, notes),
                    )
                    inserted_pt += 1
                except Exception:
                    pass
            # Enrollments من Exit (Wave) — دون تكرار (شخص، دفعة)
            seen_enr = set()
            for rec in v.get("exit_makeup", []):
                w = safe_str(rec.get("Wave"), 100)
                if not w:
                    continue
                bid = batch_name_to_id.get(w.strip().lower()) or batch_name_to_id.get(w.strip())
                if not bid or (cand_id, bid) in seen_enr:
                    continue
                seen_enr.add((cand_id, bid))
                try:
                    cursor.execute(
                        "INSERT INTO Enrollments (BatchID, CandidateID, Status, AgreedPrice) VALUES (?, ?, 'Active', 0)",
                        (bid, cand_id),
                    )
                    inserted_enr += 1
                except Exception:
                    pass
            # حفظ كل حقول الأوراق لهذا المتدرب (TraineeSheetData) — عرضها في ملف المتدرب
            try:
                cursor.execute("DELETE FROM TraineeSheetData WHERE CandidateID=?", (cand_id,))
                def json_serial(obj):
                    if hasattr(obj, "isoformat"):
                        return obj.isoformat()
                    return str(obj)
                sheets_to_save = [
                    ("Booking Placements Sheet", v.get("booking", [])),
                    ("GA Interviews", v.get("ga_interviews", [])),
                    ("Exit Make-Up", v.get("exit_makeup", [])),
                    ("Foundation(certain program)", v.get("foundation", [])),
                    ("train to hire (certain program)", v.get("train_to_hire", [])),
                ]
                for sheet_name, rows in sheets_to_save:
                    if not rows:
                        continue
                    clean = []
                    for r in rows:
                        clean.append({str(k): (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in (r or {}).items() if v is not None and str(v).strip()})
                    if clean:
                        js = json.dumps(clean, ensure_ascii=False, default=str)
                        if len(js) > 200000:
                            js = json.dumps(clean[:5], ensure_ascii=False, default=str) + "\n... (مختصر)"
                        cursor.execute(
                            "INSERT INTO TraineeSheetData (CandidateID, SheetName, JsonData) VALUES (?, ?, ?)",
                            (cand_id, sheet_name[:100], js),
                        )
            except Exception as ex:
                pass
        conn.commit()
        print("استيراد من Guide Academy 2025: مرشحون جديد:", inserted_cand, "| تقييمات:", inserted_pt, "| تسجيلات:", inserted_enr)
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def main():
    if not os.path.exists(EXCEL_PATH):
        print("لا يوجد الملف:", EXCEL_PATH)
        sys.exit(1)
    sample_only = "--sample" in sys.argv or "-s" in sys.argv
    wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True, data_only=True)
    index = build_trainee_index(wb)
    wb.close()
    print("عدد المتدربين (مفتاح فريد):", len(index))
    # تكرار: عدد الأشخاص الذين ظهروا في أكثر من ورقة
    multi = sum(1 for v in index.values() if sum([len(v["booking"]), len(v["ga_interviews"]), len(v["exit_makeup"]), len(v["foundation"]), len(v["train_to_hire"])]) > 1)
    print("عدد من ظهروا في أكثر من مصدر (ورقة):", multi)
    print()
    if sample_only:
        # عينة بمتدرب له بيانات في Exit (مثلاً nourhan)
        print_sample_trainee(index, "1204737457")
        return
    do_import = "--import" in sys.argv or "-i" in sys.argv
    if do_import:
        try:
            import pyodbc
            run_import_to_db(index)
        except Exception as e:
            print("خطأ أثناء الاستيراد:", e)
            sys.exit(1)
    else:
        print("للاستيراد إلى القاعدة: python import_guide_academy_2025.py --import")
        print("العينة فقط: python import_guide_academy_2025.py --sample")


if __name__ == "__main__":
    main()
