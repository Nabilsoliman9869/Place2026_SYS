import pandas as pd
import os

# Create 'docs' directory if it doesn't exist
if not os.path.exists('docs'):
    os.makedirs('docs')

# --- 1. Recruitment Scenario ---
recruitment_data = {
    'Step': [1, 2, 3, 4, 5, 6, 7, 8, 9],
    'Role': ['Account Manager', 'Account Manager', 'Recruitment Manager', 'Allocation Manager', 'Recruiter', 'Recruiter', 'Allocation Specialist', 'Recruitment Manager', 'Allocation Manager'],
    'Username': ['account', 'account', 'rec_mgr', 'alloc_mgr', 'recruiter', 'recruiter', 'alloc_sp', 'rec_mgr', 'alloc_mgr'],
    'Password': ['123', '123', '123', '123', '123', '123', '123', '123', '123'],
    'Menu (Window)': ['Define Client', 'Receive Job Order', 'Distribute Leads', 'Draft Campaign', 'Register Interested', 'Book Placement Test', 'Matching', 'Approve Interviews', 'Corp Invoices'],
    'Action': ['Create New Client', 'Create Request', 'Assign to Team', 'Create Ad', 'Add Candidate', 'Schedule TA', 'Match Candidate', 'Client Acceptance', 'Issue Invoice'],
    'Prerequisite (Dependency)': ['-', 'Client Exists (Step 1)', 'Open Request + Leads', 'Active Request (Step 2)', 'Active Campaign (Step 4)', 'Candidate Registered (Step 5)', 'Candidate Ready (Passed TA)', 'Match Proposed (Step 7)', 'Candidate Accepted (Step 8)'],
    'Detailed Description': [
        'Register a new corporate client (e.g., Vodafone). Enter Name, Industry, Contact Person.',
        'Receive a job order from the client (e.g., 50 German Speakers). Fill in salary, shift, language specs.',
        'Distribute available leads from the pool to Recruiters (for calling) and Allocators (for matching).',
        'Create a marketing campaign (e.g., Facebook Ad) linked to this job order to attract more candidates.',
        'Register a new candidate (e.g., Mohamed Ali) who applied via the campaign.',
        'Book a placement test (TA Assessment) for the new candidate to verify language level.',
        'Match the qualified candidate to the open job order based on skills (German B2).',
        'Record the client interview result. If accepted, the candidate status changes to "Hired".',
        'Issue an invoice to the client for the successful placement. Revenue is recorded.'
    ]
}

df_rec = pd.DataFrame(recruitment_data)
rec_file_path = os.path.join('docs', 'Recruitment_Scenario.xlsx')
df_rec.to_excel(rec_file_path, index=False)
print(f"✅ Created: {rec_file_path}")

# --- 2. Training Scenario ---
training_data = {
    'Step': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    'Role': ['Training Manager', 'Training Manager', 'Training Manager', 'Training Lead', 'Sales Agent', 'TA - Training', 'Sales/Finance', 'Coordinator', 'Trainer', 'Trainer', 'Coordinator', 'Training Lead'],
    'Username': ['train_mgr', 'train_mgr', 'train_mgr', 'train_head', 'sales', 'ta_train', 'sales', 'train_coord', 'trainer', 'trainer', 'train_coord', 'train_head'],
    'Password': ['123', '123', '123', '123', '123', '123', '123', '123', '123', '123', '123', '123'],
    'Menu (Window)': ['Engineer Programs', 'Engineer Programs', 'Engineer Programs', 'Create Wave', 'Sales Dashboard', 'Placement Tests', 'Collect Fees', 'Enroll Students', 'Daily Attendance', 'Action Plan', 'Exam Scores', 'Harvest Grads'],
    'Action': ['Add Course', 'Add Classroom', 'Add Trainer', 'Add Batch', 'Book Placement Test', 'Result Entry', 'Pay Invoice', 'Assign to Batch', 'Record Time-Grid', 'Weekly Report', 'Final Grade', 'Graduate'],
    'Prerequisite (Dependency)': ['-', '-', '-', 'Course/Room/Trainer Exist', '-', 'Test Booked', 'Candidate Exists', 'Fees Paid + Passed TA', 'Student Enrolled', 'Student Attended', 'Course Finished', 'Passed Exam'],
    'Detailed Description': [
        'Define a new course curriculum (e.g., English A1) and set its price.',
        'Register a physical classroom (e.g., Room A) and its capacity.',
        'Register a trainer profile and their hourly rate.',
        'Create a new Wave (Batch) linking Course + Trainer + Room + Dates (e.g., Wave-01).',
        'Register a new student (e.g., Ali Ahmed) and book a placement test.',
        'Enter the test result (e.g., A1). Student cannot proceed without this.',
        'Collect course fees from the student. System may block enrollment if unpaid.',
        'Enroll the eligible student into the specific Wave (Batch).',
        'Daily task: Record student attendance (In/Out time) on the Time-Grid.',
        'Weekly task: Write a performance report and action plan for the student.',
        'Enter final exam scores. System blocks this if student has outstanding dues.',
        'Final step: Change student status to "Graduate". Now ready for employment.'
    ]
}

df_train = pd.DataFrame(training_data)
train_file_path = os.path.join('docs', 'Training_Scenario.xlsx')
df_train.to_excel(train_file_path, index=False)
print(f"✅ Created: {train_file_path}")
