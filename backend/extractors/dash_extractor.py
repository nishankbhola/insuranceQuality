import fitz  # PyMuPDF
import re
import json


def extract_dash_data(path):
    # Open PDF with PyMuPDF
    pdf_document = fitz.open(path)
    text = ""
    
    # Extract text from all pages
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    
    # Close the document
    pdf_document.close()

    with open("Dash_test.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    result = {
        "dln": None,
        "name": None,
        "date_of_birth": None,
        "address": None,
        "gender": None,
        "marital_status": None,
        "policies": [],
        "claims": []
    }

    # DLN (Driver License Number) - handle with or without spaces/dashes
    dln_patterns = [
        r'DLN:\s*([A-Z]\d{4}[\-\s]?\d{5}[\-\s]?\d{5})',
        r'DLN:\s*([A-Z0-9\-\s]+)\s+Ontario'
    ]
    for pattern in dln_patterns:
        dln_match = re.search(pattern, text)
        if dln_match:
            result["dln"] = dln_match.group(1).strip()
            break

    # Name - Look for the main driver name after DRIVER REPORT
    name_patterns = [
        r'DRIVER REPORT\s*\n([A-Za-z\s]+?)\s*\n',
        r'DRIVER REPORT\s*\n([A-Za-z\s]+)\s+DLN:'
    ]
    for pattern in name_patterns:
        name_match = re.search(pattern, text)
        if name_match:
            result["name"] = name_match.group(1).strip()
            break

    # Date of Birth
    dob_match = re.search(r'Date of Birth:\s*(\d{4}-\d{2}-\d{2})', text)
    if dob_match:
        result["date_of_birth"] = dob_match.group(1)

    # Address - more specific pattern
    address_patterns = [
        r'Address:\s*([^\n]+?)\s+Number of',
        r'(\d+\s+[A-Za-z\s]+[A-Za-z]+\s+[A-Z]{2}\s+[A-Z0-9]{6})'
    ]
    for pattern in address_patterns:
        address_match = re.search(pattern, text)
        if address_match:
            result["address"] = address_match.group(1).strip()
            break

    # Gender
    gender_match = re.search(r'Gender:\s*(Male|Female)', text)
    if gender_match:
        result["gender"] = gender_match.group(1)

    # Marital Status - more specific pattern to avoid capturing following text
    marital_patterns = [
        r'Marital Status:\s*(Not married|Married|Single|Divorced|Widowed)',
        r'Marital Status:\s*([A-Za-z\s]+?)\s+Years'
    ]
    for pattern in marital_patterns:
        marital_match = re.search(pattern, text)
        if marital_match:
            result["marital_status"] = marital_match.group(1).strip()
            break

    # Policies - Updated pattern to match the actual format
    policies_section = re.search(r'Policies\s*.*?\n(.*?)(?=Claims|Previous Inquiries)', text, re.DOTALL)
    if policies_section:
        policy_text = policies_section.group(1)
        
        # Pattern for: #1 2024-05-03 to 2025-05-03 The Wawanesa Mutual Insurance Company *OVERLAP* Active
        policy_patterns = [
            r'#(\d+)\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})\s+([^*]+?)(?:\s*\*[^*]*\*)?\s+(Active|Inactive|Expired)',
            r'#(\d+)\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})\s+(.+?)\s+(Active|Inactive|Expired)'
        ]
        
        for pattern in policy_patterns:
            policy_matches = re.findall(pattern, policy_text)
            if policy_matches:
                for policy_num, start_date, end_date, company, status in policy_matches:
                    # Clean company name
                    company_clean = re.sub(r'\s*\*[^*]*\*\s*', '', company).strip()
                    result["policies"].append({
                        "policy_number": policy_num,
                        "start_date": start_date,
                        "end_date": end_date,
                        "company": company_clean,
                        "status": status
                    })
                break

    # Claims - Enhanced pattern with additional fields
    claims_section = re.search(r'Claims\s*\n(.*?)(?=Previous Inquiries|Policy #|Page)', text, re.DOTALL)
    if claims_section:
        claims_text = claims_section.group(1)
        
        # Enhanced pattern for claims with additional fields
        claim_patterns = [
            r'#(\d+)\s+Date of Loss\s+(\d{4}-\d{2}-\d{2})\s+([^A]+?)\s+At-Fault\s*:\s*(\d+)%',
            r'#(\d+)\s+Date of Loss\s+(\d{4}-\d{2}-\d{2})\s+(.+?)\s+At-Fault\s*:\s*(\d+)%'
        ]
        
        for pattern in claim_patterns:
            claim_matches = re.findall(pattern, claims_text)
            if claim_matches:
                for claim_num, date, company, at_fault in claim_matches:
                    claim_data = {
                        "claim_number": claim_num,
                        "date": date,
                        "company": company.strip(),
                        "at_fault_percentage": int(at_fault)
                    }
                    
                    # Try to extract additional claim details from the full text
                    claim_details = _extract_claim_details_enhanced(text, claim_num)
                    claim_data.update(claim_details)
                    
                    result["claims"].append(claim_data)
                break

    # Additional extraction for detailed policy information if needed
    _extract_detailed_policies(text, result)
    
    # Save debug info
    with open("dash_result.json", "w") as f:
        json.dump(result, f, indent=4)

    return result


