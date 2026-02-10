import pandas as pd
import os

def analyze_booking_sheet():
    file_path = 'Booking sheet.xlsx'
    if not os.path.exists(file_path):
        print("File not found.")
        return

    try:
        df = pd.read_excel(file_path)
        
        # 1. Users (Recruiters, Interviewers, Closers)
        recruiters = df['Recruiter'].dropna().unique().tolist()
        interviewers = df['Interviewer'].dropna().unique().tolist()
        closers = df['Closer'].dropna().unique().tolist()
        
        all_staff = set(recruiters + interviewers + closers)
        
        print("\n--- 👥 STAFF FOUND (To be created as Users) ---")
        for staff in sorted(all_staff):
            roles = []
            if staff in recruiters: roles.append("Recruiter")
            if staff in interviewers: roles.append("Interviewer")
            if staff in closers: roles.append("Sales")
            print(f"- {staff} ({', '.join(roles)})")
            
        # 2. Companies (Clients)
        companies = df['Closing Account'].dropna().unique().tolist()
        companies += df['Company'].dropna().unique().tolist()
        unique_companies = sorted(list(set(companies)))
        
        print("\n--- 🏢 COMPANIES FOUND (To be created as Clients) ---")
        for comp in unique_companies:
            print(f"- {comp}")
            
        # 3. Candidates Stats
        print("\n--- 👤 CANDIDATES STATS ---")
        print(f"Total Rows: {len(df)}")
        print(f"Unique Phone Numbers: {df['PriNumber'].nunique()}")
        print(f"Unique Emails: {df['Email'].nunique()}")
        
        # 4. Statuses
        print("\n--- 📊 STATUSES FOUND ---")
        print(df['Status'].value_counts().head(10).to_string())

    except Exception as e:
        print(f"Error analysis: {e}")

if __name__ == "__main__":
    analyze_booking_sheet()
