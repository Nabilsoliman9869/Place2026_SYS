import flet as ft
import inspect
try:
    print(inspect.getsource(ft.Tabs.__init__))
except:
    print("Cannot get source")
