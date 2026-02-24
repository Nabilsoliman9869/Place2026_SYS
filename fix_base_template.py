import os

target_dir = r"E:\Place _trae"
base_template_path = os.path.join(target_dir, "templates", "base.html")

# Fix base.html to use correct endpoints
base_html = r"""<!doctype html>
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
            <a href="{{ url_for('corporate_dashboard') }}"><i class="fas fa-chart-line"></i> مؤشرات الشركات</a>
          </li>
          <li class="nav-item">
            <a href="{{ url_for('corporate_manage') }}"><i class="fas fa-building"></i> إدارة الشركات</a>
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
"""

try:
    with open(base_template_path, 'w', encoding='utf-8') as f:
        f.write(base_html)
    print(f"Updated: {base_template_path}")
except Exception as e:
    print(f"Error: {e}")
