# database.py - النسخة المحسنة والمنظمة
import pyodbc
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
import qrcode
import random
import string
from io import BytesIO
import base64

# إعداد نظام التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# إعدادات الاتصال بقاعدة البيانات
CONN_STR = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=.,1477;DATABASE=Place2026;UID=sa;PWD=123"

# ==================== دوال الأساسية للاتصال ====================
def get_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    try:
        conn = pyodbc.connect(CONN_STR)
        conn.autocommit = False
        return conn
    except pyodbc.Error as e:
        logger.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        raise
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {e}")
        raise

def fetch_all(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """تنفيذ استعلام SELECT وإرجاع النتائج كقائمة من القواميس"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        
        # إذا لم يكن الاستعلام من النوع الذي يرجع نتائج
        if not cursor.description:
            conn.commit()
            return []
        
        # استخراج أسماء الأعمدة
        columns = [column[0] for column in cursor.description]
        
        # جلب جميع الصفوف
        rows = cursor.fetchall()
        conn.commit()
        
        # تحويل النتائج إلى قواميس
        return [
            {columns[i]: row[i] for i in range(len(columns))}
            for row in rows
        ]
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"خطأ في استعلام SELECT: {e}\nالاستعلام: {query}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def exec_non_query(query: str, params: Optional[tuple] = None) -> int:
    """تنفيذ استعلام لا يرجع نتائج (INSERT, UPDATE, DELETE)"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        affected_rows = cursor.rowcount
        conn.commit()
        return affected_rows
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"خطأ في استعلام التعديل: {e}\nالاستعلام: {query}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def exec_insert_return_id(query: str, params: tuple) -> int:
    """تنفيذ INSERT وإرجاع الهوية المولدة"""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.commit()
        
        if result and result[0] is not None:
            return int(result[0])
        return 0
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"خطأ في إدراج بيانات: {e}\nالاستعلام: {query}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ==================== دوال المرشحين ====================
def get_all_candidates() -> List[Dict[str, Any]]:
    """جلب جميع المرشحين"""
    query = """
    SELECT CandidateID, FullName, Phone, Email, Age, Gender, NationalID,
           Address, EducationLevel, LanguageLevel, ComputerSkills,
           WorkExperience, ExpectedSalary, RegistrationDate, Status, Notes
    FROM Candidates
    ORDER BY RegistrationDate DESC
    """
    return fetch_all(query)

def get_candidate_by_id(candidate_id: int) -> Optional[Dict[str, Any]]:
    """جلب مرشح بواسطة الهوية"""
    query = """
    SELECT CandidateID, FullName, Phone, Email, Age, Gender, NationalID,
           Address, EducationLevel, LanguageLevel, ComputerSkills,
           WorkExperience, ExpectedSalary, RegistrationDate, Status, Notes
    FROM Candidates
    WHERE CandidateID = ?
    """
    results = fetch_all(query, (candidate_id,))
    return results[0] if results else None

def add_candidate(candidate_data: Dict[str, Any]) -> int:
    """إضافة مرشح جديد"""
    query = """
    INSERT INTO Candidates
    (FullName, Phone, Email, Age, Gender, NationalID, Address,
     EducationLevel, LanguageLevel, ComputerSkills, WorkExperience,
     ExpectedSalary, Status, Notes)
    OUTPUT INSERTED.CandidateID
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        candidate_data.get("FullName", ""),
        candidate_data.get("Phone", ""),
        candidate_data.get("Email", ""),
        candidate_data.get("Age"),
        candidate_data.get("Gender", ""),
        candidate_data.get("NationalID", ""),
        candidate_data.get("Address", ""),
        candidate_data.get("EducationLevel", ""),
        candidate_data.get("LanguageLevel", ""),
        candidate_data.get("ComputerSkills", ""),
        candidate_data.get("WorkExperience", ""),
        candidate_data.get("ExpectedSalary", 0),
        candidate_data.get("Status", "New"),
        candidate_data.get("Notes", ""),
    )
    
    return exec_insert_return_id(query, params)

def update_candidate(candidate_id: int, candidate_data: Dict[str, Any]) -> bool:
    """تحديث بيانات مرشح"""
    query = """
    UPDATE Candidates
    SET FullName = ?, Phone = ?, Email = ?, Age = ?, Gender = ?,
        NationalID = ?, Address = ?, EducationLevel = ?, LanguageLevel = ?,
        ComputerSkills = ?, WorkExperience = ?, ExpectedSalary = ?,
        Status = ?, Notes = ?
    WHERE CandidateID = ?
    """
    
    params = (
        candidate_data.get("FullName", ""),
        candidate_data.get("Phone", ""),
        candidate_data.get("Email", ""),
        candidate_data.get("Age"),
        candidate_data.get("Gender", ""),
        candidate_data.get("NationalID", ""),
        candidate_data.get("Address", ""),
        candidate_data.get("EducationLevel", ""),
        candidate_data.get("LanguageLevel", ""),
        candidate_data.get("ComputerSkills", ""),
        candidate_data.get("WorkExperience", ""),
        candidate_data.get("ExpectedSalary", 0),
        candidate_data.get("Status", ""),
        candidate_data.get("Notes", ""),
        candidate_id,
    )
    
    return exec_non_query(query, params) > 0

def delete_candidate(candidate_id: int) -> bool:
    """حذف مرشح"""
    query = "DELETE FROM Candidates WHERE CandidateID = ?"
    return exec_non_query(query, (candidate_id,)) > 0

# ==================== دوال الإحصائيات ====================
def get_dashboard_stats() -> Dict[str, Any]:
    """جلب إحصائيات لوحة التحكم"""
    stats = {
        "total_candidates": 0,
        "hired_candidates": 0,
        "active_clients": 0,
        "active_trainings": 0,
        "monthly_revenue": 0,
        "exam_success_rate": 0,
    }
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # إجمالي المرشحين
        cursor.execute("SELECT COUNT(*) FROM Candidates")
        stats["total_candidates"] = cursor.fetchone()[0] or 0
        
        # المرشحين المعينين
        cursor.execute("SELECT COUNT(*) FROM Candidates WHERE Status = 'Hired'")
        stats["hired_candidates"] = cursor.fetchone()[0] or 0
        
        # العملاء النشطين
        cursor.execute("SELECT COUNT(*) FROM Clients WHERE Status = 'Active'")
        stats["active_clients"] = cursor.fetchone()[0] or 0
        
        # التدريبات النشطة
        cursor.execute("SELECT COUNT(*) FROM Trainings WHERE Status = 'Ongoing'")
        stats["active_trainings"] = cursor.fetchone()[0] or 0
        
        # الإيرادات الشهرية
        cursor.execute("""
            SELECT ISNULL(SUM(Amount), 0)
            FROM Invoices
            WHERE MONTH(IssueDate) = MONTH(GETDATE())
              AND YEAR(IssueDate) = YEAR(GETDATE())
        """)
        stats["monthly_revenue"] = float(cursor.fetchone()[0] or 0)
        
        # معدل نجاح الامتحانات
        cursor.execute("""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN Result = 'Pass' THEN 1 ELSE 0 END) AS passed
            FROM ExamAppointments
            WHERE Result IS NOT NULL
        """)
        result = cursor.fetchone()
        if result and result[0] and result[0] > 0:
            passed = result[1] or 0
            stats["exam_success_rate"] = round((passed * 100.0) / result[0], 1)
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"خطأ في جلب الإحصائيات: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()
    
    return stats

def get_candidates_by_status() -> List[Dict[str, Any]]:
    """جلب عدد المرشحين حسب الحالة"""
    query = """
    SELECT Status, COUNT(*) AS Count
    FROM Candidates
    GROUP BY Status
    ORDER BY Count DESC
    """
    return fetch_all(query)

def get_monthly_enrollments() -> List[Dict[str, Any]]:
    """جلب التسجيلات الشهرية"""
    query = """
    SELECT 
        FORMAT(EnrollmentDate, 'yyyy-MM') AS Month,
        COUNT(*) AS Enrollments
    FROM Enrollments
    WHERE EnrollmentDate >= DATEADD(MONTH, -6, GETDATE())
    GROUP BY FORMAT(EnrollmentDate, 'yyyy-MM')
    ORDER BY Month
    """
    return fetch_all(query)

# ==================== دوال الامتحانات ====================
def get_all_exams() -> List[Dict[str, Any]]:
    """جلب جميع الامتحانات"""
    query = """
    SELECT ExamID, ExamName, ExamType, TotalScore, PassingScore, Duration, Fee
    FROM Exams
    ORDER BY ExamName
    """
    return fetch_all(query)

def add_exam(exam_data: Dict[str, Any]) -> int:
    """إضافة امتحان جديد"""
    query = """
    INSERT INTO Exams (ExamName, ExamType, TotalScore, PassingScore, Duration, Fee)
    OUTPUT INSERTED.ExamID
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    params = (
        exam_data.get("ExamName", ""),
        exam_data.get("ExamType", ""),
        exam_data.get("TotalScore", 100),
        exam_data.get("PassingScore", 60),
        exam_data.get("Duration", 60),
        exam_data.get("Fee", 0.0),
    )
    
    return exec_insert_return_id(query, params)

