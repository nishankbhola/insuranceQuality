import fitz  # PyMuPDF
import re
import json

def extract_quote_data(path):
    # Use PyMuPDF instead of pdfplumber
    doc = fitz.open(path)
    
    # Extract text with better structure preservation
    text = ""
    for page in doc:
        # Get text with layout preservation - this maintains spatial relationships better
        text += page.get_text("text")
    
    doc.close()
    
    # Save debug info (same as before)
    with open("quote_test.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    result = {
        "quote_effective_date": None,
        "quote_prepared_by": None,
        "applicant": {},
        "drivers": [],
        "vehicles": [],
        "convictions": [],
        "suspensions": [],
        "claims": [],
        "coverages": [],
        "address": None
    }

    # Effective Date - more specific patterns
    effective_patterns = [
        r"Effective Date:\s*(\d{2}/\d{2}/\d{4})",
        r"Effective:\s*(\d{2}/\d{2}/\d{4})"
    ]
    for pattern in effective_patterns:
        effective_date_match = re.search(pattern, text)
        if effective_date_match:
            result["quote_effective_date"] = effective_date_match.group(1)
            break

    # Prepared By - more specific pattern
    prepared_by_match = re.search(r"Prepared[^\n]*by\s+([A-Za-z\s]+?)(?:\s+Effective|\n)", text)
    if prepared_by_match:
        result["quote_prepared_by"] = prepared_by_match.group(1).strip()

    # Address - look for street address pattern
    address_patterns = [
        r"(\d+\s+[A-Za-z\s]+(?:Ave|St|Street|Avenue|Road|Rd|Dr|Drive|Blvd|Boulevard|Way|Lane|Ln|Court|Ct|Place|Pl))\s*,?\s*([A-Za-z\s]+)",
        r"(\d+\s+[A-Za-z\s]+)\n([A-Za-z\s]+),\s+[A-Z]{2}"
    ]
    for pattern in address_patterns:
        address_match = re.search(pattern, text)
        if address_match:
            result["address"] = f"{address_match.group(1).strip()}, {address_match.group(2).strip()}"
            break

    # Extract drivers more carefully
    found_drivers = set()
    
    # Pattern 1: Look for "Driver X of Y | NAME" format
    driver_section_matches = re.findall(r"Driver (\d+) of (\d+) \| ([A-Za-z\s]+)", text)
    for driver_num, total_drivers, name in driver_section_matches:
        driver_name = name.strip()
        if driver_name and len(driver_name.split()) >= 2 and driver_name not in found_drivers:
            found_drivers.add(driver_name)
            driver_details = _extract_driver_details(text, driver_name)
            if driver_details:
                result["drivers"].append(driver_details)

    # If no drivers found, try alternative patterns
    if not result["drivers"]:
        # Look for license numbers and nearby names
        license_matches = re.findall(r"([A-Z]\d{4}\d{5}\d{5})", text)
        for license_num in license_matches:
            license_index = text.find(license_num)
            if license_index > 0:
                # Look in a reasonable window around the license number
                window_start = max(0, license_index - 200)
                window_end = min(len(text), license_index + 200)
                window_text = text[window_start:window_end]
                
                # Look for proper names (first and last name)
                name_patterns = [
                    r"([A-Z][a-z]+\s+[A-Z][a-z]+)",
                    r"Driver.*?\|\s*([A-Za-z]+\s+[A-Za-z]+)"
                ]
                
                for pattern in name_patterns:
                    name_matches = re.findall(pattern, window_text)
                    for name in name_matches:
                        driver_name = name.strip()
                        if (driver_name and len(driver_name.split()) >= 2 and 
                            driver_name not in found_drivers and
                            not any(word.lower() in ['driver', 'licence', 'number', 'province'] for word in driver_name.lower().split())):
                            found_drivers.add(driver_name)
                            driver_details = _extract_driver_details(text, driver_name, license_num)
                            if driver_details:
                                result["drivers"].append(driver_details)
                            break
                    if result["drivers"]:
                        break

    # Extract applicant from drivers if not found elsewhere
    if result["drivers"] and not result["applicant"].get("first_name"):
        first_driver = result["drivers"][0]
        name_parts = first_driver["full_name"].split()
        if len(name_parts) >= 2:
            result["applicant"]["first_name"] = name_parts[0]
            result["applicant"]["last_name"] = " ".join(name_parts[1:])

    # Vehicles - Look for VIN patterns and surrounding info
    vehicle_sections = re.findall(r"Vehicle (\d+) of (\d+) \| (.*?)(?=Vehicle \d+ of \d+|Driver|Coverages|$)", text, re.DOTALL)
    
    for vehicle_num, total_vehicles, vehicle_text in vehicle_sections:
        vehicle_info = _extract_vehicle_details(vehicle_text)
        if vehicle_info:
            result["vehicles"].append(vehicle_info)

    # If no vehicles found through sections, try to find VINs directly
    if not result["vehicles"]:
        vin_matches = re.findall(r"([A-HJ-NPR-Z0-9]{17})", text)  # More accurate VIN pattern
        for vin in vin_matches:
            # Look for vehicle details around the VIN
            vin_index = text.find(vin)
            if vin_index > 0:
                window_start = max(0, vin_index - 300)
                window_end = min(len(text), vin_index + 300)
                window_text = text[window_start:window_end]
                
                vehicle_info = _extract_vehicle_details(window_text)
                vehicle_info["vin"] = vin
                result["vehicles"].append(vehicle_info)

    # Convictions - Much more specific extraction
    # Look for actual conviction patterns in dedicated sections
    conviction_section_patterns = [
        r"Convictions?\s*:?\s*(.*?)(?=Suspensions?|Coverage|Vehicle|Driver|Effective|$)",
        r"Violations?\s*:?\s*(.*?)(?=Suspensions?|Coverage|Vehicle|Driver|Effective|$)"
    ]
    
    for pattern in conviction_section_patterns:
        section_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if section_match:
            conviction_text = section_match.group(1)
            
            # Look for specific conviction patterns
            conviction_patterns = [
                r"([A-Za-z][A-Za-z\s\-]{10,})\s+(\d{2}/\d{2}/\d{4})",
                r"Description[:\s]*([A-Za-z][A-Za-z\s\-]{5,})[:\s]*Date[:\s]*(\d{2}/\d{2}/\d{4})",
                r"(\d{2}/\d{2}/\d{4})\s+([A-Za-z][A-Za-z\s\-]{10,})"  # Date followed by description
            ]
            
            for conv_pattern in conviction_patterns:
                convictions = re.findall(conv_pattern, conviction_text)
                for match in convictions:
                    if len(match) == 2:
                        desc, date = match
                        # Validate it's actually a conviction description
                        if (len(desc.strip()) > 10 and 
                            not any(word in desc.lower() for word in ['driver', 'licence', 'prepared', 'effective', 'vehicle', 'policy']) and
                            re.match(r'\d{2}/\d{2}/\d{4}', date)):
                            result["convictions"].append({
                                "description": desc.strip(),
                                "date": date
                            })
    
    # Remove duplicate convictions
    seen_convictions = set()
    unique_convictions = []
    for conv in result["convictions"]:
        conv_key = (conv["description"].lower(), conv["date"])
        if conv_key not in seen_convictions:
            seen_convictions.add(conv_key)
            unique_convictions.append(conv)
    result["convictions"] = unique_convictions

    # Enhanced Convictions and Suspensions Extraction
    # Look for the specific structure found in the PDF
    convictions_and_suspensions = _extract_convictions_and_suspensions(text)
    result["convictions"] = convictions_and_suspensions["convictions"]
    result["suspensions"] = convictions_and_suspensions["suspensions"]

    # Claims Extraction - Look for claims information in the PDF
    claims_info = _extract_claims_information(text)
    result["claims"] = claims_info

    # Coverages - more specific extraction
    coverage_section = re.search(r"Coverage[s]?\s*(.*?)(?=Driver|Vehicle|Effective|$)", text, re.DOTALL | re.IGNORECASE)
    if coverage_section:
        coverage_text = coverage_section.group(1)
        coverage_patterns = [
            r"(Bodily Injury|Property Damage|Accident Benefits|All Perils|Direct Compensation|Uninsured Automobile|Accident Waiver|Loss of Use|Liab to Unowned Veh|Family Protection)[^\d]*\$?([\d,]+)",
            r"(Third Party Liability|Collision|Comprehensive)[^\d]*\$?([\d,]+)"
        ]
        
        for pattern in coverage_patterns:
            coverage_matches = re.findall(pattern, coverage_text, re.IGNORECASE)
            for label, limit in coverage_matches:
                result["coverages"].append({
                    "type": label.strip(),
                    "limit": limit.replace(",", "")
                })

    # Save debug info
    with open("quote_result.json", "w") as f:
        json.dump(result, f, indent=4)

    return result


