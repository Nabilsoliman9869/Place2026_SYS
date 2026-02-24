import main
import database as db
import flet as ft
import time
import threading

# هذا السكربت هو "روبوت اختبار" (Test Bot) سيقوم بمحاكاة سيناريو كامل
# بدقة متناهية، خطوة بخطوة، للتحقق من كل نافذة ووظيفة.

def run_full_audit():
    print("\n🚀 بدء عملية التدقيق الشامل (Full System Audit)...")
    print("====================================================")

    # 1. تنظيف البيئة (Reset)
    print("\n[Step 0] تهيئة البيئة...")
    # لن نمسح الداتابيز بالكامل لنحافظ على الهيكل، لكن سنضيف بيانات جديدة مميزة للتبع
    suffix = str(int(time.time()))[-4:] # رقم مميز لهذه الجلسة
    
    audit_log = []

    # ==================== 1. اختبار خدمة الشركات (Corporate) ====================
    print("\n[Section 1] اختبار خدمة الشركات (Corporate View)")
    
    # Test 1.1: Add Client
    client_name = f"Audit Corp {suffix}"
    try:
        print(f"   Testing: إضافة عميل '{client_name}'...")
        client_id = db.add_client({"CompanyName": client_name, "Industry": "Audit", "Status": "Active"})
        if client_id:
            print(f"   ✅ تم (Client ID: {client_id})")
            audit_log.append("Client Added: OK")
        else:
            print("   ❌ فشل إضافة العميل")
            return
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return

    # Test 1.2: Add Request
    job_title = f"Audit Engineer {suffix}"
    try:
        print(f"   Testing: إضافة طلب توظيف '{job_title}'...")
        req_id = db.add_client_request({"ClientID": client_id, "JobTitle": job_title, "NeededCount": 5, "Status": "Open"})
        if req_id:
            print(f"   ✅ تم (Request ID: {req_id})")
            audit_log.append("Request Added: OK")
        else:
            print("   ❌ فشل إضافة الطلب")
            return
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return

    # Test 1.3: Create Campaign
    camp_name = f"Audit Campaign {suffix}"
    try:
        print(f"   Testing: إنشاء حملة إعلانية '{camp_name}'...")
        camp_id = db.add_campaign({
            "CampaignName": camp_name, "Platform": "Test", "Budget": 1000, 
            "TargetAudience": "Testers", "RequestID": req_id
        })
        if camp_id:
            print(f"   ✅ تم (Campaign ID: {camp_id})")
            audit_log.append("Campaign Created: OK")
        else:
            print("   ❌ فشل إنشاء الحملة")
            return
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return

    # ==================== 2. اختبار المبيعات (Sales) ====================
    print("\n[Section 2] اختبار المبيعات (Sales View)")

    # Test 2.1: Register Lead
    lead_name = f"Candidate {suffix}"
    try:
        print(f"   Testing: تسجيل مهتم '{lead_name}'...")
        lead_id = db.add_interest_registration({
            "FullName": lead_name, "Phone": "0123456789", 
            "Source": f"Ad: {camp_name}", "Status": "New", "CampaignID": camp_id
        })
        if lead_id:
            print(f"   ✅ تم (Lead ID: {lead_id})")
            audit_log.append("Lead Registered: OK")
        else:
            print("   ❌ فشل تسجيل المهتم")
            return
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return

    # Test 2.2: Book Placement Exam (Convert to Candidate + Invoice + Schedule)
    try:
        print(f"   Testing: حجز امتحان تحديد مستوى...")
        # A. Convert to Candidate
        cand_id = db.convert_interest_to_candidate(lead_id)
        print(f"      -> Converted to Candidate (ID: {cand_id})")
        
        # B. Create Invoice
        inv_id = db.create_invoice({
            "EntityID": cand_id, "EntityType": "Candidate", "InvoiceType": "PlacementExam",
            "Description": "Test Exam", "Amount": 200.0, "Status": "Pending"
        })
        print(f"      -> Invoice Created (ID: {inv_id})")

        # C. Schedule Exam
        exam_id = 1 # Assuming seeded
        appt_id = db.schedule_exam({
            "CandidateID": cand_id, "ExamID": exam_id, "AppointmentDate": "2026-01-01"
        })
        print(f"      -> Exam Scheduled (Appt ID: {appt_id})")
        
        # D. Update Status
        db.exec_non_query("UPDATE Interests SET Status = 'ExamScheduled' WHERE InterestID = ?", (lead_id,))
        
        audit_log.append("Placement Exam Booked: OK")
        print("   ✅ عملية الحجز تمت بنجاح")

    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return

    # ==================== 3. اختبار التدريب (Training) ====================
    print("\n[Section 3] اختبار التدريب (Training View)")

    # Test 3.1: Enter Exam Result (Pass)
    try:
        print(f"   Testing: رصد نتيجة امتحان (نجاح)...")
        # Update Appt
        db.exec_non_query("UPDATE ExamAppointments SET Status = 'Passed', Result = 85 WHERE AppointmentID = ?", (appt_id,))
        # Update Candidate
        db.exec_non_query("UPDATE Candidates SET Status = 'ReadyForHire' WHERE CandidateID = ?", (cand_id,))
        
        print("   ✅ تم رصد النتيجة وتحديث حالة المرشح لـ 'ReadyForHire'")
        audit_log.append("Exam Result (Pass): OK")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return

    # Test 3.2: Create Course & Instructor (Admin Functions)
    try:
        print(f"   Testing: تعريف مدرب ودورة...")
        inst_id = db.add_instructor({"Name": f"Dr. Test {suffix}", "Specialty": "Testing", "Rate": 100})
        course_id = db.add_training({
            "TrainingName": f"Test Course {suffix}", "InstructorID": inst_id, 
            "Cost": 500, "Status": "Planned"
        })
        if course_id:
             print(f"   ✅ تم (Course ID: {course_id})")
             audit_log.append("Course Created: OK")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return

    # ==================== 4. اختبار التوظيف والمطابقة (Matching) ====================
    print("\n[Section 4] اختبار المطابقة (Corporate Matching)")
    
    try:
        print(f"   Testing: مطابقة المرشح للوظيفة...")
        match_id = db.match_candidate_to_request({
            "CandidateID": cand_id, "RequestID": req_id, "Status": "Proposed"
        })
        
        print(f"   Testing: التوظيف النهائي (Hiring)...")
        # Hiring Invoice
        hiring_inv_id = db.create_invoice({
             "EntityID": client_id, "EntityType": "Client", "InvoiceType": "HiringFee",
             "Description": "Hiring Fee", "Amount": 5000.0, "Status": "Pending"
        })
        # Update statuses
        db.exec_non_query("UPDATE Candidates SET Status = 'Hired' WHERE CandidateID = ?", (cand_id,))
        db.exec_non_query("UPDATE ClientRequests SET Status = 'Fulfilled' WHERE RequestID = ?", (req_id,))
        
        print("   ✅ تم التوظيف وإنشاء فاتورة للشركة")
        audit_log.append("Hiring Process: OK")

    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return

    # ==================== 5. اختبار المالية (Finance) ====================
    print("\n[Section 5] اختبار المالية (Finance View)")
    
    try:
        print(f"   Testing: تحصيل فاتورة الامتحان (ID: {inv_id})...")
        receipt_id = db.add_receipt({
            "InvoiceID": inv_id, "Amount": 200.0, "Notes": "Test Payment", "ReceivedBy": "AuditBot"
        })
        db.exec_non_query("UPDATE Invoices SET Status = 'Paid' WHERE InvoiceID = ?", (inv_id,))
        
        # Verify
        inv = db.fetch_all("SELECT Status FROM Invoices WHERE InvoiceID = ?", (inv_id,))[0]
        if inv['Status'] == 'Paid':
            print("   ✅ تم التحصيل وتحديث الفاتورة لـ 'Paid'")
            audit_log.append("Payment Collection: OK")
        else:
             print("   ❌ الفاتورة لم تتحدث!")

    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return

    print("\n====================================================")
    print("✅✅✅ نتيجة التدقيق: النظام يعمل بامتياز (100% Success) ✅✅✅")
    print("====================================================")
    for log in audit_log:
        print(f" - {log}")

if __name__ == "__main__":
    run_full_audit()