def _extract_claim_details(text, claim_number):
    """
    Extract additional claim details for a specific claim number.
    
    Args:
        text (str): Full text from the PDF
        claim_number (str): The claim number to search for
        
    Returns:
        dict: Dictionary with additional claim details
    """
    details = {}
    
    # Look for the specific claim section
    claim_section_pattern = rf'Claim #{claim_number}.*?(?=Claim #\d+|Page \d+|$)'
    claim_section_match = re.search(claim_section_pattern, text, re.DOTALL | re.IGNORECASE)
    
    if claim_section_match:
        claim_section = claim_section_match.group(0)
        
        # Extract First Party Driver - Enhanced patterns
        driver_patterns = [
            r'First Party Driver Listed on Policy:\s*(Yes|No|True|False)',
            r'First Party Driver:\s*(Yes|No|True|False)',
            r'First Party Driver:\s*([^\n]+)',
            r'Driver Listed on Policy:\s*(Yes|No|True|False)',
            r'Driver:\s*(Yes|No|True|False)',
            r'Driver:\s*([^\n]+)',
            r'Insured Driver:\s*(Yes|No|True|False)',
            r'Insured Driver:\s*([^\n]+)'
        ]
        for pattern in driver_patterns:
            driver_match = re.search(pattern, claim_section, re.IGNORECASE)
            if driver_match:
                details['first_party_driver'] = driver_match.group(1).strip()
                break
        
        # Extract First Party Driver At-Fault - Enhanced patterns
        at_fault_patterns = [
            r'First Party Driver At-Fault:\s*(Yes|No|True|False)',
            r'First Party Driver At Fault:\s*(Yes|No|True|False)',
            r'Driver At-Fault:\s*(Yes|No|True|False)',
            r'Driver At Fault:\s*(Yes|No|True|False)',
            r'At-Fault:\s*(Yes|No|True|False)',
            r'At Fault:\s*(Yes|No|True|False)',
            r'Fault:\s*(Yes|No|True|False)'
        ]
        for pattern in at_fault_patterns:
            at_fault_match = re.search(pattern, claim_section, re.IGNORECASE)
            if at_fault_match:
                details['first_party_driver_at_fault'] = at_fault_match.group(1).strip()
                break
        
        # Extract Total Loss
        total_loss_patterns = [
            r'Total Loss:\s*\$?([\d,]+\.?\d*)',
            r'Loss Amount:\s*\$?([\d,]+\.?\d*)',
            r'Claim Amount:\s*\$?([\d,]+\.?\d*)'
        ]
        for pattern in total_loss_patterns:
            total_loss_match = re.search(pattern, claim_section, re.IGNORECASE)
            if total_loss_match:
                details['total_loss'] = total_loss_match.group(1).replace(',', '')
                break
        
        # Extract Claim Status
        status_patterns = [
            r'Claim Status:\s*([^\n]+)',
            r'Status:\s*([^\n]+)',
            r'Claim State:\s*([^\n]+)'
        ]
        for pattern in status_patterns:
            status_match = re.search(pattern, claim_section, re.IGNORECASE)
            if status_match:
                details['claim_status'] = status_match.group(1).strip()
                break
    
    return details