def _extract_claims_information(text):
    """Extract claims information from the PDF text"""
    claims = []
    
    # Pattern 1: Look for "Non-responsible Collision" claims
    # This pattern matches the structure found in the PDF
    non_responsible_pattern = r'Non-responsible Collision\s*\n\s*Description\s*\n\s*(\d{2}/\d{2}/\d{4})\s*\n\s*Date\s*\n\s*(No|Yes)\s*\n\s*Charge\s*\n\s*([^\n]+?)\s*\n\s*Vehicle Involved'
    non_responsible_matches = re.findall(non_responsible_pattern, text, re.IGNORECASE)
    
    for match in non_responsible_matches:
        date, charge, vehicle = match
        claim = {
            "claim_type": "Non-responsible Collision",
            "date": date,
            "charge": charge,
            "vehicle_involved": vehicle.strip(),
            "driver": None,  # Will be populated if we can match to a driver
            "amount": None,
            "status": "Closed" if charge == "No" else "Open"
        }
        claims.append(claim)
    
    # Pattern 2: Look for other claim patterns that might exist
    # Pattern for claims with amounts
    claim_amount_pattern = r'([A-Za-z][A-Za-z\s\-]{10,})\s*\n\s*Description\s*\n\s*(\d{2}/\d{2}/\d{4})\s*\n\s*Date\s*\n\s*\$?([\d,]+\.?\d*)'
    claim_amount_matches = re.findall(claim_amount_pattern, text, re.IGNORECASE)
    
    for match in claim_amount_matches:
        description, date, amount = match
        # Skip if it's already captured as a conviction or suspension
        if any(word in description.lower() for word in ['speeding', 'prohibited', 'suspension', 'administrative']):
            continue
            
        claim = {
            "claim_type": description.strip(),
            "date": date,
            "amount": amount.replace(',', ''),
            "driver": None,
            "charge": None,
            "vehicle_involved": None,
            "status": "Closed"
        }
        claims.append(claim)
    
    # Pattern 3: Look for claims without amounts but with other details
    claim_no_amount_pattern = r'([A-Za-z][A-Za-z\s\-]{10,})\s*\n\s*Description\s*\n\s*(\d{2}/\d{2}/\d{4})\s*\n\s*Date\s*\n\s*([^\n]+)'
    claim_no_amount_matches = re.findall(claim_no_amount_pattern, text, re.IGNORECASE)
    
    for match in claim_no_amount_matches:
        description, date, details = match
        # Skip if it's already captured as a conviction or suspension
        if any(word in description.lower() for word in ['speeding', 'prohibited', 'suspension', 'administrative']):
            continue
            
        claim = {
            "claim_type": description.strip(),
            "date": date,
            "details": details.strip(),
            "driver": None,
            "amount": None,
            "charge": None,
            "vehicle_involved": None,
            "status": "Closed"
        }
        claims.append(claim)
    
    # Remove duplicates and filter out invalid claims
    seen_claims = set()
    unique_claims = []
    for claim in claims:
        # Skip claims with invalid claim_type (too long or contains newlines)
        if len(claim["claim_type"]) > 100 or '\n' in claim["claim_type"]:
            continue
            
        claim_key = (claim["claim_type"].lower(), claim["date"])
        if claim_key not in seen_claims:
            seen_claims.add(claim_key)
            unique_claims.append(claim)
    
    return unique_claims