def schedule_exam_appointment(appointment_data: Dict[str, Any]) -> int:
    """جدولة موعد امتحان"""
    query = """
    INSERT INTO ExamAppointments 
    (CandidateID, ExamID, AppointmentDate, Status, Result, Score)
    OUTPUT INSERTED.AppointmentID
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    params = (
        appointment_data.get("CandidateID"),
        appointment_data.get("ExamID"),
        appointment_data.get("AppointmentDate"),
        appointment_data.get("Status", "Scheduled"),
        appointment_data.get("Result"),
        appointment_data.get("Score"),
    )
    
    return exec_insert_return_id(query, params)

def get_exam_appointments(candidate_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """جلب مواعيد الامتحانات"""
    if candidate_id:
        query = """
        SELECT ea.*, e.ExamName, c.FullName
        FROM ExamAppointments ea
        JOIN Exams e ON ea.ExamID = e.ExamID
        JOIN Candidates c ON ea.CandidateID = c.CandidateID
        WHERE ea.CandidateID = ?
        ORDER BY ea.AppointmentDate DESC
        """
        return fetch_all(query, (candidate_id,))
    else:
        query = """
        SELECT ea.*, e.ExamName, c.FullName
        FROM ExamAppointments ea
        JOIN Exams e ON ea.ExamID = e.ExamID
        JOIN Candidates c ON ea.CandidateID = c.CandidateID
        ORDER BY ea.AppointmentDate DESC
        """
        return fetch_all(query)

# ==================== دوال التدريبات ====================
def get_all_trainings() -> List[Dict[str, Any]]:
    """جلب جميع التدريبات"""
    query = """
    SELECT TrainingID, TrainingName, Description, Category, DurationHours,
           Fee, MaxCapacity, StartDate, EndDate, Schedule, Location,
           Instructor, Status
    FROM Trainings
    ORDER BY StartDate DESC
    """
    return fetch_all(query)

def get_training_by_id(training_id: int) -> Optional[Dict[str, Any]]:
    """جلب تدريب بواسطة الهوية"""
    query = """
    SELECT TrainingID, TrainingName, Description, Category, DurationHours,
           Fee, MaxCapacity, StartDate, EndDate, Schedule, Location,
           Instructor, Status
    FROM Trainings
    WHERE TrainingID = ?
    """
    results = fetch_all(query, (training_id,))
    return results[0] if results else None

def add_training(training_data: Dict[str, Any]) -> int:
    """إضافة تدريب جديد"""
    query = """
    INSERT INTO Trainings 
    (TrainingName, Description, Category, DurationHours, Fee, MaxCapacity,
     StartDate, EndDate, Schedule, Location, Instructor, Status)
    OUTPUT INSERTED.TrainingID
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        training_data.get("TrainingName", ""),
        training_data.get("Description", ""),
        training_data.get("Category", ""),
        training_data.get("DurationHours", 0),
        training_data.get("Fee", 0.0),
        training_data.get("MaxCapacity", 0),
        training_data.get("StartDate"),
        training_data.get("EndDate"),
        training_data.get("Schedule", ""),
        training_data.get("Location", ""),
        training_data.get("Instructor", ""),
        training_data.get("Status", "Upcoming"),
    )
    
    return exec_insert_return_id(query, params)

def get_enrollments_by_training(training_id: int) -> List[Dict[str, Any]]:
    """جلب المسجلين في تدريب معين"""
    query = """
    SELECT e.EnrollmentID, e.EnrollmentDate, e.Status, e.FinalGrade,
           c.CandidateID, c.FullName, c.Phone, c.Email
    FROM Enrollments e
    JOIN Candidates c ON e.CandidateID = c.CandidateID
    WHERE e.TrainingID = ?
    ORDER BY e.EnrollmentDate
    """
    return fetch_all(query, (training_id,))

def enroll_candidate_in_training(candidate_id: int, training_id: int) -> int:
    """تسجيل مرشح في تدريب"""
    query = """
    INSERT INTO Enrollments (CandidateID, TrainingID, Status)
    OUTPUT INSERTED.EnrollmentID
    VALUES (?, ?, 'Registered')
    """
    
    return exec_insert_return_id(query, (candidate_id, training_id))

