import pandas as pd
import os
import numpy as np
from datetime import datetime

def read_crb_file(input_path):
    """
    Read CRB Excel file and identify the header row.
    
    Args:
        input_path: Path to input Excel file
        
    Returns:
        Tuple of (DataFrame with header, header_row_index, sheet_names)
    """
    print(f"Reading CRB file: {input_path}")
    
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        return None, None, None
    
    try:
        # Read the Excel file
        xl = pd.ExcelFile(input_path)
        sheet_names = xl.sheet_names
        print(f"Available sheets: {sheet_names}")
        
        # Focus on the MAIN sheet
        sheet_name = 'MAIN'
        if sheet_name not in sheet_names:
            print(f"Error: '{sheet_name}' sheet not found in the Excel file.")
            return None, None, sheet_names
        
        # Read without header to find the actual header row
        df_raw = pd.read_excel(input_path, sheet_name=sheet_name, header=None)
        print(f"Raw MAIN sheet shape: {df_raw.shape}")
        
        # Find header row by looking for column name patterns
        header_row_idx = None
        for i in range(min(20, df_raw.shape[0])):
            row = df_raw.iloc[i]
            row_str = ' '.join([str(val).upper().strip() for val in row if pd.notna(val)])
            # Look for key column indicators
            if any(keyword in row_str for keyword in ['DATE', 'SI NO', 'CLIENT NAME', 'TOTAL AMOUNT', 'BK NO']):
                header_row_idx = i
                print(f"Header found at row {i}")
                print(f"Header values: {row.tolist()}")
                break
        
        if header_row_idx is None:
            print("Warning: Could not find header row in first 20 rows.")
            return None, None, sheet_names
        
        # Read with the identified header row
        df = pd.read_excel(input_path, sheet_name=sheet_name, header=header_row_idx)
        print(f"Data shape after header: {df.shape}")
        print(f"Original columns: {list(df.columns)}")
        
        return df, header_row_idx, sheet_names
        
    except Exception as e:
        print(f"Error reading file: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

def extract_columns(df):
    """
    Extract only the required columns from the DataFrame.
    
    Required columns: DATE, NO (BK NO.), SI NO., CLIENT NAME, TOTAL AMOUNT
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with extracted columns and column mapping dictionary
    """
    print("\n--- Extracting required columns ---")
    
    # Map required columns to actual column names in the file
    column_mapping = {}
    
    # Find matches for each required column with improved matching
    # Note: 'NO' column now maps to 'OR NO.' per user request - prioritize 'OR NO.' first
    required_columns = {
        'DATE': ['DATE'],
        'NO': ['OR NO.', 'OR NO', 'BK NO.', 'BK NO', 'BOOK NO', 'NO'],
        'SI_NO': ['SI NO.', 'SI NO', 'SI_NO'],  # Note: standardized to SI_NO
        'CLIENT_NAME': ['CLIENT NAME', 'CLIENT', 'NAME'],  # Note: standardized to CLIENT_NAME
        'TOTAL_AMOUNT': ['TOTAL AMOUNT', 'AMOUNT', 'TOTAL']  # Note: standardized to TOTAL_AMOUNT
    }
    
    # First pass: try to find exact or close matches for each column
    for std_col, possible_names in required_columns.items():
        found = False
        # Try to find the best match by checking all columns
        best_match = None
        best_match_score = 0
        
        for col in df.columns:
            col_str = str(col).upper().strip()
            
            # Score each possible name match
            for name in possible_names:
                name_upper = name.upper()
                score = 0
                
                # Exact match gets highest score
                if col_str == name_upper:
                    score = 100
                    # Extra bonus for 'OR NO' exact match (per user request)
                    if 'OR NO' in name_upper:
                        score += 1000  # Ensure this is selected over 'BK NO.'
                # Contains the name (good match)
                elif name_upper in col_str:
                    # Longer name matches get higher scores
                    score = len(name_upper) * 10
                    # Bonus for 'OR NO.' specifically
                    if 'OR NO' in name_upper:
                        score += 500  # Large bonus to prioritize OR NO
                # Column contains part of the name
                elif any(part in col_str for part in name_upper.split()):
                    score = 5
                    # Small bonus for 'OR' or 'NO' parts
                    if 'OR' in col_str or 'NO' in col_str:
                        score += 2
                
                if score > best_match_score:
                    best_match_score = score
                    best_match = col
                    found = True
        
        if found and best_match:
            column_mapping[std_col] = best_match
            print(f"Mapped '{std_col}' -> '{best_match}' (score: {best_match_score})")
        else:
            print(f"Warning: Could not find column for '{std_col}'")
    
    # Extract only the columns we need
    available_cols = [col for col in column_mapping.values() if col in df.columns]
    if not available_cols:
        print("Error: None of the required columns found in the data.")
        return None, None
    
    df_extracted = df[available_cols].copy()
    
    # Rename columns to standardized names
    reverse_mapping = {v: k for k, v in column_mapping.items()}
    df_extracted = df_extracted.rename(columns=reverse_mapping)
    
    print(f"Extracted shape: {df_extracted.shape}")
    print(f"Extracted columns: {list(df_extracted.columns)}")
    
    return df_extracted, column_mapping

def clean_data(df_extracted):
    """
    Clean and validate the extracted data.
    
    Args:
        df_extracted: DataFrame with extracted columns
        
    Returns:
        Cleaned DataFrame and cleaning report dictionary
    """
    print("\n--- Cleaning data ---")
    
    # Create a copy to avoid modifying the original
    df_clean = df_extracted.copy()
    
    # Track cleaning operations
    cleaning_report = {
        'initial_rows': len(df_clean),
        'rows_removed_summary': 0,
        'rows_removed_invalid_dates': 0,
        'rows_removed_missing_essentials': 0,
        'final_rows': 0
    }
    
    # 1. Remove summary rows (like the "TOTAL AMOUNT" row in row 0)
    # Check if first row contains "TOTAL AMOUNT" in any column
    initial_count = len(df_clean)
    if not df_clean.empty:
        first_row_str = ' '.join([str(val).upper() for val in df_clean.iloc[0] if pd.notna(val)])
        if 'TOTAL AMOUNT' in first_row_str and not any(keyword in first_row_str for keyword in ['DATE', 'CLIENT']):
            print(f"Removing summary row: {df_clean.iloc[0].to_dict()}")
            df_clean = df_clean.iloc[1:].reset_index(drop=True)
            cleaning_report['rows_removed_summary'] = 1
    
    print(f"Rows after removing summary: {len(df_clean)}")
    
    # 2. Clean each column with improved validation
    if 'DATE' in df_clean.columns:
        # Convert DATE to datetime, handle errors
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], errors='coerce')
        
        # Remove rows with invalid dates (like 1970 or NaT)
        date_mask = df_clean['DATE'].notna()
        invalid_dates = (~date_mask).sum()
        cleaning_report['rows_removed_invalid_dates'] = invalid_dates
        
        # Also filter out dates before 2000 (likely invalid)
        year_mask = df_clean['DATE'].dt.year >= 2000
        invalid_years = (~year_mask).sum()
        cleaning_report['rows_removed_invalid_dates'] += invalid_years
        
        # Apply both masks
        df_clean = df_clean[date_mask & year_mask].copy()
        print(f"Date range after cleaning: {df_clean['DATE'].min()} to {df_clean['DATE'].max()}")
    
    if 'TOTAL_AMOUNT' in df_clean.columns:
        # Convert to numeric, handle non-numeric values
        df_clean['TOTAL_AMOUNT'] = pd.to_numeric(df_clean['TOTAL_AMOUNT'], errors='coerce')
        
        # Remove rows with negative or zero amounts (likely invalid for audit)
        amount_mask = df_clean['TOTAL_AMOUNT'] > 0
        invalid_amounts = (~amount_mask).sum()
        df_clean = df_clean[amount_mask].copy()
        print(f"Total amount stats: sum={df_clean['TOTAL_AMOUNT'].sum():.2f}, mean={df_clean['TOTAL_AMOUNT'].mean():.2f}")
    
    if 'NO' in df_clean.columns:
        # Clean NO column
        df_clean['NO'] = df_clean['NO'].astype(str).str.strip()
        # Convert empty strings to NaN
        df_clean['NO'] = df_clean['NO'].replace('', pd.NA).replace('nan', pd.NA)
    
    if 'SI_NO' in df_clean.columns:
        # Clean SI_NO column
        df_clean['SI_NO'] = pd.to_numeric(df_clean['SI_NO'], errors='coerce')
    
    if 'CLIENT_NAME' in df_clean.columns:
        # Clean CLIENT_NAME column
        df_clean['CLIENT_NAME'] = df_clean['CLIENT_NAME'].astype(str).str.strip()
        
        # Remove rows with empty or invalid client names
        client_mask = (df_clean['CLIENT_NAME'].str.len() > 0) & (df_clean['CLIENT_NAME'] != 'nan')
        invalid_clients = (~client_mask).sum()
        cleaning_report['rows_removed_missing_essentials'] = invalid_clients
        df_clean = df_clean[client_mask].copy()
    
    # 3. Remove rows where essential columns are NaN
    essential_cols = ['DATE', 'CLIENT_NAME', 'TOTAL_AMOUNT']
    cols_to_check = [col for col in essential_cols if col in df_clean.columns]
    
    if cols_to_check:
        before_essential = len(df_clean)
        df_clean = df_clean.dropna(subset=cols_to_check)
        removed_essential = before_essential - len(df_clean)
        cleaning_report['rows_removed_missing_essentials'] += removed_essential
    
    cleaning_report['final_rows'] = len(df_clean)
    
    print(f"Final shape after cleaning: {df_clean.shape}")
    return df_clean, cleaning_report

