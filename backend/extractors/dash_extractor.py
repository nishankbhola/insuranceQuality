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
        "claims": [],
        "policy_gaps": []  # New field for tracking policy gaps
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

    # Policies - Updated pattern to match the actual format and extract cancellation reasons
    policies_section = re.search(r'Policies\s*\n(.*?)(?=Claims|Previous Inquiries)', text, re.DOTALL)
    if policies_section:
        policy_text = policies_section.group(1)
        
        # Split into individual policy blocks
        policy_blocks = re.split(r'#\d+', policy_text)[1:]  # Skip the first empty element
        
        for i, block in enumerate(policy_blocks):
            # Extract policy number (i+1 since we split on #)
            policy_num = str(i + 1)
            
            # Extract dates
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})', block)
            if not date_match:
                continue
                
            start_date = date_match.group(1)
            end_date = date_match.group(2)
            
            # Extract company name (everything between dates and status/cancellation)
            lines = block.split('\n')
            company_lines = []
            status = "Active"  # Default status
            cancellation_reason = None
            
            # Find the company name and status
            for line in lines:
                line = line.strip()
                if not line or line.startswith('*'):
                    continue
                    
                # Check if this line contains a status
                if any(status_word in line for status_word in ['Active', 'Inactive', 'Expired', 'Cancelled']):
                    status = line
                    # Check if cancellation reason is on the same line
                    if 'Cancelled' in line:
                        reason_patterns = [
                            r'Cancelled[^-\n]*-\s*([^-\n]+)',
                            r'Cancelled[^-\n]*\s+([^-\n]+)',
                            r'Cancelled\s*-\s*([^-\n]+)',
                            r'Cancelled\s+([^-\n]+)'
                        ]
                        
                        for reason_pattern in reason_patterns:
                            reason_match = re.search(reason_pattern, line, re.IGNORECASE)
                            if reason_match:
                                cancellation_reason = reason_match.group(1).strip()
                                break
                elif not re.match(r'^\d{4}-\d{2}-\d{2}', line):  # Not a date line
                    company_lines.append(line)
            
            # Clean company name
            company_clean = ' '.join(company_lines).strip()
            company_clean = re.sub(r'\s*\*[^*]*\*\s*', '', company_clean).strip()
            
            # If no cancellation reason found in status line, check the next line
            if 'Cancelled' in status and not cancellation_reason:
                # Look for cancellation reason on the next line
                block_lines = block.split('\n')
                for j, line in enumerate(block_lines):
                    if 'Cancelled' in line:
                        # Check next line for reason
                        if j + 1 < len(block_lines):
                            next_line = block_lines[j + 1].strip()
                            if next_line and not next_line.startswith('*'):
                                cancellation_reason = next_line
                                break
                
                # If still no reason found, use "Cancelled"
                if not cancellation_reason:
                    cancellation_reason = "Cancelled"
            
            result["policies"].append({
                "policy_number": policy_num,
                "start_date": start_date,
                "end_date": end_date,
                "company": company_clean,
                "status": status.strip(),
                "cancellation_reason": cancellation_reason
            })
        
        # Detect policy gaps
        result["policy_gaps"] = _detect_policy_gaps(result["policies"])

    # Claims - Enhanced pattern with additional fields
    claims_section = re.search(r'Claims\s*\n(.*?)(?=Previous Inquiries|Policy #|Page)', text, re.DOTALL)
    if claims_section:
        claims_text = claims_section.group(1)
        
        # Parse claims using a more robust approach
        lines = claims_text.split('\n')
        current_claim = None
        current_company_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Check for claim number
            claim_match = re.match(r'#(\d+)', line)
            if claim_match:
                # Save previous claim if exists
                if current_claim:
                    current_claim['company'] = ' '.join(current_company_lines).strip()
                    result["claims"].append(current_claim)
                
                # Start new claim
                claim_num = claim_match.group(1)
                current_claim = {
                    "claim_number": claim_num,
                    "date": None,
                    "company": None,
                    "at_fault_percentage": None
                }
                current_company_lines = []
                continue
            
            # Check for date
            date_match = re.search(r'Date of Loss\s+(\d{4}-\d{2}-\d{2})', line)
            if date_match and current_claim:
                current_claim['date'] = date_match.group(1)
                continue
            
            # Check for At-Fault percentage
            at_fault_match = re.search(r'At-Fault\s*:\s*(\d+)%', line)
            if at_fault_match and current_claim:
                current_claim['at_fault_percentage'] = int(at_fault_match.group(1))
                continue
            
            # If line is not empty and doesn't match special patterns, it's part of company name
            if line and not re.match(r'^\*.*\*$', line) and current_claim and current_claim['date'] and not current_claim['at_fault_percentage']:
                current_company_lines.append(line)
        
        # Don't forget the last claim
        if current_claim:
            current_claim['company'] = ' '.join(current_company_lines).strip()
            result["claims"].append(current_claim)
        
        # Extract additional details for all claims
        for claim_data in result["claims"]:
            claim_details = _extract_claim_details_enhanced(text, claim_data["claim_number"])
            claim_data.update(claim_details)
            
            # Ensure we have the required fields with default values if not found
            if not claim_data.get('first_party_driver'):
                claim_data['first_party_driver'] = 'N/A'
            if not claim_data.get('first_party_driver_at_fault'):
                claim_data['first_party_driver_at_fault'] = 'N/A'
            if not claim_data.get('total_loss'):
                claim_data['total_loss'] = 'N/A'
            if not claim_data.get('claim_status'):
                claim_data['claim_status'] = 'N/A'

    # Additional extraction for detailed policy information if needed
    _extract_detailed_policies(text, result)
    
    # Detect policy gaps after all policies are extracted
    result["policy_gaps"] = _detect_policy_gaps(result["policies"])
    
    # Save debug info
    with open("dash_result.json", "w") as f:
        json.dump(result, f, indent=4)

    return result


