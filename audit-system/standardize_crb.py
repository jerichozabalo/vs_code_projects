import pandas as pd
import os
import numpy as np
from datetime import datetime

def standardize_crb_data(input_path, output_path=None):
    """
    Standardize CRB Excel data by extracting required columns and cleaning.
    
    Required columns: DATE, NO (BK NO.), SI NO., CLIENT NAME, TOTAL AMOUNT
    
    Args:
        input_path: Path to input Excel file
        output_path: Path to save standardized CSV (optional)
    
    Returns:
        DataFrame with standardized columns
    """
    print(f"Standardizing CRB data from: {input_path}")
    
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        return None
    
    try:
        # Read the Excel file
        xl = pd.ExcelFile(input_path)
        print(f"Available sheets: {xl.sheet_names}")
        
        # We'll focus on the MAIN sheet as it contains the core data
        # If other sheets have similar structure, we could combine them
        sheet_name = 'MAIN'
        
        # First, find the header row (we know it's at row 6, but let's verify)
        df_raw = pd.read_excel(input_path, sheet_name=sheet_name, header=None)
        
        header_row_idx = None
        for i in range(min(20, df_raw.shape[0])):
            row = df_raw.iloc[i]
            row_str = ' '.join([str(val).upper().strip() for val in row if pd.notna(val)])
            if any(keyword in row_str for keyword in ['DATE', 'SI NO', 'CLIENT NAME', 'TOTAL AMOUNT']):
                header_row_idx = i
                print(f"Header found at row {i}")
                break
        
        if header_row_idx is None:
            print("Warning: Could not find header row. Using default header.")
            df = pd.read_excel(input_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(input_path, sheet_name=sheet_name, header=header_row_idx)
        
        print(f"Original shape: {df.shape}")
        print(f"Original columns: {list(df.columns)}")
        
        # Map required columns to actual column names in the file
        column_mapping = {}
        
        # Find matches for each required column
        required_columns = {
            'DATE': ['DATE'],
            'NO': ['BK NO.', 'BK NO', 'BOOK NO', 'NO'],
            'SI NO': ['SI NO.', 'SI NO', 'SI_NO'],
            'CLIENT NAME': ['CLIENT NAME', 'CLIENT', 'NAME'],
            'TOTAL AMOUNT': ['TOTAL AMOUNT', 'AMOUNT', 'TOTAL']
        }
        
        for std_col, possible_names in required_columns.items():
            found = False
            for col in df.columns:
                col_str = str(col).upper().strip()
                for name in possible_names:
                    if name.upper() in col_str:
                        column_mapping[std_col] = col
                        print(f"Mapped '{std_col}' -> '{col}'")
                        found = True
                        break
                if found:
                    break
            if not found:
                print(f"Warning: Could not find column for '{std_col}'")
        
        # Extract only the columns we need
        available_cols = [col for col in column_mapping.values() if col in df.columns]
        if not available_cols:
            print("Error: None of the required columns found in the data.")
            return None
        
        df_extracted = df[available_cols].copy()
        
        # Rename columns to standardized names
        reverse_mapping = {v: k for k, v in column_mapping.items()}
        df_extracted = df_extracted.rename(columns=reverse_mapping)
        
        # Clean and standardize the data
        print(f"\nData shape after extraction: {df_extracted.shape}")
        print(f"\nFirst few rows before cleaning:")
        print(df_extracted.head())
        
        # Clean each column
        if 'DATE' in df_extracted.columns:
            # Convert DATE to datetime, handle errors
            df_extracted['DATE'] = pd.to_datetime(df_extracted['DATE'], errors='coerce')
            print(f"Date range: {df_extracted['DATE'].min()} to {df_extracted['DATE'].max()}")
        
        if 'TOTAL AMOUNT' in df_extracted.columns:
            # Convert to numeric, handle non-numeric values
            df_extracted['TOTAL AMOUNT'] = pd.to_numeric(df_extracted['TOTAL AMOUNT'], errors='coerce')
            print(f"Total amount stats: sum={df_extracted['TOTAL AMOUNT'].sum():.2f}, "
                  f"mean={df_extracted['TOTAL AMOUNT'].mean():.2f}")
        
        if 'NO' in df_extracted.columns:
            # Clean NO column (might be numeric or string)
            df_extracted['NO'] = df_extracted['NO'].astype(str).str.strip()
        
        if 'SI NO' in df_extracted.columns:
            # Clean SI NO column
            df_extracted['SI NO'] = pd.to_numeric(df_extracted['SI NO'], errors='coerce')
        
        if 'CLIENT NAME' in df_extracted.columns:
            # Clean CLIENT NAME column
            df_extracted['CLIENT NAME'] = df_extracted['CLIENT NAME'].astype(str).str.strip()
            # Remove empty or NaN client names
            df_extracted = df_extracted[df_extracted['CLIENT NAME'].str.len() > 0]
            df_extracted = df_extracted[df_extracted['CLIENT NAME'] != 'nan']
        
        # Remove rows where all required columns are NaN (like the TOTAL AMOUNT summary row)
        required_for_row = ['DATE', 'CLIENT NAME', 'TOTAL AMOUNT']
        cols_to_check = [col for col in required_for_row if col in df_extracted.columns]
        if cols_to_check:
            df_extracted = df_extracted.dropna(subset=cols_to_check, how='all')
        
        print(f"\nData shape after cleaning: {df_extracted.shape}")
        print(f"\nSample of cleaned data:")
        print(df_extracted.head(10).to_string())
        
        # Summary statistics
        print(f"\n--- Summary Statistics ---")
        print(f"Total records: {len(df_extracted)}")
        print(f"Date range: {df_extracted['DATE'].min()} to {df_extracted['DATE'].max()}")
        if 'TOTAL AMOUNT' in df_extracted.columns:
            print(f"Total amount sum: {df_extracted['TOTAL AMOUNT'].sum():.2f}")
            print(f"Average amount: {df_extracted['TOTAL AMOUNT'].mean():.2f}")
            print(f"Min amount: {df_extracted['TOTAL AMOUNT'].min():.2f}")
            print(f"Max amount: {df_extracted['TOTAL AMOUNT'].max():.2f}")
        
        # Save to output file if requested
        if output_path:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Save as CSV
            df_extracted.to_csv(output_path, index=False)
            print(f"\nStandardized data saved to: {output_path}")
            
            # Also save as Excel for easier viewing
            excel_path = output_path.replace('.csv', '.xlsx')
            df_extracted.to_excel(excel_path, index=False)
            print(f"Also saved as Excel: {excel_path}")
        
        return df_extracted
        
    except Exception as e:
        print(f"Error standardizing data: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    # Input and output paths
    input_file = "data/crb/5_2024 May 2024 - CRB.xlsx"
    output_file = "output/crb_standardized.csv"
    
    # Standardize the data
    df_standardized = standardize_crb_data(input_file, output_file)
    
    if df_standardized is not None:
        print(f"\n✅ Standardization complete!")
        print(f"   Extracted {len(df_standardized)} records")
        print(f"   Columns: {list(df_standardized.columns)}")
        
        # Show column headers as requested
        print(f"\n📋 COLUMN HEADERS EXTRACTED:")
        for col in df_standardized.columns:
            print(f"   - {col}")
    else:
        print("\n❌ Standardization failed.")

if __name__ == "__main__":
    main()