def _extract_claim_details_enhanced(text, claim_number):
    """
    Enhanced extraction of claim details that searches the entire document.
    
    Args:
        text (str): Full text from the PDF
        claim_number (str): The claim number to search for
        
    Returns:
        dict: Dictionary with additional claim details
    """
    details = {}
    
    # First try the specific claim section approach
    claim_section_pattern = rf'Claim #{claim_number}.*?(?=Claim #\d+|Page \d+|$)'
    claim_section_match = re.search(claim_section_pattern, text, re.DOTALL | re.IGNORECASE)
    
    if claim_section_match:
        claim_section = claim_section_match.group(0)
        # Use the existing _extract_claim_details function
        details = _extract_claim_details(text, claim_number)
    
    # If we didn't find anything in the specific section, search the entire document
    if not details.get('first_party_driver') or details.get('first_party_driver') == 'N/A':
        # Search for First Party Driver in the entire document
        driver_patterns = [
            rf'Claim #{claim_number}.*?First Party Driver Listed on Policy:\s*(Yes|No|True|False)',
            rf'Claim #{claim_number}.*?First Party Driver:\s*(Yes|No|True|False)',
            rf'First Party Driver Listed on Policy:\s*(Yes|No|True|False).*?Claim #{claim_number}',
            rf'First Party Driver:\s*(Yes|No|True|False).*?Claim #{claim_number}'
        ]
        
        for pattern in driver_patterns:
            driver_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if driver_match:
                details['first_party_driver'] = driver_match.group(1).strip()
                break
    
    # Similar enhanced search for At-Fault
    if not details.get('first_party_driver_at_fault') or details.get('first_party_driver_at_fault') == 'N/A':
        at_fault_patterns = [
            rf'Claim #{claim_number}.*?First Party Driver At-Fault:\s*(Yes|No|True|False)',
            rf'Claim #{claim_number}.*?At-Fault:\s*(Yes|No|True|False)',
            rf'First Party Driver At-Fault:\s*(Yes|No|True|False).*?Claim #{claim_number}',
            rf'At-Fault:\s*(Yes|No|True|False).*?Claim #{claim_number}'
        ]
        
        for pattern in at_fault_patterns:
            at_fault_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if at_fault_match:
                details['first_party_driver_at_fault'] = at_fault_match.group(1).strip()
                break
    
    return details


def _extract_detailed_policies(text, result):
    """Extract detailed policy information from the detailed sections"""
    
    # Look for detailed policy sections (Policy #1, Policy #2, etc.)
    detailed_policy_sections = re.findall(
        r'Policy #(\d+)\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})\s+([^\n]+)\s+.*?\n(.*?)(?=Policy #\d+|Claim #\d+|Page \d+|$)', 
        text, 
        re.DOTALL
    )
    
    for policy_num, start_date, end_date, company, policy_details in detailed_policy_sections:
        # Find if this policy already exists in our results
        existing_policy = None
        for policy in result["policies"]:
            if policy.get("policy_number") == policy_num:
                existing_policy = policy
                break
        
        if existing_policy:
            # Extract additional details
            policy_number_match = re.search(r'Policy #:\s*(\w+)', policy_details)
            if policy_number_match:
                existing_policy["policy_id"] = policy_number_match.group(1)
            
            # Extract policyholder info
            policyholder_match = re.search(r'Policyholder Name:\s*([^\n]+)', policy_details)
            if policyholder_match:
                existing_policy["policyholder"] = policyholder_match.group(1).strip()
            
            # Extract number of vehicles and operators
            vehicles_match = re.search(r'Number of Private Passenger Vehicles:\s*(\d+)', policy_details)
            if vehicles_match:
                existing_policy["num_vehicles"] = int(vehicles_match.group(1))
            
            operators_match = re.search(r'Number of Reported Operators:\s*(\d+)', policy_details)
            if operators_match:
                existing_policy["num_operators"] = int(operators_match.group(1))
        else:
            # Create new detailed policy entry if it wasn't found in the basic list
            policy_info = {
                "policy_number": policy_num,
                "start_date": start_date,
                "end_date": end_date,
                "company": company.strip(),
                "status": "Active"  # Default, could be improved
            }
            
            # Extract additional details
            policy_number_match = re.search(r'Policy #:\s*(\w+)', policy_details)
            if policy_number_match:
                policy_info["policy_id"] = policy_number_match.group(1)
            
            result["policies"].append(policy_info)


def extract_detailed_claims(text):
    """Extract detailed claim information"""
    claims_details = []
    
    # Look for detailed claim sections
    detailed_claim_sections = re.findall(
        r'Claim #(\d+)\s+Date of Loss\s+(\d{4}-\d{2}-\d{2})\s+([^\n]+)\s+At-Fault\s*:\s*(\d+)%.*?\n(.*?)(?=Claim #\d+|Page \d+|$)', 
        text, 
        re.DOTALL
    )
    
    for claim_num, date, company, at_fault, claim_details in detailed_claim_sections:
        claim_info = {
            "claim_number": claim_num,
            "date": date,
            "company": company.strip(),
            "at_fault_percentage": int(at_fault)
        }
        
        # Extract additional claim details
        total_loss_match = re.search(r'Total Loss:\s*\$?([\d,]+\.?\d*)', claim_details)
        if total_loss_match:
            claim_info["total_loss"] = total_loss_match.group(1).replace(',', '')
        
        vehicle_match = re.search(r'Vehicle:\s*(\d{4}\s+[A-Z]+\s+-\s+[A-Z0-9\s]+)', claim_details)
        if vehicle_match:
            claim_info["vehicle"] = vehicle_match.group(1).strip()
        
        claims_details.append(claim_info)
    
    return claims_details


