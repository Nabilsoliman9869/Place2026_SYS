# لقطة مرجعية — مسار التدريب قبل تنفيذ المواصفة الكاملة (2026-04-06)

هذا الملف يثبت **ما كان يعمل فعلياً** في الكود قبل دمج مواصفة Lead / Train to Hire / القوائم / الإغلاق / الضيوف / تقارير الجداول.

## مبيعات التدريب
- **المسارات:** `training_sales_dashboard`, `training_sales_index`, `training_sales_register`, `training_sales_scheduling`, `training_sales_book_slot`, `training_sales_followup`, `training_sales_exam_fee`, `training_sales_course_fee`.
- **تسجيل الليد:** `POST /training/sales/register` — حقول فعلية: `FullName`, `Phone`, `Email` (اختياري في الواجهة)، `Status=Training_Lead`, `PrimaryIntent=Training`, `SalesAgentID`.
- **حجز اختبار التدريب:** لا يتحقق من دفع رسوم امتحان تحديد المستوى قبل الحجز.
- **لا يوجد:** نوع ليد `Interested` vs `Train to Hire`، حقول جامعة/سكن/مصدر/عمر/تخرج إلزامية، روابط مستندات Drive.

## مختبر مواهب التدريب
- **لوحة:** `talent_dashboard` مع `context=training`؛ جدول مواعيد من `TASchedules` بسياق Training.
- **تقييم موعد محجوز:** `talent_evaluate` — `EvaluationType` للمستخدم `Talent_Training` = نص `'Training'` (ليس `Training_Placement`).
- **قرارات الواجهة:** `Accepted`, `Training`, `Rejected` فقط (لا القائمة الكاملة Resc / Pending / …).
- **دفعة:** `talent_exam_feedback` + `talent_exam_feedback_evaluate` — `exam_kind`: `periodic` | `graduation` فقط → `Training_Periodic` / `Training_Graduation`.
- **قائمة:** `talent_training_completed_tests` — فلترة بـ `EvaluationType IN (Training_Periodic, Training_Graduation, Training)`.
- **لا يوجد:** قوائم `TO BE CLOSE` / `Acceptance Train to Hire` / `Pending` كـ نوافذ منفصلة؛ فلاتر أعمدة موحدة على كل الشاشات.

## الحضور
- `training_attendance` + `save_attendance_grid` — `Attendance` مرتبط بـ `EnrollmentID`؛ `AssignmentStatus` / الواجب.
- **لا يوجد:** سجل ضيف `Guest` لجلسة الدفعة.

## التقارير التشغيلية (المطلوبة لاحقاً)
- عرض الدورات/الدفعات في `training_index` و`wave_details` — **بدون** تقريرين منفصلين «دورات حالية بالتواريخ» و«دفعات مستقبلية» كما في الجدولين المرجعيين.

## ملاحظة
بعد هذا التاريخ تُضاف أعمدة وجداول ومسارات جديدة؛ للرجوع للسلوك القديم راجع `git log` و`docs/training_lead_talent_sales_vision_spec.md`.