def standardize_column_names(df):
    """
    Ensure column names are properly standardized.
    This function already handles this through extraction, but provides final validation.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        DataFrame with validated column names
    """
    # Expected standardized column names
    expected_columns = ['DATE', 'NO', 'SI_NO', 'CLIENT_NAME', 'TOTAL_AMOUNT']
    
    # Check which columns are present
    present_columns = [col for col in expected_columns if col in df.columns]
    
    print(f"\n--- Column standardization ---")
    print(f"Present columns: {present_columns}")
    
    # Reorder columns to standard order if all are present
    if set(present_columns) == set(expected_columns):
        df = df[expected_columns]
        print(f"Columns reordered to standard order")
    
    return df

def save_standardized_data(df, output_path):
    """
    Save standardized data to CSV and Excel files.
    
    Args:
        df: Cleaned DataFrame
        output_path: Path to save standardized CSV
        
    Returns:
        Tuple of (csv_path, excel_path)
    """
    print(f"\n--- Saving standardized data ---")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Save as CSV
    csv_path = output_path
    df.to_csv(csv_path, index=False)
    print(f"Standardized data saved to CSV: {csv_path}")
    
    # Also save as Excel for easier viewing
    excel_path = output_path.replace('.csv', '.xlsx')
    df.to_excel(excel_path, index=False)
    print(f"Also saved as Excel: {excel_path}")
    
    return csv_path, excel_path

