import fitz  # PyMuPDF
import re
import json

def convert_date_format(date_str):
    """
    Convert date from DD/MM/YYYY format to MM/DD/YYYY format
    """
    if not date_str or '/' not in date_str:
        return date_str
    
    parts = date_str.split('/')
    if len(parts) == 3:
        day, month, year = parts
        return f"{month}/{day}/{year}"
    
    return date_str

def extract_mvr_data(path):
    
    # Open PDF with PyMuPDF
    pdf_document = fitz.open(path)
    text = ""
    
    # Extract text from all pages
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    
    # Close the document
    pdf_document.close()

    with open("MVR_test.txt", "w", encoding="utf-8") as f:
        f.write(text)

    result = {
        "licence_number": None,
        "name": None,
        "birth_date": None,
        "gender": None,
        "address": None,
        "convictions": [],
        "expiry_date": None,
        "issue_date": None
    }

    # Licence Number
    licence_match = re.search(r'Licence Number:\s*([A-Z0-9\-]+)', text)
    if licence_match:
        result["licence_number"] = licence_match.group(1)

    # Name
    name_match = re.search(r'Name:\s*([A-Z,]+)', text)
    if name_match:
        result["name"] = name_match.group(1)

    # Birth Date - Convert from DD/MM/YYYY to MM/DD/YYYY
    birth_match = re.search(r'Birth Date:\s*(\d{2}/\d{2}/\d{4})', text)
    if birth_match:
        original_date = birth_match.group(1)
        result["birth_date"] = convert_date_format(original_date)

    # Gender
    gender_match = re.search(r'Gender:\s*([MF])', text)
    if gender_match:
        result["gender"] = gender_match.group(1)

    # Address - Capture complete multi-line address
    address_match = re.search(r'Address:\s*([^\n]+(?:\n[^\n]+)*?)(?=\n[A-Z][a-z]*\s*:|$)', text, re.DOTALL)
    if address_match:
        # Clean up the address by removing extra whitespace and newlines
        address = address_match.group(1).strip()
        # Split by newlines and clean each line
        address_lines = []
        for line in address.split('\n'):
            line = line.strip()
            if line and not line.startswith('Reference:') and not line.startswith('Comment:'):
                address_lines.append(line)
        result["address"] = '\n'.join(address_lines)

    # Expiry Date - Convert from DD/MM/YYYY to MM/DD/YYYY
    expiry_match = re.search(r'Expiry Date:\s*(\d{2}/\d{2}/\d{4})', text)
    if expiry_match:
        original_date = expiry_match.group(1)
        result["expiry_date"] = convert_date_format(original_date)

    # Issue Date - Convert from DD/MM/YYYY to MM/DD/YYYY
    issue_match = re.search(r'Issue Date:\s*(\d{2}/\d{2}/\d{4})', text)
    if issue_match:
        original_date = issue_match.group(1)
        result["issue_date"] = convert_date_format(original_date)

    # Convictions - Look for the convictions section
    # The format shows: DATE CONVICTIONS, DISCHARGES AND OTHER ACTIONS
    convictions_section = re.search(r'DATE\s+CONVICTIONS, DISCHARGES AND OTHER ACTIONS(.*?)(?=SEARCH SUCCESSFUL|END OF REPORT)', text, re.DOTALL)
    if convictions_section:
        conviction_text = convictions_section.group(1)
        # Look for date patterns followed by conviction descriptions
        # Updated pattern to better match the actual format
        conviction_matches = re.findall(r'(\d{2}/\d{2}/\d{4})\s+([^\n]+(?:\n(?!\d{2}/\d{2}/\d{4})[^\n]+)*)', conviction_text, re.DOTALL)
        for date, description in conviction_matches:
            # Convert date from DD/MM/YYYY to MM/DD/YYYY
            converted_date = convert_date_format(date)
            
            # Clean up the description
            clean_desc = re.sub(r'\n.*?OFFENCE DATE.*?\n', '', description, flags=re.DOTALL)
            clean_desc = re.sub(r'\n.*?SUSPENSION NO\..*?\n', '', clean_desc, flags=re.DOTALL)
            clean_desc = re.sub(r'\n.*?DEMERIT POINTS.*?\n', '', clean_desc, flags=re.DOTALL)
            clean_desc = re.sub(r'\n.*?SUSPENDED UNTIL.*?\n', '', clean_desc, flags=re.DOTALL)
            # Additional cleaning for inline patterns
            clean_desc = re.sub(r'OFFENCE DATE \d{4}/\d{2}/\d{2}', '', clean_desc)
            clean_desc = re.sub(r'SUSPENSION NO\. \d+', '', clean_desc)
            clean_desc = re.sub(r'SUSPENDED UNTIL [A-Z]+\. \d+, \d{4},', '', clean_desc)
            clean_desc = re.sub(r'DEMERIT POINTS - [A-Z\s]+ SUSPENSION\.', '', clean_desc)
            clean_desc = clean_desc.strip()
            
            if clean_desc and len(clean_desc) > 5:  # Avoid very short descriptions
                result["convictions"].append({
                    "description": clean_desc,
                    "offence_date": converted_date
                })
    with open("mvr_result.json", "w") as f:
        json.dump(result, f, indent=4)
    return result