def _detect_policy_gaps(policies):
    """
    Detect gaps between policy end dates and next policy start dates
    """
    gaps = []
    
    if len(policies) < 2:
        return gaps
    
    # Sort policies by start date (oldest first)
    sorted_policies = sorted(policies, key=lambda x: x.get("start_date", ""))
    
    for i in range(len(sorted_policies) - 1):
        current_policy = sorted_policies[i]
        next_policy = sorted_policies[i + 1]
        
        current_end = current_policy.get("end_date")
        next_start = next_policy.get("start_date")
        
        if current_end and next_start:
            try:
                # Parse dates
                from datetime import datetime
                end_date = datetime.strptime(current_end, "%Y-%m-%d")
                start_date = datetime.strptime(next_start, "%Y-%m-%d")
                
                # Check for gap (more than 1 day difference)
                gap_days = (start_date - end_date).days
                if gap_days > 1:
                    gap_info = {
                        "gap_days": gap_days,
                        "previous_policy_end": current_end,
                        "next_policy_start": next_start,
                        "previous_policy_company": current_policy.get("company"),
                        "next_policy_company": next_policy.get("company"),
                        "cancellation_reason": current_policy.get("cancellation_reason")
                    }
                    gaps.append(gap_info)
            except ValueError:
                # Skip if date parsing fails
                continue
    
    return gaps


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
    
    # Look for the specific claim section with more comprehensive patterns
    claim_section_pattern = rf'Claim #{claim_number}.*?(?=Claim #\d+|Page \d+|$)'
    claim_section_match = re.search(claim_section_pattern, text, re.DOTALL | re.IGNORECASE)
    
    if claim_section_match:
        claim_section = claim_section_match.group(0)
        
        # Extract First Party Driver - Enhanced patterns based on actual PDF content
        # Priority: First Party Driver name, then fallback to Listed on Policy status
        driver_name_patterns = [
            rf'First Party Driver:\s*([^\n]+)',
            rf'Driver:\s*([^\n]+)',
            rf'Insured Driver:\s*([^\n]+)'
        ]
        
        # First try to get the actual driver name
        driver_name_found = False
        for pattern in driver_name_patterns:
            driver_match = re.search(pattern, claim_section, re.IGNORECASE)
            if driver_match:
                driver_value = driver_match.group(1).strip()
                # If it's a name (not Yes/No/True/False), use it
                if driver_value and driver_value not in ['Yes', 'No', 'True', 'False', 'Not available']:
                    details['first_party_driver'] = driver_value
                    driver_name_found = True
                    break
        
        # If no driver name found, fallback to Listed on Policy status
        if not driver_name_found:
            listed_patterns = [
                rf'First Party Driver Listed on Policy:\s*(Yes|No|True|False)',
                rf'First Party Driver:\s*(Yes|No|True|False)',
                rf'Driver Listed on Policy:\s*(Yes|No|True|False)',
                rf'Driver:\s*(Yes|No|True|False)',
                rf'Insured Driver:\s*(Yes|No|True|False)'
            ]
            
            for pattern in listed_patterns:
                listed_match = re.search(pattern, claim_section, re.IGNORECASE)
                if listed_match:
                    details['first_party_driver'] = listed_match.group(1).strip()
                    break
        
        # Extract First Party Driver At-Fault - Enhanced patterns
        at_fault_patterns = [
            rf'First Party Driver At-Fault:\s*(\d+%)',
            rf'First Party Driver At-Fault:\s*(Yes|No|True|False)',
            rf'First Party Driver At Fault:\s*(Yes|No|True|False)',
            rf'Driver At-Fault:\s*(Yes|No|True|False)',
            rf'Driver At Fault:\s*(Yes|No|True|False)',
            rf'At-Fault:\s*(Yes|No|True|False)'
        ]
        
        for pattern in at_fault_patterns:
            at_fault_match = re.search(pattern, claim_section, re.IGNORECASE)
            if at_fault_match:
                at_fault_value = at_fault_match.group(1).strip()
                # Convert percentage to Yes/No
                if '%' in at_fault_value:
                    percentage = int(at_fault_value.replace('%', ''))
                    details['first_party_driver_at_fault'] = 'Yes' if percentage > 0 else 'No'
                else:
                    details['first_party_driver_at_fault'] = at_fault_value
                break
        
        # Extract Total Loss
        total_loss_patterns = [
            rf'Total Loss:\s*\$?([\d,]+\.?\d*)',
            rf'Loss Amount:\s*\$?([\d,]+\.?\d*)',
            rf'Claim Amount:\s*\$?([\d,]+\.?\d*)'
        ]
        
        for pattern in total_loss_patterns:
            total_loss_match = re.search(pattern, claim_section, re.IGNORECASE)
            if total_loss_match:
                details['total_loss'] = total_loss_match.group(1).replace(',', '')
                break
        
        # Extract Claim Status
        status_patterns = [
            rf'Claim Status:\s*([^\n]+)',
            rf'Status:\s*([^\n]+)',
            rf'Claim State:\s*([^\n]+)'
        ]
        
        for pattern in status_patterns:
            status_match = re.search(pattern, claim_section, re.IGNORECASE)
            if status_match:
                details['claim_status'] = status_match.group(1).strip()
                break
    
    # If we still don't have the required fields, search the entire document
    if not details.get('first_party_driver'):
        # Search for First Party Driver in the entire document - prioritize driver name
        driver_name_patterns = [
            rf'Claim #{claim_number}.*?First Party Driver:\s*([^\n]+)',
            rf'First Party Driver:\s*([^\n]+).*?Claim #{claim_number}',
            rf'Claim #{claim_number}.*?Driver:\s*([^\n]+)',
            rf'Driver:\s*([^\n]+).*?Claim #{claim_number}'
        ]
        
        # First try to get the actual driver name
        driver_name_found = False
        for pattern in driver_name_patterns:
            driver_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if driver_match:
                driver_value = driver_match.group(1).strip()
                # If it's a name (not Yes/No/True/False), use it
                if driver_value and driver_value not in ['Yes', 'No', 'True', 'False', 'Not available']:
                    details['first_party_driver'] = driver_value
                    driver_name_found = True
                    break
        
        # If no driver name found, fallback to Listed on Policy status
        if not driver_name_found:
            listed_patterns = [
                rf'Claim #{claim_number}.*?First Party Driver Listed on Policy:\s*(Yes|No|True|False)',
                rf'Claim #{claim_number}.*?First Party Driver:\s*(Yes|No|True|False)',
                rf'First Party Driver Listed on Policy:\s*(Yes|No|True|False).*?Claim #{claim_number}',
                rf'First Party Driver:\s*(Yes|No|True|False).*?Claim #{claim_number}'
            ]
            
            for pattern in listed_patterns:
                driver_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if driver_match:
                    details['first_party_driver'] = driver_match.group(1).strip()
                    break
    
    # Similar enhanced search for At-Fault
    if not details.get('first_party_driver_at_fault'):
        at_fault_patterns = [
            rf'Claim #{claim_number}.*?First Party Driver At-Fault:\s*(\d+%)',
            rf'Claim #{claim_number}.*?First Party Driver At-Fault:\s*(Yes|No|True|False)',
            rf'Claim #{claim_number}.*?At-Fault:\s*(Yes|No|True|False)',
            rf'First Party Driver At-Fault:\s*(\d+%).*?Claim #{claim_number}',
            rf'First Party Driver At-Fault:\s*(Yes|No|True|False).*?Claim #{claim_number}',
            rf'At-Fault:\s*(Yes|No|True|False).*?Claim #{claim_number}'
        ]
        
        for pattern in at_fault_patterns:
            at_fault_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if at_fault_match:
                at_fault_value = at_fault_match.group(1).strip()
                # Convert percentage to Yes/No
                if '%' in at_fault_value:
                    percentage = int(at_fault_value.replace('%', ''))
                    details['first_party_driver_at_fault'] = 'Yes' if percentage > 0 else 'No'
                else:
                    details['first_party_driver_at_fault'] = at_fault_value
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