# نوافذ المحاسب ودمج مشروع Nuit (إسلام)

## تم التحقق — المشروع موجود محلياً

**المسار:** `E:\Nuit Cosmetics`

---

## التمييز الأساسي

| الدور | القطاع | الوظيفة |
|-------|--------|----------|
| **Account Manager** | التوظيف | عملاء، طلبات، مقابلات — **ليس ماليات** |
| **المحاسب (Finance)** | **الماليات فقط** | فواتير، مدفوعات، إيرادات، TBL022/TBL023 |

في Nuit: دور **ACC** أو **ISLAM** = المحاسب (Accountant).

---

## مراجع Nuit في Place_2026_SYS الحالي

من ملف `sql/exam_fee_invoice_tbl022_023.sql`:

```sql
-- منسوخ من نمط Nuit Cosmetics (main.py: create_sales_invoice / warehouse APIs)
```

**ما يُستنتج من Nuit:**
- `main.py` يحتوي على `create_sales_invoice`
- واجهات **warehouse APIs**
- نمط الفواتير: TBL022 (رأس) + TBL023 (بنود)
- حقول إلزامية في Schema

---

## نوافذ و APIs المحاسب الحالية في Place_2026_SYS

### 1. السايدبار (للمحاسب Finance)
- **Finance / الحسابات** → `/finance/index`

### 2. نوافذ Finance الحالية

| النافذة | المسار | الدوار | الوظيفة |
|---------|--------|--------|---------|
| **Unified Finance** | `/finance/index` | Manager, Finance, RecruitmentManager, TrainingManager | لوحة عرض: إجمالي إيرادات، مبيعات حرة، فواتير شركات، مدفوعات طلاب |
| **Student Finance** | `/training/student-finance/<enrollment_id>` | Finance, Manager, TrainingCoordinator, TrainingManager | إضافة دفعة (Add Payment)، طباعة فاتورة |
| **Add Payment** | POST `/training/add-payment` | Finance, Manager, TrainingCoordinator, TrainingManager | تسجيل دفعة طالب في StudentPayments |
| **Print Invoice** | `/training/print-invoice/<enrollment_id>` | Finance, Manager, TrainingCoordinator, TrainingManager | طباعة فاتورة الطالب |

### 3. نوافذ مرتبطة بالماليات (لكن ليست تحت Finance حصراً)

| النافذة | المسار | الدوار | ملاحظة |
|---------|--------|--------|--------|
| **تحصيل رسوم امتحان** | `/training/sales/exam-fee` | TrainingSales | يستدعي TBL022/TBL023 |
| **فاتورة ايراد دورات** | `/training/sales/course-fee` | TrainingSales | يستدعي TBL022/TBL023 |
| **Corporate Finance** | `/corporate/finance/<client_id>` | Corporate | فواتير ومدفوعات الشركات |
| **accounting_invoices** | `/accounting/invoices` | **AccountManager** | فواتير التعيين — **هذا توظيف وليس محاسب** |

### 4. APIs الفواتير (TBL022/TBL023)

| الدالة | الملف | الوظيفة |
|--------|------|---------|
| `_create_invoice_tbl022_023()` | app.py | إنشاء فاتورة عامة |
| `_create_exam_fee_invoice_tbl022_023()` | app.py | فاتورة رسوم امتحان |
| `_create_training_fee_invoice_tbl022_023()` | app.py | فاتورة ايراد دورات |
| `_pay_method_to_int()` | app.py | تحويل طريقة الدفع |

**الجداول:** TBL022 (رأس الفاتورة), TBL023 (بنود الفاتورة), TBL020 (نوع الفاتورة), TBL007 (الصنف/المنتج)

---

## ما يجب جلبه من Nuit لإسلام (المحاسب)

عند توفر رابط GitHub لمشروع Nuit:

