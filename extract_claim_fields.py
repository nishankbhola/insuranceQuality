import json
import pandas as pd
from typing import Dict, List, Any

def extract_claim_fields(json_file_path: str) -> pd.DataFrame:
    """
    Extract specific fields from claims in the dash report JSON file.
    
    Args:
        json_file_path (str): Path to the JSON file containing dash report data
        
    Returns:
        pd.DataFrame: DataFrame with extracted claim fields
    """
    
    # Read the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Extract claims data
    claims = data.get('claims', [])
    
    # Initialize list to store extracted data
    extracted_data = []
    
    for claim in claims:
        # Extract the required fields
        claim_data = {
            'Claim Number': claim.get('claim_number', 'N/A'),
            'Claim Date': claim.get('date', 'N/A'),
            'Company': claim.get('company', 'N/A'),
            'First Party Driver': claim.get('first_party_driver', 'N/A'),
            'First Party Driver At-Fault': claim.get('first_party_driver_at_fault', 'N/A'),
            'Total Loss': claim.get('total_loss', 'N/A'),
            'Claim Status': claim.get('claim_status', 'N/A'),
            'At Fault Percentage': claim.get('at_fault_percentage', 'N/A')
        }
        
        extracted_data.append(claim_data)
    
    # Create DataFrame
    df = pd.DataFrame(extracted_data)
    
    return df

def save_to_csv(df: pd.DataFrame, output_file: str = 'extracted_claims.csv'):
    """
    Save the extracted data to a CSV file.
    
    Args:
        df (pd.DataFrame): DataFrame with extracted data
        output_file (str): Output CSV file name
    """
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

def print_summary(df: pd.DataFrame):
    """
    Print a summary of the extracted data.
    
    Args:
        df (pd.DataFrame): DataFrame with extracted data
    """
    print("\n=== EXTRACTED CLAIM FIELDS ===")
    print(f"Total claims found: {len(df)}")
    print("\nExtracted data:")
    print(df.to_string(index=False))
    
    # Print missing fields summary
    print("\n=== MISSING FIELDS SUMMARY ===")
    for column in ['First Party Driver', 'First Party Driver At-Fault', 'Total Loss', 'Claim Status']:
        missing_count = df[column].eq('N/A').sum()
        print(f"{column}: {missing_count} missing values out of {len(df)} claims")

def main():
    """Main function to run the extraction process."""
    
    # File path
    json_file = 'backend/dash_result.json'
    
    try:
        # Extract data
        df = extract_claim_fields(json_file)
        
        # Print summary
        print_summary(df)
        
        # Save to CSV
        save_to_csv(df)
        
        # Also save as JSON for easy viewing
        output_json = 'extracted_claims.json'
        df.to_json(output_json, orient='records', indent=2)
        print(f"Data also saved to {output_json}")
        
    except FileNotFoundError:
        print(f"Error: File {json_file} not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 