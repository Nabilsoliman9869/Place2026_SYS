import os

# Define target paths (using the correct directory structure)
target_dir = r"E:\Place _trae"

# 1. Matching Template
matching_template_path = os.path.join(target_dir, "templates", "corporate", "matching.html")
matching_html = r"""{% extends 'base.html' %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
    <h2><i class="fas fa-handshake"></i> نافذة المطابقة (Matching Window)</h2>
    <a href="{{ url_for('corporate_dashboard') }}" class="btn btn-outline-secondary">
        <i class="fas fa-arrow-right"></i> العودة
    </a>
</div>

<div class="row">
    <!-- Left: Open Requests -->
    <div class="col-md-6">
        <div class="card shadow-sm h-100">
            <div class="card-header bg-primary text-white">
                <i class="fas fa-briefcase"></i> طلبات التوظيف المفتوحة
            </div>
            <div class="card-body p-0">
                <div class="list-group list-group-flush" id="requestsList">
                    {% for req in requests %}
                    <a href="#" class="list-group-item list-group-item-action" onclick="selectRequest('{{ req.RequestID }}', '{{ req.JobTitle }} - {{ req.CompanyName }}')">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">{{ req.JobTitle }}</h6>
                            <small class="text-muted">{{ req.NeededCount }} مطلوب</small>
                        </div>
                        <p class="mb-1 small text-muted">{{ req.CompanyName }}</p>
                        <small class="text-info">{{ req.Location }}</small>
                    </a>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    <!-- Right: Qualified Candidates -->
    <div class="col-md-6">
        <div class="card shadow-sm h-100">
            <div class="card-header bg-success text-white">
                <i class="fas fa-user-check"></i> المرشحين المؤهلين (Passed Exams)
            </div>
            <div class="card-body p-0">
                <form action="{{ url_for('corporate_submit_match') }}" method="POST">
                    <input type="hidden" name="request_id" id="selectedRequestId">
                    
                    <div class="p-3 bg-light border-bottom" id="selectionHeader" style="display:none;">
                        <strong>جاري المطابقة لـ:</strong> <span id="selectedJobTitle" class="text-primary fw-bold"></span>
                        <button type="submit" class="btn btn-sm btn-primary float-end">تأكيد المطابقة</button>
                    </div>

                    <div class="list-group list-group-flush" id="candidatesList">
                        {% for cand in candidates %}
                        <label class="list-group-item d-flex gap-3">
                            <input class="form-check-input flex-shrink-0" type="checkbox" name="candidate_ids" value="{{ cand.CandidateID }}">
                            <span class="pt-1 form-checked-content">
                                <strong>{{ cand.FullName }}</strong>
                                <small class="d-block text-muted">
                                    <i class="fas fa-star text-warning"></i> {{ cand.ExamResult }} | {{ cand.EvaluationDetails }}
                                </small>
                            </span>
                        </label>
                        {% endfor %}
                        {% if not candidates %}
                        <div class="p-4 text-center text-muted">لا يوجد مرشحين جاهزين حالياً</div>
                        {% endif %}
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<script>
function selectRequest(id, title) {
    document.getElementById('selectedRequestId').value = id;
    document.getElementById('selectedJobTitle').innerText = title;
    document.getElementById('selectionHeader').style.display = 'block';
    
    // Highlight selected
    document.querySelectorAll('#requestsList a').forEach(el => el.classList.remove('active'));
    event.currentTarget.classList.add('active');
}
</script>
{% endblock %}
"""