def generate_cleaning_report(cleaning_report, column_mapping):
    """
    Generate a comprehensive cleaning report.
    
    Args:
        cleaning_report: Dictionary with cleaning statistics
        column_mapping: Dictionary of column mappings
    """
    print("\n" + "="*60)
    print("CLEANING REPORT")
    print("="*60)
    
    print(f"\n📊 Data Cleaning Statistics:")
    print(f"   Initial rows: {cleaning_report['initial_rows']}")
    print(f"   Rows removed (summary): {cleaning_report['rows_removed_summary']}")
    print(f"   Rows removed (invalid dates): {cleaning_report['rows_removed_invalid_dates']}")
    print(f"   Rows removed (missing essentials): {cleaning_report['rows_removed_missing_essentials']}")
    print(f"   Final rows: {cleaning_report['final_rows']}")
    print(f"   Retention rate: {(cleaning_report['final_rows']/cleaning_report['initial_rows']*100):.1f}%")
    
    print(f"\n📋 Column Mappings Applied:")
    for std_col, orig_col in column_mapping.items():
        print(f"   {std_col:15} ← {orig_col}")
    
    print(f"\n✅ Standardized Column Names:")
    print(f"   DATE → DATE (datetime)")
    print(f"   NO → NO (as requested)")
    print(f"   SI NO → SI_NO (underscore added)")
    print(f"   CLIENT NAME → CLIENT_NAME (underscore added)")
    print(f"   TOTAL AMOUNT → TOTAL_AMOUNT (underscore added)")
    
    print("\n" + "="*60)