# ==================== دوال نظام الحضور ====================
def random_string(length: int = 8) -> str:
    """إنشاء نص عشوائي"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

def generate_qr_code() -> Tuple[str, str]:
    """إنشاء رمز QR"""
    code = f"SESSION_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random_string(6)}"
    
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(f"HR_ATTENDANCE:{code}")
    qr.make(fit=True)
    
    # إنشاء الصورة
    img = qr.make_image(fill_color="#1a237e", back_color="white")
    
    # تحويل إلى base64
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return qr_base64, code

def create_training_session(session_data: Dict[str, Any]) -> Tuple[int, str]:
    """إنشاء جلسة تدريب"""
    qr_base64, qr_code = generate_qr_code()
    expiry_time = datetime.now() + timedelta(hours=24)
    
    query = """
    INSERT INTO TrainingSessions
    (TrainingID, SessionNumber, SessionDate, StartTime, EndTime,
     Topic, Location, QRCode, QRExpiry, Status)
    OUTPUT INSERTED.SessionID
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        session_data.get("TrainingID"),
        session_data.get("SessionNumber", 1),
        session_data.get("SessionDate"),
        session_data.get("StartTime"),
        session_data.get("EndTime"),
        session_data.get("Topic", ""),
        session_data.get("Location", ""),
        qr_code,
        expiry_time,
        session_data.get("Status", "Scheduled"),
    )
    
    session_id = exec_insert_return_id(query, params)
    return session_id, qr_base64

def get_upcoming_sessions() -> List[Dict[str, Any]]:
    """جلب الجلسات القادمة"""
    query = """
    SELECT TOP 5 
        ts.SessionID, ts.SessionDate, ts.StartTime, ts.EndTime,
        ts.Topic, ts.Location, t.TrainingName,
        (SELECT COUNT(*) FROM Attendance a WHERE a.SessionID = ts.SessionID) AS Attendees
    FROM TrainingSessions ts
    JOIN Trainings t ON ts.TrainingID = t.TrainingID
    WHERE ts.SessionDate >= CAST(GETDATE() AS DATE)
      AND ts.Status = 'Scheduled'
    ORDER BY ts.SessionDate, ts.StartTime
    """
    return fetch_all(query)

def record_attendance(session_id: int, candidate_id: int, method: str = "QR") -> bool:
    """تسجيل حضور"""
    query = """
    INSERT INTO Attendance (SessionID, CandidateID, Method)
    VALUES (?, ?, ?)
    """
    
    return exec_non_query(query, (session_id, candidate_id, method)) > 0

# ==================== دوال العملاء ====================
def get_all_clients() -> List[Dict[str, Any]]:
    """جلب جميع العملاء"""
    query = """
    SELECT ClientID, CompanyName, ContactPerson, Phone, Email, Industry,
           RequiredCount, MinAge, MaxAge, RequiredGender, RequiredLevel,
           RequiredSkills, SalaryRange, Status
    FROM Clients
    ORDER BY CompanyName
    """
    return fetch_all(query)

def add_client(client_data: Dict[str, Any]) -> int:
    """إضافة عميل جديد"""
    query = """
    INSERT INTO Clients
    (CompanyName, ContactPerson, Phone, Email, Industry, RequiredCount,
     MinAge, MaxAge, RequiredGender, RequiredLevel, RequiredSkills,
     SalaryRange, Status)
    OUTPUT INSERTED.ClientID
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        client_data.get("CompanyName", ""),
        client_data.get("ContactPerson", ""),
        client_data.get("Phone", ""),
        client_data.get("Email", ""),
        client_data.get("Industry", ""),
        client_data.get("RequiredCount", 0),
        client_data.get("MinAge", 0),
        client_data.get("MaxAge", 0),
        client_data.get("RequiredGender", "Any"),
        client_data.get("RequiredLevel", ""),
        client_data.get("RequiredSkills", ""),
        client_data.get("SalaryRange", ""),
        client_data.get("Status", "Active"),
    )
    
    return exec_insert_return_id(query, params)

# ==================== دوال الفواتير ====================
def get_pending_invoices() -> List[Dict[str, Any]]:
    """جلب الفواتير المعلقة"""
    query = """
    SELECT 
        i.InvoiceID, i.InvoiceType, i.Amount, i.PaidAmount, i.DueDate,
        c.FullName, c.Phone
    FROM Invoices i
    JOIN Candidates c ON i.CandidateID = c.CandidateID
    WHERE i.Status IN ('Pending', 'Partial')
    ORDER BY i.DueDate
    """
    return fetch_all(query)

def create_invoice(invoice_data: Dict[str, Any]) -> int:
    """إنشاء فاتورة جديدة"""
    query = """
    INSERT INTO Invoices 
    (CandidateID, InvoiceType, ReferenceID, Amount, DueDate, Status)
    OUTPUT INSERTED.InvoiceID
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    params = (
        invoice_data.get("CandidateID"),
        invoice_data.get("InvoiceType", "Training"),
        invoice_data.get("ReferenceID"),
        invoice_data.get("Amount", 0.0),
        invoice_data.get("DueDate"),
        invoice_data.get("Status", "Pending"),
    )
    
    return exec_insert_return_id(query, params)

# ==================== دوال المطابقة ====================
def match_candidate_to_client(match_data: Dict[str, Any]) -> int:
    """مطابقة مرشح مع عميل"""
    query = """
    INSERT INTO Matches (CandidateID, ClientID, MatchScore, Status)
    OUTPUT INSERTED.MatchID
    VALUES (?, ?, ?, ?)
    """
    
    params = (
        match_data.get("CandidateID"),
        match_data.get("ClientID"),
        match_data.get("MatchScore", 0),
        match_data.get("Status", "Pending"),
    )
    
    return exec_insert_return_id(query, params)

# ==================== دوال مساعدة للجدول ====================
def _table_exists(cursor, table_name: str) -> bool:
    """التحقق من وجود جدول"""
    cursor.execute("""
        SELECT 1 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = ?
    """, (table_name,))
    return cursor.fetchone() is not None

def _column_exists(cursor, table_name: str, column_name: str) -> bool:
    """التحقق من وجود عمود"""
    cursor.execute("""
        SELECT 1 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = ? AND COLUMN_NAME = ?
    """, (table_name, column_name))
    return cursor.fetchone() is not None

