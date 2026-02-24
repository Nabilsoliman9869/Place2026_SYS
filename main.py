import flet as ft
from datetime import datetime
import database as db
import traceback

# ==================== UI HELPERS ====================
def show_snackbar(page: ft.Page, message: str, color=ft.Colors.GREEN):
    page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
    page.snack_bar.open = True
    page.update()

def create_table(columns: list, data: list, actions: dict = None) -> ft.DataTable:
    table_columns = [ft.DataColumn(ft.Text(col["title"])) for col in columns]
    if actions:
        table_columns.append(ft.DataColumn(ft.Text("إجراءات")))

    rows = []
    for item in data:
        cells = []
        for col in columns:
            val = item.get(col["key"], "")
            cells.append(ft.DataCell(ft.Text(str(val))))
        
        if actions:
            action_buttons = []
            for btn in actions:
                # Check condition if exists
                if "condition" in btn and not btn["condition"](item):
                    continue
                    
                action_buttons.append(
                    ft.IconButton(
                        icon=btn["icon"],
                        tooltip=btn["tooltip"],
                        icon_color=btn.get("color", ft.Colors.BLUE),
                        on_click=lambda e, i=item, h=btn["handler"]: h(e, i)
                    )
                )
            cells.append(ft.DataCell(ft.Row(action_buttons, spacing=0)))
        
        rows.append(ft.DataRow(cells=cells))

    return ft.DataTable(
        columns=table_columns,
        rows=rows,
        border=ft.Border.all(1, ft.Colors.GREY_300),
        vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
        heading_row_color=ft.Colors.BLUE_50,
    )

def create_tabs_layout(tabs_config: list, initial_index=0) -> ft.Column:
    content_area = ft.Container(content=tabs_config[initial_index]["content"], expand=True)
    
    def on_change(e):
        try:
            index = e.control.selected_index
            if index is not None and 0 <= index < len(tabs_config):
                content_area.content = tabs_config[index]["content"]
                content_area.update()
        except Exception as ex:
            print(f"Error switching tab: {ex}")
            traceback.print_exc()

    tab_bar = ft.TabBar(
        tabs=[ft.Tab(text=t["label"]) if hasattr(ft.Tab(), "text") else ft.Tab(label=t["label"]) for t in tabs_config]
    )
    
    if hasattr(tab_bar, "on_change"):
        tab_bar.on_change = on_change
    
    if hasattr(tab_bar, "selected_index"):
        tab_bar.selected_index = initial_index
    
    return ft.Column([
        tab_bar,
        content_area
    ], expand=True)