def extract_specific_claim_fields(json_data):
    """
    Extract specific fields from claims in the dash report data.
    
    Args:
        json_data (dict): The extracted dash report data
        
    Returns:
        list: List of dictionaries with the specific claim fields
    """
    claims = json_data.get('claims', [])
    extracted_claims = []
    
    for claim in claims:
        # Extract the required fields with multiple possible field names
        claim_data = {
            'Claim Number': claim.get('claim_number', 'N/A'),
            'Claim Date': claim.get('date', 'N/A'),
            'Company': claim.get('company', 'N/A'),
            'First Party Driver': claim.get('first_party_driver') or claim.get('driver') or claim.get('insured_driver', 'N/A'),
            'First Party Driver At-Fault': claim.get('first_party_driver_at_fault') or claim.get('driver_at_fault') or claim.get('at_fault', 'N/A'),
            'Total Loss': claim.get('total_loss') or claim.get('total_loss_amount') or claim.get('loss_amount', 'N/A'),
            'Claim Status': claim.get('claim_status') or claim.get('status') or claim.get('claim_state', 'N/A'),
            'At Fault Percentage': claim.get('at_fault_percentage', 'N/A')
        }
        
        extracted_claims.append(claim_data)
    
    return extracted_claims


def save_claim_fields_to_csv(extracted_claims, output_file='extracted_claims.csv'):
    """
    Save the extracted claim fields to a CSV file.
    
    Args:
        extracted_claims (list): List of claim dictionaries
        output_file (str): Output CSV file name
    """
    import csv
    
    if not extracted_claims:
        print("No claims data to save.")
        return
    
    fieldnames = ['Claim Number', 'Claim Date', 'Company', 'First Party Driver', 
                  'First Party Driver At-Fault', 'Total Loss', 'Claim Status', 'At Fault Percentage']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(extracted_claims)
    
    print(f"Claim fields saved to {output_file}")


def save_claim_fields_to_json(extracted_claims, output_file='extracted_claims.json'):
    """
    Save the extracted claim fields to a JSON file.
    
    Args:
        extracted_claims (list): List of claim dictionaries
        output_file (str): Output JSON file name
    """
    import json
    
    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(extracted_claims, jsonfile, indent=2)
    
    print(f"Claim fields saved to {output_file}")


def print_claim_fields_summary(extracted_claims):
    """
    Print a summary of the extracted claim fields.
    
    Args:
        extracted_claims (list): List of claim dictionaries
    """
    print("\n=== EXTRACTED CLAIM FIELDS ===")
    print(f"Total claims found: {len(extracted_claims)}")
    
    if extracted_claims:
        print("\nExtracted data:")
        for i, claim in enumerate(extracted_claims, 1):
            print(f"\nClaim {i}:")
            for field, value in claim.items():
                print(f"  {field}: {value}")
        
        # Print missing fields summary
        print("\n=== MISSING FIELDS SUMMARY ===")
        required_fields = ['First Party Driver', 'First Party Driver At-Fault', 'Total Loss', 'Claim Status']
        
        for field in required_fields:
            missing_count = sum(1 for claim in extracted_claims if claim.get(field) == 'N/A')
            print(f"{field}: {missing_count} missing values out of {len(extracted_claims)} claims")
    else:
        print("No claims data found.")


def extract_and_save_claim_fields(json_file_path='dash_result.json'):
    """
    Extract specific claim fields from the dash result JSON and save to files.
    
    Args:
        json_file_path (str): Path to the JSON file containing dash report data
    """
    import json
    
    try:
        # Read the JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        # Extract specific claim fields
        extracted_claims = extract_specific_claim_fields(data)
        
        # Print summary
        print_claim_fields_summary(extracted_claims)
        
        # Save to files
        save_claim_fields_to_csv(extracted_claims)
        save_claim_fields_to_json(extracted_claims)
        
        return extracted_claims
        
    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file_path}")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None