def _extract_vehicle_details(vehicle_text):
    """Extract vehicle information from vehicle section text using PyMuPDF's better structure"""
    vehicle_info = {
        "vehicle_type": None,
        "vin": None,
        "body_style": None,
        "fuel_type": None,
        "hybrid": None,
        "primary_use": None,
        "annual_km": None,
        "business_km": None,
        "daily_km": None,
        "garaging_location": None,
        "single_vehicle_mvd": None,
        "leased": None,
        "cylinders": None,
        "anti_theft_device_type": None,
        "anti_theft_manufacturer": None,
        "anti_theft_engraving": None,
        "purchase_condition": None,
        "purchase_date": None,
        "km_at_purchase": None,
        "list_price_new": None,
        "purchase_price": None,
        "winter_tires": None,
        "parking_at_night": None
    }
    
    # Extract VIN
    vin_match = re.search(r"([A-HJ-NPR-Z0-9]{17})", vehicle_text)
    if vin_match:
        vehicle_info["vin"] = vin_match.group(1)
    
    # Extract Vehicle Type - look for "Vehicle Type" followed by type
    vehicle_type_match = re.search(r"Vehicle Type\s*(Private Passenger|Commercial|Motorcycle|RV|Trailer)", vehicle_text, re.IGNORECASE)
    if vehicle_type_match:
        vehicle_info["vehicle_type"] = vehicle_type_match.group(1)
    else:
        # Try alternative pattern - type on line before "Vehicle Type"
        vehicle_type_match = re.search(r"(Private Passenger|Commercial|Motorcycle|RV|Trailer)\s*\n\s*Vehicle Type", vehicle_text, re.IGNORECASE)
        if vehicle_type_match:
            vehicle_info["vehicle_type"] = vehicle_type_match.group(1)

    # Extract Body Style - look for "Body Style" followed by style
    body_style_match = re.search(r"Body Style\s*([A-Za-z\s/]+)", vehicle_text, re.IGNORECASE)
    if body_style_match:
        vehicle_info["body_style"] = body_style_match.group(1).strip()
    else:
        # Try alternative pattern - style on line before "Body Style"
        body_style_match = re.search(r"([A-Za-z\s/]+)\s*\n\s*Body Style", vehicle_text, re.IGNORECASE)
        if body_style_match:
            vehicle_info["body_style"] = body_style_match.group(1).strip()

    # Extract Fuel Type - look for "Fuel Type" followed by type
    fuel_type_match = re.search(r"Fuel Type\s*(Gasoline|Diesel|Electric|Hybrid|Plug-in Hybrid)", vehicle_text, re.IGNORECASE)
    if fuel_type_match:
        vehicle_info["fuel_type"] = fuel_type_match.group(1)
    else:
        # Try alternative pattern - type on line before "Fuel Type"
        fuel_type_match = re.search(r"(Gasoline|Diesel|Electric|Hybrid|Plug-in Hybrid)\s*\n\s*Fuel Type", vehicle_text, re.IGNORECASE)
        if fuel_type_match:
            vehicle_info["fuel_type"] = fuel_type_match.group(1)

    # Extract Hybrid - look for "Hybrid" followed by value
    hybrid_match = re.search(r"Hybrid\s*(Yes|No)", vehicle_text, re.IGNORECASE)
    if hybrid_match:
        vehicle_info["hybrid"] = hybrid_match.group(1)
    else:
        # Try alternative pattern - value on line before "Hybrid"
        hybrid_match = re.search(r"(Yes|No)\s*\n\s*Hybrid", vehicle_text, re.IGNORECASE)
        if hybrid_match:
            vehicle_info["hybrid"] = hybrid_match.group(1)

    # Extract Primary Use - look for "Primary Use" followed by use
    primary_use_match = re.search(r"Primary Use\s*(Pleasure|Business|Commute|Other)", vehicle_text, re.IGNORECASE)
    if primary_use_match:
        vehicle_info["primary_use"] = primary_use_match.group(1)
    else:
        # Try alternative pattern - use on line before "Primary Use"
        primary_use_match = re.search(r"(Pleasure|Business|Commute|Other)\s*\n\s*Primary Use", vehicle_text, re.IGNORECASE)
        if primary_use_match:
            vehicle_info["primary_use"] = primary_use_match.group(1)

    # Extract Annual km - look for "Annual km" followed by number
    annual_km_match = re.search(r"Annual km\s*(\d+)", vehicle_text)
    if annual_km_match:
        vehicle_info["annual_km"] = int(annual_km_match.group(1))
    else:
        # Try alternative pattern - number on line before "Annual km"
        annual_km_match = re.search(r"(\d+)\s*\n\s*Annual km", vehicle_text)
        if annual_km_match:
            vehicle_info["annual_km"] = int(annual_km_match.group(1))

    # Extract Business km - look for "Business km" followed by number
    business_km_match = re.search(r"Business km\s*(\d+)", vehicle_text)
    if business_km_match:
        vehicle_info["business_km"] = int(business_km_match.group(1))
    else:
        # Try alternative pattern - number on line before "Business km"
        business_km_match = re.search(r"(\d+)\s*\n\s*Business km", vehicle_text)
        if business_km_match:
            vehicle_info["business_km"] = int(business_km_match.group(1))

    # Extract Daily km - look for "Daily km" followed by number
    daily_km_match = re.search(r"Daily km\s*(\d+)", vehicle_text)
    if daily_km_match:
        vehicle_info["daily_km"] = int(daily_km_match.group(1))
    else:
        # Try alternative pattern - number on line before "Daily km"
        daily_km_match = re.search(r"(\d+)\s*\n\s*Daily km", vehicle_text)
        if daily_km_match:
            vehicle_info["daily_km"] = int(daily_km_match.group(1))

    # Extract Garaging Location - look for location on line before "Garaging Location"
    garaging_match = re.search(r"([A-Z]+\s+[A-Z0-9]+)\s*\n\s*Garaging Location", vehicle_text)
    if garaging_match:
        vehicle_info["garaging_location"] = garaging_match.group(1).strip()
    else:
        # Try alternative pattern - location on same line as "Garaging Location"
        garaging_match = re.search(r"([A-Z]+\s+[A-Z0-9]+)\s*Garaging Location", vehicle_text)
        if garaging_match:
            vehicle_info["garaging_location"] = garaging_match.group(1).strip()
        else:
            # Try pattern for location after "Garaging Location" (less likely but possible)
            garaging_match = re.search(r"Garaging Location\s*([A-Z]+\s+[A-Z0-9]+)", vehicle_text)
            if garaging_match:
                vehicle_info["garaging_location"] = garaging_match.group(1).strip()

    # Extract Single Vehicle MVD - look for "Single Vehicle MVD" followed by value
    single_mvd_match = re.search(r"Single Vehicle MVD\s*(Yes|No)", vehicle_text, re.IGNORECASE)
    if single_mvd_match:
        vehicle_info["single_vehicle_mvd"] = single_mvd_match.group(1)
    else:
        # Try alternative pattern - value on line before "Single Vehicle MVD"
        single_mvd_match = re.search(r"(Yes|No)\s*\n\s*Single Vehicle MVD", vehicle_text, re.IGNORECASE)
        if single_mvd_match:
            vehicle_info["single_vehicle_mvd"] = single_mvd_match.group(1)

    # Extract Leased - look for "Leased" followed by value
    leased_match = re.search(r"Leased\s*(Yes|No)", vehicle_text, re.IGNORECASE)
    if leased_match:
        vehicle_info["leased"] = leased_match.group(1)
    else:
        # Try alternative pattern - value on line before "Leased"
        leased_match = re.search(r"(Yes|No)\s*\n\s*Leased", vehicle_text, re.IGNORECASE)
        if leased_match:
            vehicle_info["leased"] = leased_match.group(1)

    # Extract Cylinders - look for "Cylinders" followed by number
    cylinders_match = re.search(r"Cylinders\s*(\d+)", vehicle_text)
    if cylinders_match:
        vehicle_info["cylinders"] = int(cylinders_match.group(1))
    else:
        # Try alternative pattern - number on line before "Cylinders"
        cylinders_match = re.search(r"(\d+)\s*\n\s*Cylinders", vehicle_text)
        if cylinders_match:
            vehicle_info["cylinders"] = int(cylinders_match.group(1))

    # Extract Purchase Condition - look for "Purchase Condition" followed by condition
    purchase_condition_match = re.search(r"Purchase\s*Condition\s*(Used|New)", vehicle_text, re.IGNORECASE)
    if purchase_condition_match:
        vehicle_info["purchase_condition"] = purchase_condition_match.group(1)
    else:
        # Try alternative pattern - condition on line before "Purchase Condition"
        purchase_condition_match = re.search(r"(Used|New)\s*\n\s*Purchase\s*Condition", vehicle_text, re.IGNORECASE)
        if purchase_condition_match:
            vehicle_info["purchase_condition"] = purchase_condition_match.group(1)

    # Extract Purchase Date - look for "Purchase Date" followed by date
    purchase_date_match = re.search(r"Purchase Date\s*(\d{2}/\d{2}/\d{4})", vehicle_text)
    if purchase_date_match:
        vehicle_info["purchase_date"] = purchase_date_match.group(1)
    else:
        # Try alternative pattern - date on line before "Purchase Date"
        purchase_date_match = re.search(r"(\d{2}/\d{2}/\d{4})\s*\n\s*Purchase Date", vehicle_text)
        if purchase_date_match:
            vehicle_info["purchase_date"] = purchase_date_match.group(1)

    # Extract km at Purchase - look for "km at Purchase" followed by number
    km_purchase_match = re.search(r"km at Purchase\s*(\d+)", vehicle_text)
    if km_purchase_match:
        vehicle_info["km_at_purchase"] = int(km_purchase_match.group(1))
    else:
        # Try alternative pattern - number on line before "km at Purchase"
        km_purchase_match = re.search(r"(\d+)\s*\n\s*km at Purchase", vehicle_text)
        if km_purchase_match:
            vehicle_info["km_at_purchase"] = int(km_purchase_match.group(1))

    # Extract Winter Tires - look for "Winter Tires" followed by value
    winter_tires_match = re.search(r"Winter Tires\s*(Yes|No)", vehicle_text, re.IGNORECASE)
    if winter_tires_match:
        vehicle_info["winter_tires"] = winter_tires_match.group(1)
    else:
        # Try alternative pattern - value on line before "Winter Tires"
        winter_tires_match = re.search(r"(Yes|No)\s*\n\s*Winter Tires", vehicle_text, re.IGNORECASE)
        if winter_tires_match:
            vehicle_info["winter_tires"] = winter_tires_match.group(1)

    # Set None for missing values
    for key in vehicle_info:
        if vehicle_info[key] is None:
            vehicle_info[key] = None

    return vehicle_info

