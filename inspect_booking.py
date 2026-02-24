import pandas as pd
import os

file_path = 'Booking sheet.xlsx'

if os.path.exists(file_path):
    try:
        df = pd.read_excel(file_path)
        print("Columns found:")
        for col in df.columns:
            print(f"- {col}")
        
        print("\nFirst row sample:")
        print(df.iloc[0].to_dict())
    except Exception as e:
        print(f"Error reading excel: {e}")
else:
    print(f"File not found: {file_path}")
