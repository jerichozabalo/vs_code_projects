import pandas as pd
import numpy as np
import os
from datetime import datetime

def read_and_prepare_crb_data(crb_path):
    """
    Read and prepare CRB data for reconciliation.
    
    Args:
        crb_path: Path to CRB standardized CSV file
        
    Returns:
        DataFrame with prepared CRB data
    """
    print(f"Reading CRB data from: {crb_path}")
    
    if not os.path.exists(crb_path):
        print(f"Error: CRB file '{crb_path}' not found.")
        return None
    
    try:
        df_crb = pd.read_csv(crb_path)
        
        # Ensure we have the required columns
        required_cols = ['DATE', 'NO', 'SI_NO', 'CLIENT_NAME', 'TOTAL_AMOUNT']
        missing_cols = [col for col in required_cols if col not in df_crb.columns]
        if missing_cols:
            print(f"Error: CRB file missing columns: {missing_cols}")
            return None
        
        # Clean and prepare CRB data
        df_crb_clean = df_crb.copy()
        
        # Convert NO to string for better matching (remove .0 from float values)
        df_crb_clean['NO'] = df_crb_clean['NO'].astype(str).str.replace(r'\.0$', '', regex=True)
        
        # Clean CLIENT_NAME
        df_crb_clean['CLIENT_NAME'] = df_crb_clean['CLIENT_NAME'].astype(str).str.strip().str.upper()
        
        # Ensure TOTAL_AMOUNT is numeric
        df_crb_clean['TOTAL_AMOUNT'] = pd.to_numeric(df_crb_clean['TOTAL_AMOUNT'], errors='coerce')
        
        # Convert DATE to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df_crb_clean['DATE']):
            df_crb_clean['DATE'] = pd.to_datetime(df_crb_clean['DATE'], errors='coerce')
        
        print(f"CRB data prepared: {len(df_crb_clean)} records")
        return df_crb_clean
        
    except Exception as e:
        print(f"Error reading CRB data: {e}")
        import traceback
        traceback.print_exc()
        return None

def read_and_prepare_saasant_data(saasant_path):
    """
    Read and prepare saasant data for reconciliation.
    
    Args:
        saasant_path: Path to saasant Excel file
        
    Returns:
        DataFrame with prepared saasant data
    """
    print(f"Reading saasant data from: {saasant_path}")
    
    if not os.path.exists(saasant_path):
        print(f"Error: saasant file '{saasant_path}' not found.")
        return None
    
    try:
        df_saasant = pd.read_excel(saasant_path)
        
        # Map column names based on user requirements
        # Reference No → NO
        # Total → TOTAL_AMOUNT
        # Customer → CLIENT_NAME
        # QB Invoice Id → SI_NO
        
        # Create mapping dictionary
        column_mapping = {}
        available_cols = list(df_saasant.columns)
        
        # Find Reference No column (could be 'Reference No' or similar)
        ref_no_candidates = ['Reference No', 'Reference No', 'Ref No', 'Ref No (Payment No)']
        ref_no_col = None
        for candidate in ref_no_candidates:
            if candidate in available_cols:
                ref_no_col = candidate
                break
        
        if not ref_no_col:
            print(f"Warning: Could not find Reference No column. Available columns: {available_cols}")
            ref_no_col = available_cols[0] if available_cols else None
        
        # Find other columns
        total_col = 'Total' if 'Total' in available_cols else None
        customer_col = 'Customer' if 'Customer' in available_cols else None
        qb_invoice_col = 'QB Invoice Id' if 'QB Invoice Id' in available_cols else None
        
        # Prepare saasant data
        df_saasant_clean = df_saasant.copy()
        
        # Clean Reference No (convert to string, handle NaN)
        if ref_no_col:
            df_saasant_clean['REFERENCE_NO'] = df_saasant_clean[ref_no_col].astype(str).str.strip()
            # Remove 'nan' strings
            df_saasant_clean['REFERENCE_NO'] = df_saasant_clean['REFERENCE_NO'].replace('nan', pd.NA)
        else:
            df_saasant_clean['REFERENCE_NO'] = pd.NA
        
        # Clean Total
        if total_col:
            df_saasant_clean['TOTAL'] = pd.to_numeric(df_saasant_clean[total_col], errors='coerce')
        else:
            df_saasant_clean['TOTAL'] = pd.NA
        
        # Clean Customer
        if customer_col:
            df_saasant_clean['CUSTOMER'] = df_saasant_clean[customer_col].astype(str).str.strip().str.upper()
        else:
            df_saasant_clean['CUSTOMER'] = pd.NA
        
        # Clean QB Invoice Id
        if qb_invoice_col:
            df_saasant_clean['QB_INVOICE_ID'] = df_saasant_clean[qb_invoice_col].astype(str).str.replace(r'\.0$', '', regex=True)
            df_saasant_clean['QB_INVOICE_ID'] = df_saasant_clean['QB_INVOICE_ID'].replace('nan', pd.NA)
        else:
            df_saasant_clean['QB_INVOICE_ID'] = pd.NA
        
        # Also include the original columns for reference
        df_saasant_clean['ORIG_REFERENCE_NO'] = df_saasant_clean[ref_no_col] if ref_no_col else pd.NA
        df_saasant_clean['ORIG_TOTAL'] = df_saasant_clean[total_col] if total_col else pd.NA
        df_saasant_clean['ORIG_CUSTOMER'] = df_saasant_clean[customer_col] if customer_col else pd.NA
        df_saasant_clean['ORIG_QB_INVOICE_ID'] = df_saasant_clean[qb_invoice_col] if qb_invoice_col else pd.NA
        
        print(f"Saasant data prepared: {len(df_saasant_clean)} records")
        print(f"Columns mapped: Reference No -> {ref_no_col}, Total -> {total_col}, "
              f"Customer -> {customer_col}, QB Invoice Id -> {qb_invoice_col}")
        
        return df_saasant_clean
        
    except Exception as e:
        print(f"Error reading saasant data: {e}")
        import traceback
        traceback.print_exc()
        return None

