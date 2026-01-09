import pandas as pd
import os

file_path = "On the trail_Odisha.xlsx"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

try:
    xl = pd.ExcelFile(file_path)
    print(f"Sheet names: {xl.sheet_names}")
    
    for sheet in xl.sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        df = xl.parse(sheet)
        print("Columns:", df.columns.tolist())
        print("First 3 rows:")
        print(df.head(3).to_string())
        print("Data Types:")
        print(df.dtypes)
        
except Exception as e:
    print(f"Error reading file: {e}")