def standardize_crb_data(input_path, output_path=None):
    """
    Main function to standardize CRB Excel data.
    
    Args:
        input_path: Path to input Excel file
        output_path: Path to save standardized CSV (optional)
        
    Returns:
        DataFrame with standardized columns
    """
    print(f"\n{'='*60}")
    print(f"STANDARDIZING CRB DATA")
    print(f"{'='*60}")
    
    # Step 1: Read file and identify header
    df, header_row_idx, sheet_names = read_crb_file(input_path)
    if df is None:
        return None
    
    # Step 2: Extract required columns
    df_extracted, column_mapping = extract_columns(df)
    if df_extracted is None:
        return None
    
    # Step 3: Clean the data
    df_cleaned, cleaning_report = clean_data(df_extracted)
    
    # Step 4: Standardize column names
    df_standardized = standardize_column_names(df_cleaned)
    
    # Step 5: Generate cleaning report
    generate_cleaning_report(cleaning_report, column_mapping)
    
    # Step 6: Show sample of cleaned data
    print(f"\n📄 Sample of cleaned data (first 5 rows):")
    print(df_standardized.head().to_string())
    
    # Step 7: Save to output file if requested
    if output_path:
        csv_path, excel_path = save_standardized_data(df_standardized, output_path)
        
        # Show column headers as requested
        print(f"\n📋 COLUMN HEADERS EXTRACTED AND STANDARDIZED:")
        for col in df_standardized.columns:
            print(f"   - {col}")
    
    return df_standardized

def main():
    """
    Main function to run the standardization process.
    """
    # Input and output paths
    input_file = "data/crb/5_2024 May 2024 - CRB.xlsx"
    output_file = "output/crb_standardized_enhanced.csv"
    
    print(f"\n🔧 CRB Data Standardization Tool")
    print(f"   Input: {input_file}")
    print(f"   Output: {output_file}")
    
    # Standardize the data
    df_standardized = standardize_crb_data(input_file, output_file)
    
    if df_standardized is not None:
        print(f"\n✅ STANDARDIZATION COMPLETE!")
        print(f"   Extracted {len(df_standardized)} clean records")
        print(f"   Columns: {list(df_standardized.columns)}")
        
        # Show summary statistics
        print(f"\n📊 Final Summary:")
        if 'DATE' in df_standardized.columns:
            print(f"   Date range: {df_standardized['DATE'].min().date()} to {df_standardized['DATE'].max().date()}")
        if 'TOTAL_AMOUNT' in df_standardized.columns:
            print(f"   Total amount: {df_standardized['TOTAL_AMOUNT'].sum():,.2f}")
            print(f"   Average amount: {df_standardized['TOTAL_AMOUNT'].mean():,.2f}")
            print(f"   Min amount: {df_standardized['TOTAL_AMOUNT'].min():,.2f}")
            print(f"   Max amount: {df_standardized['TOTAL_AMOUNT'].max():,.2f}")
    else:
        print("\n❌ Standardization failed.")

if __name__ == "__main__":
    main()