def _extract_driver_details(text, driver_name, license_num=None):
    """Extract detailed information for a specific driver using PyMuPDF's better text structure"""
    driver_info = {
        "full_name": driver_name,
        "birth_date": None,
        "single": None,
        "marital_status": None,
        "male": None,
        "gender": None,
        "insured": None,
        "relationship_to_applicant": None,
        "driver_training": None,
        "driver_training_date": None,
        "out_of_province_country_driver": None,
        "licence_class": None,
        "date_g": None,
        "date_g2": None,
        "date_g1": None,
        "licence_number": None,
        "licence_province": None,
        "occupation": None,
        "date_insured": None,
        "current_carrier": None,
        "date_with_company": None,
        "brokerage_insured": None,
        "owner_principal": None,
        "applicant_lives_with_parents": None,
        "student_away_at_school_km": None,
        "retired": None
    }
    
    # Find the driver section in the text
    driver_patterns = [
        rf"Driver \d+ of \d+ \| {re.escape(driver_name)}(.*?)(?=Driver \d+ of \d+|Vehicle|Coverage|Effective|$)",
        rf"{re.escape(driver_name)}(.*?)(?=Driver|Vehicle|Coverage|Effective|\n[A-Z][a-z]+\s+[A-Z][a-z]+)"
    ]
    
    driver_section = None
    for pattern in driver_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            driver_section = match.group(1)
            break
    
    if not driver_section:
        # Fallback: look for driver info in a window around the name
        name_index = text.find(driver_name)
        if name_index > 0:
            window_start = max(0, name_index)
            window_end = min(len(text), name_index + 1000)
            driver_section = text[window_start:window_end]
    
    if driver_section:
        # With PyMuPDF's better structure, we can use more precise patterns
        
        # Extract Birth Date - look for "Birth Date" followed by date
        birth_date_match = re.search(r"Birth Date\s*(\d{2}/\d{2}/\d{4})", driver_section)
        if birth_date_match:
            driver_info["birth_date"] = birth_date_match.group(1)
        else:
            # Try alternative pattern - date on line before "Birth Date"
            birth_date_match = re.search(r"(\d{2}/\d{2}/\d{4})\s*\n\s*Birth Date", driver_section)
            if birth_date_match:
                driver_info["birth_date"] = birth_date_match.group(1)

        # Extract Marital Status - look for "Marital Status" followed by status
        marital_match = re.search(r"Marital Status\s*(Single|Married|Divorced|Widowed)", driver_section, re.IGNORECASE)
        if marital_match:
            marital_status = marital_match.group(1)
            driver_info["marital_status"] = marital_status
            driver_info["single"] = "Yes" if marital_status.lower() == 'single' else "No"
        else:
            # Try alternative pattern - status on line before "Marital Status"
            marital_match = re.search(r"(Single|Married|Divorced|Widowed)\s*\n\s*Marital Status", driver_section, re.IGNORECASE)
            if marital_match:
                marital_status = marital_match.group(1)
                driver_info["marital_status"] = marital_status
                driver_info["single"] = "Yes" if marital_status.lower() == 'single' else "No"

        # Extract Gender - look for "Gender" followed by gender
        gender_match = re.search(r"Gender\s*(Male|Female)", driver_section, re.IGNORECASE)
        if gender_match:
            gender = gender_match.group(1)
            driver_info["gender"] = gender
            driver_info["male"] = "Yes" if gender.lower() == 'male' else "No"
        else:
            # Try alternative pattern - gender on line before "Gender"
            gender_match = re.search(r"(Male|Female)\s*\n\s*Gender", driver_section, re.IGNORECASE)
            if gender_match:
                gender = gender_match.group(1)
                driver_info["gender"] = gender
                driver_info["male"] = "Yes" if gender.lower() == 'male' else "No"

        # Extract Insured status - look for "Insured" word
        insured_match = re.search(r"Insured", driver_section, re.IGNORECASE)
        driver_info["insured"] = "Yes" if insured_match else "No"

        # Look for "(Prn)" in the driver name to determine relationship
        if "(Prn)" in driver_name:
            driver_info["relationship_to_applicant"] = "Principal"

        # Extract Driver Training - look for "Driver Training" followed by value
        driver_training_match = re.search(r"Driver Training\s*(Yes|No)", driver_section, re.IGNORECASE)
        if driver_training_match:
            driver_info["driver_training"] = driver_training_match.group(1)
        else:
            # Try alternative pattern - value on line before "Driver Training"
            driver_training_match = re.search(r"(Yes|No)\s*\n\s*Driver Training", driver_section, re.IGNORECASE)
            if driver_training_match:
                driver_info["driver_training"] = driver_training_match.group(1)

        # Extract Out of Province Driver - look for "Out of Province" followed by value
        out_province_match = re.search(r"Out of Province / Country Driver\s*(Yes|No)", driver_section, re.IGNORECASE)
        if out_province_match:
            driver_info["out_of_province_country_driver"] = out_province_match.group(1)
        else:
            # Try alternative pattern - value on line before "Out of Province"
            out_province_match = re.search(r"(Yes|No)\s*\n\s*Out of Province / Country Driver", driver_section, re.IGNORECASE)
            if out_province_match:
                driver_info["out_of_province_country_driver"] = out_province_match.group(1)

        # Extract Licence Class - look for "Licence Class" followed by class
        licence_class_match = re.search(r"Licence Class\s*(G1|G2|G|M1|M2|M)", driver_section, re.IGNORECASE)
        if licence_class_match:
            driver_info["licence_class"] = licence_class_match.group(1)
        else:
            # Try alternative pattern - class on line before "Licence Class"
            licence_class_match = re.search(r"(G1|G2|G|M1|M2|M)\s*\n\s*Licence Class", driver_section, re.IGNORECASE)
            if licence_class_match:
                driver_info["licence_class"] = licence_class_match.group(1)

        # Extract all dates and their corresponding labels first
        date_mappings = {}
        
        # Look for all "Date G", "Date G2", "Date G1" patterns and their associated dates
        # The dates appear BEFORE the labels in the PDF structure
        date_patterns = [
            (r"(\d{1,2}/\d{1,2}/\d{4})\s*\n\s*Date G", "date_g"),
            (r"(\d{1,2}/\d{1,2}/\d{4})\s*Date G", "date_g"),
            (r"(\d{1,2}/\d{1,2}/\d{4})\s*\n\s*Date G2", "date_g2"),
            (r"(\d{1,2}/\d{1,2}/\d{4})\s*Date G2", "date_g2"),
            (r"(\d{1,2}/\d{1,2}/\d{4})\s*\n\s*Date G1", "date_g1"),
            (r"(\d{1,2}/\d{1,2}/\d{4})\s*Date G1", "date_g1")
        ]
        
        for pattern, field_name in date_patterns:
            match = re.search(pattern, driver_section)
            if match:
                potential_date = match.group(1)
                # Additional validation: make sure it's actually a date and not a license number
                if re.match(r'\d{1,2}/\d{1,2}/\d{4}', potential_date) and not re.match(r'[A-Z]\d{4}\d{5}\d{5}', potential_date):
                    date_mappings[field_name] = potential_date
        
        # Now assign the dates to the correct fields
        # The mapping should be direct - Date G maps to date_g, Date G2 maps to date_g2, Date G1 maps to date_g1
        driver_info["date_g"] = date_mappings.get("date_g")  # Date G maps to date_g
        driver_info["date_g2"] = date_mappings.get("date_g2")  # Date G2 maps to date_g2
        driver_info["date_g1"] = date_mappings.get("date_g1")  # Date G1 maps to date_g1

        # Debug: Save the driver section to see what we're working with
        with open("driver_section_debug.txt", "w", encoding="utf-8") as f:
            f.write(f"Driver: {driver_name}\n")
            f.write(f"Section: {driver_section}\n")
            f.write(f"Extracted dates - G: {driver_info['date_g']}, G2: {driver_info['date_g2']}, G1: {driver_info['date_g1']}\n")
            
            # Add detailed debugging for each date extraction
            f.write("\n=== DETAILED DEBUG ===\n")
            
            # Test each pattern for all date fields
            f.write("Testing all date patterns:\n")
            for i, (pattern, field_name) in enumerate(date_patterns):
                matches = re.findall(pattern, driver_section)
                f.write(f"Pattern {i+1} ({field_name}): {pattern} -> Found: {matches}\n")
            
            # Look for all date patterns in the section
            f.write("\nAll date patterns found:\n")
            all_dates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', driver_section)
            f.write(f"All dates: {all_dates}\n")
            
            # Look for Date G1 specifically
            f.write("\nLooking for 'Date G1' specifically:\n")
            date_g1_context = re.search(r'Date G1.*?(?=\n[A-Z]|$)', driver_section, re.DOTALL)
            if date_g1_context:
                f.write(f"Date G1 context: '{date_g1_context.group(0)}'\n")
            else:
                f.write("No Date G1 context found\n")

        # Extract Licence Number - look for "Licence Number" followed by number
        licence_number_match = re.search(r"Licence Number\s*([A-Z]\d{4}\d{5}\d{5})", driver_section)
        if licence_number_match:
            driver_info["licence_number"] = licence_number_match.group(1)
        else:
            # Try alternative pattern - number on line before "Licence Number"
            licence_number_match = re.search(r"([A-Z]\d{4}\d{5}\d{5})\s*\n\s*Licence Number", driver_section)
            if licence_number_match:
                driver_info["licence_number"] = licence_number_match.group(1)

        # Extract Licence Province - look for "Licence Province" followed by province
        licence_province_match = re.search(r"Licence Province\s*([A-Z]{2})", driver_section)
        if licence_province_match:
            driver_info["licence_province"] = licence_province_match.group(1)
        else:
            # Try alternative pattern - province on line before "Licence Province"
            licence_province_match = re.search(r"([A-Z]{2})\s*\n\s*Licence Province", driver_section)
            if licence_province_match:
                driver_info["licence_province"] = licence_province_match.group(1)

        # Extract Date Insured - look for "Date Insured" followed by date
        date_insured_match = re.search(r"Date Insured\s*(\d{2}/\d{2}/\d{4})", driver_section)
        if date_insured_match:
            driver_info["date_insured"] = date_insured_match.group(1)
        else:
            # Try alternative pattern - date on line before "Date Insured"
            date_insured_match = re.search(r"(\d{2}/\d{2}/\d{4})\s*\n\s*Date Insured", driver_section)
            if date_insured_match:
                driver_info["date_insured"] = date_insured_match.group(1)

        # Extract Current Carrier - look for "Current Carrier" followed by carrier name
        current_carrier_match = re.search(r"Current Carrier\s*([A-Za-z\s]+)", driver_section)
        if current_carrier_match:
            driver_info["current_carrier"] = current_carrier_match.group(1).strip()
        else:
            # Try alternative pattern - carrier on line before "Current Carrier"
            current_carrier_match = re.search(r"([A-Za-z\s]+)\s*\n\s*Current Carrier", driver_section)
            if current_carrier_match:
                driver_info["current_carrier"] = current_carrier_match.group(1).strip()

        # Extract Date with Company - look for "Date with Company" followed by date
        date_company_match = re.search(r"Date with\s*Company\s*(\d{2}/\d{2}/\d{4})", driver_section)
        if date_company_match:
            driver_info["date_with_company"] = date_company_match.group(1)
        else:
            # Try alternative pattern - date on line before "Date with Company"
            date_company_match = re.search(r"(\d{2}/\d{2}/\d{4})\s*\n\s*Date with\s*Company", driver_section)
            if date_company_match:
                driver_info["date_with_company"] = date_company_match.group(1)

        # Extract Owner/Principal - look for "Owner/Principal" followed by value
        owner_principal_match = re.search(r"Owner/Principal\s*(Yes|No)", driver_section, re.IGNORECASE)
        if owner_principal_match:
            driver_info["owner_principal"] = owner_principal_match.group(1)
        else:
            # Try alternative pattern - value on line before "Owner/Principal"
            owner_principal_match = re.search(r"(Yes|No)\s*\n\s*Owner/Principal", driver_section, re.IGNORECASE)
            if owner_principal_match:
                driver_info["owner_principal"] = owner_principal_match.group(1)

        # Extract Applicant lives with Parents - look for "Applicant lives with Parents" followed by value
        applicant_parents_match = re.search(r"Applicant lives with Parents\s*(Yes|No)", driver_section, re.IGNORECASE)
        if applicant_parents_match:
            driver_info["applicant_lives_with_parents"] = applicant_parents_match.group(1)
        else:
            # Try alternative pattern - value on line before "Applicant lives with Parents"
            applicant_parents_match = re.search(r"(Yes|No)\s*\n\s*Applicant lives with Parents", driver_section, re.IGNORECASE)
            if applicant_parents_match:
                driver_info["applicant_lives_with_parents"] = applicant_parents_match.group(1)

        # Extract Student Away at School - look for "Student Away at School" followed by value
        student_school_match = re.search(r"Student Away at School \(km\)\s*(Yes|No|\d+)", driver_section, re.IGNORECASE)
        if student_school_match:
            driver_info["student_away_at_school_km"] = student_school_match.group(1)
        else:
            # Try alternative pattern - value on line before "Student Away at School"
            student_school_match = re.search(r"(Yes|No|\d+)\s*\n\s*Student Away at School \(km\)", driver_section, re.IGNORECASE)
            if student_school_match:
                driver_info["student_away_at_school_km"] = student_school_match.group(1)

        # Extract Retired - look for "Retired" followed by value
        retired_match = re.search(r"Retired\s*(Yes|No)", driver_section, re.IGNORECASE)
        if retired_match:
            driver_info["retired"] = retired_match.group(1)
        else:
            # Try alternative pattern - value on line before "Retired"
            retired_match = re.search(r"(Yes|No)\s*\n\s*Retired", driver_section, re.IGNORECASE)
            if retired_match:
                driver_info["retired"] = retired_match.group(1)

        # Extract Licence Number if not found above
        if not driver_info["licence_number"] and license_num:
            driver_info["licence_number"] = license_num
        elif not driver_info["licence_number"]:
            licence_number_match = re.search(r"([A-Z]\d{4}\d{5}\d{5})", driver_section)
            if licence_number_match:
                driver_info["licence_number"] = licence_number_match.group(1)

    # Set None for missing values
    for key in driver_info:
        if driver_info[key] is None:
            driver_info[key] = None

    return driver_info

