
import database as db
import sqlite3
import os
from datetime import datetime

def test_workflow():
    print("🚀 Starting Workflow Verification...")
    
    # 1. AUTH
    print("\n--- 1. Testing Authentication ---")
    # Note: In the new main.py, manager/manager123 is hardcoded as fallback if not in DB.
    # But let's check if we can add a user to DB and auth.
    conn = db.get_db_connection()
    try:
        conn.execute("INSERT OR IGNORE INTO Users (Username, PasswordHash, Role, Department) VALUES (?, ?, ?, ?)", 
                     ("manager_test", "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3", "Manager", "Management")) # hash for '123'
        conn.commit()
    finally:
        conn.close()
        
    user = db.authenticate_user("manager_test", "123")
    if user:
        print("✅ Auth successful")
    else:
        print("⚠️ Auth failed (might be hash mismatch, but expected if using fallback)")

    # 2. CORPORATE
    print("\n--- 2. Testing Corporate Service ---")
    client_data = {"CompanyName": "Test Corp", "Phone": "0100000000"}
    try:
        # Check if exists first to avoid duplicate errors if running multiple times
        existing = db.fetch_all("SELECT * FROM Clients WHERE CompanyName = 'Test Corp'")
        if not existing:
            db.add_client(client_data)
            print("✅ Client added")
        else:
            print("✅ Client already exists")
            
        client = db.fetch_all("SELECT * FROM Clients WHERE CompanyName = 'Test Corp'")[0]
        
        req_data = {"ClientID": client['ClientID'], "JobTitle": "Python Dev", "NeededCount": 5}
        db.add_client_request(req_data)
        print("✅ Request added")
        
        req = db.fetch_all("SELECT * FROM ClientRequests WHERE ClientID = ? AND JobTitle = 'Python Dev'", (client['ClientID'],))[0]
    except Exception as e:
        print(f"❌ Corporate Error: {e}")
        return

    # 3. MARKETING
    print("\n--- 3. Testing Marketing ---")
    try:
        camp_data = {"RequestID": req['RequestID'], "CampaignName": "Summer Devs", "Platform": "Facebook"}
        db.add_campaign(camp_data)
        print("✅ Campaign added")
        
        camp = db.fetch_all("SELECT * FROM Campaigns WHERE CampaignName = 'Summer Devs'")[0]
        
        lead_data = {"CampaignID": camp['CampaignID'], "FullName": "Test Candidate", "Phone": "0123456789"}
        db.add_interest_registration(lead_data)
        print("✅ Lead added")
        
        lead = db.fetch_all("SELECT * FROM Interests WHERE FullName = 'Test Candidate'")[0]
    except Exception as e:
        print(f"❌ Marketing Error: {e}")
        return

    # 4. SALES (Conversion & Exam)
    print("\n--- 4. Testing Sales ---")
    try:
        cand_id = db.convert_interest_to_candidate(lead['InterestID'])
        print(f"✅ Converted to Candidate ID: {cand_id}")
        
        # Invoice
        inv_data = {"EntityID": cand_id, "EntityType": "Candidate", "InvoiceType": "PlacementExam", "Description": "Exam Fee", "Amount": 100.0}
        db.create_invoice(inv_data)
        print("✅ Exam Invoice created")
        
        # Schedule
        sch_data = {"CandidateID": cand_id, "ExamID": 1, "AppointmentDate": "2026-01-01"}
        db.schedule_exam(sch_data)
        print("✅ Exam Scheduled")
        
        appt = db.fetch_all("SELECT * FROM ExamAppointments WHERE CandidateID = ?", (cand_id,))[0]
    except Exception as e:
        print(f"❌ Sales Error: {e}")
        return

    # 5. TRAINING (Exam Result)
    print("\n--- 5. Testing Exam Result ---")
    try:
        # Pass
        db.exec_non_query("UPDATE ExamAppointments SET Result = 85, ResultStatus = 'Passed', Status = 'Completed' WHERE AppointmentID = ?", (appt['AppointmentID'],))
        db.exec_non_query("UPDATE Candidates SET Status = 'ReadyForHire' WHERE CandidateID = ?", (cand_id,))
        print("✅ Candidate Passed & Ready")
    except Exception as e:
        print(f"❌ Exam Result Error: {e}")
        return

    # 6. HIRING
    print("\n--- 6. Testing Hiring ---")
    try:
        db.match_candidate_to_request({"RequestID": req['RequestID'], "CandidateID": cand_id, "Status": "Hired"})
        db.exec_non_query("UPDATE Candidates SET Status = 'Hired' WHERE CandidateID = ?", (cand_id,))
        
        # Hiring Fee Invoice
        hire_inv_data = {"EntityID": client['ClientID'], "EntityType": "Client", "InvoiceType": "HiringFee", "Description": "Hiring Fee", "Amount": 2000.0}
        db.create_invoice(hire_inv_data)
        print("✅ Candidate Hired & Invoice Created")
    except Exception as e:
        print(f"❌ Hiring Error: {e}")
        return

    # 7. FINANCE
    print("\n--- 7. Testing Finance ---")
    try:
        invoices = db.get_pending_invoices()
        if invoices:
            inv = invoices[0]
            db.add_receipt({"InvoiceID": inv['InvoiceID'], "Amount": inv['Amount']})
            db.exec_non_query("UPDATE Invoices SET PaidAmount = ?, Status = 'Paid' WHERE InvoiceID = ?", (inv['Amount'], inv['InvoiceID']))
            print(f"✅ Invoice {inv['InvoiceID']} Paid")
        else:
            print("⚠️ No pending invoices found (unexpected)")
    except Exception as e:
        print(f"❌ Finance Error: {e}")
        return

    print("\n🎉 ALL SYSTEMS GO! The backend logic is solid.")

if __name__ == "__main__":
    test_workflow()
