import os

target_dir = r"E:\Place _trae"
schema_path = os.path.join(target_dir, "schema_mssql.sql")
template_path = os.path.join(target_dir, "templates", "corporate", "index.html")
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
    ('trainer', 'trainer123', 'Trainer'),
    ('dev', '123', 'Developer');
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

-- ClientRequests Table (Updated with new columns)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ClientRequests' AND xtype='U')
BEGIN
    CREATE TABLE ClientRequests (
        RequestID INT IDENTITY(1,1) PRIMARY KEY,
        ClientID INT FOREIGN KEY REFERENCES Clients(ClientID),
        JobTitle NVARCHAR(100) NOT NULL,
        Requirements NVARCHAR(MAX),
        NeededCount INT DEFAULT 1,
        Status NVARCHAR(50) DEFAULT 'Open',
        
        -- New Columns
        Gender NVARCHAR(20), -- Male, Female, Any
        SalaryFrom DECIMAL(18,2),
        SalaryTo DECIMAL(18,2),
        Benefits NVARCHAR(MAX), -- JSON or Comma Separated
        SoftSkills NVARCHAR(MAX), -- JSON or Comma Separated
        EnglishLevel NVARCHAR(10), -- A1..C3
        ThirdLanguage NVARCHAR(50),
        ComputerLevel NVARCHAR(50),
        Location NVARCHAR(50),
        AgeFrom INT,
        AgeTo INT,
        PhysicalTraits NVARCHAR(MAX),
        Smoker NVARCHAR(20), -- Accepted, Non-Smoker
        AppearanceLevel NVARCHAR(50)
    );
END
ELSE
BEGIN
    -- Add columns if they don't exist (Idempotent update)
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'Gender' AND Object_ID = Object_ID(N'ClientRequests'))
        ALTER TABLE ClientRequests ADD Gender NVARCHAR(20);
        
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'SalaryFrom' AND Object_ID = Object_ID(N'ClientRequests'))
        ALTER TABLE ClientRequests ADD SalaryFrom DECIMAL(18,2);
        
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'SalaryTo' AND Object_ID = Object_ID(N'ClientRequests'))
        ALTER TABLE ClientRequests ADD SalaryTo DECIMAL(18,2);
        
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'Benefits' AND Object_ID = Object_ID(N'ClientRequests'))
        ALTER TABLE ClientRequests ADD Benefits NVARCHAR(MAX);
        
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'SoftSkills' AND Object_ID = Object_ID(N'ClientRequests'))
        ALTER TABLE ClientRequests ADD SoftSkills NVARCHAR(MAX);
        
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'EnglishLevel' AND Object_ID = Object_ID(N'ClientRequests'))
        ALTER TABLE ClientRequests ADD EnglishLevel NVARCHAR(10);
        
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'ThirdLanguage' AND Object_ID = Object_ID(N'ClientRequests'))
        ALTER TABLE ClientRequests ADD ThirdLanguage NVARCHAR(50);
        
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'ComputerLevel' AND Object_ID = Object_ID(N'ClientRequests'))
        ALTER TABLE ClientRequests ADD ComputerLevel NVARCHAR(50);
        
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'Location' AND Object_ID = Object_ID(N'ClientRequests'))
        ALTER TABLE ClientRequests ADD Location NVARCHAR(50);
        
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'AgeFrom' AND Object_ID = Object_ID(N'ClientRequests'))
        ALTER TABLE ClientRequests ADD AgeFrom INT;
        
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'AgeTo' AND Object_ID = Object_ID(N'ClientRequests'))
        ALTER TABLE ClientRequests ADD AgeTo INT;
        
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'PhysicalTraits' AND Object_ID = Object_ID(N'ClientRequests'))
        ALTER TABLE ClientRequests ADD PhysicalTraits NVARCHAR(MAX);
        
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'Smoker' AND Object_ID = Object_ID(N'ClientRequests'))
        ALTER TABLE ClientRequests ADD Smoker NVARCHAR(20);
        
    IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'AppearanceLevel' AND Object_ID = Object_ID(N'ClientRequests'))
        ALTER TABLE ClientRequests ADD AppearanceLevel NVARCHAR(50);
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

