import pandas as pd
import os

file_path = "data/crb/5_2024 May 2024 - CRB.xlsx"

print(f"Checking file: {file_path}")
print(f"File exists: {os.path.exists(file_path)}")

if os.path.exists(file_path):
    try:
        # Read sheet names
        xl = pd.ExcelFile(file_path)
        print(f"Sheet names: {xl.sheet_names}")
        
        # Read MAIN sheet without header to see raw structure
        df_raw = pd.read_excel(file_path, sheet_name='MAIN', header=None)
        print(f"\nRaw MAIN sheet shape: {df_raw.shape}")
        
        # Print first 15 rows to see structure
        print("\nFirst 15 rows (first 10 columns each):")
        for i in range(15):
            row = df_raw.iloc[i]
            # Take first 10 values, convert to string
            values = [str(v) if pd.notna(v) else 'NaN' for v in row.tolist()[:10]]
            print(f"Row {i:2d}: {values}")
        
        # Try to find header row by looking for typical column names
        print("\n--- Searching for header row ---")
        header_candidates = []
        for i in range(min(20, df_raw.shape[0])):
            row = df_raw.iloc[i]
            row_str = ' '.join([str(val).upper().strip() for val in row if pd.notna(val)])
            # Check for common column name indicators
            if any(keyword in row_str for keyword in ['DATE', 'CLIENT', 'AMOUNT', 'NO', 'SI']):
                header_candidates.append((i, row.tolist()))
                print(f"Row {i} looks like a header: {row.tolist()}")
        
        # If we found candidate headers, try reading with that header
        if header_candidates:
            header_row = header_candidates[0][0]
            print(f"\nUsing row {header_row} as header")
            df_with_header = pd.read_excel(file_path, sheet_name='MAIN', header=header_row)
            print(f"Data shape after header: {df_with_header.shape}")
            print(f"Column names: {list(df_with_header.columns)}")
            
            # Show first few rows of actual data
            print("\nFirst 5 rows of data (after header):")
            print(df_with_header.head().to_string())
        else:
            print("No header row found in first 20 rows")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("File not found!")