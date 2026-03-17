import pandas as pd
import os

def load_data(file_path):
    """
    Reads an Excel file and returns a pandas DataFrame.
    Prints the first few rows for verification.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return None

    try:
        print(f"\nLoading data from: {file_path}")
        df = pd.read_excel(file_path)
        print("First few rows:")
        print(df.head())
        return df
    except Exception as e:
        print(f"Error reading the Excel file: {e}")
        return None

def match_by_reference(saasant_df, crb_df):
    """
    Placeholder for matching records by reference number.
    Returns DataFrames unchanged for now.
    """
    print("\nMatching by reference number...")
    return saasant_df, crb_df

def match_by_name_amount(saasant_unmatched, crb_unmatched):
    """
    Placeholder for matching records by name and amount.
    Returns DataFrames unchanged for now.
    """
    print("\nMatching by name and amount...")
    return saasant_unmatched, crb_unmatched

def main():
    print("Welcome to the Audit System!")
    print("This tool matches records between Saasant reports and Cash Receipt Books (CRB).")
    
    saasant_file = "saasant_report.xlsx"
    crb_file = "crb_report.xlsx"
    
    saasant_df = load_data(saasant_file)
    crb_df = load_data(crb_file)
    
    if saasant_df is not None and crb_df is not None:
        # Initial matching step
        saasant_unmatched, crb_unmatched = match_by_reference(saasant_df, crb_df)
        
        # Second matching step for remaining records
        saasant_final_unmatched, crb_final_unmatched = match_by_name_amount(saasant_unmatched, crb_unmatched)
        
        print("\n--- Summary ---")
        print(f"Saasant records: {len(saasant_df)}")
        print(f"CRB records: {len(crb_df)}")
        print(f"Remaining Saasant unmatched: {len(saasant_final_unmatched)}")
        print(f"Remaining CRB unmatched: {len(crb_final_unmatched)}")
    else:
        print("\nCould not proceed with matching due to missing data.")

if __name__ == "__main__":
    main()