template_content = r"""{% extends 'base.html' %}

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
    <div class="table-responsive">
        <table class="table table-striped table-hover">
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
  </div>
  
  <!-- Requests Tab -->
  <div class="tab-pane fade" id="requests" role="tabpanel">
    <button class="btn btn-success mb-3" data-bs-toggle="modal" data-bs-target="#addRequestModal">
        <i class="fas fa-plus"></i> إضافة طلب جديد
    </button>
    <div class="table-responsive">
        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>الشركة</th>
                    <th>المسمى الوظيفي</th>
                    <th>العدد</th>
                    <th>الراتب</th>
                    <th>الموقع</th>
                    <th>الحالة</th>
                    <th>التفاصيل</th>
                </tr>
            </thead>
            <tbody>
                {% for req in requests %}
                <tr>
                    <td>{{ req.RequestID }}</td>
                    <td>{{ req.CompanyName }}</td>
                    <td>{{ req.JobTitle }}</td>
                    <td>{{ req.NeededCount }}</td>
                    <td>{{ req.SalaryFrom }} - {{ req.SalaryTo }}</td>
                    <td>{{ req.Location }}</td>
                    <td>
                        <span class="badge bg-{{ 'success' if req.Status == 'Open' else 'secondary' }}">
                            {{ req.Status }}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-info text-white" title="عرض التفاصيل">
                            <i class="fas fa-eye"></i>
                        </button>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
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

<!-- Add Request Modal (Comprehensive) -->
<div class="modal fade" id="addRequestModal" tabindex="-1" data-bs-backdrop="static">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header bg-light">
        <h5 class="modal-title text-primary"><i class="fas fa-briefcase"></i> إضافة طلب توظيف جديد</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <form action="{{ url_for('add_request') }}" method="POST">
      <div class="modal-body">
          
          <!-- Tabs for Sections -->
          <ul class="nav nav-tabs mb-3" id="reqTabs" role="tablist">
            <li class="nav-item">
                <button class="nav-link active" id="basic-tab" data-bs-toggle="tab" data-bs-target="#basic" type="button">بيانات الوظيفة</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="benefits-tab" data-bs-toggle="tab" data-bs-target="#benefits" type="button">المميزات والراتب</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="skills-tab" data-bs-toggle="tab" data-bs-target="#skills" type="button">المهارات والمؤهلات</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="traits-tab" data-bs-toggle="tab" data-bs-target="#traits" type="button">السمات الشخصية</button>
            </li>
          </ul>

          <div class="tab-content" id="reqTabsContent">
            
            <!-- 1. Basic Info -->
            <div class="tab-pane fade show active" id="basic">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">العميل <span class="text-danger">*</span></label>
                        <select name="client_id" class="form-select" required>
                            <option value="">اختر العميل...</option>
                            {% for client in clients %}
                            <option value="{{ client.ClientID }}">{{ client.CompanyName }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">المسمى الوظيفي <span class="text-danger">*</span></label>
                        <input type="text" name="job_title" class="form-control" required placeholder="مثال: محاسب، مهندس مبيعات...">
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">العدد المطلوب</label>
                        <input type="number" name="needed_count" class="form-control" value="1" min="1">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">الجنس المطلوب <span class="text-danger">*</span></label>
                        <div class="mt-2">
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="radio" name="gender" value="Any" checked>
                                <label class="form-check-label">الجنسين</label>
                            </div>
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="radio" name="gender" value="Male">
                                <label class="form-check-label">ذكر</label>
                            </div>
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="radio" name="gender" value="Female">
                                <label class="form-check-label">أنثى</label>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">منطقة السكن (الموقع) <span class="text-danger">*</span></label>
                        <select name="location" class="form-select" required>
                            <option value="">اختر المنطقة...</option>
                            <option value="Cairo">القاهرة</option>
                            <option value="Giza">الجيزة</option>
                            <option value="Alexandria">الإسكندرية</option>
                            <option value="Upper Egypt">وجه قبلي</option>
                            <option value="Sinai">سيناء</option>
                            <option value="Sharm">شرم الشيخ</option>
                            <option value="Other">أخرى</option>
                        </select>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">السن (من - إلى) <span class="text-danger">*</span></label>
                        <div class="input-group">
                            <input type="number" name="age_from" class="form-control" placeholder="من" required>
                            <span class="input-group-text">-</span>
                            <input type="number" name="age_to" class="form-control" placeholder="إلى" required>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 2. Benefits & Salary -->
            <div class="tab-pane fade" id="benefits">
                <div class="mb-3">
                    <label class="form-label fw-bold">الراتب المقرر (من - إلى)</label>
                    <div class="input-group">
                        <input type="number" name="salary_from" class="form-control" placeholder="الحد الأدنى">
                        <span class="input-group-text">-</span>
                        <input type="number" name="salary_to" class="form-control" placeholder="الحد الأقصى">
                        <span class="input-group-text">EGP</span>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label fw-bold">المميزات الإضافية</label>
                    <div class="row">
                        <div class="col-md-4">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="benefits" value="Health Insurance">
                                <label class="form-check-label">تأمين صحي</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="benefits" value="Social Security">
                                <label class="form-check-label">تأمين اجتماعي</label>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="benefits" value="Transportation">
                                <label class="form-check-label">تأمين انتقال (مواصلات)</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="benefits" value="Housing">
                                <label class="form-check-label">سكن (إقامة)</label>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="benefits" value="Monthly Bonus">
                                <label class="form-check-label">حوافز شهرية</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="benefits" value="Annual Bonus">
                                <label class="form-check-label">حوافز سنوية</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="benefits" value="Salary Increase">
                                <label class="form-check-label">زيادات سنوية</label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 3. Skills & Qualifications -->
            <div class="tab-pane fade" id="skills">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">اللغة الإنجليزية (Standard) <span class="text-danger">*</span></label>
                        <select name="english_level" class="form-select" required>
                            <option value="">اختر المستوى...</option>
                            <option value="A1">A1 - مبتدئ 1</option>
                            <option value="A2">A2 - مبتدئ 2</option>
                            <option value="A3">A3 - مبتدئ 3</option>
                            <option value="B1">B1 - متوسط 1</option>
                            <option value="B2">B2 - متوسط 2</option>
                            <option value="B3">B3 - متوسط 3</option>
                            <option value="C1">C1 - متقدم 1</option>
                            <option value="C2">C2 - متقدم 2</option>
                            <option value="C3">C3 - خبير (Native-like)</option>
                        </select>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">لغة ثالثة (اختياري)</label>
                        <select name="third_language" class="form-select">
                            <option value="">لا يوجد</option>
                            <option value="French">الفرنسية</option>
                            <option value="German">الألمانية</option>
                            <option value="Italian">الإيطالية</option>
                            <option value="Chinese">الصينية</option>
                            <option value="Turkish">التركية</option>
                            <option value="Other">أخرى</option>
                        </select>
                    </div>
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold">مهارات الحاسب الآلي</label>
                    <div class="btn-group w-100" role="group">
                        <input type="radio" class="btn-check" name="computer_level" id="comp1" value="Acceptable" checked>
                        <label class="btn btn-outline-primary" for="comp1">مقبول</label>

                        <input type="radio" class="btn-check" name="computer_level" id="comp2" value="Good">
                        <label class="btn btn-outline-primary" for="comp2">جيد</label>

                        <input type="radio" class="btn-check" name="computer_level" id="comp3" value="Advanced">
                        <label class="btn btn-outline-primary" for="comp3">متقدم</label>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label fw-bold">متطلبات الوظيفة التفصيلية</label>
                    <textarea name="requirements" class="form-control" rows="3" placeholder="أي تفاصيل فنية أخرى..."></textarea>
                </div>
            </div>

            <!-- 4. Traits & Soft Skills -->
            <div class="tab-pane fade" id="traits">
                <div class="mb-3">
                    <label class="form-label fw-bold">السمات الشخصية والقدرات</label>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="soft_skills" value="Shift Work">
                                <label class="form-check-label">القدرة على العمل شيفتات</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="soft_skills" value="Travel/Relocation">
                                <label class="form-check-label">القدرة على العمل خارج المحافظة</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="soft_skills" value="Learning">
                                <label class="form-check-label">القدرة على التطور والتعلم</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="soft_skills" value="Leadership">
                                <label class="form-check-label">القدرة على القيادة</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="soft_skills" value="Work Under Pressure">
                                <label class="form-check-label">العمل تحت ضغط</label>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="soft_skills" value="Teamwork">
                                <label class="form-check-label">العمل الجماعي</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="soft_skills" value="Communication">
                                <label class="form-check-label">مهارات التواصل</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="soft_skills" value="Problem Solving">
                                <label class="form-check-label">حل المشكلات</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="soft_skills" value="Time Management">
                                <label class="form-check-label">إدارة الوقت</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="soft_skills" value="Adaptability">
                                <label class="form-check-label">المرونة والتكيف</label>
                            </div>
                        </div>
                    </div>
                </div>

                <hr>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">التدخين</label>
                        <div class="mt-1">
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="radio" name="smoker" value="Accepted" checked>
                                <label class="form-check-label">مقبول</label>
                            </div>
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="radio" name="smoker" value="Non-Smoker">
                                <label class="form-check-label">غير مدخن</label>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label fw-bold">لياقة المظهر والقبول</label>
                        <select name="appearance" class="form-select">
                            <option value="Acceptable">مقبول</option>
                            <option value="Normal" selected>عادي</option>
                            <option value="Good">جيد / حسن المظهر</option>
                        </select>
                    </div>
                </div>

                <div class="mb-3">
                    <label class="form-label fw-bold">وصف السمات الشكلية (اختياري)</label>
                    <textarea name="physical_traits" class="form-control" rows="2" placeholder="أي مواصفات شكلية مطلوبة..."></textarea>
                </div>
            </div>

          </div> <!-- End Tab Content -->

      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
        <button type="submit" class="btn btn-primary fw-bold">حفظ الطلب</button>
      </div>
      </form>
    </div>
  </div>
</div>
{% endblock %}
"""