# ==================== دوال المرحلة 1: الإعلان والتسجيل ====================
def add_interest_registration(interest_data: Dict[str, Any]) -> int:
    """إضافة تسجيل اهتمام جديد"""
    query = """
    INSERT INTO InterestRegistrations 
    (FullName, Phone, Governorate, Profession, Source, CampaignName, Status, AgentName)
    OUTPUT INSERTED.InterestID
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        interest_data.get("FullName", ""),
        interest_data.get("Phone", ""),
        interest_data.get("Governorate", ""),
        interest_data.get("Profession", ""),
        interest_data.get("Source", "Website"),
        interest_data.get("CampaignName", "General"),
        interest_data.get("Status", "New"),
        interest_data.get("AgentName", ""),
    )
    
    return exec_insert_return_id(query, params)

def get_all_interests(status: str = None) -> List[Dict[str, Any]]:
    """جلب جميع تسجيلات الاهتمام"""
    if status:
        query = """
        SELECT InterestID, FullName, Phone, Governorate, Profession, Source,
               CampaignName, RegistrationDate, Status, AgentName, LastContactDate
        FROM InterestRegistrations
        WHERE Status = ?
        ORDER BY RegistrationDate DESC
        """
        return fetch_all(query, (status,))
    else:
        query = """
        SELECT InterestID, FullName, Phone, Governorate, Profession, Source,
               CampaignName, RegistrationDate, Status, AgentName, LastContactDate
        FROM InterestRegistrations
        ORDER BY RegistrationDate DESC
        """
        return fetch_all(query)

def update_interest_status(interest_id: int, status: str, agent_name: str = None) -> bool:
    """تحديث حالة المهتم"""
    query = """
    UPDATE InterestRegistrations
    SET Status = ?, 
        AgentName = ISNULL(?, AgentName),
        LastContactDate = GETDATE()
    WHERE InterestID = ?
    """
    return exec_non_query(query, (status, agent_name, interest_id)) > 0

def convert_interest_to_candidate(interest_id: int) -> int:
    """تحويل تسجيل اهتمام إلى مرشح كامل"""
    # جلب بيانات المهتم
    query = "SELECT * FROM InterestRegistrations WHERE InterestID = ?"
    interests = fetch_all(query, (interest_id,))
    
    if not interests:
        return 0
    
    interest = interests[0]
    
    # إنشاء مرشح جديد
    candidate_data = {
        "FullName": interest["FullName"],
        "Phone": interest["Phone"],
        "Status": "New",
        "Notes": f"تم التحويل من تسجيل اهتمام رقم {interest_id}"
    }
    
    candidate_id = add_candidate(candidate_data)
    
    # تحديث حالة المهتم
    update_interest_status(interest_id, "Registered")
    
    return candidate_id

def add_sales_followup(followup_data: Dict[str, Any]) -> int:
    """إضافة متابعة مبيعات"""
    query = """
    INSERT INTO SalesFollowups 
    (InterestID, AgentName, FollowupType, Status, Notes, NextFollowupDate)
    OUTPUT INSERTED.FollowupID
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    params = (
        followup_data.get("InterestID"),
        followup_data.get("AgentName", ""),
        followup_data.get("FollowupType", "Call"),
        followup_data.get("Status", "Contacted"),
        followup_data.get("Notes", ""),
        followup_data.get("NextFollowupDate"),
    )
    
    return exec_insert_return_id(query, params)

def get_sales_dashboard() -> Dict[str, Any]:
    """لوحة تحكم المبيعات"""
    stats = {}
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # إجمالي المهتمين
        cursor.execute("SELECT COUNT(*) FROM InterestRegistrations")
        stats["total_leads"] = cursor.fetchone()[0] or 0
        
        # المهتمين الجدد اليوم
        cursor.execute("""
            SELECT COUNT(*) 
            FROM InterestRegistrations 
            WHERE CONVERT(DATE, RegistrationDate) = CONVERT(DATE, GETDATE())
        """)
        stats["today_leads"] = cursor.fetchone()[0] or 0
        
        # المهتمين المتصل بهم
        cursor.execute("SELECT COUNT(*) FROM InterestRegistrations WHERE Status = 'Contacted'")
        stats["contacted_leads"] = cursor.fetchone()[0] or 0
        
        # المهتمين المحولين لمرشحين
        cursor.execute("SELECT COUNT(*) FROM InterestRegistrations WHERE Status = 'Registered'")
        stats["converted_leads"] = cursor.fetchone()[0] or 0
        
        # معدل التحويل
        if stats["total_leads"] > 0:
            stats["conversion_rate"] = round((stats["converted_leads"] / stats["total_leads"]) * 100, 1)
        else:
            stats["conversion_rate"] = 0
        
        conn.close()
    except Exception as e:
        logger.error(f"خطأ في جلب إحصائيات المبيعات: {e}")
    
    return stats

def get_followups_by_interest(interest_id: int) -> List[Dict[str, Any]]:
    """جلب متابعات مهتم معين"""
    query = """
    SELECT FollowupID, AgentName, FollowupDate, FollowupType, 
           Status, Notes, NextFollowupDate
    FROM SalesFollowups
    WHERE InterestID = ?
    ORDER BY FollowupDate DESC
    """
    return fetch_all(query, (interest_id,))

def update_lead_status(interest_id: int, status: str, agent_name: str = None) -> bool:
    """تحديث حالة المهتم مع تسجيل متابعة"""
    # تحديث حالة المهتم
    query1 = """
    UPDATE InterestRegistrations 
    SET Status = ?, 
        AgentName = ISNULL(?, AgentName),
        LastContactDate = GETDATE()
    WHERE InterestID = ?
    """
    exec_non_query(query1, (status, agent_name, interest_id))
    
    # إذا كان هناك تحويل لمرشح
    if status == 'Registered':
        candidate_id = convert_interest_to_candidate(interest_id)
        
        # تسجيل متابعة للتحويل
        if agent_name:
            followup_data = {
                'InterestID': interest_id,
                'AgentName': agent_name,
                'FollowupType': 'Conversion',
                'Status': 'Converted',
                'Notes': f'تم التحويل إلى مرشح رقم {candidate_id}'
            }
            add_sales_followup(followup_data)
    
    return True

def get_sales_performance(month_year: str = None) -> List[Dict[str, Any]]:
    """أداء المبيعات الشهري"""
    if not month_year:
        month_year = datetime.now().strftime('%Y-%m')
    
    query = """
    SELECT 
        AgentName,
        COUNT(DISTINCT s.InterestID) AS TotalFollowups,
        SUM(CASE WHEN s.Status = 'Converted' THEN 1 ELSE 0 END) AS Conversions,
        SUM(CASE WHEN s.Status = 'Contacted' THEN 1 ELSE 0 END) AS Contacted
    FROM SalesFollowups s
    WHERE CONVERT(CHAR(7), s.FollowupDate, 120) = ?
    GROUP BY AgentName
    ORDER BY Conversions DESC
    """
    return fetch_all(query, (month_year,))

