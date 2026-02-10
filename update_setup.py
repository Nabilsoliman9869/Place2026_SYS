import os

target_dir = r"E:\Place _trae"
setup_template_path = os.path.join(target_dir, "templates", "setup.html")
config_path = os.path.join(target_dir, "db_config.json")
app_path = os.path.join(target_dir, "app.py")

setup_html = r"""<!doctype html>
<html lang="ar" dir="rtl">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>إعدادات الاتصال بالسيرفر - Place 2026</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css">
  </head>
  <body class="bg-dark d-flex align-items-center justify-content-center" style="height: 100vh;">
    <div class="card shadow p-4" style="width: 500px;">
      <h3 class="text-center mb-4 text-primary">⚙️ إعدادات السيرفر (للمطورين)</h3>
      
      {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
          {% endif %}
      {% endwith %}

      <form method="post">
        <div class="mb-3">
          <label class="form-label fw-bold">اسم السيرفر / IP</label>
          <input type="text" name="server" class="form-control" value="{{ config.server }}" required>
          <small class="text-muted">مثال: . أو localhost أو IP Address</small>
        </div>
        
        <div class="mb-3">
          <label class="form-label fw-bold">المنفذ (Port)</label>
          <input type="text" name="port" class="form-control" value="{{ config.port }}" required>
          <small class="text-muted">الافتراضي: 1433 (لديك: 1477)</small>
        </div>

        <div class="mb-3">
          <label class="form-label fw-bold">اسم قاعدة البيانات</label>
          <input type="text" name="database" class="form-control" value="{{ config.database }}" required>
        </div>

        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label fw-bold">اسم المستخدم (User)</label>
                <input type="text" name="username" class="form-control" value="{{ config.username }}" required>
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label fw-bold">كلمة المرور (Password)</label>
                <input type="password" name="password" class="form-control" value="{{ config.password }}" required>
            </div>
        </div>

        <div class="d-grid gap-2">
            <button type="submit" class="btn btn-primary">حفظ الإعدادات والاتصال</button>
            <a href="{{ url_for('login') }}" class="btn btn-outline-secondary">عودة لتسجيل الدخول</a>
        </div>
      </form>
    </div>
  </body>
</html>
"""

config_json = r"""{
    "server": ".",
    "port": "1477",
    "database": "Place2026DB",
    "username": "sa",
    "password": "123"
}
"""

app_code = r"""from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import pyodbc
import functools
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key_place_2026'

CONFIG_FILE = 'db_config.json'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {
            "server": ".",
            "port": "1433",
            "database": "Place2026DB",
            "username": "sa",
            "password": ""
        }
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_config_file(config_data):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_db_connection_string():
    config = load_config()
    server = config.get('server', '.')
    port = config.get('port', '1433')
    database = config.get('database', 'Place2026DB')
    username = config.get('username', 'sa')
    password = config.get('password', '')
    
    # SQL Server Connection String
    return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}'

def get_db():
    if 'db' not in g:
        try:
            conn_str = get_db_connection_string()
            g.db = pyodbc.connect(conn_str, timeout=5)
        except Exception as e:
            g.db_error = str(e)
            g.db = None
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Helper to execute queries
def query_db(query, args=(), one=False):
    db = get_db()
    if db is None:
        return None
        
    cursor = db.cursor()
    try:
        cursor.execute(query, args)
        if cursor.description:
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            cursor.close()
            return (results[0] if results else None) if one else results
        else:
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
    # Check DB connection first
    db = get_db()
    
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        try:
            g.user = query_db('SELECT * FROM Users WHERE UserID = ?', (user_id,), one=True)
        except:
            g.user = None

# --- Setup Route (Developer Only) ---
@app.route('/setup', methods=('GET', 'POST'))
def setup():
    if request.method == 'POST':
        new_config = {
            "server": request.form['server'],
            "port": request.form['port'],
            "database": request.form['database'],
            "username": request.form['username'],
            "password": request.form['password']
        }
        if save_config_file(new_config):
            flash('تم حفظ الإعدادات بنجاح. جاري محاولة الاتصال...', 'success')
            # Try to connect to verify
            try:
                # Force reload of connection
                if 'db' in g:
                    g.pop('db').close()
                get_db()
                if g.db:
                    flash('تم الاتصال بقاعدة البيانات بنجاح!', 'success')
                    return redirect(url_for('login'))
                else:
                    flash(f'فشل الاتصال: {g.db_error}', 'danger')
            except Exception as e:
                flash(f'خطأ أثناء الاختبار: {e}', 'danger')
        else:
            flash('فشل حفظ ملف الإعدادات', 'danger')
    
    current_config = load_config()
    return render_template('setup.html', config=current_config)

# --- Auth Routes ---
@app.route('/', methods=('GET', 'POST'))
def login():
    # If DB is down, redirect to setup
    if get_db() is None:
        flash(f'خطأ في الاتصال بقاعدة البيانات. يرجى مراجعة الإعدادات. ({getattr(g, "db_error", "Unknown")})', 'danger')
        return redirect(url_for('setup'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        
        try:
            user = query_db('SELECT * FROM Users WHERE Username = ?', (username,), one=True)
        except Exception as e:
             flash(f"خطأ في الاستعلام: {e}", "danger")
             return render_template('login.html')

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
    with open(setup_template_path, 'w', encoding='utf-8') as f:
        f.write(setup_html)
    print(f"Written: {setup_template_path}")
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_json)
    print(f"Written: {config_path}")
    
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(app_code)
    print(f"Written: {app_path}")
except Exception as e:
    print(f"Error: {e}")