# ==================== MAIN APP CLASS ====================
class TrainingApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "نظام إدارة التدريب والتوظيف 2026"
        self.page.rtl = True
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window.width = 1200
        self.page.window.height = 800
        
        # Current User State
        self.user = None
        
        # Navigation State
        self.current_view = "dashboard"
        
        self.show_login()

    # ==================== LOGIN ====================
    def show_login(self):
        self.page.clean()
        
        username = ft.TextField(label="اسم المستخدم", width=300)
        password = ft.TextField(label="كلمة المرور", password=True, width=300, can_reveal_password=True)
        
        def login_handler(e):
            # Try DB Login first
            user_data = db.authenticate_user(username.value, password.value)
            
            # Fallback for dev/testing if DB is empty or issues
            if not user_data and username.value == "manager" and password.value == "manager123":
                user_data = {"Username": "manager", "Role": "Manager"}
            
            if user_data:
                self.user = user_data
                show_snackbar(self.page, f"مرحباً {user_data['Username']} ({user_data['Role']})")
                self.build_main_layout()
            else:
                show_snackbar(self.page, "بيانات الدخول غير صحيحة", ft.Colors.RED)

        # Background Image Container
        self.page.add(
            ft.Container(
                image=ft.DecorationImage(src="assets/login_photo.jpg", fit="cover"),
                expand=True,
                alignment=ft.Alignment(0, 0),
                content=ft.Container(
                    bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                    padding=50,
                    border_radius=20,
                    content=ft.Column(
                        [
                            ft.Text("تسجيل الدخول", size=30, weight="bold", color=ft.Colors.BLUE_900),
                            username,
                            password,
                            ft.FilledButton("دخول", width=300, on_click=login_handler)
                        ],
                        tight=True,
                        horizontal_alignment="center"
                    )
                )
            )
        )

    # ==================== MAIN LAYOUT ====================
    def build_main_layout(self):
        self.page.clean()
        
        self.content_area = ft.Container(expand=True, padding=20)
        
        
        # Role-based Navigation
        role = self.user['Role']
        
        nav_items = [
            ft.Text("Place 2026", color="white", size=24, weight="bold"),
            ft.Divider(color="white24"),
            self.nav_button("لوحة التحكم", ft.Icons.DASHBOARD, "dashboard")
        ]
        
        # Corporate Menu
        if role in ["Manager", "Corporate"]:
            nav_items.append(self.nav_button("خدمة الشركات", ft.Icons.BUSINESS, "corporate"))
            
        # Sales Menu
        if role in ["Manager", "Sales"]:
            nav_items.append(self.nav_button("المبيعات والتسويق", ft.Icons.CAMPAIGN, "sales"))
            
        # Training Menu
        if role in ["Manager", "Trainer"]:
            nav_items.append(self.nav_button("التدريب والامتحانات", ft.Icons.SCHOOL, "training"))
            
        # Finance Menu
        if role in ["Manager"]: # Only Manager for now, maybe accountant later
            nav_items.append(self.nav_button("الإدارة المالية", ft.Icons.MONETIZATION_ON, "finance"))
            
        nav_items.extend([
            ft.Divider(color="white24"),
            self.nav_button("تسجيل خروج", ft.Icons.LOGOUT, "logout", color=ft.Colors.RED_400)
        ])
        
        sidebar = ft.Container(
            width=250,
            bgcolor=ft.Colors.BLUE_GREY_900,
            padding=10,
            content=ft.Column(nav_items)
        )
        
        self.page.add(
            ft.Row(
                [sidebar, self.content_area],
                expand=True,
                spacing=0
            )
        )
        self.navigate("dashboard")

    def nav_button(self, text, icon, view_name, color="white"):
        return ft.Container(
            content=ft.Row([ft.Icon(icon, color=color), ft.Text(text, color=color, size=16)]),
            padding=10,
            border_radius=5,
            ink=True,
            on_click=lambda e: self.navigate(view_name)
        )

    def navigate(self, view_name):
        self.content_area.content = ft.ProgressRing()
        self.page.update()
        
        if view_name == "logout":
            self.user = None
            self.show_login()
            return
            
        if view_name == "dashboard":
            self.content_area.content = self.view_dashboard()
        elif view_name == "corporate":
            self.content_area.content = self.view_corporate()
        elif view_name == "sales":
            self.content_area.content = self.view_sales()
        elif view_name == "training":
            self.content_area.content = self.view_training()
        elif view_name == "finance":
            self.content_area.content = self.view_finance()
            
        self.content_area.update()

    # ==================== VIEWS ====================
    def view_dashboard(self):
        stats = db.get_dashboard_stats()
        return ft.Column([
            ft.Text("لوحة التحكم", size=30, weight="bold"),
            ft.Row([
                self.stat_card("المرشحين", stats.get('total_candidates', 0), ft.Colors.BLUE_100),
                self.stat_card("تم التوظيف", stats.get('hired_candidates', 0), ft.Colors.GREEN_100),
                self.stat_card("نسبة النجاح", f"{stats.get('exam_success_rate', 0)}%", ft.Colors.ORANGE_100),
            ])
        ])

    def stat_card(self, title, value, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(str(value), size=40, weight="bold"),
                ft.Text(title, size=16)
            ], horizontal_alignment="center"),
            bgcolor=color, padding=20, border_radius=10, expand=True
        )

    # ----- CORPORATE -----
    def view_corporate(self):
        # Tabs: Clients, Requests
        clients = db.get_all_clients()
        
        def add_request_handler(e, item):
            self.open_add_request_dialog(item['ClientID'], item['CompanyName'])
            
        def add_client_handler(e):
            print("DEBUG: add_client_handler clicked") # DEBUG
            self.open_add_client_dialog()

        clients_table = create_table(
            [{"title": "ID", "key": "ClientID"}, {"title": "الشركة", "key": "CompanyName"}, {"title": "الهاتف", "key": "Phone"}],
            clients,
            [{"icon": ft.Icons.ADD, "tooltip": "إضافة طلب توظيف", "handler": add_request_handler}]
        )

        requests = db.fetch_all("SELECT r.*, c.CompanyName FROM ClientRequests r JOIN Clients c ON r.ClientID = c.ClientID")
        
        def add_campaign_handler(e, item):
            self.open_add_campaign_dialog(item['RequestID'], item['JobTitle'])

        def search_candidate_handler(e, item):
            self.open_match_dialog(item)

        requests_table = create_table(
            [{"title": "الوظيفة", "key": "JobTitle"}, {"title": "الشركة", "key": "CompanyName"}, {"title": "العدد", "key": "NeededCount"}, {"title": "الحالة", "key": "Status"}],
            requests,
            [
                {"icon": ft.Icons.CAMPAIGN, "tooltip": "إنشاء حملة", "handler": add_campaign_handler},
                {"icon": ft.Icons.SEARCH, "tooltip": "بحث عن مرشحين", "handler": search_candidate_handler, "color": ft.Colors.ORANGE},
            ]
        )

        return create_tabs_layout([
            {"label": "العملاء", "content": ft.Column([
                ft.Row([
                    ft.FilledButton("إضافة عميل جديد", icon=ft.Icons.ADD, on_click=add_client_handler, style=ft.ButtonStyle(bgcolor={ft.ControlState.HOVERED: ft.Colors.BLUE_700})),
                    ft.IconButton(ft.Icons.REFRESH, tooltip="تحديث", on_click=lambda e: self.navigate("corporate"))
                ]),
                clients_table
            ], scroll=True)},
            {"label": "طلبات التوظيف", "content": ft.Column([requests_table], scroll=True)}
        ])

    # ----- SALES -----
    def view_sales(self):
        campaigns = db.get_campaigns()
        
        def add_lead_handler(e, item):
            self.open_add_lead_dialog(item['CampaignID'])

        campaigns_table = create_table(
            [{"title": "الحملة", "key": "CampaignName"}, {"title": "المنصة", "key": "Platform"}, {"title": "الوظيفة", "key": "JobTitle"}, {"title": "الإعلان", "key": "AdText"}],
            campaigns,
            [{"icon": ft.Icons.PERSON_ADD, "tooltip": "تسجيل مهتم (Lead)", "handler": add_lead_handler}]
        )

        leads = db.get_all_interests()
        
        def schedule_exam_handler(e, item):
            self.open_schedule_exam_dialog(item)

        leads_table = create_table(
            [{"title": "الاسم", "key": "FullName"}, {"title": "الهاتف", "key": "Phone"}, {"title": "المصدر", "key": "CampaignName"}, {"title": "الحالة", "key": "Status"}],
            leads,
            [{"icon": ft.Icons.ASSIGNMENT, "tooltip": "حجز امتحان", "handler": schedule_exam_handler}]
        )

        # Training Leads (Upselling) - Moved from Training tab logic but kept access
        training_leads = db.fetch_all("SELECT c.* FROM Candidates c LEFT JOIN ExamAppointments a ON c.CandidateID = a.CandidateID WHERE c.Status IN ('TrainingNeeded', 'PlacementFailed')")
        
        def offer_course_handler(e, item):
            self.open_enroll_dialog(item)

        training_leads_table = create_table(
            [{"title": "المرشح", "key": "FullName"}, {"title": "الهاتف", "key": "Phone"}, {"title": "المستوى", "key": "EducationLevel"}],
            training_leads,
            [{"icon": ft.Icons.SCHOOL, "tooltip": "عرض دورة تدريبية", "handler": offer_course_handler}]
        )

        return create_tabs_layout([
            {"label": "الحملات الإعلانية", "content": ft.Column([campaigns_table], scroll=True)},
            {"label": "متابعة المهتمين", "content": ft.Column([
                ft.Row([ft.FilledButton("إعداد مواعيد الامتحانات", on_click=lambda e: self.open_manage_sessions_dialog())]),
                leads_table
            ], scroll=True)},
            {"label": "فرص التدريب (Upsell)", "content": ft.Column([training_leads_table], scroll=True)}
        ])

    # ----- TRAINING -----
    def view_training(self):
        # Exam Results
        exams = db.fetch_all("SELECT a.*, c.FullName, e.ExamName FROM ExamAppointments a JOIN Candidates c ON a.CandidateID = c.CandidateID JOIN Exams e ON a.ExamID = e.ExamID WHERE a.ResultStatus IS NULL")
        
        def result_handler(e, item):
            self.open_exam_result_dialog(item)
            
        exams_table = create_table(
            [{"title": "المرشح", "key": "FullName"}, {"title": "الامتحان", "key": "ExamName"}, {"title": "التاريخ", "key": "AppointmentDate"}],
            exams,
            [{"icon": ft.Icons.STAR, "tooltip": "رصد النتيجة", "handler": result_handler}]
        )

        # Courses
        courses = db.get_all_trainings()
        courses_table = create_table(
            [{"title": "الدورة", "key": "TrainingName"}, {"title": "المدرب", "key": "InstructorName"}, {"title": "الحالة", "key": "Status"}],
            courses,
            [
                {"icon": ft.Icons.CHECK, "tooltip": "تسجيل الحضور", "handler": lambda e,i: self.open_attendance_dialog(i)},
                {"icon": ft.Icons.GRADE, "tooltip": "رصد نتائج الدورة", "handler": lambda e,i: show_snackbar(self.page, "قريباً - نتائج الدورات")}
            ]
        )

        return create_tabs_layout([
            {"label": "نتائج تحديد المستوى", "content": ft.Column([exams_table], scroll=True)},
            {"label": "الدورات الحالية", "content": ft.Column([
                ft.Row([
                    ft.FilledButton("إضافة دورة", on_click=lambda e: self.open_add_training_dialog()),
                    ft.FilledButton("إضافة مدرب", on_click=lambda e: self.open_add_instructor_dialog())
                ]),
                courses_table
            ], scroll=True)}
        ])

    # ----- FINANCE -----
    def view_finance(self):
        invoices = db.get_pending_invoices()
        
        def pay_handler(e, item):
            self.open_pay_dialog(item)
            
        inv_table = create_table(
            [{"title": "رقم الفاتورة", "key": "InvoiceID"}, {"title": "الوصف", "key": "Description"}, {"title": "المبلغ", "key": "Amount"}, {"title": "المدفوع", "key": "PaidAmount"}],
            invoices,
            [{"icon": ft.Icons.MONETIZATION_ON, "tooltip": "تحصيل / قسط", "handler": pay_handler, "color": ft.Colors.GREEN}]
        )
        
        return ft.Column([
            ft.Text("الإدارة المالية - الفواتير المستحقة", size=20, weight="bold"),
            inv_table
        ], scroll=True)

    # ==================== DIALOGS ====================
    def open_dialog(self, title, content, actions):
        print(f"DEBUG: Opening dialog {title}") # DEBUG
        try:
            # Create Dialog
            dlg = ft.AlertDialog(
                title=ft.Text(title),
                content=content,
                actions=actions,
                modal=True
            )
            # Add to overlay if not using page.dialog (Flet 0.21+ recommended approach for some cases)
            # self.page.dialog = dlg
            # dlg.open = True
            
            # Alternative approach: append to overlay
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()
            
            print("DEBUG: Dialog opened via overlay and page updated") # DEBUG
        except Exception as e:
            print(f"DEBUG ERROR in open_dialog: {e}")
            traceback.print_exc()

    def close_dialog(self, e):
        # Close the last dialog in overlay
        if self.page.overlay:
            dlg = self.page.overlay[-1]
            dlg.open = False
            self.page.overlay.remove(dlg)
            self.page.update()

    # 1. Add Client
    def open_add_client_dialog(self):
        print("DEBUG: open_add_client_dialog called") # DEBUG
        
        # Fields based on Database Schema
        name = ft.TextField(label="اسم الشركة", width=400)
        industry = ft.Dropdown(
            label="مجال العمل (Industry)", 
            width=400,
            options=[
                ft.dropdown.Option("Software"), 
                ft.dropdown.Option("Marketing"),
                ft.dropdown.Option("Construction"),
                ft.dropdown.Option("Education"),
                ft.dropdown.Option("Other")
            ]
        )
        contact = ft.TextField(label="الشخص المسؤول", width=400)
        phone = ft.TextField(label="رقم الهاتف", width=400)
        email = ft.TextField(label="البريد الإلكتروني", width=400)
        address = ft.TextField(label="العنوان", width=400) # Assuming we might want address later, or use SalaryRange field temporarily if schema rigid
        
        # Status is Active by default
        
        def save(e):
            print(f"DEBUG: Saving client {name.value}") # DEBUG
            try:
                if not name.value:
                    show_snackbar(self.page, "يرجى إدخال اسم الشركة", ft.Colors.RED)
                    return

                # Using all available fields in the UI
                db.add_client({
                    "CompanyName": name.value, 
                    "Industry": industry.value,
                    "ContactPerson": contact.value,
                    "Phone": phone.value,
                    "Email": email.value
                })
                print("DEBUG: Client saved to DB") # DEBUG
                
                # Show confirmation dialog
                def close_confirm(e):
                    print("DEBUG: close_confirm clicked")
                    try:
                        # Safe closure strategy:
                        # 1. Close all open dialogs in overlay visually first
                        for dlg in self.page.overlay:
                            dlg.open = False
                        self.page.update()
                        
                        # 2. Clear the overlay list entirely (since we want to close everything)
                        self.page.overlay.clear()
                        
                        # 3. Navigate/Refresh
                        print("DEBUG: Dialogs closed, navigating...")
                        self.navigate("corporate") # Refresh list
                        
                    except Exception as ex:
                        print(f"DEBUG ERROR in close_confirm: {ex}")
                        traceback.print_exc()

                confirm_dlg = ft.AlertDialog(
                    title=ft.Text("تمت العملية بنجاح"),
                    content=ft.Text(f"تمت إضافة العميل '{name.value}' بنجاح."),
                    actions=[ft.TextButton("موافق", on_click=close_confirm)],
                    modal=True
                )
                self.page.overlay.append(confirm_dlg)
                confirm_dlg.open = True
                self.page.update()
                
            except Exception as ex:
                print(f"DEBUG ERROR: {ex}") # DEBUG
                traceback.print_exc()
            
        content = ft.Column([
            name,
            industry,
            contact,
            phone,
            email
        ], height=400, width=450, scroll=True)
        
        self.open_dialog("إضافة عميل جديد", content, [ft.TextButton("حفظ البيانات", on_click=save), ft.TextButton("إلغاء", on_click=self.close_dialog)])

    # 2. Add Request
    def open_add_request_dialog(self, client_id, client_name):
        print(f"DEBUG: open_add_request_dialog called for client {client_id}")
        
        # Fields based on DB Schema: JobTitle, NeededCount, Requirements
        title = ft.TextField(label="المسمى الوظيفي", width=400)
        count = ft.TextField(label="العدد المطلوب", value="1", keyboard_type="number", width=400)
        requirements = ft.TextField(
            label="متطلبات الوظيفة (المهارات، الخبرة، المؤهل...)", 
            multiline=True, 
            min_lines=3, 
            max_lines=5, 
            width=400
        )
        
        def save(e):
            try:
                if not title.value:
                    show_snackbar(self.page, "يرجى إدخال المسمى الوظيفي", ft.Colors.RED)
                    return
                
                print(f"DEBUG: Saving request for {title.value}")
                
                db.add_client_request({
                    "ClientID": client_id, 
                    "JobTitle": title.value, 
                    "NeededCount": int(count.value) if count.value else 1,
                    "Requirements": requirements.value,
                    "Status": "Open" # Default status
                })
                
                # Show confirmation dialog
                def close_confirm(e):
                    # Safe closure strategy
                    for dlg in self.page.overlay:
                        dlg.open = False
                    self.page.update()
                    self.page.overlay.clear()
                    self.navigate("corporate")

                confirm_dlg = ft.AlertDialog(
                    title=ft.Text("تمت العملية بنجاح"),
                    content=ft.Text(f"تمت إضافة طلب توظيف '{title.value}' لشركة {client_name}."),
                    actions=[ft.TextButton("موافق", on_click=close_confirm)],
                    modal=True
                )
                self.page.overlay.append(confirm_dlg)
                confirm_dlg.open = True
                self.page.update()
                
            except Exception as ex:
                print(f"DEBUG ERROR: {ex}")
                traceback.print_exc()
        
        content = ft.Column([
            ft.Text(f"الشركة: {client_name}", weight="bold", size=16),
            ft.Divider(),
            title,
            count,
            requirements
        ], height=350, width=450, scroll=True)
            
        self.open_dialog(f"طلب توظيف جديد", content, [ft.TextButton("حفظ الطلب", on_click=save), ft.TextButton("إلغاء", on_click=self.close_dialog)])

    # 3. Add Campaign (UPDATED)
    def open_add_campaign_dialog(self, request_id, job_title):
        print(f"DEBUG: open_add_campaign_dialog called for req {request_id}")
        
        name = ft.TextField(label="اسم الحملة", width=400)
        platform = ft.Dropdown(
            label="المنصة", 
            width=400,
            options=[
                ft.dropdown.Option("Facebook"), 
                ft.dropdown.Option("LinkedIn"), 
                ft.dropdown.Option("Instagram"), 
                ft.dropdown.Option("Google Ads"),
                ft.dropdown.Option("Other")
            ]
        )
        ad_text = ft.TextField(label="نص الإعلان (Ad Copy)", multiline=True, min_lines=2, max_lines=4, width=400)
        target = ft.TextField(label="الجمهور المستهدف (Target Audience)", width=400)
        budget = ft.TextField(label="الميزانية التقديرية (Budget)", keyboard_type="number", width=400)
        start_date = ft.TextField(label="تاريخ البدء (YYYY-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"), width=400)
        
        def save(e):
            try:
                if not name.value:
                     show_snackbar(self.page, "يرجى إدخال اسم الحملة", ft.Colors.RED)
                     return

                db.add_campaign({
                    "RequestID": request_id, 
                    "CampaignName": name.value, 
                    "Platform": platform.value,
                    "AdText": ad_text.value,
                    "TargetAudience": target.value,
                    "Budget": float(budget.value) if budget.value else 0.0,
                    "StartDate": start_date.value,
                    "Status": "Active"
                })
                
                # Close Logic (Safe)
                for dlg in self.page.overlay:
                    dlg.open = False
                self.page.update()
                self.page.overlay.clear()
                
                show_snackbar(self.page, "تم إنشاء الحملة بنجاح")
                self.page.update()
                self.navigate("corporate")
                
            except Exception as ex:
                print(f"DEBUG ERROR: {ex}")
                traceback.print_exc()
            
        content = ft.Column([
            ft.Text(f"حملة لوظيفة: {job_title}", weight="bold"),
            name, platform, ad_text, target, budget, start_date
        ], height=400, width=450, scroll=True)
            
        self.open_dialog(f"إنشاء حملة إعلانية جديدة", content, [ft.TextButton("حفظ الحملة", on_click=save), ft.TextButton("إلغاء", on_click=self.close_dialog)])

    # 4. Add Lead
    def open_add_lead_dialog(self, campaign_id):
        print(f"DEBUG: open_add_lead_dialog called for camp {campaign_id}")
        
        name = ft.TextField(label="الاسم بالكامل", width=400)
        phone = ft.TextField(label="رقم الهاتف", width=400)
        email = ft.TextField(label="البريد الإلكتروني", width=400)
        source = ft.Dropdown(
            label="المصدر (Source)", 
            width=400,
            options=[
                ft.dropdown.Option("Social Media Ad"), 
                ft.dropdown.Option("Website"), 
                ft.dropdown.Option("Referral"), 
                ft.dropdown.Option("Walk-in")
            ]
        )
        notes = ft.TextField(label="ملاحظات أولية", multiline=True, width=400)
        
        def save(e):
            try:
                if not name.value or not phone.value:
                     show_snackbar(self.page, "الاسم والهاتف مطلوبان", ft.Colors.RED)
                     return

                db.add_interest_registration({
                    "CampaignID": campaign_id, 
                    "FullName": name.value, 
                    "Phone": phone.value,
                    "Email": email.value,
                    "Source": source.value,
                    "Notes": notes.value,
                    "Status": "New"
                })
                
                # Close Logic (Safe)
                for dlg in self.page.overlay:
                    dlg.open = False
                self.page.update()
                self.page.overlay.clear()
                
                show_snackbar(self.page, "تم تسجيل المهتم بنجاح")
                self.page.update()
                self.navigate("sales")
            
            except Exception as ex:
                print(f"DEBUG ERROR: {ex}")
                traceback.print_exc()
            
        content = ft.Column([
            name, phone, email, source, notes
        ], height=400, width=450, scroll=True)
            
        self.open_dialog("تسجيل مهتم جديد (Lead)", content, [ft.TextButton("حفظ البيانات", on_click=save), ft.TextButton("إلغاء", on_click=self.close_dialog)])

    # 5. Schedule Exam (UPDATED with Sessions & Payment)
    def open_schedule_exam_dialog(self, interest):
        cand_id = db.convert_interest_to_candidate(interest['InterestID'])
        
        # Get Available Sessions
        exams = db.get_placement_exams()
        exam_dd = ft.Dropdown(label="نوع الامتحان", options=[ft.dropdown.Option(ex['ExamID'], ex['ExamName']) for ex in exams], value=exams[0]['ExamID'] if exams else None)
        
        # Dynamic Session Dropdown based on Exam
        sessions = db.get_exam_sessions(exam_dd.value)
        session_dd = ft.Dropdown(
            label="الموعد المتاح", 
            options=[ft.dropdown.Option(s['SessionID'], f"{s['SessionDate']} ({s['CurrentCount']}/{s['MaxCapacity']})") for s in sessions]
        )
        
        is_paid = ft.Switch(label="امتحان مدفوع؟ (يصدر فاتورة)", value=True)
        
        def on_exam_change(e):
            new_sessions = db.get_exam_sessions(exam_dd.value)
            session_dd.options = [ft.dropdown.Option(s['SessionID'], f"{s['SessionDate']} ({s['CurrentCount']}/{s['MaxCapacity']})") for s in new_sessions]
            session_dd.value = None
            session_dd.update()

        exam_dd.on_change = on_exam_change

        def save(e):
            if not session_dd.value:
                show_snackbar(self.page, "الرجاء اختيار موعد", ft.Colors.RED)
                return

            # 1. Invoice if Paid
            if is_paid.value:
                db.create_invoice({"EntityID": cand_id, "EntityType": "Candidate", "InvoiceType": "PlacementExam", "Description": "رسوم امتحان تحديد مستوى", "Amount": 100})
            
            # 2. Schedule
            db.schedule_exam({
                "CandidateID": cand_id, 
                "ExamID": exam_dd.value, 
                "SessionID": session_dd.value,
                "Status": "Scheduled",
                "IsPaid": is_paid.value
            })
            
            show_snackbar(self.page, "تم حجز الامتحان")
            self.close_dialog(e)
            self.navigate("sales")
            
        self.open_dialog(
            f"حجز امتحان لـ {interest['FullName']}", 
            ft.Column([exam_dd, session_dd, is_paid], height=250), 
            [ft.TextButton("تأكيد وحجز", on_click=save)]
        )

    # 5.5 Manage Exam Sessions (NEW)
    def open_manage_sessions_dialog(self):
        exams = db.get_placement_exams()
        exam_dd = ft.Dropdown(label="الامتحان", options=[ft.dropdown.Option(ex['ExamID'], ex['ExamName']) for ex in exams])
        date = ft.TextField(label="التاريخ والوقت (YYYY-MM-DD HH:MM)", value=datetime.now().strftime("%Y-%m-%d 10:00"))
        capacity = ft.TextField(label="السعة القصوى", value="20", keyboard_type="number")
        
        def save(e):
            db.add_exam_session({
                "ExamID": exam_dd.value,
                "SessionDate": date.value,
                "MaxCapacity": int(capacity.value)
            })
            show_snackbar(self.page, "تم إضافة الموعد")
            self.close_dialog(e)
            
        self.open_dialog("إضافة موعد امتحان جديد", ft.Column([exam_dd, date, capacity], height=250), [ft.TextButton("حفظ", on_click=save)])

    # 6. Exam Result
    def open_exam_result_dialog(self, appt):
        score = ft.TextField(label="الدرجة (من 100)")
        
        def save(e):
            s = int(score.value)
            status = "Passed" if s >= 70 else "Failed"
            
            # Update Appointment
            db.exec_non_query("UPDATE ExamAppointments SET Result = ?, ResultStatus = ?, Status = 'Completed' WHERE AppointmentID = ?", (s, status, appt['AppointmentID']))
            
            # Update Candidate Status
            new_status = "ReadyForHire" if status == "Passed" else "TrainingNeeded"
            db.exec_non_query("UPDATE Candidates SET Status = ? WHERE CandidateID = ?", (new_status, appt['CandidateID']))
            
            show_snackbar(self.page, f"تم رصد النتيجة: {status}")
            self.close_dialog(e)
            self.navigate("training")
            
        self.open_dialog(f"نتيجة {appt['FullName']}", ft.Column([score], height=100), [ft.TextButton("حفظ", on_click=save)])

    # 7. Enroll Course (Upsell)
    def open_enroll_dialog(self, candidate):
        trainings = db.get_all_trainings()
        dd = ft.Dropdown(label="اختر الدورة", options=[ft.dropdown.Option(t['TrainingID'], t['TrainingName']) for t in trainings])
        
        def save(e):
            if not dd.value: return
            db.enroll_candidate({"TrainingID": dd.value, "CandidateID": candidate['CandidateID']})
            # Create Invoice
            db.create_invoice({"EntityID": candidate['CandidateID'], "EntityType": "Candidate", "InvoiceType": "CourseFee", "Description": "رسوم دورة تدريبية", "Amount": 500})
            
            show_snackbar(self.page, "تم التسجيل في الدورة")
            self.close_dialog(e)
            self.navigate("training")
            
        self.open_dialog(f"تسجيل {candidate['FullName']}", ft.Column([dd], height=100), [ft.TextButton("تسجيل", on_click=save)])

    # 7.5 Attendance Dialog (NEW)
    def open_attendance_dialog(self, course):
        # This would typically load students enrolled in this course
        # For now, just a placeholder list or mock
        # We need a function get_enrolled_students(training_id)
        
        # Let's add a quick mock query or use existing enrollments table
        enrollments = db.fetch_all("SELECT e.*, c.FullName FROM TrainingEnrollments e JOIN Candidates c ON e.CandidateID = c.CandidateID WHERE e.TrainingID = ?", (course['TrainingID'],))
        
        lv = ft.ListView(expand=True, spacing=10)
        
        for enr in enrollments:
            lv.controls.append(
                ft.Checkbox(label=enr['FullName'], value=True)
            )
            
        def save(e):
            show_snackbar(self.page, "تم حفظ الحضور (تجريبي)")
            self.close_dialog(e)
            
        self.open_dialog(f"حضور: {course['TrainingName']}", ft.Container(content=lv, height=300, width=400), [ft.TextButton("حفظ الحضور", on_click=save)])

    # 8. Match & Hire
    def open_match_dialog(self, request):
        # Find Ready Candidates
        candidates = db.fetch_all("SELECT * FROM Candidates WHERE Status = 'ReadyForHire'")
        
        lv = ft.ListView(expand=True, spacing=10)
        
        def hire(e, cand_id):
            # Match
            db.match_candidate_to_request({"RequestID": request['RequestID'], "CandidateID": cand_id, "Status": "Hired"})
            # Update Candidate
            db.exec_non_query("UPDATE Candidates SET Status = 'Hired' WHERE CandidateID = ?", (cand_id,))
            # Invoice Client
            db.create_invoice({"EntityID": request['ClientID'], "EntityType": "Client", "InvoiceType": "HiringFee", "Description": f"توظيف {request['JobTitle']}", "Amount": 2000})
            
            show_snackbar(self.page, "تم التوظيف بنجاح!")
            self.close_dialog(e)
            self.navigate("corporate")

        for c in candidates:
            lv.controls.append(
                ft.ListTile(
                    title=ft.Text(c['FullName']),
                    subtitle=ft.Text(c['EducationLevel']),
                    trailing=ft.IconButton(ft.Icons.HANDSHAKE, icon_color="green", tooltip="توظيف", on_click=lambda e, cid=c['CandidateID']: hire(e, cid))
                )
            )
            
        self.open_dialog(f"مرشحين لـ {request['JobTitle']}", ft.Container(content=lv, height=300, width=400), [ft.TextButton("إغلاق", on_click=lambda e: self.close_dialog(e))])

    # 9. Pay
    def open_pay_dialog(self, invoice):
        amount = ft.TextField(label="المبلغ المدفوع", value=str(invoice['Amount'] - invoice['PaidAmount']))
        
        def save(e):
            val = float(amount.value)
            db.add_receipt({"InvoiceID": invoice['InvoiceID'], "Amount": val})
            # Update Invoice
            new_paid = invoice['PaidAmount'] + val
            status = 'Paid' if new_paid >= invoice['Amount'] else 'Partial'
            db.exec_non_query("UPDATE Invoices SET PaidAmount = ?, Status = ? WHERE InvoiceID = ?", (new_paid, status, invoice['InvoiceID']))
            
            show_snackbar(self.page, "تم التحصيل")
            self.close_dialog(e)
            self.navigate("finance")
            
        self.open_dialog(f"تحصيل فاتورة #{invoice['InvoiceID']}", ft.Column([amount], height=100), [ft.TextButton("دفع", on_click=save)])

    # Helpers for Training View Buttons
    def open_add_training_dialog(self):
        name = ft.TextField(label="اسم الدورة")
        def save(e):
            db.add_training({"TrainingName": name.value})
            self.close_dialog(e)
            self.navigate("training")
        self.open_dialog("إضافة دورة", ft.Column([name], height=100), [ft.TextButton("حفظ", on_click=save)])

    def open_add_instructor_dialog(self):
        name = ft.TextField(label="اسم المدرب")
        def save(e):
            db.add_instructor({"Name": name.value})
            self.close_dialog(e)
            self.navigate("training")
        self.open_dialog("إضافة مدرب", ft.Column([name], height=100), [ft.TextButton("حفظ", on_click=save)])

def main(page: ft.Page):
    app = TrainingApp(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
