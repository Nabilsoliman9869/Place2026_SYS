import flet as ft
import inspect

print("Flet version:", ft.version)
print("ft.Tab arguments:", inspect.signature(ft.Tab.__init__))
