# main.py - نظام إدارة التدريب والموارد البشرية
import flet as ft
from datetime import datetime, timedelta
import traceback
import database as db  # تأكد من وجود ملف database.py يحتوي على كل الدوال المطلوبة


# ==================== إعدادات أساسية ====================
def show_snackbar(page: ft.Page, message: str, color=ft.Colors.GREEN):
    page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
    page.snack_bar.open = True
    page.update()


# ==================== دالة مشتركة لإنشاء الجداول ====================
def create_table(columns: list, data: list, actions: dict = None) -> ft.DataTable:
    table_columns = [ft.DataColumn(ft.Text(col["title"])) for col in columns]

    # ✅ لو فيه actions يبقى لازم نضيف عمود "إجراءات" في الأعمدة
    if actions and "buttons" in actions:
        table_columns.append(ft.DataColumn(ft.Text("إجراءات")))

    rows = []

    for item in data:
        cells = []
        for col in columns:
            value = item.get(col["key"], "")
            if "format" in col:
                try:
                    value = col["format"](value)
                except:
                    value = str(value)
            cells.append(ft.DataCell(ft.Text(str(value))))

        # ✅ خلايا الإجراءات (مع fallback icon)
        if actions and "buttons" in actions:
            action_icons = []
            for btn in actions["buttons"]:
                icon_val = btn.get("icon", ft.Icons.MORE_HORIZ)
                icon_btn = ft.IconButton(
                    icon=icon_val,
                    tooltip=btn.get("tooltip", ""),
                    on_click=lambda e, i=item, h=btn["handler"]: h(e, i)
                )
                action_icons.append(icon_btn)
            cells.append(ft.DataCell(ft.Row(action_icons, spacing=5)))

        rows.append(ft.DataRow(cells=cells))

    return ft.DataTable(
        columns=table_columns,
        rows=rows,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
        heading_row_color=ft.Colors.BLUE_50,
        heading_row_height=50,
        data_row_height=60,
    )


