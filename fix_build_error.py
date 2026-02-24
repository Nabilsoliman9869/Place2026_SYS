import os

target_dir = r"E:\Place _trae"
app_path = os.path.join(target_dir, "app.py")

# Fixed app.py content to include setup_logout route and fix BuildError
app_code = r"""from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import pyodbc
import functools
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key_place_2026'

CONFIG_FILE = 'db_config.json'
SCHEMA_FILE = 'schema_mssql.sql'
DEV_USERNAME = "dev"
DEV_PASSWORD = "123"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"server": ".", "port": "1433", "database": "Place2026DB", "username": "sa", "password": ""}
    try:
        with open(CONFIG_FILE, 'r') as f: return json.load(f)
    except: return {}

def save_config_file(config_data):
    try:
        with open(CONFIG_FILE, 'w') as f: json.dump(config_data, f, indent=4)
        return True
    except: return False

def get_db_connection_string():
    config = load_config()
    return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.get("server")},{config.get("port")};DATABASE={config.get("database")};UID={config.get("username")};PWD={config.get("password")}'

def get_db():
    if 'db' not in g:
        try:
            g.db = pyodbc.connect(get_db_connection_string(), timeout=5)
        except Exception as e:
            g.db_error = str(e)
            g.db = None
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None: db.close()

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

def init_db_from_schema():
    if not os.path.exists(SCHEMA_FILE): return False, "Schema file not found"
    db = get_db()
    if db is None: return False, "DB Connection Failed"
    try:
        with open(SCHEMA_FILE, 'r') as f:
            commands = f.read().replace('\r\n', '\n').split('GO\n')
        cursor = db.cursor()
        for cmd in commands:
            if cmd.strip(): cursor.execute(cmd); db.commit()
        cursor.close()
        return True, "Schema Updated Successfully"
    except Exception as e: return False, str(e)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None: return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

def role_required(allowed_roles):
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None: return redirect(url_for('login'))
            if g.user['Role'] not in allowed_roles and 'Manager' not in g.user['Role']:
                flash('Access Denied', 'danger')
                return redirect(url_for('dashboard'))
            return view(**kwargs)
        return wrapped_view
    return decorator

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    g.user = query_db('SELECT * FROM Users WHERE UserID = ?', (user_id,), one=True) if user_id else None

# --- Routes ---

@app.route('/setup', methods=('GET', 'POST'))
def setup():
    if not session.get('setup_authorized'): return render_template('setup.html', authorized=False)
    if request.method == 'POST':
        save_config_file(request.form)
        flash('Settings Saved', 'success')
    return render_template('setup.html', config=load_config(), authorized=True)

@app.route('/setup_login', methods=['POST'])
def setup_login():
    if request.form['username'] == DEV_USERNAME and request.form['password'] == DEV_PASSWORD:
        session['setup_authorized'] = True
        flash('Logged In', 'success')
    else: flash('Invalid', 'danger')
    return redirect(url_for('setup'))

@app.route('/setup_logout')
def setup_logout():
    session.pop('setup_authorized', None)
    return redirect(url_for('setup'))

@app.route('/setup/init_db', methods=('POST',))
def init_db_route():
    success, msg = init_db_from_schema()
    flash(msg, 'success' if success else 'danger')
    return redirect(url_for('setup'))

@app.route('/', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        user = query_db('SELECT * FROM Users WHERE Username = ?', (request.form['username'],), one=True)
        if user and user['Password'] == request.form['password']:
            session['user_id'] = user['UserID']
            return redirect(url_for('dashboard'))
        flash('Invalid Credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    role = g.user['Role']
    if role == 'Corporate': return redirect(url_for('corporate_dashboard'))
    if role == 'Sales': return redirect(url_for('sales_index'))
    return render_template('dashboard.html')

# --- CORPORATE ---
@app.route('/corporate/dashboard')
@login_required
@role_required(['Corporate', 'Manager'])
def corporate_dashboard():
    # Fetch Stats
    stats = {}
    stats['client_count'] = query_db('SELECT COUNT(*) as c FROM Clients', one=True)['c']
    stats['open_requests'] = query_db("SELECT COUNT(*) as c FROM ClientRequests WHERE Status='Open'", one=True)['c']
    stats['active_campaigns'] = query_db("SELECT COUNT(*) as c FROM Campaigns WHERE Type='Linked'", one=True)['c']
    stats['total_candidates'] = query_db("SELECT COUNT(*) as c FROM Candidates", one=True)['c'] # Placeholder
    
    stats['recent_clients'] = query_db('SELECT TOP 5 * FROM Clients ORDER BY CreatedAt DESC')
    stats['recent_requests'] = query_db('''
        SELECT TOP 5 CR.*, C.CompanyName 
        FROM ClientRequests CR JOIN Clients C ON CR.ClientID = C.ClientID 
        WHERE CR.Status='Open' ORDER BY CR.CreatedAt DESC
    ''')
    
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
             (request.form['company_name'], request.form['industry'], request.form['contact_person'],
              request.form['email'], request.form['phone'], request.form['address']))
    flash('تم إضافة العميل', 'success')
    return redirect(url_for('corporate_manage'))

@app.route('/corporate/add_request', methods=('POST',))
@login_required
def add_request():
    f = request.form
    benefits = ", ".join(f.getlist('benefits'))
    soft = ", ".join(f.getlist('soft_skills'))
    query_db('''INSERT INTO ClientRequests (ClientID, JobTitle, NeededCount, Status, Gender, Location, 
                AgeFrom, AgeTo, SalaryFrom, SalaryTo, Benefits, EnglishLevel, ThirdLanguage, 
                ComputerLevel, Requirements, SoftSkills, Smoker, AppearanceLevel, PhysicalTraits) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
             (f['client_id'], f['job_title'], f.get('needed_count',1), 'Open', f.get('gender'), f.get('location'),
              f.get('age_from'), f.get('age_to'), f.get('salary_from'), f.get('salary_to'), benefits,
              f.get('english_level'), f.get('third_language'), f.get('computer_level'), f.get('requirements'),
              soft, f.get('smoker'), f.get('appearance'), f.get('physical_traits')))
    flash('تم إضافة الطلب', 'success')
    return redirect(url_for('corporate_manage'))

# --- SALES (Placeholder for next step) ---
@app.route('/sales')
@login_required
def sales_index():
    return render_template('sales/index.html', campaigns=[], active_requests=[], leads=[])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""

try:
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(app_code)
    print(f"Updated: {app_path}")
except Exception as e:
    print(f"Error: {e}")