### 1. نوافذ (Windows/Screens)
- [ ] شاشة إنشاء فاتورة مبيعات (`create_sales_invoice`)
- [ ] شاشات المستودع (warehouse) المرتبطة بالمحاسب
- [ ] أي واجهات إدخال مالية أخرى
- [ ] تقارير مالية / لوحة محاسب

### 2. APIs
- [ ] `create_sales_invoice`
- [ ] warehouse APIs (القسم المالي)
- [ ] أي endpoints خاصة بالمحاسب

### 3. الجداول والـ Schema
- [ ] حقول TBL022/TBL023 الإضافية المستخدمة في Nuit
- [ ] أي جداول مالية إضافية

### 4. قواعد الصلاحيات
- [ ] من يدخل البيانات المالية
- [ ] ربط دور إسلام بـ **Finance** وليس AccountManager

---

## خطة الدمج (عند توفر Nuit)

1. استنساخ/جلب مشروع Nuit من GitHub
2. استخراج ملفات `main.py` و warehouse APIs
3. مراجعة نوافذ إسلام وتحديد ما يناسب المحاسب
4. إنشاء routes جديدة تحت `/finance/` بدلاً من `/accounting/` (لتفادي الخلط مع AccountManager)
5. تقييد النوافذ الجديدة بدور `Finance` و `Manager`
6. تحديث `base.html` (السايدبار) لإظهار روابط المحاسب الجديدة
7. تحديث `add_islam_user.py` لتعيين دور `Finance` بدلاً من `Manager` إن لزم

---

## المستخدم إسلام

من `add_islam_user.py` و `check_islam_place.py`:
- **Username:** islam
- **FullName:** إسلام
- **الدور الحالي:** Manager (في السكريبت)

**التوصية:** تعيين إسلام بدور **Finance** (المحاسب) في النظام، مع منحه كل نوافذ و APIs المالية المستخرجة من Nuit.

---

## نوافذ إسلام (ACC) في Nuit Cosmetics — المُتحقق منها

المصدر: `E:\Nuit Cosmetics\window_permissions.py` و `docs\XTRA_DEFINITION_WINDOWS_FOR_ISLAM.md` و `النوافذ_والصلاحيات_مرجع.csv`

### 1. قسم المالية (Finance)
| النافذة | المسار | الوصف |
|---------|--------|-------|
| **Smart CashFlow** | `/api/cashflow/ui` | إدارة التدفقات النقدية |
| **Reports** | `/reports` | التقارير العامة |

### 2. نوافذ التعريف (للمحاسب)
| النافذة | المسار | الجدول | الوصف |
|---------|--------|--------|-------|
| **تعريف العملاء** | `/definition/agents` | TBL016 | إنشاء عميل + حساب في TBL004 |
| **تعريف الأصناف** | `/definition/products` | TBL007 | إنشاء صنف |
| **تعريف المستودعات** | `/definition/warehouses` | TBL008 | إنشاء مستودع |
| **دليل الحسابات** | `/definition/accounts` | TBL004 | عرض وتصفية فقط |

### 3. نوافذ إضافية لإسلام
| القسم | النافذة | المسار |
|-------|---------|--------|
| E-Commerce | Shipping Settlement | `/shopify/settlement` |
| Sales | Corporate Trans. | `/sales/transactions` |
| Warehouse | Inventory Tracking | `/inventory/tracking` |
| Warehouse | Inventory List | `/inventory` |
| System | Dashboard | `/` |

---

## APIs إسلام في Nuit — المُتحقق منها

المصدر: `routers/definition.py` و `main.py`

