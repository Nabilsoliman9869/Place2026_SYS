import os

base_dir = r"E:\Place _trae"
templates_dir = os.path.join(base_dir, "templates")
corporate_dir = os.path.join(templates_dir, "corporate")
sales_dir = os.path.join(templates_dir, "sales")
training_dir = os.path.join(templates_dir, "training")
finance_dir = os.path.join(templates_dir, "finance")

os.makedirs(corporate_dir, exist_ok=True)
os.makedirs(sales_dir, exist_ok=True)
os.makedirs(training_dir, exist_ok=True)
os.makedirs(finance_dir, exist_ok=True)

files = {
    os.path.join(base_dir, "app.py"): r"""from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import sqlite3
import functools
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key_place_2026'
DATABASE = 'place_2026.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

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
        g.user = get_db().execute('SELECT * FROM Users WHERE UserID = ?', (user_id,)).fetchone()

# --- Auth Routes ---
@app.route('/', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM Users WHERE Username = ?', (username,)
        ).fetchone()

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
    db = get_db()
    clients = db.execute('SELECT * FROM Clients').fetchall()
    requests = db.execute('''
        SELECT CR.*, C.CompanyName 
        FROM ClientRequests CR 
        JOIN Clients C ON CR.ClientID = C.ClientID
    ''').fetchall()
    return render_template('corporate/index.html', clients=clients, requests=requests)

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
        
        db = get_db()
        try:
            db.execute(
                'INSERT INTO Clients (CompanyName, Industry, ContactPerson, Email, Phone, Address) VALUES (?, ?, ?, ?, ?, ?)',
                (company_name, industry, contact_person, email, phone, address)
            )
            db.commit()
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
        
        db = get_db()
        try:
            db.execute(
                'INSERT INTO ClientRequests (ClientID, JobTitle, Requirements, NeededCount, Status) VALUES (?, ?, ?, ?, ?)',
                (client_id, job_title, requirements, needed_count, 'Open')
            )
            db.commit()
            flash('تم إضافة الطلب بنجاح', 'success')
        except Exception as e:
            flash(f'حدث خطأ: {e}', 'danger')
            
    return redirect(url_for('corporate_index'))

# --- Sales Routes ---
@app.route('/sales')
@login_required
@role_required(['Sales', 'Manager'])
def sales_index():
    db = get_db()
    campaigns = db.execute('''
        SELECT Cmp.*, CR.JobTitle, C.CompanyName
        FROM Campaigns Cmp
        LEFT JOIN ClientRequests CR ON Cmp.RequestID = CR.RequestID
        LEFT JOIN Clients C ON CR.ClientID = C.ClientID
    ''').fetchall()
    
    # Fetch active requests for the dropdown
    active_requests = db.execute('''
        SELECT CR.RequestID, CR.JobTitle, C.CompanyName 
        FROM ClientRequests CR 
        JOIN Clients C ON CR.ClientID = C.ClientID 
        WHERE CR.Status = "Open"
    ''').fetchall()

    leads = db.execute('SELECT * FROM Candidates').fetchall() # Assuming leads are candidates for now
    
    return render_template('sales/index.html', campaigns=campaigns, active_requests=active_requests, leads=leads)

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
        
        db = get_db()
        try:
            db.execute(
                'INSERT INTO Campaigns (RequestID, MediaChannel, AdText, TargetAudience, Budget, StartDate, EndDate) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (request_id, media_channel, ad_text, target_audience, budget, start_date, end_date)
            )
            db.commit()
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
        source = request.form['source'] # Could be linked to CampaignID
        
        db = get_db()
        try:
            db.execute(
                'INSERT INTO Candidates (FullName, Email, Phone, Status) VALUES (?, ?, ?, ?)',
                (full_name, email, phone, 'Lead') # Initial status
            )
            db.commit()
            flash('تم إضافة المرشح (Lead) بنجاح', 'success')
        except Exception as e:
            flash(f'حدث خطأ: {e}', 'danger')

    return redirect(url_for('sales_index'))

# --- Training Routes ---
@app.route('/training')
@login_required
@role_required(['Trainer', 'Manager'])
def training_index():
    db = get_db()
    exams = db.execute('SELECT * FROM Exams').fetchall()
    sessions = db.execute('SELECT * FROM ExamSessions').fetchall()
    return render_template('training/index.html', exams=exams, sessions=sessions)

@app.route('/training/add_exam', methods=('POST',))
@login_required
@role_required(['Trainer', 'Manager'])
def add_exam():
    if request.method == 'POST':
        exam_name = request.form['exam_name']
        exam_type = request.form['exam_type']
        description = request.form['description']
        cost = request.form['cost']
        
        db = get_db()
        try:
            db.execute(
                'INSERT INTO Exams (ExamName, Type, Description, Cost) VALUES (?, ?, ?, ?)',
                (exam_name, exam_type, description, cost)
            )
            db.commit()
            flash('تم إضافة الاختبار بنجاح', 'success')
        except Exception as e:
            flash(f'حدث خطأ: {e}', 'danger')
            
    return redirect(url_for('training_index'))

# --- Finance Routes ---
@app.route('/finance')
@login_required
@role_required(['Manager']) # Assuming Manager handles finance for now
def finance_index():
    db = get_db()
    invoices = db.execute('''
        SELECT I.*, C.FullName 
        FROM Invoices I 
        LEFT JOIN Candidates C ON I.CandidateID = C.CandidateID
    ''').fetchall()
    return render_template('finance/index.html', invoices=invoices)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
""",
    os.path.join(templates_dir, "base.html"): r"""<!doctype html>
<html lang="ar" dir="rtl">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Place 2026 - نظام إدارة التدريب</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
      body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f8f9fa;
      }
      .sidebar {
        min-height: 100vh;
        background-color: #343a40;
        color: white;
      }
      .sidebar a {
        color: white;
        text-decoration: none;
        display: block;
        padding: 10px 15px;
      }
      .sidebar a:hover {
        background-color: #495057;
      }
      .content {
        padding: 20px;
      }
    </style>
  </head>
  <body>
    <div class="d-flex">
      <div class="sidebar p-3" style="width: 250px;">
        <h4>Place 2026</h4>
        <hr>
        <ul class="nav flex-column">
          <li class="nav-item">
            <a href="{{ url_for('dashboard') }}"><i class="fas fa-home"></i> الرئيسية</a>
          </li>
          {% if g.user and (g.user['Role'] == 'Manager' or g.user['Role'] == 'Corporate') %}
          <li class="nav-item">
            <a href="{{ url_for('corporate_index') }}"><i class="fas fa-building"></i> خدمة الشركات</a>
          </li>
          {% endif %}
          {% if g.user and (g.user['Role'] == 'Manager' or g.user['Role'] == 'Sales') %}
          <li class="nav-item">
            <a href="{{ url_for('sales_index') }}"><i class="fas fa-bullhorn"></i> المبيعات</a>
          </li>
          {% endif %}
          {% if g.user and (g.user['Role'] == 'Manager' or g.user['Role'] == 'Trainer') %}
          <li class="nav-item">
            <a href="{{ url_for('training_index') }}"><i class="fas fa-chalkboard-teacher"></i> التدريب</a>
          </li>
          {% endif %}
          {% if g.user and g.user['Role'] == 'Manager' %}
          <li class="nav-item">
            <a href="{{ url_for('finance_index') }}"><i class="fas fa-file-invoice-dollar"></i> الحسابات</a>
          </li>
          {% endif %}
          <li class="nav-item">
            <a href="{{ url_for('logout') }}" class="text-danger"><i class="fas fa-sign-out-alt"></i> تسجيل الخروج</a>
          </li>
        </ul>
      </div>
      <div class="flex-grow-1 content">
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
      </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
""",
    os.path.join(templates_dir, "login.html"): r"""<!doctype html>
<html lang="ar" dir="rtl">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>تسجيل الدخول - Place 2026</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css">
  </head>
  <body class="bg-light d-flex align-items-center justify-content-center" style="height: 100vh;">
    <div class="card shadow p-4" style="width: 400px;">
      <h3 class="text-center mb-4">تسجيل الدخول</h3>
      {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
          {% endif %}
      {% endwith %}
      <form method="post">
        <div class="mb-3">
          <label class="form-label">اسم المستخدم</label>
          <input type="text" name="username" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label">كلمة المرور</label>
          <input type="password" name="password" class="form-control" required>
        </div>
        <button type="submit" class="btn btn-primary w-100">دخول</button>
      </form>
    </div>
  </body>
</html>
""",
    os.path.join(templates_dir, "dashboard.html"): r"""{% extends 'base.html' %}

{% block content %}
<h2>لوحة التحكم</h2>
<p>مرحباً بك، {{ g.user['Username'] }} ({{ g.user['Role'] }})</p>
<div class="row mt-4">
    <div class="col-md-3">
        <div class="card text-white bg-primary mb-3">
            <div class="card-header">خدمة الشركات</div>
            <div class="card-body">
                <h5 class="card-title">إدارة العملاء والطلبات</h5>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-success mb-3">
            <div class="card-header">المبيعات</div>
            <div class="card-body">
                <h5 class="card-title">إدارة الحملات والعملاء المحتملين</h5>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-warning mb-3">
            <div class="card-header">التدريب</div>
            <div class="card-body">
                <h5 class="card-title">إدارة الامتحانات والدورات</h5>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-danger mb-3">
            <div class="card-header">الحسابات</div>
            <div class="card-body">
                <h5 class="card-title">الفواتير والتحصيل</h5>
            </div>
        </div>
    </div>
</div>
{% endblock %}
""",
    os.path.join(corporate_dir, "index.html"): r"""{% extends 'base.html' %}

{% block content %}
<h2>خدمة الشركات</h2>

<ul class="nav nav-tabs" id="myTab" role="tablist">
  <li class="nav-item" role="presentation">
    <button class="nav-link active" id="clients-tab" data-bs-toggle="tab" data-bs-target="#clients" type="button" role="tab">العملاء</button>
  </li>
  <li class="nav-item" role="presentation">
    <button class="nav-link" id="requests-tab" data-bs-toggle="tab" data-bs-target="#requests" type="button" role="tab">الطلبات</button>
  </li>
</ul>
<div class="tab-content p-3 border border-top-0 rounded-bottom" id="myTabContent">
  <!-- Clients Tab -->
  <div class="tab-pane fade show active" id="clients" role="tabpanel">
    <button class="btn btn-success mb-3" data-bs-toggle="modal" data-bs-target="#addClientModal">
        <i class="fas fa-plus"></i> إضافة عميل جديد
    </button>
    <table class="table table-striped">
        <thead>
            <tr>
                <th>ID</th>
                <th>اسم الشركة</th>
                <th>الصناعة</th>
                <th>الشخص المسؤول</th>
                <th>الهاتف</th>
                <th>البريد</th>
            </tr>
        </thead>
        <tbody>
            {% for client in clients %}
            <tr>
                <td>{{ client.ClientID }}</td>
                <td>{{ client.CompanyName }}</td>
                <td>{{ client.Industry }}</td>
                <td>{{ client.ContactPerson }}</td>
                <td>{{ client.Phone }}</td>
                <td>{{ client.Email }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
  </div>
  
  <!-- Requests Tab -->
  <div class="tab-pane fade" id="requests" role="tabpanel">
    <button class="btn btn-success mb-3" data-bs-toggle="modal" data-bs-target="#addRequestModal">
        <i class="fas fa-plus"></i> إضافة طلب جديد
    </button>
    <table class="table table-striped">
        <thead>
            <tr>
                <th>ID</th>
                <th>الشركة</th>
                <th>المسمى الوظيفي</th>
                <th>المتطلبات</th>
                <th>العدد المطلوب</th>
                <th>الحالة</th>
            </tr>
        </thead>
        <tbody>
            {% for req in requests %}
            <tr>
                <td>{{ req.RequestID }}</td>
                <td>{{ req.CompanyName }}</td>
                <td>{{ req.JobTitle }}</td>
                <td>{{ req.Requirements }}</td>
                <td>{{ req.NeededCount }}</td>
                <td>{{ req.Status }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
  </div>
</div>

<!-- Add Client Modal -->
<div class="modal fade" id="addClientModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">إضافة عميل جديد</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <form action="{{ url_for('add_client') }}" method="POST">
      <div class="modal-body">
          <div class="mb-3">
              <label>اسم الشركة</label>
              <input type="text" name="company_name" class="form-control" required>
          </div>
          <div class="mb-3">
              <label>الصناعة / المجال</label>
              <input type="text" name="industry" class="form-control">
          </div>
          <div class="mb-3">
              <label>الشخص المسؤول</label>
              <input type="text" name="contact_person" class="form-control" required>
          </div>
          <div class="mb-3">
              <label>البريد الإلكتروني</label>
              <input type="email" name="email" class="form-control">
          </div>
          <div class="mb-3">
              <label>الهاتف</label>
              <input type="text" name="phone" class="form-control">
          </div>
          <div class="mb-3">
              <label>العنوان</label>
              <textarea name="address" class="form-control"></textarea>
          </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
        <button type="submit" class="btn btn-primary">حفظ</button>
      </div>
      </form>
    </div>
  </div>
</div>

<!-- Add Request Modal -->
<div class="modal fade" id="addRequestModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">إضافة طلب توظيف</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <form action="{{ url_for('add_request') }}" method="POST">
      <div class="modal-body">
          <div class="mb-3">
              <label>العميل</label>
              <select name="client_id" class="form-select" required>
                  {% for client in clients %}
                  <option value="{{ client.ClientID }}">{{ client.CompanyName }}</option>
                  {% endfor %}
              </select>
          </div>
          <div class="mb-3">
              <label>المسمى الوظيفي</label>
              <input type="text" name="job_title" class="form-control" required>
          </div>
          <div class="mb-3">
              <label>المتطلبات</label>
              <textarea name="requirements" class="form-control"></textarea>
          </div>
          <div class="mb-3">
              <label>العدد المطلوب</label>
              <input type="number" name="needed_count" class="form-control" value="1">
          </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
        <button type="submit" class="btn btn-primary">حفظ</button>
      </div>
      </form>
    </div>
  </div>
</div>
{% endblock %}
""",
    os.path.join(sales_dir, "index.html"): r"""{% extends 'base.html' %}

{% block content %}
<h2>المبيعات</h2>

<ul class="nav nav-tabs" id="salesTab" role="tablist">
  <li class="nav-item">
    <button class="nav-link active" id="campaigns-tab" data-bs-toggle="tab" data-bs-target="#campaigns" type="button">الحملات الإعلانية</button>
  </li>
  <li class="nav-item">
    <button class="nav-link" id="leads-tab" data-bs-toggle="tab" data-bs-target="#leads" type="button">العملاء المحتملين (Leads)</button>
  </li>
</ul>
<div class="tab-content p-3 border border-top-0 rounded-bottom">
  <!-- Campaigns Tab -->
  <div class="tab-pane fade show active" id="campaigns">
    <button class="btn btn-success mb-3" data-bs-toggle="modal" data-bs-target="#addCampaignModal">
        <i class="fas fa-plus"></i> إضافة حملة
    </button>
    <table class="table table-striped">
        <thead>
            <tr>
                <th>ID</th>
                <th>الطلب المرتبط</th>
                <th>القناة</th>
                <th>الجمهور المستهدف</th>
                <th>الميزانية</th>
                <th>من - إلى</th>
            </tr>
        </thead>
        <tbody>
            {% for cmp in campaigns %}
            <tr>
                <td>{{ cmp.CampaignID }}</td>
                <td>{{ cmp.CompanyName }} - {{ cmp.JobTitle }}</td>
                <td>{{ cmp.MediaChannel }}</td>
                <td>{{ cmp.TargetAudience }}</td>
                <td>{{ cmp.Budget }}</td>
                <td>{{ cmp.StartDate }} / {{ cmp.EndDate }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
  </div>

  <!-- Leads Tab -->
  <div class="tab-pane fade" id="leads">
    <button class="btn btn-success mb-3" data-bs-toggle="modal" data-bs-target="#addLeadModal">
        <i class="fas fa-plus"></i> إضافة عميل محتمل
    </button>
    <table class="table table-striped">
        <thead>
            <tr>
                <th>ID</th>
                <th>الاسم</th>
                <th>الايميل</th>
                <th>الهاتف</th>
                <th>الحالة</th>
            </tr>
        </thead>
        <tbody>
            {% for lead in leads %}
            <tr>
                <td>{{ lead.CandidateID }}</td>
                <td>{{ lead.FullName }}</td>
                <td>{{ lead.Email }}</td>
                <td>{{ lead.Phone }}</td>
                <td>{{ lead.Status }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
  </div>
</div>

<!-- Add Campaign Modal -->
<div class="modal fade" id="addCampaignModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">إضافة حملة إعلانية</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <form action="{{ url_for('add_campaign') }}" method="POST">
      <div class="modal-body">
          <div class="mb-3">
              <label>الطلب المرتبط</label>
              <select name="request_id" class="form-select" required>
                  {% for req in active_requests %}
                  <option value="{{ req.RequestID }}">{{ req.CompanyName }} - {{ req.JobTitle }}</option>
                  {% endfor %}
              </select>
          </div>
          <div class="mb-3">
              <label>القناة الإعلانية</label>
              <input type="text" name="media_channel" class="form-control" placeholder="مثال: Facebook, LinkedIn">
          </div>
          <div class="mb-3">
              <label>نص الإعلان</label>
              <textarea name="ad_text" class="form-control"></textarea>
          </div>
          <div class="mb-3">
              <label>الجمهور المستهدف</label>
              <input type="text" name="target_audience" class="form-control">
          </div>
          <div class="mb-3">
              <label>الميزانية</label>
              <input type="number" step="0.01" name="budget" class="form-control">
          </div>
          <div class="row">
              <div class="col">
                  <label>تاريخ البدء</label>
                  <input type="date" name="start_date" class="form-control">
              </div>
              <div class="col">
                  <label>تاريخ الانتهاء</label>
                  <input type="date" name="end_date" class="form-control">
              </div>
          </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
        <button type="submit" class="btn btn-primary">حفظ</button>
      </div>
      </form>
    </div>
  </div>
</div>

<!-- Add Lead Modal -->
<div class="modal fade" id="addLeadModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">تسجيل اهتمام / عميل محتمل</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <form action="{{ url_for('add_lead') }}" method="POST">
      <div class="modal-body">
          <div class="mb-3">
              <label>الاسم الكامل</label>
              <input type="text" name="full_name" class="form-control" required>
          </div>
          <div class="mb-3">
              <label>البريد الإلكتروني</label>
              <input type="email" name="email" class="form-control">
          </div>
          <div class="mb-3">
              <label>رقم الهاتف</label>
              <input type="text" name="phone" class="form-control">
          </div>
          <div class="mb-3">
              <label>المصدر (اختياري)</label>
              <input type="text" name="source" class="form-control" placeholder="رقم الحملة أو الموقع">
          </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
        <button type="submit" class="btn btn-primary">حفظ</button>
      </div>
      </form>
    </div>
  </div>
</div>
{% endblock %}
""",
    os.path.join(training_dir, "index.html"): r"""{% extends 'base.html' %}

{% block content %}
<h2>التدريب والامتحانات</h2>

<ul class="nav nav-tabs" id="trainingTab" role="tablist">
  <li class="nav-item">
    <button class="nav-link active" id="exams-tab" data-bs-toggle="tab" data-bs-target="#exams" type="button">الاختبارات</button>
  </li>
  <li class="nav-item">
    <button class="nav-link" id="sessions-tab" data-bs-toggle="tab" data-bs-target="#sessions" type="button">المواعيد المتاحة</button>
  </li>
</ul>
<div class="tab-content p-3 border border-top-0 rounded-bottom">
    <!-- Exams Tab -->
    <div class="tab-pane fade show active" id="exams">
        <button class="btn btn-success mb-3" data-bs-toggle="modal" data-bs-target="#addExamModal">
            <i class="fas fa-plus"></i> إضافة اختبار جديد
        </button>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>اسم الاختبار</th>
                    <th>النوع</th>
                    <th>الوصف</th>
                    <th>التكلفة</th>
                </tr>
            </thead>
            <tbody>
                {% for exam in exams %}
                <tr>
                    <td>{{ exam.ExamID }}</td>
                    <td>{{ exam.ExamName }}</td>
                    <td>{{ exam.Type }}</td>
                    <td>{{ exam.Description }}</td>
                    <td>{{ exam.Cost }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- Sessions Tab -->
    <div class="tab-pane fade" id="sessions">
        <p>قائمة المواعيد المتاحة للامتحانات (قيد التنفيذ)</p>
    </div>
</div>

<!-- Add Exam Modal -->
<div class="modal fade" id="addExamModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">إضافة اختبار جديد</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <form action="{{ url_for('add_exam') }}" method="POST">
      <div class="modal-body">
          <div class="mb-3">
              <label>اسم الاختبار</label>
              <input type="text" name="exam_name" class="form-control" required>
          </div>
          <div class="mb-3">
              <label>النوع (تحديد مستوى / نهائي)</label>
              <select name="exam_type" class="form-select">
                  <option value="Placement">تحديد مستوى</option>
                  <option value="Final">نهائي</option>
              </select>
          </div>
          <div class="mb-3">
              <label>الوصف</label>
              <textarea name="description" class="form-control"></textarea>
          </div>
          <div class="mb-3">
              <label>التكلفة</label>
              <input type="number" step="0.01" name="cost" class="form-control">
          </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
        <button type="submit" class="btn btn-primary">حفظ</button>
      </div>
      </form>
    </div>
  </div>
</div>
{% endblock %}
""",
    os.path.join(finance_dir, "index.html"): r"""{% extends 'base.html' %}

{% block content %}
<h2>الحسابات والفواتير</h2>
<table class="table table-striped">
    <thead>
        <tr>
            <th>رقم الفاتورة</th>
            <th>المرشح / العميل</th>
            <th>المبلغ</th>
            <th>التاريخ</th>
            <th>الحالة</th>
        </tr>
    </thead>
    <tbody>
        {% for inv in invoices %}
        <tr>
            <td>{{ inv.InvoiceID }}</td>
            <td>{{ inv.FullName }}</td>
            <td>{{ inv.Amount }}</td>
            <td>{{ inv.IssueDate }}</td>
            <td>{{ inv.Status }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
"""
}

for path, content in files.items():
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Written: {path}")
    except Exception as e:
        print(f"Error writing {path}: {e}")
