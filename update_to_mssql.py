import os

target_dir = r"E:\Place _trae"
schema_path = os.path.join(target_dir, "schema_mssql.sql")
app_path = os.path.join(target_dir, "app.py")

schema_content = r"""-- Place 2026 Database Schema for SQL Server

-- Users Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
BEGIN
    CREATE TABLE Users (
        UserID INT IDENTITY(1,1) PRIMARY KEY,
        Username NVARCHAR(50) NOT NULL UNIQUE,
        Password NVARCHAR(100) NOT NULL,
        Role NVARCHAR(50) NOT NULL
    );
    
    INSERT INTO Users (Username, Password, Role) VALUES 
    ('manager', 'manager123', 'Manager'),
    ('sales', 'sales123', 'Sales'),
    ('corporate', 'corp123', 'Corporate'),
    ('trainer', 'trainer123', 'Trainer');
END
GO

-- Clients Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Clients' AND xtype='U')
BEGIN
    CREATE TABLE Clients (
        ClientID INT IDENTITY(1,1) PRIMARY KEY,
        CompanyName NVARCHAR(100) NOT NULL,
        Industry NVARCHAR(100),
        ContactPerson NVARCHAR(100),
        Email NVARCHAR(100),
        Phone NVARCHAR(50),
        Address NVARCHAR(MAX)
    );
END
GO

-- ClientRequests Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ClientRequests' AND xtype='U')
BEGIN
    CREATE TABLE ClientRequests (
        RequestID INT IDENTITY(1,1) PRIMARY KEY,
        ClientID INT FOREIGN KEY REFERENCES Clients(ClientID),
        JobTitle NVARCHAR(100) NOT NULL,
        Requirements NVARCHAR(MAX),
        NeededCount INT DEFAULT 1,
        Status NVARCHAR(50) DEFAULT 'Open'
    );
END
GO

-- Campaigns Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Campaigns' AND xtype='U')
BEGIN
    CREATE TABLE Campaigns (
        CampaignID INT IDENTITY(1,1) PRIMARY KEY,
        RequestID INT FOREIGN KEY REFERENCES ClientRequests(RequestID),
        MediaChannel NVARCHAR(100),
        AdText NVARCHAR(MAX),
        TargetAudience NVARCHAR(MAX),
        Budget DECIMAL(18, 2),
        StartDate DATE,
        EndDate DATE
    );
END
GO

-- Candidates Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Candidates' AND xtype='U')
BEGIN
    CREATE TABLE Candidates (
        CandidateID INT IDENTITY(1,1) PRIMARY KEY,
        FullName NVARCHAR(100) NOT NULL,
        Email NVARCHAR(100),
        Phone NVARCHAR(50),
        Status NVARCHAR(50) DEFAULT 'Lead',
        Source NVARCHAR(100)
    );
END
GO

-- Exams Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Exams' AND xtype='U')
BEGIN
    CREATE TABLE Exams (
        ExamID INT IDENTITY(1,1) PRIMARY KEY,
        ExamName NVARCHAR(100) NOT NULL,
        Type NVARCHAR(50),
        Description NVARCHAR(MAX),
        Cost DECIMAL(18, 2)
    );
END
GO

-- ExamSessions Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ExamSessions' AND xtype='U')
BEGIN
    CREATE TABLE ExamSessions (
        SessionID INT IDENTITY(1,1) PRIMARY KEY,
        ExamID INT FOREIGN KEY REFERENCES Exams(ExamID),
        SessionDate DATETIME,
        MaxCapacity INT,
        Location NVARCHAR(100)
    );
END
GO

-- Invoices Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Invoices' AND xtype='U')
BEGIN
    CREATE TABLE Invoices (
        InvoiceID INT IDENTITY(1,1) PRIMARY KEY,
        CandidateID INT FOREIGN KEY REFERENCES Candidates(CandidateID),
        Amount DECIMAL(18, 2),
        IssueDate DATE DEFAULT GETDATE(),
        Status NVARCHAR(50) DEFAULT 'Unpaid'
    );
END
GO
"""