# ==================== شاشة الدخول ====================
def login_view(open_view=None) -> ft.View:
    username = ft.TextField(label="اسم المستخدم", width=400, autofocus=True)
    password = ft.TextField(label="كلمة السر", password=True, can_reveal_password=True, width=400)
    error_text = ft.Text("", color=ft.Colors.RED)

    def handle_login(e: ft.ControlEvent):
        if username.value == "admin" and password.value == "admin@123":
            error_text.value = ""
            if callable(open_view):
                open_view(dashboard_view)   # ✅ بدون Routing
            else:
                show_snackbar(e.page, "open_view غير متاح", ft.Colors.RED)
        else:
            error_text.value = "اسم المستخدم أو كلمة السر غير صحيحة"
        e.page.update()

    return ft.View(
        route="/login",
        controls=[
            ft.Column(
                controls=[
                    ft.Text("تسجيل الدخول إلى النظام", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                    ft.Container(height=40),
                    username,
                    password,
                    error_text,
                    ft.Container(height=20),
                    ft.FilledButton("دخول", on_click=handle_login, width=400, height=50),
                    ft.Container(height=20),
                    ft.Text("تلميح: admin / admin@123", size=12, color=ft.Colors.GREY_600),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        bgcolor=ft.Colors.BLUE_GREY_50,
    )


def dashboard_view() -> ft.View:
    stats = db.get_dashboard_stats()
    return ft.View(
        route="/dashboard",
        controls=[
            ft.Column(
                controls=[
                    ft.Text("لوحة التحكم الرئيسية", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                    ft.Divider(),
                    ft.ResponsiveRow(
                        controls=[
                            ft.Container(
                                content=ft.Column(
                                    [ft.Text(f"{stats.get('total_candidates', 0):,}", size=36, weight="bold"),
                                     ft.Text("إجمالي المرشحين")],
                                    horizontal_alignment="center",
                                ),
                                padding=20, bgcolor=ft.Colors.BLUE_50, border_radius=10,
                                col={"sm": 12, "md": 4}
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [ft.Text(f"{stats.get('hired_candidates', 0):,}", size=36, weight="bold"),
                                     ft.Text("تم توظيفهم")],
                                    horizontal_alignment="center",
                                ),
                                padding=20, bgcolor=ft.Colors.GREEN_50, border_radius=10,
                                col={"sm": 12, "md": 4}
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [ft.Text(f"{stats.get('exam_success_rate', 0)}%", size=36, weight="bold"),
                                     ft.Text("نسبة نجاح الامتحانات")],
                                    horizontal_alignment="center",
                                ),
                                padding=20, bgcolor=ft.Colors.AMBER_50, border_radius=10,
                                col={"sm": 12, "md": 4}
                            ),
                        ]
                    ),
                    ft.Container(height=20),
                    ft.Text("مرحبًا بك! اختر قسمًا من القائمة الجانبية."),
                ],
                scroll=ft.ScrollMode.AUTO,
            )
        ],
    )

# ==================== 1. تسجيل الاهتمام (Landing Page) ====================
def phase1_landing_page() -> ft.View:
    name = ft.TextField(label="الاسم بالكامل", width=350, border_color=ft.Colors.BLUE_400)
    phone = ft.TextField(label="رقم الهاتف", width=350, keyboard_type=ft.KeyboardType.PHONE)
    area = ft.Dropdown(label="منطقة السكن", width=350, options=[ft.dropdown.Option(v) for v in ["القاهرة", "الجيزة", "الإسكندرية", "المنوفية", "الغربية", "أخرى"]])
    education = ft.Dropdown(label="المستوى التعليمي", width=350, options=[ft.dropdown.Option(v) for v in ["ثانوية", "دبلوم", "بكالوريوس", "ماجستير", "دكتوراه"]])
    result = ft.Text("", color=ft.Colors.GREEN, size=14)

    def register_interest(e: ft.ControlEvent):
        if not name.value.strip() or not phone.value.strip():
            result.value = "❌ الاسم ورقم الهاتف مطلوبان"
            result.color = ft.Colors.RED
            e.page.update()
            return

        data = {"FullName": name.value.strip(), "Phone": phone.value.strip(), "Governorate": area.value, "Profession": education.value, "Source": "Website", "Status": "New"}

        try:
            interest_id = db.add_interest_registration(data)
            result.value = f"✅ تم التسجيل بنجاح! رقم التسجيل: {interest_id}\nسنتصل بك قريباً"
            result.color = ft.Colors.GREEN
            name.value = phone.value = ""
            area.value = education.value = None
            show_snackbar(e.page, "شكراً لتسجيل اهتمامك!")
        except Exception as ex:
            result.value = f"❌ خطأ في التسجيل: {str(ex)}"
            result.color = ft.Colors.RED
        e.page.update()

    return ft.View(route="/landing",
        controls=[
            ft.Column(
                controls=[
                    ft.Container(bgcolor=ft.Colors.BLUE_800, padding=40, border_radius=ft.BorderRadius.only(bottom_left=30, bottom_right=30),
                        content=ft.Column([ft.Text("وظائف مميزة بانتظارك", size=34, color=ft.Colors.WHITE, weight="bold"), ft.Text("سجل بياناتك وسنتواصل معك في أقرب وقت", size=18, color=ft.Colors.WHITE70)], horizontal_alignment="center")),
                    ft.Container(padding=40, alignment=ft.Alignment(0, 0),
                        content=ft.Card(elevation=10, content=ft.Container(padding=40, width=450,
                            content=ft.Column(controls=[
                                ft.Text("سجل اهتمامك الآن", size=26, weight="bold", color=ft.Colors.BLUE_900),
                                ft.Container(height=20),
                                name, phone, area, education,
                                ft.Container(height=30),
                                ft.FilledButton("🚀 سجل الآن", on_click=register_interest, width=350, height=50),
                                ft.Container(height=20),
                                result
                            ], horizontal_alignment="center", spacing=15)
                        )))
                ],
                scroll=ft.ScrollMode.AUTO
            )
        ]
    )


# ==================== 2. لوحة المبيعات ====================
def phase1_sales_dashboard() -> ft.View:
    status_filter = ft.Dropdown(label="فلترة حسب الحالة", width=200, value="all", options=[
        ft.dropdown.Option(key="all", text="الكل"), ft.dropdown.Option(key="New", text="جديد"),
        ft.dropdown.Option(key="Contacted", text="تم الاتصال"), ft.dropdown.Option(key="Registered", text="مسجل كمرشح"),
        ft.dropdown.Option(key="InTraining", text="في تدريب"),
    ])
    interests_container = ft.Container()

    def load_interests():
        status = status_filter.value if status_filter.value != "all" else None
        interests = db.get_all_interests(status=status)

        columns = [
            {'title': 'الاسم الكامل', 'key': 'FullName'},
            {'title': 'رقم الهاتف', 'key': 'Phone'},
            {'title': 'المحافظة', 'key': 'Governorate'},
            {'title': 'المؤهل', 'key': 'Profession'},
            {'title': 'الحالة', 'key': 'Status'},
            {'title': 'تاريخ التسجيل', 'key': 'RegistrationDate', 'format': lambda x: x.strftime('%Y-%m-%d') if x else ''},
        ]

        def mark_as_contacted(e, item):
            db.update_interest_status(item['InterestID'], "Contacted")
            show_snackbar(e.page, f"تم تحديث حالة {item['FullName']} إلى 'تم الاتصال'")
            load_interests()

        def convert_to_candidate(e, item):
            candidate_id = db.convert_interest_to_candidate(item['InterestID'])
            show_snackbar(e.page, f"تم تحويل {item['FullName']} إلى مرشح رقم {candidate_id}")
            load_interests()

        def offer_training(e, item):
            db.update_interest_status(item['InterestID'], "InTraining")
            show_snackbar(e.page, f"تم عرض التدريب على {item['FullName']}")
            load_interests()

        actions = {'buttons': [
            {'icon': ft.Icons.PHONE, 'tooltip': 'تم الاتصال', 'handler': mark_as_contacted},
            {'icon': ft.Icons.PERSON_ADD, 'tooltip': 'تحويل إلى مرشح', 'handler': convert_to_candidate},
            {'icon': ft.Icons.SCHOOL, 'tooltip': 'عرض تدريب', 'handler': offer_training},
        ]}


        table = create_table(columns, interests, actions)
        interests_container.content = table
        interests_container.update()

    status_filter.on_change = lambda e: load_interests()
    sales_stats = db.get_sales_dashboard()

    def refresh_stats(e):
        load_interests()
        show_snackbar(e.page, "تم تحديث البيانات")

    load_interests()

    return ft.View(route="/sales",
        controls=[
            ft.Column(
                controls=[
                    ft.Row([ft.Text("المبيعات والتسويق - متابعة المهتمين", size=26, weight="bold", color=ft.Colors.BLUE_900),
                            ft.Row([status_filter, ft.IconButton(tooltip="تحديث", on_click=refresh_stats)])],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=2, color=ft.Colors.BLUE_100),
                    ft.ResponsiveRow(controls=[
                        ft.Container(content=ft.Column([ft.Text(str(sales_stats.get('total_leads', 0)), size=32, weight="bold"), ft.Text("إجمالي المهتمين")], horizontal_alignment="center"), padding=20, bgcolor=ft.Colors.BLUE_50, border_radius=10, col={"sm": 12, "md": 3}),
                        ft.Container(content=ft.Column([ft.Text(str(sales_stats.get('today_leads', 0)), size=32, weight="bold"), ft.Text("مهتمين اليوم")], horizontal_alignment="center"), padding=20, bgcolor=ft.Colors.GREEN_50, border_radius=10, col={"sm": 12, "md": 3}),
                        ft.Container(content=ft.Column([ft.Text(str(sales_stats.get('contacted_leads', 0)), size=32, weight="bold"), ft.Text("تم الاتصال")], horizontal_alignment="center"), padding=20, bgcolor=ft.Colors.AMBER_50, border_radius=10, col={"sm": 12, "md": 3}),
                        ft.Container(content=ft.Column([ft.Text(f"{sales_stats.get('conversion_rate', 0)}%", size=32, weight="bold"), ft.Text("معدل التحويل")], horizontal_alignment="center"), padding=20, bgcolor=ft.Colors.PURPLE_50, border_radius=10, col={"sm": 12, "md": 3}),
                    ]),
                    ft.Container(height=30),
                    ft.Text("قائمة المهتمين", size=20, weight="bold"),
                    interests_container
                ],
                scroll=ft.ScrollMode.AUTO
            )
        ]
    )


# ==================== 3. جدولة امتحانات تحديد المستوى ====================
def phase1_exam_scheduling() -> ft.View:
    exam_table = ft.Container()

    def load_exams():
        exams = db.get_placement_exams()
        columns = [
            {'title': 'اسم الامتحان', 'key': 'ExamName'},
            {'title': 'النوع', 'key': 'ExamType'},
            {'title': 'المدة', 'key': 'Duration', 'format': lambda x: f"{x} دقيقة"},
            {'title': 'الرسوم', 'key': 'Fee', 'format': lambda x: f"{x:,.2f} ج.م"},
            {'title': 'درجة النجاح', 'key': 'PassingScore'},
        ]

        def schedule_exam(e, item):
            candidates = db.get_all_candidates()
            candidate_dropdown = ft.Dropdown(label="اختر المرشح", width=350, options=[ft.dropdown.Option(key=str(c['CandidateID']), text=c['FullName']) for c in candidates])
            date_field = ft.TextField(label="التاريخ", value=datetime.now().strftime('%Y-%m-%d'), width=350)

            def save_appointment(btn_e):
                if not candidate_dropdown.value:
                    show_snackbar(btn_e.page, "اختر المرشح", ft.Colors.RED)
                    return
                appointment_data = {"CandidateID": int(candidate_dropdown.value), "ExamID": item['ExamID'], "AppointmentDate": date_field.value, "Status": "Scheduled"}
                try:
                    appointment_id = db.schedule_exam_appointment(appointment_data)
                    show_snackbar(btn_e.page, f"تم جدولة الامتحان رقم {appointment_id}")
                    btn_e.page.close(dlg)
                except Exception as ex:
                    show_snackbar(btn_e.page, f"خطأ: {str(ex)}", ft.Colors.RED)

            dlg = ft.AlertDialog(title=ft.Text(f"جدولة امتحان: {item['ExamName']}"), content=ft.Column([candidate_dropdown, date_field]), actions=[
                ft.TextButton("إلغاء", on_click=lambda e: e.page.close(dlg)),
                ft.FilledButton("حفظ الموعد", on_click=save_appointment)
            ])
            e.page.open(dlg)

            actions = {'buttons': [
               {'icon': ft.Icons.SCHEDULE, 'tooltip': 'جدولة الامتحان', 'handler': schedule_exam}
            ]}

        table = create_table(columns, exams, actions)
        exam_table.content = table
        exam_table.update()

    load_exams()

    return ft.View(route="/exam_scheduling",
        controls=[
            ft.Column(
                controls=[
                    ft.Text("جدولة امتحانات تحديد المستوى", size=26, weight="bold", color=ft.Colors.BLUE_900),
                    ft.Divider(height=2, color=ft.Colors.BLUE_100),
                    ft.Text("اختر امتحاناً ثم اضغط 'جدولة' لتحديد موعد لمرشح", size=16),
                    ft.Container(height=20),
                    exam_table
                ],
                scroll=ft.ScrollMode.AUTO
            )
        ]
    )


# ==================== 4. إدارة التدريبات ====================
def phase2_trainings_management() -> ft.View:
    trainings_container = ft.Container()

    def load_trainings():
        trainings = db.get_all_trainings()
        columns = [
            {'title': 'اسم التدريب', 'key': 'TrainingName'},
            {'title': 'التصنيف', 'key': 'Category'},
            {'title': 'المدة', 'key': 'DurationHours', 'format': lambda x: f"{x} ساعة"},
            {'title': 'الرسوم', 'key': 'Fee', 'format': lambda x: f"{x:,.2f} ج.م"},
            {'title': 'المدرب', 'key': 'Instructor'},
            {'title': 'الحالة', 'key': 'Status'},
        ]

        def enroll_candidate(e, item):
            candidates = db.get_all_candidates()
            candidate_dropdown = ft.Dropdown(label="اختر المرشح", width=350, options=[ft.dropdown.Option(key=str(c['CandidateID']), text=f"{c['FullName']} - {c['Phone']}") for c in candidates])

            def save_enrollment(btn_e):
                if not candidate_dropdown.value:
                    show_snackbar(btn_e.page, "اختر المرشح أولاً", ft.Colors.RED)
                    return
                try:
                    enrollment_id = db.enroll_candidate_in_training(int(candidate_dropdown.value), item['TrainingID'])
                    show_snackbar(btn_e.page, f"تم تسجيل المرشح في التدريب رقم {enrollment_id}")
                    btn_e.page.close(dlg)
                except Exception as ex:
                    show_snackbar(btn_e.page, f"خطأ: {str(ex)}", ft.Colors.RED)

            dlg = ft.AlertDialog(title=ft.Text(f"تسجيل مرشح في تدريب: {item['TrainingName']}"), content=candidate_dropdown, actions=[
                ft.TextButton("إلغاء", on_click=lambda e: e.page.close(dlg)),
                ft.FilledButton("تسجيل", on_click=save_enrollment)
            ])
            e.page.open(dlg)

            actions = {'buttons': [
                {'icon': ft.Icons.PERSON_ADD, 'tooltip': 'تسجيل مرشح', 'handler': enroll_candidate}
            ]}

        table = create_table(columns, trainings, actions)
        trainings_container.content = table
        trainings_container.update()

    def add_new_training(e):
        name_field = ft.TextField(label="اسم التدريب", width=400)
        category_dropdown = ft.Dropdown(label="التصنيف", width=400, options=[ft.dropdown.Option(v) for v in ["تكنولوجيا", "إدارة", "لغات", "مهارات شخصية"]])
        duration_field = ft.TextField(label="عدد الساعات", value="40", width=400, keyboard_type=ft.KeyboardType.NUMBER)
        fee_field = ft.TextField(label="الرسوم", value="5000", width=400, keyboard_type=ft.KeyboardType.NUMBER)
        instructor_field = ft.TextField(label="اسم المدرب", width=400)

        def save_training(btn_e):
            if not name_field.value:
                show_snackbar(btn_e.page, "اسم التدريب مطلوب", ft.Colors.RED)
                return
            training_data = {
                "TrainingName": name_field.value.strip(),
                "Category": category_dropdown.value or "غير محدد",
                "DurationHours": int(duration_field.value or 40),
                "Fee": float(fee_field.value or 5000),
                "Instructor": instructor_field.value or "غير محدد",
                "Status": "Upcoming"
            }
            try:
                training_id = db.add_training(training_data)
                show_snackbar(btn_e.page, f"تم إضافة التدريب رقم {training_id}")
                btn_e.page.close(dlg)
                load_trainings()
            except Exception as ex:
                show_snackbar(btn_e.page, f"خطأ: {str(ex)}", ft.Colors.RED)

        dlg = ft.AlertDialog(title=ft.Text("إضافة تدريب جديد"), content=ft.Column([name_field, category_dropdown, duration_field, fee_field, instructor_field]), actions=[
            ft.TextButton("إلغاء", on_click=lambda e: e.page.close(dlg)),
            ft.FilledButton("حفظ التدريب", on_click=save_training)
        ])
        e.page.open(dlg)

    load_trainings()

    return ft.View(route="/trainings",
        controls=[
            ft.Column(
                controls=[
                    ft.Row([ft.Text("إدارة التدريبات", size=26, weight="bold", color=ft.Colors.BLUE_900),
                            ft.FilledButton("إضافة تدريب جديد", on_click=add_new_training)],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=2, color=ft.Colors.BLUE_100),
                    ft.Text("قائمة التدريبات المتاحة", size=18, weight="bold"),
                    ft.Container(height=20),
                    trainings_container
                ],
                scroll=ft.ScrollMode.AUTO
            )
        ]
    )


# ==================== 5. نظام الحضور الذكي ====================
def attendance_view() -> ft.View:
    qr_image = ft.Image(width=300, height=300, fit=ft.ImageFit.CONTAIN, border_radius=10, src_base64="")
    qr_info_text = ft.Text("لا يوجد QR Code حالياً", size=14, color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER)
    upcoming_sessions_container = ft.Container()

    def generate_new_qr(e):
        session_data = {
            "TrainingID": 1,
            "SessionNumber": db.get_next_session_number(1),
            "SessionDate": datetime.now().date(),
            "StartTime": "10:00",
            "EndTime": "12:00",
            "Topic": "جلسة تجريبية"
        }
        try:
            session_id, qr_base64 = db.create_training_session(session_data)
            qr_image.src_base64 = qr_base64
            qr_info_text.value = f"كود الجلسة: {session_id}\nالتاريخ: {session_data['SessionDate']}\nالوقت: {session_data['StartTime']} - {session_data['EndTime']}"
            show_snackbar(e.page, "تم إنشاء QR Code جديد بنجاح!")
            load_upcoming_sessions()
        except Exception as ex:
            show_snackbar(e.page, f"خطأ في إنشاء QR: {str(ex)}", ft.Colors.RED)

    def load_upcoming_sessions():
        sessions = db.get_upcoming_sessions(limit=10)
        if not sessions:
            upcoming_sessions_container.content = ft.Text("لا توجد جلسات قادمة")
            upcoming_sessions_container.update()
            return

        session_list = ft.Column([ft.Card(content=ft.Container(content=ft.ListTile(
            leading=ft.Icon(ft.Icons.CALENDAR_MONTH, color=ft.Colors.BLUE_700),
            title=ft.Text(f"{s['TrainingName']} - جلسة {s['SessionNumber']}"),
            subtitle=ft.Text(f"{s['SessionDate']} | {s['StartTime']} - {s['EndTime']} | موضوع: {s['Topic']}"),
            trailing=ft.Text(f"{s['Attendees']} حاضر", weight="bold", color=ft.Colors.GREEN_800)
        ), padding=10), elevation=2, margin=5) for s in sessions], scroll=ft.ScrollMode.AUTO, height=300)
        upcoming_sessions_container.content = session_list
        upcoming_sessions_container.update()

    load_upcoming_sessions()

    return ft.View(route="/attendance",
        controls=[
            ft.Column(
                controls=[
                    ft.Text("نظام الحضور الذكي", size=26, weight="bold", color=ft.Colors.BLUE_900),
                    ft.Divider(height=2, color=ft.Colors.BLUE_100),
                    ft.ResponsiveRow(controls=[
                        ft.Container(content=ft.Column([
                            ft.Text("QR Code لتسجيل الحضور", size=20, weight="bold"),
                            ft.Container(height=20),
                            qr_image,
                            qr_info_text,
                            ft.Container(height=20),
                            ft.FilledButton("إنشاء QR Code جديد", icon=ft.Icons.QR_CODE_2, on_click=generate_new_qr, width=300)
                        ], horizontal_alignment="center"), padding=20, bgcolor=ft.Colors.WHITE, border_radius=10, col={"sm": 12, "md": 6}),
                        ft.Container(content=ft.Column([
                            ft.Text("طرق تسجيل الحضور المتاحة", size=20, weight="bold"),
                            ft.Container(height=10),
                            ft.Card(content=ft.Container(content=ft.Column([
                                ft.ListTile(leading=ft.Icon(ft.Icons.QR_CODE_SCANNER, color=ft.Colors.GREEN_700, size=40), title=ft.Text("مسح QR Code", weight="bold"), subtitle=ft.Text("عبر كاميرا الموبايل")),
                                ft.ListTile(leading=ft.Icon(ft.Icons.SMS, color=ft.Colors.BLUE_700, size=40), title=ft.Text("إرسال كود عبر SMS", weight="bold"), subtitle=ft.Text("إرسال الكود إلى رقم 1212")),
                            ]), padding=10), elevation=3),
                            ft.Container(height=30),
                            ft.Text("الجلسات القادمة", size=20, weight="bold"),
                            upcoming_sessions_container
                        ]), padding=20, bgcolor=ft.Colors.WHITE, border_radius=10, col={"sm": 12, "md": 6}),
                    ])
                ],
                scroll=ft.ScrollMode.AUTO
            )
        ]
    )


# ==================== 6. العملاء والمطابقة ====================
def clients_view() -> ft.View:
    clients_container = ft.Container()

    def load_clients():
        clients = db.get_all_clients()
        columns = [
            {'title': 'اسم الشركة', 'key': 'CompanyName'},
            {'title': 'المجال', 'key': 'Industry'},
            {'title': 'عدد المطلوب', 'key': 'RequiredCount', 'format': lambda x: f"{x} مرشح"},
            {'title': 'نطاق الراتب', 'key': 'SalaryRange'},
            {'title': 'الحالة', 'key': 'Status'},
        ]

        def view_client_requests(e, item):
            requests = db.get_requests_by_client(item['ClientID'])
            candidates = db.get_all_candidates()
            request_list = ft.Column()
            if requests:
                for req in requests:
                    request_list.controls.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text(f"الوظيفة: {req['JobTitle']}"),
                                    ft.Text(f"العدد المطلوب: {req['NeededCount']}"),
                                    ft.Text(f"الحالة: {req['RequestStatus']}"),
                                    ft.FilledButton(
                                        "مطابقة مرشحين",
                                        icon=ft.Icons.PERSON_SEARCH,
                                        on_click=lambda e, r=req: match_candidates(e.page, r['RequestID'], candidates)
                                    )
                                ]),
                                padding=15
                            ),
                            elevation=3,
                            margin=5
                        )
                    )
            else:
                request_list.controls.append(ft.Text("لا توجد طلبات توظيف بعد"))

            dlg = ft.AlertDialog(
                title=ft.Text(f"طلبات توظيف - {item['CompanyName']}"),
                content=ft.Column([request_list], scroll=ft.ScrollMode.AUTO, height=400),
                actions=[ft.TextButton("إغلاق", on_click=lambda e: e.page.close(dlg))]
            )
            e.page.open(dlg)

        actions = {
            'buttons': [
                {
                    'icon': ft.Icons.LIST,  # ✅ بديل مضمون بدل VIEW_LIST
                    'tooltip': 'عرض طلبات التوظيف',
                    'handler': view_client_requests
                }
            ]
        }

        table = create_table(columns, clients, actions)
        clients_container.content = table
        clients_container.update()

    def match_candidates(page, request_id, candidates):
        candidate_dropdown = ft.Dropdown(
            label="اختر المرشح للمطابقة",
            width=350,
            options=[ft.dropdown.Option(key=str(c['CandidateID']), text=f"{c['FullName']} - {c['EducationLevel']}") for c in candidates]
        )

        def save_match(btn_e):
            if not candidate_dropdown.value:
                show_snackbar(btn_e.page, "اختر المرشح", ft.Colors.RED)
                return
            match_data = {"CandidateID": int(candidate_dropdown.value), "RequestID": request_id, "MatchScore": 85, "Status": "Pending"}
            try:
                match_id = db.match_candidate_to_request(match_data)
                show_snackbar(btn_e.page, f"تمت المطابقة رقم {match_id}")
                btn_e.page.close(dlg)
            except Exception as ex:
                show_snackbar(btn_e.page, f"خطأ: {str(ex)}", ft.Colors.RED)

        dlg = ft.AlertDialog(
            title=ft.Text("مطابقة مرشح مع طلب توظيف"),
            content=candidate_dropdown,
            actions=[
                ft.TextButton("إلغاء", on_click=lambda e: e.page.close(dlg)),
                ft.FilledButton("تأكيد المطابقة", icon=ft.Icons.CHECK, on_click=save_match)
            ]
        )
        page.open(dlg)

    def add_new_client(e):
        company_name = ft.TextField(label="اسم الشركة", width=400)
        industry = ft.TextField(label="المجال", width=400)
        required_count = ft.TextField(label="عدد المرشحين المطلوب", width=400, keyboard_type=ft.KeyboardType.NUMBER)
        salary_range = ft.TextField(label="نطاق الراتب", width=400)

        def save_client(btn_e):
            if not company_name.value:
                show_snackbar(btn_e.page, "اسم الشركة مطلوب", ft.Colors.RED)
                return
            client_data = {
                "CompanyName": company_name.value.strip(),
                "Industry": industry.value or "غير محدد",
                "RequiredCount": int(required_count.value or 0),
                "SalaryRange": salary_range.value or "غير محدد",
                "Status": "Active"
            }
            try:
                client_id = db.add_client(client_data)
                show_snackbar(btn_e.page, f"تم إضافة العميل رقم {client_id}")
                btn_e.page.close(dlg)
                load_clients()
            except Exception as ex:
                show_snackbar(btn_e.page, f"خطأ: {str(ex)}", ft.Colors.RED)

        dlg = ft.AlertDialog(
            title=ft.Text("إضافة عميل جديد"),
            content=ft.Column([company_name, industry, required_count, salary_range]),
            actions=[
                ft.TextButton("إلغاء", on_click=lambda e: e.page.close(dlg)),
                ft.FilledButton("حفظ العميل", icon=ft.Icons.SAVE, on_click=save_client)
            ]
        )
        e.page.open(dlg)

    load_clients()

    return ft.View(
        route="/clients",
        controls=[
            ft.Column(
                controls=[
                    ft.Row(
                        [
                            ft.Text("العملاء والمطابقة", size=26, weight="bold", color=ft.Colors.BLUE_900),
                            ft.FilledButton("إضافة عميل جديد", icon=ft.Icons.ADD_BUSINESS, on_click=add_new_client)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(height=2, color=ft.Colors.BLUE_100),
                    ft.Text("قائمة الشركات والعملاء", size=18, weight="bold"),
                    ft.Container(height=20),
                    clients_container
                ],
                scroll=ft.ScrollMode.AUTO
            )
        ]
    )


# ==================== 7. الفواتير والمدفوعات ====================
def invoices_view() -> ft.View:
    invoices_container = ft.Container()

    def load_invoices():
        invoices = db.get_pending_invoices()
        columns = [
            {'title': 'رقم الفاتورة', 'key': 'InvoiceID'},
            {'title': 'المرشح', 'key': 'FullName'},
            {'title': 'نوع الفاتورة', 'key': 'InvoiceType'},
            {'title': 'المبلغ الكلي', 'key': 'Amount', 'format': lambda x: f"{x:,.2f} ج.م"},
            {'title': 'المسدد', 'key': 'PaidAmount', 'format': lambda x: f"{x:,.2f} ج.م"},
            {'title': 'المتبقي', 'key': 'Remaining', 'format': lambda x: f"{x:,.2f} ج.م"},
            {'title': 'تاريخ الاستحقاق', 'key': 'DueDate', 'format': lambda x: x.strftime('%Y-%m-%d') if x else ''},
        ]

        def record_payment(e, item):
            amount_field = ft.TextField(label="المبلغ المسدد", width=300, keyboard_type=ft.KeyboardType.NUMBER)
            date_field = ft.TextField(label="تاريخ السداد", value=datetime.now().strftime('%Y-%m-%d'), width=300)

            def save_payment(btn_e):
                if not amount_field.value:
                    show_snackbar(btn_e.page, "أدخل المبلغ المسدد", ft.Colors.RED)
                    return
                payment_data = {"InvoiceID": item['InvoiceID'], "PaidAmount": float(amount_field.value), "PaymentDate": date_field.value}
                try:
                    db.record_payment(payment_data)
                    show_snackbar(btn_e.page, "تم تسجيل السداد بنجاح")
                    btn_e.page.close(dlg)
                    load_invoices()
                except Exception as ex:
                    show_snackbar(btn_e.page, f"خطأ: {str(ex)}", ft.Colors.RED)

            dlg = ft.AlertDialog(title=ft.Text(f"تسجيل سداد لفاتورة {item['InvoiceID']}"), content=ft.Column([amount_field, date_field]), actions=[
                ft.TextButton("إلغاء", on_click=lambda e: e.page.close(dlg)),
                ft.FilledButton("تسجيل السداد", on_click=save_payment)
            ])
            e.page.open(dlg)

        actions = {'buttons': [
            {'icon': ft.Icons.PAYMENT, 'tooltip': 'تسجيل سداد', 'handler': record_payment}
        ]}
        table = create_table(columns, invoices, actions)
        invoices_container.content = table
        invoices_container.update()

    def create_new_invoice(e):
        candidate_dropdown = ft.Dropdown(label="اختر المرشح", width=400, options=[ft.dropdown.Option(key=str(c['CandidateID']), text=c['FullName']) for c in db.get_all_candidates()])
        type_dropdown = ft.Dropdown(label="نوع الفاتورة", width=400, options=[ft.dropdown.Option("ExamFee", "رسوم امتحان"), ft.dropdown.Option("TrainingFee", "رسوم تدريب"), ft.dropdown.Option("Other", "أخرى")], value="TrainingFee")
        amount_field = ft.TextField(label="المبلغ الكلي", width=400, keyboard_type=ft.KeyboardType.NUMBER, value="5000")
        due_date_field = ft.TextField(label="تاريخ الاستحقاق", value=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'), width=400)

        def save_invoice(btn_e):
            if not candidate_dropdown.value or not amount_field.value:
                show_snackbar(btn_e.page, "اختر المرشح وأدخل المبلغ", ft.Colors.RED)
                return
            invoice_data = {"CandidateID": int(candidate_dropdown.value), "InvoiceType": type_dropdown.value, "Amount": float(amount_field.value), "DueDate": due_date_field.value, "Status": "Pending"}
            try:
                invoice_id = db.create_invoice(invoice_data)
                show_snackbar(btn_e.page, f"تم إنشاء فاتورة جديدة رقم {invoice_id}")
                btn_e.page.close(dlg)
                load_invoices()
            except Exception as ex:
                show_snackbar(btn_e.page, f"خطأ: {str(ex)}", ft.Colors.RED)

        dlg = ft.AlertDialog(title=ft.Text("إنشاء فاتورة جديدة"), content=ft.Column([candidate_dropdown, type_dropdown, amount_field, due_date_field]), actions=[
            ft.TextButton("إلغاء", on_click=lambda e: e.page.close(dlg)),
            ft.FilledButton("إنشاء الفاتورة", on_click=save_invoice)
        ])
        e.page.open(dlg)

    load_invoices()

    return ft.View(route="/invoices",
        controls=[
            ft.Column(
                controls=[
                    ft.Row([ft.Text("الفواتير والمدفوعات", size=26, weight="bold", color=ft.Colors.BLUE_900),
                            ft.FilledButton("إنشاء فاتورة جديدة", on_click=create_new_invoice)],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=2, color=ft.Colors.BLUE_100),
                    ft.Text("الفواتير المعلقة", size=18, weight="bold"),
                    ft.Container(height=20),
                    invoices_container
                ],
                scroll=ft.ScrollMode.AUTO
            )
        ]
    )


# ==================== 8. التقارير والإحصائيات ====================
def reports_view() -> ft.View:
    period_dropdown = ft.Dropdown(label="الفترة الزمنية", width=200, value="الشهر الحالي", options=[
        ft.dropdown.Option("الأسبوع الحالي"), ft.dropdown.Option("الشهر الحالي"), ft.dropdown.Option("الثلاثة أشهر الأخيرة"),
        ft.dropdown.Option("السنة الحالية"), ft.dropdown.Option("كل الوقت")
    ])
    reports_grid = ft.GridView(max_extent=220, child_aspect_ratio=1.0, spacing=20, run_spacing=20)
    recent_reports_container = ft.Container()

    report_types = [
        {"name": "تقرير المرشحين", "icon": ft.Icons.PEOPLE, "color": ft.Colors.BLUE_700, "desc": "إحصائيات التسجيل والحالة"},
        {"name": "تقرير التدريبات", "icon": ft.Icons.SCHOOL, "color": ft.Colors.GREEN_700, "desc": "الحضور والتقييم"},
        {"name": "تقرير المالية", "icon": ft.Icons.ATTACH_MONEY, "color": ft.Colors.AMBER_700, "desc": "الإيرادات والفواتير"},
        {"name": "تقرير الحضور", "icon": ft.Icons.CHECK_CIRCLE, "color": ft.Colors.PURPLE_700, "desc": "نسب الحضور بالجلسات"},
        {"name": "تقرير العملاء", "icon": ft.Icons.BUSINESS, "color": ft.Colors.TEAL_700, "desc": "طلبات التوظيف والمطابقة"},
        {"name": "تقرير المطابقة", "icon": ft.Icons.HANDSHAKE, "color": ft.Colors.PINK_700, "desc": "معدل التوظيف الناجح"},
    ]

    def generate_report(e, report_name):
        show_snackbar(e.page, f"جارٍ إنشاء {report_name}... (سيتم التنزيل قريبًا)")

    for report in report_types:
        reports_grid.controls.append(ft.Container(
            content=ft.FilledButton(content=ft.Column([
                ft.Icon(report["icon"], size=50, color=report["color"]),
                ft.Text(report["name"], size=16, weight="bold", text_align="center"),
                ft.Text(report["desc"], size=12, color=ft.Colors.GREY_700, text_align="center")
            ], horizontal_alignment="center", spacing=10),
            style=ft.ButtonStyle(bgcolor=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=15), padding=20, elevation=5),
            on_click=lambda e, n=report["name"]: generate_report(e, n)),
            alignment=ft.Alignment(0, 0)
        ))

    def load_recent_reports():
        recent = [
            {"name": "تقرير الحضور الشهري", "date": "2026-01-01", "size": "2.4 MB"},
            {"name": "تقرير المالية الربع سنوي", "date": "2025-12-15", "size": "3.1 MB"},
            {"name": "تقرير المرشحين الجدد", "date": "2025-12-10", "size": "1.8 MB"},
        ]
        table = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("اسم التقرير")), ft.DataColumn(ft.Text("التاريخ")), ft.DataColumn(ft.Text("الحجم")), ft.DataColumn(ft.Text("تحميل"))
        ], rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(r["name"])), ft.DataCell(ft.Text(r["date"])), ft.DataCell(ft.Text(r["size"])),
                ft.DataCell(ft.IconButton(ft.Icons.DOWNLOAD, tooltip="تحميل", on_click=lambda e: show_snackbar(e.page, f"تم تحميل {r['name']}")))
            ]) for r in recent
        ], border=ft.Border.all(1, ft.Colors.GREY_300), border_radius=10)
        recent_reports_container.content = table
        recent_reports_container.update()

    load_recent_reports()
    period_dropdown.on_change = lambda e: load_recent_reports()

    return ft.View(route="/reports",
        controls=[
            ft.Column(
                controls=[
                    ft.Row([ft.Text("التقارير والإحصائيات", size=26, weight="bold", color=ft.Colors.BLUE_900), period_dropdown], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=2, color=ft.Colors.BLUE_100),
                    ft.Text("اختر نوع التقرير لتوليده", size=18, weight="bold"),
                    ft.Container(height=20),
                    reports_grid,
                    ft.Container(height=40),
                    ft.Text("التقارير الحديثة", size=20, weight="bold"),
                    ft.Container(height=10),
                    recent_reports_container
                ],
                scroll=ft.ScrollMode.AUTO
            )
        ]
    )