def perform_reconciliation(df_crb, df_saasant):
    """
    Perform reconciliation between CRB and saasant data.
    
    Matching levels:
    1. 1st level: Reference No (saasant) <-> NO (CRB)
    2. 2nd level: Customer (saasant) and Total (saasant) <-> CLIENT_NAME and TOTAL_AMOUNT (CRB)
    
    Args:
        df_crb: Prepared CRB DataFrame
        df_saasant: Prepared saasant DataFrame
        
    Returns:
        Dictionary with reconciliation results
    """
    print("\n" + "="*60)
    print("PERFORMING RECONCILIATION")
    print("="*60)
    
    # Create copies to avoid modifying originals
    crb = df_crb.copy()
    saasant = df_saasant.copy()
    
    # Add match tracking columns
    crb['MATCH_LEVEL'] = None
    crb['MATCHED_SAASANT_INDEX'] = None
    crb['MATCH_TYPE'] = None
    
    saasant['MATCH_LEVEL'] = None
    saasant['MATCHED_CRB_INDEX'] = None
    saasant['MATCH_TYPE'] = None
    
    # Track matches
    matches = []
    match_stats = {
        'level1_matches': 0,
        'level2_matches': 0,
        'unmatched_crb': 0,
        'unmatched_saasant': 0
    }
    
    # ===== 1ST LEVEL MATCHING: Reference No <-> NO =====
    print("\n--- Level 1 Matching: Reference No <-> NO ---")
    
    # Create dictionaries for faster lookups
    crb_by_no = {}
    for idx, row in crb.iterrows():
        no_value = row['NO']
        if pd.notna(no_value) and no_value != '':
            crb_by_no[no_value] = idx
    
    # Try to match saasant records by Reference No
    for saasant_idx, saasant_row in saasant.iterrows():
        ref_no = saasant_row['REFERENCE_NO']
        if pd.notna(ref_no) and ref_no in crb_by_no:
            crb_idx = crb_by_no[ref_no]
            
            # Check if already matched
            if pd.isna(crb.loc[crb_idx, 'MATCH_LEVEL']):
                # Record the match
                matches.append({
                    'match_level': 1,
                    'crb_index': crb_idx,
                    'saasant_index': saasant_idx,
                    'match_key': f"Reference No: {ref_no}",
                    'match_type': 'Reference No'
                })
                
                # Update tracking columns
                crb.loc[crb_idx, 'MATCH_LEVEL'] = 1
                crb.loc[crb_idx, 'MATCHED_SAASANT_INDEX'] = saasant_idx
                crb.loc[crb_idx, 'MATCH_TYPE'] = 'Reference No'
                
                saasant.loc[saasant_idx, 'MATCH_LEVEL'] = 1
                saasant.loc[saasant_idx, 'MATCHED_CRB_INDEX'] = crb_idx
                saasant.loc[saasant_idx, 'MATCH_TYPE'] = 'Reference No'
                
                match_stats['level1_matches'] += 1
    
    print(f"Level 1 matches found: {match_stats['level1_matches']}")
    
    # ===== 2ND LEVEL MATCHING: Customer + Total <-> CLIENT_NAME + TOTAL_AMOUNT =====
    print("\n--- Level 2 Matching: Customer + Total <-> CLIENT_NAME + TOTAL_AMOUNT ---")
    
    # Get unmatched records
    unmatched_crb = crb[crb['MATCH_LEVEL'].isna()].copy()
    unmatched_saasant = saasant[saasant['MATCH_LEVEL'].isna()].copy()
    
    # Create a composite key for CRB: CLIENT_NAME + TOTAL_AMOUNT
    crb_unmatched_keys = {}
    for idx, row in unmatched_crb.iterrows():
        client_name = row['CLIENT_NAME']
        total_amount = row['TOTAL_AMOUNT']
        
        if pd.notna(client_name) and pd.notna(total_amount):
            # Round total to 2 decimal places for matching
            key = f"{client_name}_{round(total_amount, 2)}"
            crb_unmatched_keys[key] = idx
    
    # Try to match saasant records by Customer + Total
    for saasant_idx, saasant_row in unmatched_saasant.iterrows():
        customer = saasant_row['CUSTOMER']
        total = saasant_row['TOTAL']
        
        if pd.notna(customer) and pd.notna(total):
            # Round total to 2 decimal places for matching
            key = f"{customer}_{round(total, 2)}"
            
            if key in crb_unmatched_keys:
                crb_idx = crb_unmatched_keys[key]
                
                # Record the match
                matches.append({
                    'match_level': 2,
                    'crb_index': crb_idx,
                    'saasant_index': saasant_idx,
                    'match_key': f"Customer+Total: {key}",
                    'match_type': 'Customer+Total'
                })
                
                # Update tracking columns
                crb.loc[crb_idx, 'MATCH_LEVEL'] = 2
                crb.loc[crb_idx, 'MATCHED_SAASANT_INDEX'] = saasant_idx
                crb.loc[crb_idx, 'MATCH_TYPE'] = 'Customer+Total'
                
                saasant.loc[saasant_idx, 'MATCH_LEVEL'] = 2
                saasant.loc[saasant_idx, 'MATCHED_CRB_INDEX'] = crb_idx
                saasant.loc[saasant_idx, 'MATCH_TYPE'] = 'Customer+Total'
                
                match_stats['level2_matches'] += 1
                
                # Remove from unmatched keys to prevent duplicate matches
                del crb_unmatched_keys[key]
    
    print(f"Level 2 matches found: {match_stats['level2_matches']}")
    
    # ===== FINAL STATISTICS =====
    match_stats['unmatched_crb'] = len(crb[crb['MATCH_LEVEL'].isna()])
    match_stats['unmatched_saasant'] = len(saasant[saasant['MATCH_LEVEL'].isna()])
    
    total_matches = match_stats['level1_matches'] + match_stats['level2_matches']
    total_crb = len(crb)
    total_saasant = len(saasant)
    
    print(f"\n--- Reconciliation Summary ---")
    print(f"Total CRB records: {total_crb}")
    print(f"Total saasant records: {total_saasant}")
    print(f"Total matches: {total_matches}")
    print(f"  Level 1 (Reference No): {match_stats['level1_matches']}")
    print(f"  Level 2 (Customer+Total): {match_stats['level2_matches']}")
    print(f"Unmatched CRB records: {match_stats['unmatched_crb']}")
    print(f"Unmatched saasant records: {match_stats['unmatched_saasant']}")
    
    if total_crb > 0:
        match_rate_crb = (total_matches / total_crb) * 100
        print(f"CRB match rate: {match_rate_crb:.1f}%")
    
    if total_saasant > 0:
        match_rate_saasant = (total_matches / total_saasant) * 100
        print(f"Saasant match rate: {match_rate_saasant:.1f}%")
    
    return {
        'crb_matched': crb,
        'saasant_matched': saasant,
        'matches': matches,
        'stats': match_stats
    }

