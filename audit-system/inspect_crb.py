import pandas as pd
import os
import numpy as np

file_path = "data/crb/5_2024 May 2024 - CRB.xlsx"

print(f"Checking file: {file_path}")
print(f"File exists: {os.path.exists(file_path)}")

# Read sheet names
try:
    xl = pd.ExcelFile(file_path)
    print(f"Sheet names: {xl.sheet_names}")
    
    # Let's examine the MAIN sheet
    print("\n--- Examining MAIN sheet ---")
    df_main = pd.read_excel(file_path, sheet_name='MAIN', header=None)
    print(f"Shape of MAIN sheet: {df_main.shape}")
    
    # Find header row by looking for expected keywords
    print("\n--- Searching for header row ---")
    header_row_idx = None
    for i in range(min(20, df_main.shape[0])):
        row = df_main.iloc[i]
        # Convert to string, handle NaN
        row_str = ' '.join([str(val).upper().strip() for val in row if pd.notna(val)])
        if any(keyword in row_str for keyword in ['DATE', 'SI NO', 'CLIENT NAME', 'TOTAL AMOUNT']):
            header_row_idx = i
            print(f"Found potential header at row {i}:")
            print(f"Row values: {row.tolist()}")
            break
    
    if header_row_idx is not None:
        print(f"\nUsing row {header_row_idx} as header")
        # Read again with header row
        df_data = pd.read_excel(file_path, sheet_name='MAIN', header=header_row_idx)
        print(f"Data shape after header: {df_data.shape}")
        print(f"Column names: {list(df_data.columns)}")
        
        # Show first few rows of data
        print("\nFirst 5 rows of data:")
        print(df_data.head().to_string())
        
        # Check for the specific columns we need
        print("\n--- Looking for required columns ---")
        required = ['DATE', 'NO', 'SI NO', 'CLIENT NAME', 'TOTAL AMOUNT']
        available_cols = [col for col in df_data.columns if isinstance(col, str)]
        print(f"Available string columns: {available_cols}")
        
        # Try to match columns (case-insensitive)
        for req in required:
            matches = [col for col in available_cols if req.lower() in str(col).lower()]
            print(f"'{req}' matches: {matches}")
    
    # Also check raw data near where we think data starts
    print("\n--- Raw data around row 10-15 ---")
    for i in range(10, 16):
        row = df_main.iloc[i]
        print(f"Row {i}: {row.tolist()[:10]}...")  # First 10 values
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