app_content = r"""from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import pyodbc
import functools
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key_place_2026'

# --- SQL SERVER CONFIGURATION ---
# Change these values to match your SQL Server environment
SERVER = 'localhost' 
DATABASE = 'Place2026DB'
# For Windows Authentication (Trusted Connection):
CONNECTION_STRING = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
# For SQL Server Authentication (User/Password):
# USERNAME = 'sa'
# PASSWORD = 'your_password'
# CONNECTION_STRING = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'

def get_db():
    if 'db' not in g:
        try:
            g.db = pyodbc.connect(CONNECTION_STRING)
        except Exception as e:
            # Fallback for development if SQL Server is not reachable, purely to avoid instant crash
            # But in production this should fail hard.
            print(f"Connection Error: {e}")
            g.db = None
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Helper to execute queries and return list of dictionaries
def query_db(query, args=(), one=False):
    db = get_db()
    if db is None:
        return None
    cursor = db.cursor()
    try:
        cursor.execute(query, args)
        if cursor.description: # If query returns rows (SELECT)
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            cursor.close()
            return (results[0] if results else None) if one else results
        else: # INSERT, UPDATE, DELETE
            db.commit()
            cursor.close()
            return None
    except Exception as e:
        print(f"Query Error: {e}")
        cursor.close()
        raise e

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

def role_required(allowed_roles):
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                return redirect(url_for('login'))
            if g.user['Role'] not in allowed_roles and 'Manager' not in g.user['Role']:
                flash('غير مصرح لك بالدخول لهذه الصفحة', 'danger')
                return redirect(url_for('dashboard'))
            return view(**kwargs)
        return wrapped_view
    return decorator

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        # Note: query_db returns dict, so g.user is a dict
        g.user = query_db('SELECT * FROM Users WHERE UserID = ?', (user_id,), one=True)

# --- Auth Routes ---
@app.route('/', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        
        user = query_db('SELECT * FROM Users WHERE Username = ?', (username,), one=True)

        if user is None:
            error = 'اسم المستخدم غير صحيح.'
        elif user['Password'] != password:
            error = 'كلمة المرور غير صحيحة.'

        if error is None:
            session.clear()
            session['user_id'] = user['UserID']
            return redirect(url_for('dashboard'))

        flash(error, 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# --- Corporate Routes ---
@app.route('/corporate')
@login_required
@role_required(['Corporate', 'Manager'])
def corporate_index():
    clients = query_db('SELECT * FROM Clients')
    requests = query_db('''
        SELECT CR.*, C.CompanyName 
        FROM ClientRequests CR 
        JOIN Clients C ON CR.ClientID = C.ClientID
    ''') or []
    return render_template('corporate/index.html', clients=clients or [], requests=requests)

@app.route('/corporate/add_client', methods=('POST',))
@login_required
@role_required(['Corporate', 'Manager'])
def add_client():
    if request.method == 'POST':
        company_name = request.form['company_name']
        industry = request.form['industry']
        contact_person = request.form['contact_person']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        try:
            query_db(
                'INSERT INTO Clients (CompanyName, Industry, ContactPerson, Email, Phone, Address) VALUES (?, ?, ?, ?, ?, ?)',
                (company_name, industry, contact_person, email, phone, address)
            )
            flash('تم إضافة العميل بنجاح', 'success')
        except Exception as e:
            flash(f'حدث خطأ: {e}', 'danger')
            
    return redirect(url_for('corporate_index'))

@app.route('/corporate/add_request', methods=('POST',))
@login_required
@role_required(['Corporate', 'Manager'])
def add_request():
    if request.method == 'POST':
        client_id = request.form['client_id']
        job_title = request.form['job_title']
        requirements = request.form['requirements']
        needed_count = request.form['needed_count']
        
        try:
            query_db(
                'INSERT INTO ClientRequests (ClientID, JobTitle, Requirements, NeededCount, Status) VALUES (?, ?, ?, ?, ?)',
                (client_id, job_title, requirements, needed_count, 'Open')
            )
            flash('تم إضافة الطلب بنجاح', 'success')
        except Exception as e:
            flash(f'حدث خطأ: {e}', 'danger')
            
    return redirect(url_for('corporate_index'))

# --- Sales Routes ---
@app.route('/sales')
@login_required
@role_required(['Sales', 'Manager'])
def sales_index():
    campaigns = query_db('''
        SELECT Cmp.*, CR.JobTitle, C.CompanyName
        FROM Campaigns Cmp
        LEFT JOIN ClientRequests CR ON Cmp.RequestID = CR.RequestID
        LEFT JOIN Clients C ON CR.ClientID = C.ClientID
    ''')
    
    active_requests = query_db('''
        SELECT CR.RequestID, CR.JobTitle, C.CompanyName 
        FROM ClientRequests CR 
        JOIN Clients C ON CR.ClientID = C.ClientID 
        WHERE CR.Status = 'Open'
    ''')

    leads = query_db('SELECT * FROM Candidates')
    
    return render_template('sales/index.html', campaigns=campaigns or [], active_requests=active_requests or [], leads=leads or [])

@app.route('/sales/add_campaign', methods=('POST',))
@login_required
@role_required(['Sales', 'Manager'])
def add_campaign():
    if request.method == 'POST':
        request_id = request.form['request_id']
        media_channel = request.form['media_channel']
        ad_text = request.form['ad_text']
        target_audience = request.form['target_audience']
        budget = request.form['budget']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        try:
            query_db(
                'INSERT INTO Campaigns (RequestID, MediaChannel, AdText, TargetAudience, Budget, StartDate, EndDate) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (request_id, media_channel, ad_text, target_audience, budget, start_date, end_date)
            )
            flash('تم إضافة الحملة بنجاح', 'success')
        except Exception as e:
            flash(f'حدث خطأ: {e}', 'danger')
            
    return redirect(url_for('sales_index'))

@app.route('/sales/add_lead', methods=('POST',))
@login_required
@role_required(['Sales', 'Manager'])
def add_lead():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        source = request.form['source']
        
        try:
            query_db(
                'INSERT INTO Candidates (FullName, Email, Phone, Status) VALUES (?, ?, ?, ?)',
                (full_name, email, phone, 'Lead')
            )
            flash('تم إضافة المرشح (Lead) بنجاح', 'success')
        except Exception as e:
            flash(f'حدث خطأ: {e}', 'danger')

    return redirect(url_for('sales_index'))

# --- Training Routes ---
@app.route('/training')
@login_required
@role_required(['Trainer', 'Manager'])
def training_index():
    exams = query_db('SELECT * FROM Exams')
    sessions = query_db('SELECT * FROM ExamSessions')
    return render_template('training/index.html', exams=exams or [], sessions=sessions or [])

@app.route('/training/add_exam', methods=('POST',))
@login_required
@role_required(['Trainer', 'Manager'])
def add_exam():
    if request.method == 'POST':
        exam_name = request.form['exam_name']
        exam_type = request.form['exam_type']
        description = request.form['description']
        cost = request.form['cost']
        
        try:
            query_db(
                'INSERT INTO Exams (ExamName, Type, Description, Cost) VALUES (?, ?, ?, ?)',
                (exam_name, exam_type, description, cost)
            )
            flash('تم إضافة الاختبار بنجاح', 'success')
        except Exception as e:
            flash(f'حدث خطأ: {e}', 'danger')
            
    return redirect(url_for('training_index'))

# --- Finance Routes ---
@app.route('/finance')
@login_required
@role_required(['Manager'])
def finance_index():
    invoices = query_db('''
        SELECT I.*, C.FullName 
        FROM Invoices I 
        LEFT JOIN Candidates C ON I.CandidateID = C.CandidateID
    ''')
    return render_template('finance/index.html', invoices=invoices or [])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""

try:
    with open(schema_path, 'w', encoding='utf-8') as f:
        f.write(schema_content)
    print(f"Written: {schema_path}")
    
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(app_content)
    print(f"Written: {app_path}")
except Exception as e:
    print(f"Error: {e}")
