
import fileinput
import sys

file_path = "e:\\Place_2026_SYS\\main.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("ft.Colors", "ft.colors")
content = content.replace("ft.Icons", "ft.icons")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed imports")