def generate_reconciliation_report(results, output_dir='output'):
    """
    Generate detailed reconciliation report and output files.
    
    Args:
        results: Dictionary with reconciliation results
        output_dir: Directory to save output files
    """
    print("\n" + "="*60)
    print("GENERATING RECONCILIATION REPORT")
    print("="*60)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    crb_matched = results['crb_matched']
    saasant_matched = results['saasant_matched']
    matches = results['matches']
    stats = results['stats']
    
    # ===== 1. Save matched data with match info =====
    # CRB with match info
    crb_output_path = os.path.join(output_dir, 'crb_reconciled.csv')
    crb_matched.to_csv(crb_output_path, index=False)
    print(f"CRB matched data saved to: {crb_output_path}")
    
    # Saasant with match info
    saasant_output_path = os.path.join(output_dir, 'saasant_reconciled.csv')
    saasant_matched.to_csv(saasant_output_path, index=False)
    print(f"Saasant matched data saved to: {saasant_output_path}")
    
    # ===== 2. Create matched pairs file with all requested saasant columns =====
    # First read the original saasant file to get all column names
    saasant_path = "data/saasant/Payment-May 01, 2024-to-May 31, 2024.xlsx"
    original_saasant_df = pd.read_excel(saasant_path)
    
    matched_pairs = []
    for match in matches:
        crb_idx = match['crb_index']
        saasant_idx = match['saasant_index']
        
        crb_row = crb_matched.loc[crb_idx]
        saasant_row = saasant_matched.loc[saasant_idx]
        
        # Get original saasant row to preserve all columns
        original_saasant_row = original_saasant_df.loc[saasant_idx]
        
        # Build matched pair with all requested columns
        matched_pair = {
            'MATCH_LEVEL': match['match_level'],
            'MATCH_TYPE': match['match_type'],
            'CRB_NO': crb_row['NO'],
            'CRB_CLIENT_NAME': crb_row['CLIENT_NAME'],
            'CRB_TOTAL_AMOUNT': crb_row['TOTAL_AMOUNT'],
            'CRB_SI_NO': crb_row['SI_NO'],
            'CRB_DATE': crb_row['DATE'],
            'SAASANT_REFERENCE_NO': saasant_row['REFERENCE_NO'],
            'SAASANT_CUSTOMER': saasant_row['CUSTOMER'],
            'SAASANT_TOTAL': saasant_row['TOTAL'],
            'SAASANT_QB_INVOICE_ID': saasant_row['QB_INVOICE_ID'],
        }
        
        # Add all requested saasant columns with original column names
        requested_saasant_columns = [
            'QbId', 'Ref No (Payment No)', 'Payment Date', 'Customer',
            'Payment method', 'Deposit To Account Name', 'Invoice No',
            'Journal No', 'QB Journal Id', 'QB Invoice Id', 'QB Credit Memo Id',
            'Credit Memo No', 'Amount', 'Total', 'Reference No', 'Memo',
            'Currency Code', 'Exchange Rate'
        ]
        
        # Add each requested column if it exists in the original file
        for col in requested_saasant_columns:
            if col in original_saasant_df.columns:
                matched_pair[f'SAASANT_{col}'] = original_saasant_row[col]
            else:
                matched_pair[f'SAASANT_{col}'] = pd.NA
        
        matched_pairs.append(matched_pair)
    
    if matched_pairs:
        df_matched_pairs = pd.DataFrame(matched_pairs)
        pairs_output_path = os.path.join(output_dir, 'reconciliation_matched_pairs.csv')
        df_matched_pairs.to_csv(pairs_output_path, index=False)
        print(f"Matched pairs saved to: {pairs_output_path}")
    
    # ===== 3. Create unmatched records files =====
    # Unmatched CRB
    unmatched_crb = crb_matched[crb_matched['MATCH_LEVEL'].isna()].copy()
    if len(unmatched_crb) > 0:
        unmatched_crb_path = os.path.join(output_dir, 'reconciliation_unmatched_crb.csv')
        unmatched_crb.to_csv(unmatched_crb_path, index=False)
        print(f"Unmatched CRB records saved to: {unmatched_crb_path}")
    
    # Unmatched saasant
    unmatched_saasant = saasant_matched[saasant_matched['MATCH_LEVEL'].isna()].copy()
    if len(unmatched_saasant) > 0:
        unmatched_saasant_path = os.path.join(output_dir, 'reconciliation_unmatched_saasant.csv')
        unmatched_saasant.to_csv(unmatched_saasant_path, index=False)
        print(f"Unmatched saasant records saved to: {unmatched_saasant_path}")
    
    # ===== 4. Generate summary report =====
    report_path = os.path.join(output_dir, 'reconciliation_summary.txt')
    with open(report_path, 'w') as f:
        f.write("="*60 + "\n")
        f.write("CRB-SAASANT RECONCILIATION SUMMARY\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("RECONCILIATION STATISTICS:\n")
        f.write("-"*40 + "\n")
        f.write(f"Total CRB records: {len(crb_matched)}\n")
        f.write(f"Total saasant records: {len(saasant_matched)}\n")
        f.write(f"Total matches: {stats['level1_matches'] + stats['level2_matches']}\n")
        f.write(f"  Level 1 matches (Reference No): {stats['level1_matches']}\n")
        f.write(f"  Level 2 matches (Customer+Total): {stats['level2_matches']}\n")
        f.write(f"Unmatched CRB records: {stats['unmatched_crb']}\n")
        f.write(f"Unmatched saasant records: {stats['unmatched_saasant']}\n\n")
        
        if len(crb_matched) > 0:
            match_rate = ((stats['level1_matches'] + stats['level2_matches']) / len(crb_matched)) * 100
            f.write(f"Overall match rate: {match_rate:.1f}%\n\n")
        
        f.write("MATCHING CRITERIA:\n")
        f.write("-"*40 + "\n")
        f.write("1. Level 1: Reference No (saasant) <-> NO (CRB)\n")
        f.write("2. Level 2: Customer (saasant) + Total (saasant) <-> CLIENT_NAME + TOTAL_AMOUNT (CRB)\n\n")
        
        f.write("OUTPUT FILES:\n")
        f.write("-"*40 + "\n")
        f.write(f"1. CRB matched data: {crb_output_path}\n")
        f.write(f"2. Saasant matched data: {saasant_output_path}\n")
        if matched_pairs:
            f.write(f"3. Matched pairs: {pairs_output_path}\n")
        if len(unmatched_crb) > 0:
            f.write(f"4. Unmatched CRB: {unmatched_crb_path}\n")
        if len(unmatched_saasant) > 0:
            f.write(f"5. Unmatched saasant: {unmatched_saasant_path}\n")
    
    print(f"Summary report saved to: {report_path}")
    
    # Print summary to console
    print("\n" + "="*60)
    print("RECONCILIATION COMPLETE")
    print("="*60)
    print(f"\n✅ Reconciliation completed successfully!")
    print(f"   Total matches: {stats['level1_matches'] + stats['level2_matches']}")
    print(f"   Match rate: {((stats['level1_matches'] + stats['level2_matches']) / len(crb_matched) * 100):.1f}%")
    print(f"\n📁 Output files saved to: {output_dir}/")

def main():
    """
    Main function to run the reconciliation process.
    """
    print("\n" + "="*60)
    print("CRB-SAASANT RECONCILIATION TOOL")
    print("="*60)
    
    # File paths
    crb_path = "output/crb_standardized_enhanced.csv"
    saasant_path = "data/saasant/Payment-May 01, 2024-to-May 31, 2024.xlsx"
    output_dir = "output"
    
    # Step 1: Read and prepare data
    print("\n📂 Reading and preparing data...")
    df_crb = read_and_prepare_crb_data(crb_path)
    if df_crb is None:
        return
    
    df_saasant = read_and_prepare_saasant_data(saasant_path)
    if df_saasant is None:
        return
    
    # Step 2: Perform reconciliation
    print("\n🔍 Performing reconciliation...")
    results = perform_reconciliation(df_crb, df_saasant)
    
    # Step 3: Generate reports
    print("\n📊 Generating reports...")
    generate_reconciliation_report(results, output_dir)

if __name__ == "__main__":
    main()