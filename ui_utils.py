import flet as ft
import traceback

# ==================== إدارة الصفحة العامة (Singleton Pattern) ====================
APP_PAGE = None
DIALOG_LAYER = None # طبقة النوافذ اليدوية

def set_app_page(page):
    global APP_PAGE
    APP_PAGE = page

def get_app_page():
    return APP_PAGE

def set_dialog_layer(layer):
    global DIALOG_LAYER
    DIALOG_LAYER = layer

# ==================== إعدادات أساسية ====================
def show_snackbar(page: ft.Page, message: str, color=ft.Colors.GREEN):
    print(f"DEBUG: Showing Snackbar: {message}")
    if not page: page = get_app_page()
    if not page: 
        print("ERROR: No page found for snackbar")
        return

    page.snack_bar = ft.SnackBar(content=ft.Text(message, font_family="Cairo"), bgcolor=color)
    page.snack_bar.open = True
    page.update()

# ==================== دوال مساعدة للنوافذ المنبثقة ====================
def close_dialog(page, dlg_or_overlay):
    print("DEBUG: Closing dialog...")
    global DIALOG_LAYER
    if DIALOG_LAYER:
        DIALOG_LAYER.visible = False
        DIALOG_LAYER.controls.clear()
        DIALOG_LAYER.update()

def open_dialog(page, dlg):
    print("DEBUG: Attempting to open dialog via Manual Stack Injection...")
    if not page: page = get_app_page()
    
    global DIALOG_LAYER
    
    # 1. إعداد محتوى النافذة (Overlay Container)
    # ملاحظة: تم إزالة clickable=True لأن الإصدار القديم من Flet لا يدعمها
    # سنستخدم on_click مباشرة، وهي مدعومة غالباً، أو نتجاهل النقر الخلفي
    overlay_content = ft.Container(
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
        alignment=ft.Alignment(0, 0),
        # clickable=True,  <-- REMOVED due to old Flet version
        # محتوى النافذة الفعلي (Dialog Content)
        content=ft.Container(
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK),
            content=ft.Column([
                dlg.title if dlg.title else ft.Container(),
                ft.Divider(),
                dlg.content if dlg.content else ft.Container(),
                ft.Row(dlg.actions if dlg.actions else [], alignment="end")
            ], tight=True, width=500),
            # لمنع إغلاق النافذة عند النقر داخلها، يجب أن نوقف انتشار الحدث (Event Bubbling)
            # ولكن في الإصدارات القديمة، on_click على الابن يمنع وصول النقر للأب، وهذا ما نريده
            on_click=lambda e: None 
        ),
        # الإغلاق عند النقر في الخلفية
        on_click=lambda e: close_dialog(page, None)
    )

    # 3. الحقن المباشر في الطبقة العلوية
    if DIALOG_LAYER:
        DIALOG_LAYER.controls.clear() # تنظيف أي نافذة سابقة
        DIALOG_LAYER.controls.append(overlay_content)
        DIALOG_LAYER.visible = True
        DIALOG_LAYER.update()
        print("DEBUG: Dialog injected into DIALOG_LAYER successfully")
    else:
        print("CRITICAL ERROR: DIALOG_LAYER is not initialized!")