def _extract_convictions_and_suspensions(text):
    """Extract convictions and suspensions with detailed information"""
    result = {
        "convictions": [],
        "suspensions": []
    }
    
    # Extract convictions - look for specific patterns
    # Pattern 1: Look for "Prohibited Use of Hand-Held Device" specifically
    prohibited_pattern = r"Prohibited Use of Hand-Held Device\s*\n\s*Description\s*\n\s*(\d{2}/\d{2}/\d{4})\s*\n\s*Date\s*\n\s*([^\n]*?)\s*\n\s*km/h\s*\n\s*([A-Za-z]+)\s*\n\s*Severity"
    prohibited_matches = re.findall(prohibited_pattern, text, re.IGNORECASE)
    
    for match in prohibited_matches:
        date, km_h, severity = match
        conviction = {
            "description": "Prohibited Use of Hand-Held Device",
            "date": date,
            "km_h": km_h if km_h.strip() else None,
            "severity": severity
        }
        result["convictions"].append(conviction)
    
    # Pattern 2: Look for other conviction descriptions with more flexible pattern
    conviction_patterns = [
        # Pattern for convictions with km/h and severity (km/h value on separate line)
        r"([A-Za-z][A-Za-z\s\-]{10,})\s*\n\s*Description\s*\n\s*(\d{2}/\d{2}/\d{4})\s*\n\s*Date\s*\n\s*(\d+)\s*\n\s*km/h\s*\n\s*([A-Za-z]+)\s*\n\s*Severity",
        # Pattern for convictions with km/h and severity (km/h value on same line)
        r"([A-Za-z][A-Za-z\s\-]{10,})\s*\n\s*Description\s*\n\s*(\d{2}/\d{2}/\d{4})\s*\n\s*Date\s*\n\s*([^\n]*?)\s*\n\s*km/h\s*\n\s*([A-Za-z]+)\s*\n\s*Severity",
        # Pattern for convictions without km/h (just date and severity)
        r"([A-Za-z][A-Za-z\s\-]{10,})\s*\n\s*Description\s*\n\s*(\d{2}/\d{2}/\d{4})\s*\n\s*Date\s*\n\s*([A-Za-z]+)\s*\n\s*Severity",
    ]
    
    for pattern in conviction_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match) >= 3:
                description = match[0].strip()
                date = match[1].strip()
                
                # Skip if it's not actually a conviction description
                if any(word in description.lower() for word in ['driver', 'licence', 'prepared', 'effective', 'vehicle', 'policy', 'birth', 'marital', 'gender', 'insured', 'relationship', 'training', 'province', 'occupation', 'carrier', 'company', 'brokerage', 'owner', 'principal', 'applicant', 'student', 'retired', 'other', 'class', 'date']):
                    continue
                
                # Skip if it's already captured as "Prohibited Use of Hand-Held Device"
                if "prohibited use of hand-held device" in description.lower():
                    continue
                
                conviction = {
                    "description": description,
                    "date": date,
                    "km_h": None,
                    "severity": None
                }
                
                # Handle different pattern lengths
                if len(match) >= 4:
                    # Pattern with km/h
                    km_h = match[2].strip()
                    severity = match[3].strip()
                    conviction["km_h"] = km_h if km_h and km_h.strip() else None
                    conviction["severity"] = severity
                elif len(match) >= 3:
                    # Pattern without km/h
                    severity = match[2].strip()
                    conviction["severity"] = severity
                
                result["convictions"].append(conviction)
    
    # Extract suspensions - look for specific patterns
    # Pattern 1: Look for "Other - Administrative" specifically
    admin_pattern = r"Other - Administrative\s*\n\s*Description\s*\n\s*(\d{2}/\d{2}/\d{4})\s*\n\s*Date\s*\n\s*(\d+)\s*\n\s*Duration months\s*\n\s*(\d{2}/\d{2}/\d{4})\s*\n\s*Re-Instate Date"
    admin_matches = re.findall(admin_pattern, text, re.IGNORECASE)
    
    for match in admin_matches:
        date, duration, re_instate_date = match
        suspension = {
            "description": "Other - Administrative",
            "date": date,
            "duration_months": int(duration),
            "re_instate_date": re_instate_date
        }
        result["suspensions"].append(suspension)
    
    # Pattern 2: Look for other suspension descriptions
    suspension_patterns = [
        r"([A-Za-z][A-Za-z\s\-]{10,})\s*\n\s*Description\s*\n\s*(\d{2}/\d{2}/\d{4})\s*\n\s*Date\s*\n\s*(\d+)\s*\n\s*Duration months\s*\n\s*(\d{2}/\d{2}/\d{4})\s*\n\s*Re-Instate Date",
    ]
    
    for pattern in suspension_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match) >= 4:
                description = match[0].strip()
                date = match[1].strip()
                duration = match[2].strip()
                re_instate_date = match[3].strip()
                
                # Skip if it's not actually a suspension description
                if any(word in description.lower() for word in ['driver', 'licence', 'prepared', 'effective', 'vehicle', 'policy', 'birth', 'marital', 'gender', 'insured', 'relationship', 'training', 'province', 'occupation', 'carrier', 'company', 'brokerage', 'owner', 'principal', 'applicant', 'student', 'retired', 'other', 'class', 'date']):
                    continue
                
                # Skip if it's already captured as "Other - Administrative"
                if "other - administrative" in description.lower():
                    continue
                
                suspension = {
                    "description": description,
                    "date": date,
                    "duration_months": int(duration),
                    "re_instate_date": re_instate_date
                }
                result["suspensions"].append(suspension)
    
    # Remove duplicates
    seen_convictions = set()
    unique_convictions = []
    for conv in result["convictions"]:
        conv_key = (conv["description"].lower(), conv["date"])
        if conv_key not in seen_convictions:
            seen_convictions.add(conv_key)
            unique_convictions.append(conv)
    result["convictions"] = unique_convictions
    
    seen_suspensions = set()
    unique_suspensions = []
    for susp in result["suspensions"]:
        susp_key = (susp["description"].lower(), susp["date"])
        if susp_key not in seen_suspensions:
            seen_suspensions.add(susp_key)
            unique_suspensions.append(susp)
    result["suspensions"] = unique_suspensions
    
    return result