# ==================== دوال المرحلة 2: التدريبات المتقدمة ====================
def add_assessment(assessment_data: Dict[str, Any]) -> int:
    """إضافة تقييم خلال التدريب"""
    query = """
    INSERT INTO Assessments 
    (CandidateID, TrainingID, AssessmentType, Score, MaxScore, Evaluator, Comments)
    OUTPUT INSERTED.AssessmentID
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        assessment_data.get("CandidateID"),
        assessment_data.get("TrainingID"),
        assessment_data.get("AssessmentType", "Weekly"),
        assessment_data.get("Score", 0),
        assessment_data.get("MaxScore", 100),
        assessment_data.get("Evaluator", ""),
        assessment_data.get("Comments", ""),
    )
    
    return exec_insert_return_id(query, params)

def get_assessments_by_candidate(candidate_id: int) -> List[Dict[str, Any]]:
    """جلب تقييمات مرشح"""
    query = """
    SELECT a.*, t.TrainingName
    FROM Assessments a
    JOIN Trainings t ON a.TrainingID = t.TrainingID
    WHERE a.CandidateID = ?
    ORDER BY a.AssessmentDate DESC
    """
    return fetch_all(query, (candidate_id,))

def generate_certificate(certificate_data: Dict[str, Any]) -> int:
    """إنشاء شهادة تدريب"""
    query = """
    INSERT INTO Certificates 
    (CandidateID, TrainingID, CertificateNumber, Grades, Status)
    OUTPUT INSERTED.CertificateID
    VALUES (?, ?, ?, ?, ?)
    """
    
    params = (
        certificate_data.get("CandidateID"),
        certificate_data.get("TrainingID"),
        certificate_data.get("CertificateNumber"),
        certificate_data.get("Grades", ""),
        certificate_data.get("Status", "Active"),
    )
    
    return exec_insert_return_id(query, params)

def get_certificates_by_candidate(candidate_id: int) -> List[Dict[str, Any]]:
    """جلب شهادات مرشح"""
    query = """
    SELECT c.*, t.TrainingName
    FROM Certificates c
    JOIN Trainings t ON c.TrainingID = t.TrainingID
    WHERE c.CandidateID = ?
    ORDER BY c.IssueDate DESC
    """
    return fetch_all(query, (candidate_id,))

def add_client_request(request_data: Dict[str, Any]) -> int:
    """إضافة طلب توظيف من عميل"""
    query = """
    INSERT INTO ClientRequests 
    (ClientID, JobTitle, RequiredCount, MinAge, MaxAge, RequiredGender,
     RequiredEducation, RequiredLanguageLevel, RequiredSkills, SalaryRange,
     Area, Deadline, Status, Notes)
    OUTPUT INSERTED.RequestID
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        request_data.get("ClientID"),
        request_data.get("JobTitle", ""),
        request_data.get("RequiredCount", 1),
        request_data.get("MinAge", 18),
        request_data.get("MaxAge", 60),
        request_data.get("RequiredGender", "Any"),
        request_data.get("RequiredEducation", ""),
        request_data.get("RequiredLanguageLevel", ""),
        request_data.get("RequiredSkills", ""),
        request_data.get("SalaryRange", ""),
        request_data.get("Area", ""),
        request_data.get("Deadline"),
        request_data.get("Status", "Active"),
        request_data.get("Notes", ""),
    )
    
    return exec_insert_return_id(query, params)

def get_matching_candidates(client_request_id: int) -> List[Dict[str, Any]]:
    """العثور على مرشحين مطابقين لطلب عميل"""
    # جلب مواصفات الطلب
    query = """
    SELECT * FROM ClientRequests WHERE RequestID = ?
    """
    requests = fetch_all(query, (client_request_id,))
    
    if not requests:
        return []
    
    request = requests[0]
    
    # بناء استعلام البحث عن مرشحين مطابقين
    conditions = []
    params = []
    
    if request.get("MinAge"):
        conditions.append("Age >= ?")
        params.append(request["MinAge"])
    
    if request.get("MaxAge"):
        conditions.append("Age <= ?")
        params.append(request["MaxAge"])
    
    if request.get("RequiredGender") and request["RequiredGender"] != "Any":
        conditions.append("Gender = ?")
        params.append(request["RequiredGender"])
    
    if request.get("RequiredEducation"):
        conditions.append("EducationLevel LIKE ?")
        params.append(f"%{request['RequiredEducation']}%")
    
    if request.get("RequiredLanguageLevel"):
        conditions.append("LanguageLevel >= ?")
        params.append(request["RequiredLanguageLevel"])
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
    SELECT CandidateID, FullName, Age, Gender, EducationLevel, 
           LanguageLevel, WorkExperience, ExpectedSalary
    FROM Candidates
    WHERE Status IN ('New', 'Available') AND {where_clause}
    ORDER BY CandidateID DESC
    """
    
    return fetch_all(query, tuple(params))

def record_hiring(hiring_data: Dict[str, Any]) -> int:
    """تسجيل توظيف ناجح"""
    query = """
    INSERT INTO HiringRecords 
    (CandidateID, ClientID, JobTitle, OfferedSalary, StartDate, Status, Notes)
    OUTPUT INSERTED.HiringID
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        hiring_data.get("CandidateID"),
        hiring_data.get("ClientID"),
        hiring_data.get("JobTitle", ""),
        hiring_data.get("OfferedSalary", 0),
        hiring_data.get("StartDate"),
        hiring_data.get("Status", "Offered"),
        hiring_data.get("Notes", ""),
    )
    
    return exec_insert_return_id(query, params)

def schedule_interview(interview_data: Dict[str, Any]) -> int:
    """جدولة مقابلة"""
    query = """
    INSERT INTO InterviewTracking 
    (CandidateID, ClientID, InterviewDate, InterviewTime, Location, 
     Interviewer, Status, NextStep)
    OUTPUT INSERTED.InterviewID
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        interview_data.get("CandidateID"),
        interview_data.get("ClientID"),
        interview_data.get("InterviewDate"),
        interview_data.get("InterviewTime"),
        interview_data.get("Location", ""),
        interview_data.get("Interviewer", ""),
        interview_data.get("Status", "Scheduled"),
        interview_data.get("NextStep", ""),
    )
    
    return exec_insert_return_id(query, params)

def get_placement_exams() -> List[Dict[str, Any]]:
    """جلب امتحانات تحديد المستوى"""
    query = """
    SELECT ExamID, ExamName, Duration, Fee, PassingScore
    FROM Exams
    WHERE ExamType = 'Placement'
    ORDER BY ExamName
    """
    return fetch_all(query)

def get_training_assessments(training_id: int) -> List[Dict[str, Any]]:
    """جلب امتحانات تدريب معين"""
    query = """
    SELECT * FROM TrainingAssessments
    WHERE TrainingID = ?
    ORDER BY AssessmentDate
    """
    return fetch_all(query, (training_id,))

def get_active_client_requests() -> List[Dict[str, Any]]:
    """جلب طلبات التوظيف النشطة"""
    query = """
    SELECT cr.*, c.CompanyName, c.ContactPerson, c.Phone
    FROM ClientRequests cr
    JOIN Clients c ON cr.ClientID = c.ClientID
    WHERE cr.Status = 'Active' AND cr.Deadline >= GETDATE()
    ORDER BY cr.RequestDate DESC
    """
    return fetch_all(query)

def get_interviews_by_candidate(candidate_id: int) -> List[Dict[str, Any]]:
    """جلب مقابلات مرشح"""
    query = """
    SELECT it.*, c.CompanyName
    FROM InterviewTracking it
    JOIN Clients c ON it.ClientID = c.ClientID
    LEFT JOIN Candidates cl ON it.CandidateID = cl.CandidateID
    WHERE it.CandidateID = ?
    ORDER BY it.InterviewDate DESC
    """
    return fetch_all(query, (candidate_id,))

def get_hiring_records(status: str = None) -> List[Dict[str, Any]]:
    """جلب سجلات التوظيف"""
    if status:
        query = """
        SELECT hr.*, c.FullName, cl.CompanyName
        FROM HiringRecords hr
        JOIN Candidates c ON hr.CandidateID = c.CandidateID
        JOIN Clients cl ON hr.ClientID = cl.ClientID
        WHERE hr.Status = ?
        ORDER BY hr.StartDate DESC
        """
        return fetch_all(query, (status,))
    else:
        query = """
        SELECT hr.*, c.FullName, cl.CompanyName
        FROM HiringRecords hr
        JOIN Candidates c ON hr.CandidateID = c.CandidateID
        JOIN Clients cl ON hr.ClientID = cl.ClientID
        ORDER BY hr.StartDate DESC
        """
        return fetch_all(query)

# ==================== دوال إضافية ====================
def get_daily_leads_count(days: int = 30) -> List[Dict[str, Any]]:
    """عدد التسجيلات اليومي"""
    query = """
    SELECT 
        CONVERT(DATE, RegistrationDate) AS Date,
        COUNT(*) AS LeadsCount,
        SUM(CASE WHEN Status = 'Registered' THEN 1 ELSE 0 END) AS Converted
    FROM InterestRegistrations
    WHERE RegistrationDate >= DATEADD(DAY, -?, GETDATE())
    GROUP BY CONVERT(DATE, RegistrationDate)
    ORDER BY Date DESC
    """
    return fetch_all(query, (days,))

def get_conversion_rate() -> float:
    """معدل التحويل (تسجيلات اهتمام → مرشحين)"""
    query = """
    SELECT 
        (COUNT(CASE WHEN Status = 'Registered' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)) AS ConversionRate
    FROM InterestRegistrations
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    
    return float(result[0]) if result and result[0] else 0.0