### APIs التعريف
| Method | المسار | الوظيفة |
|--------|--------|---------|
| GET | `/api/agent-groups` | مجموعات العملاء TBL015 |
| GET | `/api/agents` | قائمة العملاء TBL016 |
| GET | `/api/agents/search?search_text=` | بحث العملاء |
| POST | `/api/agents` | إنشاء عميل (TBL004 + TBL016) |
| GET | `/api/product-groups` | مجموعات الأصناف TBL006 |
| GET | `/api/products/definition` | قائمة الأصناف TBL007 |
| GET | `/api/products/search/definition?search_text=` | بحث الأصناف |
| POST | `/api/products/definition` | إنشاء صنف |
| GET | `/api/warehouses` | قائمة المستودعات TBL008 |
| POST | `/api/warehouses` | إنشاء مستودع |
| GET | `/api/accounts/main` | الحسابات الرئيسية |
| GET | `/api/accounts/list` | دليل الحسابات |
| POST | `/api/accounts/definition` | إنشاء حساب |

### API إنشاء فاتورة المبيعات (TBL022/TBL023)
| Method | المسار | الوظيفة |
|--------|--------|---------|
| POST | `/api/sales/create` | إنشاء فاتورة مبيعات (main.py ~سطر 1312) |

**Body:** `store_id`, `customer_id`, `ref_number`, `items` (كل بند: `id`, `qty`, `price`)

---

## الملفات المهمة في Nuit للمحاسب

| الملف | الوظيفة |
|-------|---------|
| `routers/definition.py` | APIs ومسارات نوافذ التعريف |
| `routers/cashflow.py` | شاشة الصرف والقبض |
| `main.py` | create_sales_invoice، RBAC، تسجيل إسلام |
| `window_permissions.py` | صلاحيات إسلام (ISLAM/ACC) |
| `menu_config.py` | القائمة الجانبية حسب الدور |
| `templates/definition_agents.html` | واجهة تعريف العملاء |
| `templates/definition_products.html` | واجهة تعريف الأصناف |
| `templates/definition_warehouses.html` | واجهة تعريف المستودعات |
| `templates/definition_accounts.html` | واجهة دليل الحسابات |
| `templates/cashflow_ui.html` | واجهة التدفقات النقدية |
| `db_services/warehouse.py` | دوال المستودع |
| `db_services/sales.py` | دوال المبيعات |

---

## تمّ الدمج (آذار 2026)

### السايدبار للمحاسب (Finance) — ماليات فقط
| الرابط | الوظيفة |
|--------|----------|
| **Finance** | الحسابات (إجمالي الإيرادات) |
| **Smart CashFlow** | التدفق النقدي الزكي (قبض/صرف) |
| **Reports** | التقارير المالية |

قسم المالية يظهر للمدير (Manager) والمحاسب (Finance) فقط. لا يظهر لـ TrainingManager.

### ما نُقل إلى Place_2026_SYS
1. **التدفق النقدي الزكي (Smart CashFlow)** — `/finance/cashflow`
   - إضافة سندات قبض/صرف
   - عرض آخر السندات
   - APIs: `/api/cashflow/accounts/sub`, `/api/cashflow/transactions`, `/api/cashflow/transactions` (POST)
2. **التقارير (Reports)** — `/finance/reports`
   - ميزان المراجعة، دفتر الأستاذ، قائمة الحسابات، قائمة السندات، قائمة القيود
   - أرصدة سريعة (صندوق/بنك/عهد)
   - APIs: `/api/reports`, `/api/reports/account-balances`, `/api/reports/<id>/run`
3. **السايدبار** — روابط «التدفق النقدي الزكي» و «التقارير» للمحاسب (Finance) و Manager
4. **ملفات جديدة:** `services/voucher_manager.py`, `templates/finance/cashflow_ui.html`, `templates/finance/reports_dashboard.html`, `scripts/create_cashflow_config_table.sql`

### تشغيل السكربت (إن لزم)
```sql
-- لتخزين مفضّلات التدفق النقدي (اختياري)
-- شغّل: scripts/create_cashflow_config_table.sql
```

### ما قد يُضاف لاحقاً
- نوافذ التعريف (عميل، صنف، مستودع، دليل حسابات)
- الواجهة الكاملة للتدفق النقدي من Nuit (مع المرفقات والإعدادات المحفوظة)
