import re

def fix_main():
    file_path = "main.py"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Helpers definition
    helpers = """
# ==================== دوال مساعدة للنوافذ المنبثقة ====================
def open_dialog(page, dlg):
    page.dialog = dlg
    dlg.open = True
    page.update()

def close_dialog(page, dlg):
    dlg.open = False
    page.update()

"""
    
    # Insert helpers if not present
    if "def open_dialog" not in content:
        # Insert after show_snackbar function (around line 11)
        # We look for the end of show_snackbar
        pattern_insert = r"(def show_snackbar.*?\n\s+page\.update\(\)\n)"
        if re.search(pattern_insert, content, re.DOTALL):
            content = re.sub(pattern_insert, r"\1" + helpers, content, count=1, flags=re.DOTALL)
        else:
            # Fallback: insert after imports
            content = content.replace("import database as db\n", "import database as db\n" + helpers)

    # Replace .open(dlg) calls
    # Regex to capture the object: e.g. 'page', 'e.page', 'btn_e.page'
    # We assume the object ends with .page or is just 'page' or similar
    # We look for: <something>.open(dlg)
    
    # Using a function for replacement to handle the capture group
    def replace_open(match):
        obj = match.group(1)
        return f"open_dialog({obj}, dlg)"

    content = re.sub(r"([\w\.]+)\.open\(dlg\)", replace_open, content)

    # Replace .close(dlg) calls
    def replace_close(match):
        obj = match.group(1)
        return f"close_dialog({obj}, dlg)"

    content = re.sub(r"([\w\.]+)\.close\(dlg\)", replace_close, content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("Successfully patched main.py")

if __name__ == "__main__":
    fix_main()