# 2. Sales Index Template (Campaigns & Leads)
sales_template_path = os.path.join(target_dir, "templates", "sales", "index.html")
sales_html = r"""{% extends 'base.html' %}

{% block content %}
<h2><i class="fas fa-bullhorn"></i> إدارة المبيعات والحملات</h2>

<ul class="nav nav-tabs mb-3" id="salesTab" role="tablist">
  <li class="nav-item"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#campaigns">الحملات الإعلانية</button></li>
  <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#leads">العملاء المحتملين (Leads)</button></li>
</ul>

<div class="tab-content">
  <!-- Campaigns Tab -->
  <div class="tab-pane fade show active" id="campaigns">
      <button class="btn btn-primary mb-3" data-bs-toggle="modal" data-bs-target="#addCampaignModal">
          <i class="fas fa-plus"></i> إضافة حملة جديدة
      </button>
      
      <table class="table table-striped">
          <thead>
              <tr>
                  <th>ID</th>
                  <th>اسم الحملة</th>
                  <th>النوع</th>
                  <th>المرتبط بـ</th>
                  <th>القناة</th>
                  <th>الميزانية</th>
                  <th>الفترة</th>
              </tr>
          </thead>
          <tbody>
              {% for camp in campaigns %}
              <tr>
                  <td>{{ camp.CampaignID }}</td>
                  <td>{{ camp.Name }}</td>
                  <td>
                      <span class="badge bg-{{ 'info' if camp.Type == 'Linked' else 'warning' }}">
                          {{ 'مرتبطة بطلب' if camp.Type == 'Linked' else 'عامة (تسويق)' }}
                      </span>
                  </td>
                  <td>{{ camp.CompanyName if camp.CompanyName else '-' }}</td>
                  <td>{{ camp.MediaChannel }}</td>
                  <td>{{ camp.Budget }}</td>
                  <td>{{ camp.StartDate }} - {{ camp.EndDate }}</td>
              </tr>
              {% endfor %}
          </tbody>
      </table>
  </div>

  <!-- Leads Tab -->
  <div class="tab-pane fade" id="leads">
      <button class="btn btn-success mb-3" data-bs-toggle="modal" data-bs-target="#addLeadModal">
          <i class="fas fa-user-plus"></i> إضافة عميل محتمل (Lead)
      </button>
      
      <table class="table table-hover">
          <thead>
              <tr>
                  <th>الاسم</th>
                  <th>الهاتف</th>
                  <th>الحملة</th>
                  <th>حالة الاهتمام</th>
                  <th>تاريخ الاتصال</th>
                  <th>إجراءات</th>
              </tr>
          </thead>
          <tbody>
              {% for lead in leads %}
              <tr>
                  <td>{{ lead.FullName }}</td>
                  <td>{{ lead.Phone }}</td>
                  <td>{{ lead.CampaignName or 'غير محدد' }}</td>
                  <td>{{ lead.InterestLevel }}</td>
                  <td>{{ lead.LastContactDate }}</td>
                  <td>
                      <button class="btn btn-sm btn-outline-primary">متابعة</button>
                  </td>
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
              <label>اسم الحملة</label>
              <input type="text" name="name" class="form-control" required>
          </div>
          <div class="mb-3">
              <label>نوع الحملة</label>
              <select name="type" class="form-select" id="campType" onchange="toggleRequestSelect()">
                  <option value="Linked">مرتبطة بطلب عميل</option>
                  <option value="General">عامة (تسويقية)</option>
              </select>
          </div>
          <div class="mb-3" id="reqSelectDiv">
              <label>الطلب المرتبط (للشركات)</label>
              <select name="request_id" class="form-select">
                  <option value="">اختر الطلب...</option>
                  {% for req in active_requests %}
                  <option value="{{ req.RequestID }}">{{ req.CompanyName }} - {{ req.JobTitle }}</option>
                  {% endfor %}
              </select>
          </div>
          <div class="row">
              <div class="col-md-6 mb-3">
                  <label>قناة الإعلان</label>
                  <input type="text" name="media_channel" class="form-control" placeholder="Facebook, LinkedIn...">
              </div>
              <div class="col-md-6 mb-3">
                  <label>الميزانية</label>
                  <input type="number" name="budget" class="form-control">
              </div>
          </div>
          <div class="row">
              <div class="col-md-6 mb-3">
                  <label>تاريخ البدء</label>
                  <input type="date" name="start_date" class="form-control">
              </div>
              <div class="col-md-6 mb-3">
                  <label>تاريخ الانتهاء</label>
                  <input type="date" name="end_date" class="form-control">
              </div>
          </div>
          <div class="mb-3">
              <label>نص الإعلان</label>
              <textarea name="ad_text" class="form-control"></textarea>
          </div>
      </div>
      <div class="modal-footer">
        <button type="submit" class="btn btn-primary">حفظ وإرسال للتدريب</button>
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
        <h5 class="modal-title">تسجيل عميل محتمل جديد</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <form action="{{ url_for('add_lead') }}" method="POST">
      <div class="modal-body">
          <div class="row">
              <div class="col-md-6 mb-3">
                  <label>الاسم بالكامل</label>
                  <input type="text" name="full_name" class="form-control" required>
              </div>
              <div class="col-md-6 mb-3">
                  <label>رقم الهاتف</label>
                  <input type="text" name="phone" class="form-control" required>
              </div>
          </div>
          <div class="mb-3">
              <label>البريد الإلكتروني</label>
              <input type="email" name="email" class="form-control">
          </div>
          <hr>
          <div class="mb-3">
              <label>الاهتمام بالحملة</label>
              <select name="campaign_id" class="form-select">
                  <option value="">اختر الحملة...</option>
                  {% for camp in campaigns %}
                  <option value="{{ camp.CampaignID }}">[{{ camp.Type }}] {{ camp.Name }}</option>
                  {% endfor %}
              </select>
          </div>
          <div class="row">
              <div class="col-md-6 mb-3">
                  <label>مستوى الاهتمام</label>
                  <select name="interest_level" class="form-select">
                      <option value="High">مرتفع</option>
                      <option value="Medium">متوسط</option>
                      <option value="Low">منخفض</option>
                  </select>
              </div>
              <div class="col-md-6 mb-3">
                  <label>تاريخ معاودة الاتصال</label>
                  <input type="datetime-local" name="next_followup" class="form-control">
              </div>
          </div>
          <div class="mb-3">
              <label>ملاحظات (CRM)</label>
              <textarea name="feedback" class="form-control" placeholder="تم شرح المطلوب، العميل مستاء من السعر..."></textarea>
          </div>
      </div>
      <div class="modal-footer">
        <button type="submit" class="btn btn-success">حفظ البيانات</button>
      </div>
      </form>
    </div>
  </div>
</div>

<script>
function toggleRequestSelect() {
    var type = document.getElementById('campType').value;
    var div = document.getElementById('reqSelectDiv');
    if (type === 'Linked') {
        div.style.display = 'block';
    } else {
        div.style.display = 'none';
    }
}
</script>
{% endblock %}
"""

# Write files
try:
    with open(matching_template_path, 'w', encoding='utf-8') as f:
        f.write(matching_html)
    print(f"Created: {matching_template_path}")
    
    with open(sales_template_path, 'w', encoding='utf-8') as f:
        f.write(sales_html)
    print(f"Updated: {sales_template_path}")
    
except Exception as e:
    print(f"Error: {e}")