app_content = r"""from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import pyodbc
import functools
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key_place_2026'

CONFIG_FILE = 'db_config.json'
SCHEMA_FILE = 'schema_mssql.sql'

# Developer Credentials
DEV_USERNAME = "dev"
DEV_PASSWORD = "123"

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
        cursor.close()
        raise e

def init_db_from_schema():
    if not os.path.exists(SCHEMA_FILE):
        return False, "ملف Schema غير موجود"
    
    db = get_db()
    if db is None:
        return False, f"فشل الاتصال بقاعدة البيانات: {getattr(g, 'db_error', 'Unknown')}"

    try:
        with open(SCHEMA_FILE, 'r') as f:
            schema_script = f.read()
        
        commands = schema_script.replace('\r\n', '\n').split('GO\n')
        
        cursor = db.cursor()
        for command in commands:
            if command.strip():
                try:
                    cursor.execute(command)
                    db.commit()
                except Exception as cmd_error:
                    print(f"Error executing command: {cmd_error}")
        
        cursor.close()
        return True, "تم إنشاء/تحديث الجداول بنجاح"
    except Exception as e:
        return False, str(e)

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
    db = get_db()
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        try:
            g.user = query_db('SELECT * FROM Users WHERE UserID = ?', (user_id,), one=True)
        except:
            g.user = None

# --- Setup Routes (Developer Only) ---
@app.route('/setup_login', methods=['POST'])
def setup_login():
    username = request.form['username']
    password = request.form['password']
    if username == DEV_USERNAME and password == DEV_PASSWORD:
        session['setup_authorized'] = True
        flash('تم تسجيل الدخول بنجاح', 'success')
    else:
        flash('بيانات الدخول غير صحيحة', 'danger')
    return redirect(url_for('setup'))

@app.route('/setup_logout')
def setup_logout():
    session.pop('setup_authorized', None)
    return redirect(url_for('setup'))

@app.route('/setup', methods=('GET', 'POST'))
def setup():
    if not session.get('setup_authorized'):
        return render_template('setup.html', authorized=False)

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
            try:
                if 'db' in g:
                    g.pop('db').close()
                get_db()
                if g.db:
                    flash('تم الاتصال بقاعدة البيانات بنجاح!', 'success')
                else:
                    flash(f'فشل الاتصال: {g.db_error}', 'danger')
            except Exception as e:
                flash(f'خطأ أثناء الاختبار: {e}', 'danger')
        else:
            flash('فشل حفظ ملف الإعدادات', 'danger')
    
    current_config = load_config()
    return render_template('setup.html', config=current_config, authorized=True)

@app.route('/setup/init_db', methods=('POST',))
def init_db_route():
    if not session.get('setup_authorized'):
        return redirect(url_for('setup'))
        
    success, message = init_db_from_schema()
    if success:
        return render_template('setup.html', 
                               config=load_config(), 
                               authorized=True, 
                               success_state=True, 
                               message=message)
    else:
        flash(f'حدث خطأ: {message}', 'danger')
        return redirect(url_for('setup'))

# --- Auth Routes ---
@app.route('/', methods=('GET', 'POST'))
def login():
    if get_db() is None:
        if request.endpoint != 'setup' and request.endpoint != 'setup_login':
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
        # 1. Basic Info
        client_id = request.form['client_id']
        job_title = request.form['job_title']
        needed_count = request.form.get('needed_count', 1)
        gender = request.form.get('gender', 'Any')
        location = request.form.get('location')
        age_from = request.form.get('age_from')
        age_to = request.form.get('age_to')
        
        # 2. Benefits & Salary
        salary_from = request.form.get('salary_from') or 0
        salary_to = request.form.get('salary_to') or 0
        
        # Handle Checkboxes for Benefits (List to String)
        benefits_list = request.form.getlist('benefits')
        benefits_str = ", ".join(benefits_list) if benefits_list else ""

        # 3. Skills
        english_level = request.form.get('english_level')
        third_language = request.form.get('third_language')
        computer_level = request.form.get('computer_level')
        requirements = request.form.get('requirements', '') # Additional text

        # 4. Traits
        # Handle Checkboxes for Soft Skills
        soft_skills_list = request.form.getlist('soft_skills')
        soft_skills_str = ", ".join(soft_skills_list) if soft_skills_list else ""
        
        smoker = request.form.get('smoker', 'Accepted')
        appearance = request.form.get('appearance')
        physical_traits = request.form.get('physical_traits', '')

        try:
            query_db(
                '''INSERT INTO ClientRequests 
                   (ClientID, JobTitle, NeededCount, Status, Gender, Location, AgeFrom, AgeTo, 
                    SalaryFrom, SalaryTo, Benefits, EnglishLevel, ThirdLanguage, ComputerLevel, 
                    Requirements, SoftSkills, Smoker, AppearanceLevel, PhysicalTraits) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (client_id, job_title, needed_count, 'Open', gender, location, age_from, age_to,
                 salary_from, salary_to, benefits_str, english_level, third_language, computer_level,
                 requirements, soft_skills_str, smoker, appearance, physical_traits)
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
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    print(f"Written: {template_path}")
    
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(app_content)
    print(f"Written: {app_path}")

except Exception as e:
    print(f"Error: {e}")