# ==================== التطبيق الرئيسي والروتات ====================
def main(page: ft.Page):
    page.title = "نظام إدارة التدريب والموارد البشرية"
    page.window_width = 1400
    page.window_height = 900
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    body = ft.Container(expand=True, padding=20)

    def open_view(view_factory):
        try:
            v = view_factory()
            body.content = v.controls[0] if v.controls else ft.Text("View فارغة")
        except Exception as ex:
            body.content = ft.Column([
                ft.Text("❌ خطأ أثناء فتح الشاشة", size=18, color=ft.Colors.RED, weight="bold"),
                ft.Text(str(ex), color=ft.Colors.RED),
            ])
        page.update()

    # ✅ أزرار اختبار كل الشاشات (بدون Routing)
    sidebar = ft.Container(
        width=240,
        bgcolor=ft.Colors.BLUE_GREY_50,
        padding=15,
        content=ft.Column(
            controls=[
                ft.Text("اختبار الموديولات", size=18, weight="bold"),
                ft.Divider(),
                ft.ElevatedButton("Dashboard", icon=ft.Icons.DASHBOARD, on_click=lambda e: open_view(dashboard_view)),
                ft.ElevatedButton("Landing", icon=ft.Icons.APP_REGISTRATION, on_click=lambda e: open_view(phase1_landing_page)),
                ft.ElevatedButton("Sales", icon=ft.Icons.CAMPAIGN, on_click=lambda e: open_view(phase1_sales_dashboard)),
                ft.ElevatedButton("Exam Scheduling", icon=ft.Icons.SCHEDULE, on_click=lambda e: open_view(phase1_exam_scheduling)),
                ft.ElevatedButton("Trainings", icon=ft.Icons.SCHOOL, on_click=lambda e: open_view(phase2_trainings_management)),
                ft.ElevatedButton("Attendance", icon=ft.Icons.QR_CODE_2, on_click=lambda e: open_view(attendance_view)),
                ft.ElevatedButton("Clients", icon=ft.Icons.BUSINESS, on_click=lambda e: open_view(clients_view)),
                ft.ElevatedButton("Invoices", icon=ft.Icons.RECEIPT_LONG, on_click=lambda e: open_view(invoices_view)),
                ft.ElevatedButton("Reports", icon=ft.Icons.ASSESSMENT, on_click=lambda e: open_view(reports_view)),
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )
    )

    # ✅ أول شاشة: Login (بدون Routing) وتمرير open_view لها
    body.content = login_view(open_view=open_view).controls[0]

    page.add(
        ft.Row(
            controls=[sidebar, body],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH
        )
    )

if __name__ == "__main__":
    ft.run(main, view=ft.AppView.FLET_APP)