def get_system_stats() -> Dict[str, Any]:
    """إحصائيات النظام الكاملة"""
    stats = get_dashboard_stats()
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # إحصائيات التسجيلات
        cursor.execute("SELECT COUNT(*) FROM InterestRegistrations")
        stats["total_interests"] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM Campaigns WHERE Status = 'Active'")
        stats["active_campaigns"] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(Amount) FROM Invoices WHERE Status = 'Paid'")
        stats["total_revenue"] = float(cursor.fetchone()[0] or 0)
        
        cursor.execute("SELECT COUNT(*) FROM Certificates")
        stats["certificates_issued"] = cursor.fetchone()[0] or 0
        
        # إحصائيات التوظيف
        cursor.execute("SELECT COUNT(*) FROM HiringRecords WHERE Status = 'Started'")
        stats["active_placements"] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM ClientRequests WHERE Status = 'Active'")
        stats["active_requests"] = cursor.fetchone()[0] or 0
        
        conn.close()
    except Exception as e:
        logger.error(f"خطأ في جلب إحصائيات النظام: {e}")
    
    return stats

def backup_database(backup_path: str = None) -> bool:
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    try:
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_Place2026_{timestamp}.bak"
        
        conn = get_connection()
        cursor = conn.cursor()
        
        query = f"BACKUP DATABASE Place2026 TO DISK = '{backup_path}'"
        cursor.execute(query)
        conn.commit()
        conn.close()
        
        logger.info(f"تم إنشاء نسخة احتياطية في: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"فشل في إنشاء نسخة احتياطية: {e}")
        return False

# ==================== تهيئة قاعدة البيانات ====================
def init_database():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    connection = None
    cursor = None
    actions_log = []
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        print("\n" + "="*80)
        print("🎯 بدء تهيئة قاعدة البيانات Place2026")
        print("="*80)
        
        # ============== الجداول الأساسية ==============
        
        # 1. جدول المرشحين ✅
        if not _table_exists(cursor, "Candidates"):
            cursor.execute("""
                CREATE TABLE Candidates (
                    CandidateID INT IDENTITY(1,1) PRIMARY KEY,
                    FullName NVARCHAR(100) NOT NULL,
                    Phone NVARCHAR(20) NOT NULL UNIQUE,
                    Email NVARCHAR(100),
                    Age INT,
                    Gender NVARCHAR(10),
                    NationalID NVARCHAR(14),
                    Address NVARCHAR(200),
                    EducationLevel NVARCHAR(50),
                    LanguageLevel NVARCHAR(20),
                    ComputerSkills NVARCHAR(200),
                    WorkExperience NVARCHAR(500),
                    ExpectedSalary DECIMAL(10,2),
                    RegistrationDate DATETIME DEFAULT GETDATE(),
                    Status NVARCHAR(20) DEFAULT 'New',
                    Notes NVARCHAR(MAX)
                )
            """)
            actions_log.append("✅ تم إنشاء جدول المرشحين")
        
        # 2. جدول الامتحانات ✅
        if not _table_exists(cursor, "Exams"):
            cursor.execute("""
                CREATE TABLE Exams (
                    ExamID INT IDENTITY(1,1) PRIMARY KEY,
                    ExamName NVARCHAR(100) NOT NULL,
                    ExamType NVARCHAR(30),
                    TotalScore INT DEFAULT 100,
                    PassingScore INT DEFAULT 60,
                    Duration INT,
                    Fee DECIMAL(10,2) DEFAULT 300.00
                )
            """)
            actions_log.append("✅ تم إنشاء جدول الامتحانات")
        
        # 3. جدول التدريبات ✅
        if not _table_exists(cursor, "Trainings"):
            cursor.execute("""
                CREATE TABLE Trainings (
                    TrainingID INT IDENTITY(1,1) PRIMARY KEY,
                    TrainingName NVARCHAR(100) NOT NULL,
                    Description NVARCHAR(MAX),
                    Category NVARCHAR(50),
                    DurationHours INT,
                    Fee DECIMAL(10,2),
                    MaxCapacity INT,
                    StartDate DATE,
                    EndDate DATE,
                    Schedule NVARCHAR(200),
                    Location NVARCHAR(200),
                    Instructor NVARCHAR(100),
                    Status NVARCHAR(20) DEFAULT 'Upcoming'
                )
            """)
            actions_log.append("✅ تم إنشاء جدول التدريبات")
        
        # 4. جدول العملاء ✅
        if not _table_exists(cursor, "Clients"):
            cursor.execute("""
                CREATE TABLE Clients (
                    ClientID INT IDENTITY(1,1) PRIMARY KEY,
                    CompanyName NVARCHAR(100) NOT NULL,
                    ContactPerson NVARCHAR(100),
                    Phone NVARCHAR(20),
                    Email NVARCHAR(100),
                    Industry NVARCHAR(50),
                    RequiredCount INT,
                    MinAge INT,
                    MaxAge INT,
                    RequiredGender NVARCHAR(10),
                    RequiredLevel NVARCHAR(20),
                    RequiredSkills NVARCHAR(200),
                    SalaryRange NVARCHAR(50),
                    Status NVARCHAR(20) DEFAULT 'Active'
                )
            """)
            actions_log.append("✅ تم إنشاء جدول العملاء")
        
        # 5. جدول التسجيلات ✅
        if not _table_exists(cursor, "Enrollments"):
            cursor.execute("""
                CREATE TABLE Enrollments (
                    EnrollmentID INT IDENTITY(1,1) PRIMARY KEY,
                    CandidateID INT NOT NULL,
                    TrainingID INT NOT NULL,
                    EnrollmentDate DATETIME DEFAULT GETDATE(),
                    Status NVARCHAR(20) DEFAULT 'Registered',
                    FinalGrade DECIMAL(5,2),
                    CertificateIssued BIT DEFAULT 0
                )
            """)
            actions_log.append("✅ تم إنشاء جدول التسجيلات")
        
        # 6. جدول مواعيد الامتحانات ✅
        if not _table_exists(cursor, "ExamAppointments"):
            cursor.execute("""
                CREATE TABLE ExamAppointments (
                    AppointmentID INT IDENTITY(1,1) PRIMARY KEY,
                    CandidateID INT NOT NULL,
                    ExamID INT NOT NULL,
                    AppointmentDate DATETIME NOT NULL,
                    Status NVARCHAR(20) DEFAULT 'Scheduled',
                    Result NVARCHAR(10),
                    Score DECIMAL(5,2)
                )
            """)
            actions_log.append("✅ تم إنشاء جدول مواعيد الامتحانات")
        
        # 7. جدول جلسات التدريب ✅
        if not _table_exists(cursor, "TrainingSessions"):
            cursor.execute("""
                CREATE TABLE TrainingSessions (
                    SessionID INT IDENTITY(1,1) PRIMARY KEY,
                    TrainingID INT NOT NULL,
                    SessionNumber INT DEFAULT 1,
                    SessionDate DATE NOT NULL,
                    StartTime NVARCHAR(10) NOT NULL,
                    EndTime NVARCHAR(10) NOT NULL,
                    Topic NVARCHAR(200),
                    Location NVARCHAR(200),
                    QRCode NVARCHAR(200) NOT NULL,
                    QRExpiry DATETIME,
                    Status NVARCHAR(20) DEFAULT 'Scheduled'
                )
            """)
            actions_log.append("✅ تم إنشاء جدول جلسات التدريب")
        
        # 8. جدول الحضور ✅
        if not _table_exists(cursor, "Attendance"):
            cursor.execute("""
                CREATE TABLE Attendance (
                    AttendanceID INT IDENTITY(1,1) PRIMARY KEY,
                    SessionID INT NOT NULL,
                    CandidateID INT NOT NULL,
                    CheckInTime DATETIME DEFAULT GETDATE(),
                    Method NVARCHAR(20)
                )
            """)
            actions_log.append("✅ تم إنشاء جدول الحضور")
        
        # 9. جدول الفواتير ✅
        if not _table_exists(cursor, "Invoices"):
            cursor.execute("""
                CREATE TABLE Invoices (
                    InvoiceID INT IDENTITY(1,1) PRIMARY KEY,
                    CandidateID INT NOT NULL,
                    InvoiceType NVARCHAR(20),
                    ReferenceID INT,
                    Amount DECIMAL(10,2) NOT NULL,
                    PaidAmount DECIMAL(10,2) DEFAULT 0,
                    IssueDate DATETIME DEFAULT GETDATE(),
                    DueDate DATE,
                    Status NVARCHAR(20) DEFAULT 'Pending'
                )
            """)
            actions_log.append("✅ تم إنشاء جدول الفواتير")
        
        # 10. جدول المطابقات ✅
        if not _table_exists(cursor, "Matches"):
            cursor.execute("""
                CREATE TABLE Matches (
                    MatchID INT IDENTITY(1,1) PRIMARY KEY,
                    CandidateID INT NOT NULL,
                    ClientID INT NOT NULL,
                    MatchScore DECIMAL(5,2) DEFAULT 0,
                    Status NVARCHAR(20) DEFAULT 'Pending',
                    CreatedAt DATETIME DEFAULT GETDATE()
                )
            """)
            actions_log.append("✅ تم إنشاء جدول المطابقات")
        
        # ============== جداول المرحلة 1: الإعلان والتسجيل ==============
        
        # 11. جدول تسجيلات الاهتمام ✅
        if not _table_exists(cursor, "InterestRegistrations"):
            cursor.execute("""
                CREATE TABLE InterestRegistrations (
                    InterestID INT IDENTITY(1,1) PRIMARY KEY,
                    FullName NVARCHAR(100) NOT NULL,
                    Phone NVARCHAR(20) NOT NULL,
                    Governorate NVARCHAR(50),
                    Profession NVARCHAR(50),
                    Source NVARCHAR(50) DEFAULT 'Website',
                    CampaignName NVARCHAR(100),
                    RegistrationDate DATETIME DEFAULT GETDATE(),
                    Status NVARCHAR(20) DEFAULT 'New',
                    Notes NVARCHAR(MAX),
                    AgentName NVARCHAR(100),
                    LastContactDate DATETIME
                )
            """)
            actions_log.append("✅ تم إنشاء جدول InterestRegistrations")
        
        # 12. جدول الحملات الإعلانية ✅
        if not _table_exists(cursor, "Campaigns"):
            cursor.execute("""
                CREATE TABLE Campaigns (
                    CampaignID INT IDENTITY(1,1) PRIMARY KEY,
                    CampaignName NVARCHAR(100) NOT NULL,
                    Platform NVARCHAR(50),
                    StartDate DATE,
                    EndDate DATE,
                    Budget DECIMAL(10,2),
                    LeadsTarget INT,
                    ActualLeads INT DEFAULT 0,
                    CostPerLead DECIMAL(10,2),
                    Status NVARCHAR(20) DEFAULT 'Active'
                )
            """)
            actions_log.append("✅ تم إنشاء جدول Campaigns")
        
        # 13. جدول متابعات المبيعات ✅
        if not _table_exists(cursor, "SalesFollowups"):
            cursor.execute("""
                CREATE TABLE SalesFollowups (
                    FollowupID INT IDENTITY(1,1) PRIMARY KEY,
                    InterestID INT NOT NULL,
                    AgentName NVARCHAR(100),
                    FollowupDate DATETIME DEFAULT GETDATE(),
                    FollowupType NVARCHAR(20),
                    Status NVARCHAR(20),
                    Notes NVARCHAR(MAX),
                    NextFollowupDate DATETIME
                )
            """)
            actions_log.append("✅ تم إنشاء جدول SalesFollowups")
        
        # 14. جدول أهداف المبيعات ✅
        if not _table_exists(cursor, "SalesTargets"):
            cursor.execute("""
                CREATE TABLE SalesTargets (
                    TargetID INT IDENTITY(1,1) PRIMARY KEY,
                    AgentName NVARCHAR(100),
                    MonthYear CHAR(7),
                    TargetLeads INT DEFAULT 30,
                    TargetConversions INT DEFAULT 10,
                    TargetRevenue DECIMAL(10,2) DEFAULT 0,
                    ActualLeads INT DEFAULT 0,
                    ActualConversions INT DEFAULT 0,
                    ActualRevenue DECIMAL(10,2) DEFAULT 0
                )
            """)
            actions_log.append("✅ تم إنشاء جدول SalesTargets")
        
        # ============== جداول المرحلة 2: التدريبات المتقدمة ==============
        
        # 15. جدول التقييمات ✅
        if not _table_exists(cursor, "Assessments"):
            cursor.execute("""
                CREATE TABLE Assessments (
                    AssessmentID INT IDENTITY(1,1) PRIMARY KEY,
                    CandidateID INT NOT NULL,
                    TrainingID INT NOT NULL,
                    AssessmentType NVARCHAR(30),
                    AssessmentDate DATE DEFAULT GETDATE(),
                    Score DECIMAL(5,2),
                    MaxScore DECIMAL(5,2) DEFAULT 100,
                    Evaluator NVARCHAR(100),
                    Comments NVARCHAR(MAX)
                )
            """)
            actions_log.append("✅ تم إنشاء جدول Assessments")
        
        # 16. جدول الشهادات ✅
        if not _table_exists(cursor, "Certificates"):
            cursor.execute("""
                CREATE TABLE Certificates (
                    CertificateID INT IDENTITY(1,1) PRIMARY KEY,
                    CandidateID INT NOT NULL,
                    TrainingID INT NOT NULL,
                    CertificateNumber VARCHAR(50) UNIQUE,
                    IssueDate DATE DEFAULT GETDATE(),
                    ExpiryDate DATE,
                    Grades NVARCHAR(50),
                    DigitalURL NVARCHAR(500),
                    QRCode VARCHAR(100),
                    Status NVARCHAR(20) DEFAULT 'Active'
                )
            """)
            actions_log.append("✅ تم إنشاء جدول Certificates")
        
        # 17. جدول امتحانات التدريب ✅
        if not _table_exists(cursor, "TrainingAssessments"):
            cursor.execute("""
                CREATE TABLE TrainingAssessments (
                    TrainingAssessmentID INT IDENTITY(1,1) PRIMARY KEY,
                    TrainingID INT NOT NULL,
                    AssessmentName NVARCHAR(100),
                    AssessmentType NVARCHAR(30),
                    TotalScore INT DEFAULT 100,
                    PassingScore INT DEFAULT 70,
                    AssessmentDate DATE,
                    Location NVARCHAR(200),
                    Instructor NVARCHAR(100),
                    Status NVARCHAR(20) DEFAULT 'Scheduled'
                )
            """)
            actions_log.append("✅ تم إنشاء جدول TrainingAssessments")
        
        # 18. جدول سجلات التوظيف ✅
        if not _table_exists(cursor, "HiringRecords"):
            cursor.execute("""
                CREATE TABLE HiringRecords (
                    HiringID INT IDENTITY(1,1) PRIMARY KEY,
                    CandidateID INT NOT NULL,
                    ClientID INT NOT NULL,
                    InterviewDate DATE,
                    JobTitle NVARCHAR(100),
                    OfferedSalary DECIMAL(10,2),
                    StartDate DATE,
                    Status NVARCHAR(20),
                    Notes NVARCHAR(MAX)
                )
            """)
            actions_log.append("✅ تم إنشاء جدول HiringRecords")
        
        # 19. جدول طلبات التوظيف من العملاء ✅
        if not _table_exists(cursor, "ClientRequests"):
            cursor.execute("""
                CREATE TABLE ClientRequests (
                    RequestID INT IDENTITY(1,1) PRIMARY KEY,
                    ClientID INT NOT NULL,
                    JobTitle NVARCHAR(100),
                    RequiredCount INT,
                    MinAge INT,
                    MaxAge INT,
                    RequiredGender NVARCHAR(10),
                    RequiredEducation NVARCHAR(50),
                    RequiredLanguageLevel NVARCHAR(10),
                    RequiredSkills NVARCHAR(MAX),
                    SalaryRange NVARCHAR(50),
                    Area NVARCHAR(100),
                    RequestDate DATE DEFAULT GETDATE(),
                    Deadline DATE,
                    Status NVARCHAR(20) DEFAULT 'Active',
                    Notes NVARCHAR(MAX)
                )
            """)
            actions_log.append("✅ تم إنشاء جدول ClientRequests")
        
        # 20. جدول تتبع المقابلات ✅
        if not _table_exists(cursor, "InterviewTracking"):
            cursor.execute("""
                CREATE TABLE InterviewTracking (
                    InterviewID INT IDENTITY(1,1) PRIMARY KEY,
                    CandidateID INT NOT NULL,
                    ClientID INT NOT NULL,
                    InterviewDate DATE,
                    InterviewTime NVARCHAR(10),
                    Location NVARCHAR(200),
                    Interviewer NVARCHAR(100),
                    Status NVARCHAR(20),
                    Result NVARCHAR(20),
                    Feedback NVARCHAR(MAX),
                    NextStep NVARCHAR(100)
                )
            """)
            actions_log.append("✅ تم إنشاء جدول InterviewTracking")
        
        # ============== إضافة بيانات تجريبية أساسية ==============
        
        # إضافة امتحانات تحديد المستوى
        cursor.execute("SELECT COUNT(*) FROM Exams WHERE ExamType = 'Placement'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO Exams (ExamName, ExamType, Duration, Fee, PassingScore)
                VALUES 
                ('امتحان تحديد مستوى اللغة الإنجليزية - A1', 'Placement', 60, 100, 50),
                ('امتحان تحديد مستوى اللغة الإنجليزية - A2', 'Placement', 60, 100, 50),
                ('امتحان تحديد مستوى اللغة الإنجليزية - B1', 'Placement', 60, 100, 60),
                ('امتحان تحديد مستوى اللغة الإنجليزية - B2', 'Placement', 60, 100, 60),
                ('امتحان تحديد مستوى اللغة الإنجليزية - C1', 'Placement', 60, 100, 70)
            """)
            actions_log.append("✅ تم إضافة امتحانات تحديد المستوى")
        
        # إضافة تدريبات أساسية
        cursor.execute("SELECT COUNT(*) FROM Trainings")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO Trainings (TrainingName, Category, DurationHours, Fee, MaxCapacity, Instructor, Status)
                VALUES 
                ('دورة خدمة العملاء المتقدمة', 'Customer Service', 40, 5000, 30, 'أ. أحمد محمد', 'Upcoming'),
                ('دورة مهارات الاتصال الفعال', 'Communication', 30, 4000, 25, 'أ. منى حسن', 'Upcoming'),
                ('دورة اللغة الإنجليزية للمكاتب', 'Language', 60, 6000, 20, 'أ. سارة علي', 'Upcoming')
            """)
            actions_log.append("✅ تم إضافة تدريبات أساسية")
        
        connection.commit()
        
        # عرض تقرير التهيئة
        print("\n📋 ملخص التهيئة:")
        print("-" * 40)
        for action in actions_log:
            print(action)
        
        print("="*80)
        print(f"📅 تم التنفيذ في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🚀 قاعدة البيانات جاهزة للعمل!")
        print("="*80 + "\n")
        
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"\n❌ فشل في تهيئة قاعدة البيانات: {str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# ==================== نقطة الدخول الرئيسية ====================
if __name__ == "__main__":
    print("🔧 بدء تهيئة قاعدة البيانات...")
    try:
        init_database()
        print("✅ تمت التهيئة بنجاح!")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء التهيئة: {e}")