"""
Consolidate CRB-Saasant reconciliation outputs into a single Excel workbook.
This script creates an Excel file with multiple sheets containing all reconciliation results.
"""

import pandas as pd
import os
from datetime import datetime

def create_consolidated_workbook(output_dir='output'):
    """
    Create a consolidated Excel workbook with all reconciliation results.
    
    Args:
        output_dir: Directory containing reconciliation output files
    """
    print("\n" + "="*60)
    print("CREATING CONSOLIDATED RECONCILIATION WORKBOOK")
    print("="*60)
    
    # Define output file path
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_path = os.path.join(output_dir, f'reconciliation_consolidated_{timestamp}.xlsx')
    
    # Create Excel writer
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        print(f"Creating Excel workbook: {excel_path}")
        
        # ===== 1. Matched Pairs =====
        print("\n📊 Adding Matched Pairs sheet...")
        matched_pairs_path = os.path.join(output_dir, 'reconciliation_matched_pairs.csv')
        if os.path.exists(matched_pairs_path):
            df_matched = pd.read_csv(matched_pairs_path)
            df_matched.to_excel(writer, sheet_name='Matched_Pairs', index=False)
            print(f"  ✓ Added {len(df_matched)} matched pairs")
        else:
            print(f"  ⚠️ File not found: {matched_pairs_path}")
        
        # ===== 2. Unmatched CRB =====
        print("📊 Adding Unmatched CRB sheet...")
        unmatched_crb_path = os.path.join(output_dir, 'reconciliation_unmatched_crb.csv')
        if os.path.exists(unmatched_crb_path):
            df_unmatched_crb = pd.read_csv(unmatched_crb_path)
            df_unmatched_crb.to_excel(writer, sheet_name='Unmatched_CRB', index=False)
            print(f"  ✓ Added {len(df_unmatched_crb)} unmatched CRB records")
        else:
            print(f"  ⚠️ File not found: {unmatched_crb_path}")
        
        # ===== 3. Unmatched Saasant =====
        print("📊 Adding Unmatched Saasant sheet...")
        unmatched_saasant_path = os.path.join(output_dir, 'reconciliation_unmatched_saasant.csv')
        if os.path.exists(unmatched_saasant_path):
            df_unmatched_saasant = pd.read_csv(unmatched_saasant_path)
            df_unmatched_saasant.to_excel(writer, sheet_name='Unmatched_Saasant', index=False)
            print(f"  ✓ Added {len(df_unmatched_saasant)} unmatched saasant records")
        else:
            print(f"  ⚠️ File not found: {unmatched_saasant_path}")
        
        # ===== 4. CRB Reconciled =====
        print("📊 Adding CRB Reconciled sheet...")
        crb_reconciled_path = os.path.join(output_dir, 'crb_reconciled.csv')
        if os.path.exists(crb_reconciled_path):
            df_crb_reconciled = pd.read_csv(crb_reconciled_path)
            df_crb_reconciled.to_excel(writer, sheet_name='CRB_Reconciled', index=False)
            print(f"  ✓ Added {len(df_crb_reconciled)} CRB reconciled records")
        else:
            print(f"  ⚠️ File not found: {crb_reconciled_path}")
        
        # ===== 5. Saasant Reconciled =====
        print("📊 Adding Saasant Reconciled sheet...")
        saasant_reconciled_path = os.path.join(output_dir, 'saasant_reconciled.csv')
        if os.path.exists(saasant_reconciled_path):
            df_saasant_reconciled = pd.read_csv(saasant_reconciled_path)
            df_saasant_reconciled.to_excel(writer, sheet_name='Saasant_Reconciled', index=False)
            print(f"  ✓ Added {len(df_saasant_reconciled)} saasant reconciled records")
        else:
            print(f"  ⚠️ File not found: {saasant_reconciled_path}")
        
        # ===== 6. Summary Statistics =====
        print("📊 Adding Summary sheet...")
        summary_path = os.path.join(output_dir, 'reconciliation_summary.txt')
        if os.path.exists(summary_path):
            # Read summary text file
            with open(summary_path, 'r') as f:
                summary_text = f.read()
            
            # Create a DataFrame for the summary
            summary_data = []
            for line in summary_text.split('\n'):
                if line.strip():
                    summary_data.append([line])
            
            df_summary = pd.DataFrame(summary_data, columns=['Reconciliation Summary'])
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            print(f"  ✓ Added summary statistics")
        else:
            print(f"  ⚠️ File not found: {summary_path}")
            
            # Create a basic summary from available data
            summary_data = [
                ['RECONCILIATION SUMMARY'],
                ['Generated on: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                [''],
                ['STATISTICS:'],
                [f'Total Matched Pairs: {len(df_matched) if "df_matched" in locals() else "N/A"}'],
                [f'Total Unmatched CRB: {len(df_unmatched_crb) if "df_unmatched_crb" in locals() else "N/A"}'],
                [f'Total Unmatched Saasant: {len(df_unmatched_saasant) if "df_unmatched_saasant" in locals() else "N/A"}'],
                [''],
                ['FILES INCLUDED:'],
                ['1. Matched_Pairs - All matched records between CRB and Saasant'],
                ['2. Unmatched_CRB - CRB records with no match in Saasant'],
                ['3. Unmatched_Saasant - Saasant records with no match in CRB'],
                ['4. CRB_Reconciled - CRB data with match status'],
                ['5. Saasant_Reconciled - Saasant data with match status'],
                ['6. Summary - This summary sheet']
            ]
            
            df_summary = pd.DataFrame(summary_data, columns=['Summary'])
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            print(f"  ✓ Created basic summary")
        
        # ===== 7. Apply formatting to all sheets =====
        print("\n🎨 Applying formatting to sheets...")
        workbook = writer.book
        
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                # Find the maximum length in the column
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                # Set column width (with some padding)
                adjusted_width = min(max_length + 2, 50)  # Max width of 50
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Add auto-filter to header row
            if sheet_name != 'Summary':  # Don't add filter to summary sheet
                worksheet.auto_filter.ref = worksheet.dimensions
    
    print("\n" + "="*60)
    print("✅ CONSOLIDATED WORKBOOK CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📁 Workbook saved to: {excel_path}")
    print(f"\n📋 Sheets included:")
    print(f"   1. Matched_Pairs - All matched records")
    print(f"   2. Unmatched_CRB - Unmatched CRB records")
    print(f"   3. Unmatched_Saasant - Unmatched saasant records")
    print(f"   4. CRB_Reconciled - CRB data with match status")
    print(f"   5. Saasant_Reconciled - Saasant data with match status")
    print(f"   6. Summary - Reconciliation summary")
    print(f"\n✨ Features:")
    print(f"   • Auto-adjusted column widths")
    print(f"   • Auto-filters on all data sheets")
    print(f"   • Clean formatting")
    
    return excel_path

def main():
    """
    Main function to create consolidated workbook.
    """
    print("\n" + "="*60)
    print("CONSOLIDATE RECONCILIATION OUTPUTS")
    print("="*60)
    
    output_dir = "output"
    
    # Check if output directory exists
    if not os.path.exists(output_dir):
        print(f"Error: Output directory '{output_dir}' not found.")
        print("Please run reconciliation first using reconcile_crb_saasant.py")
        return
    
    # Create consolidated workbook
    excel_path = create_consolidated_workbook(output_dir)
    
    print(f"\n📊 To open the workbook, run:")
    print(f"   python -c \"import os; os.startfile(r'{excel_path}')\"")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()