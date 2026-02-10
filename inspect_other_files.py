import pandas as pd
import os

files = [
    'GA2.1W34 - Yehia- 141225.xlsx',
    'Guide Academy Placements 2025.xlsx'
]

for file_path in files:
    print(f"\n--- Inspecting: {file_path} ---")
    if os.path.exists(file_path):
        try:
            # Read first sheet
            df = pd.read_excel(file_path)
            print("Columns:", df.columns.tolist())
            print("First row:", df.iloc[0].to_dict())
            
            # Check sheet names if multiple
            xl = pd.ExcelFile(file_path)
            print("Sheet Names:", xl.sheet_names)
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("File not found.")
