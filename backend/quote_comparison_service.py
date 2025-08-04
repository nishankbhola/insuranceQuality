import fitz  # PyMuPDF
import json
import re
import os
from datetime import datetime
from validator.compare_engine import ValidationEngine

class QuoteComparisonService:
    """
    Service to compare PDF content with quote_result.json data
    """
    
    def __init__(self):
        self.validation_engine = ValidationEngine()
        self.quote_data = None
        self.load_quote_data()
    
    def load_quote_data(self):
        """Load the quote_result.json data"""
        try:
            with open('quote_result.json', 'r', encoding='utf-8') as f:
                self.quote_data = json.load(f)
        except Exception as e:
            print(f"Error loading quote_result.json: {e}")
            self.quote_data = {}
    
    def extract_pdf_text(self, pdf_path):
        """Extract text from PDF using PyMuPDF with better extraction"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Try multiple extraction methods
                page_text = page.get_text("text")
                if not page_text or len(page_text.strip()) < 50:
                    # Try alternative method
                    page_text = page.get_text("dict")
                    text_content = ""
                    for block in page_text.get("blocks", []):
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line.get("spans", []):
                                    text_content += span.get("text", "") + " "
                    page_text = text_content
                
                text += page_text + "\n"
            
            doc.close()
            
            # Clean up the text
            text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
            text = re.sub(r'\n\s*\n', '\n', text)  # Remove empty lines
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    def extract_pdf_fields(self, pdf_text):
        """Extract key fields from PDF text using structured patterns"""
        extracted_data = {
            "drivers": [],
            "vehicles": [],
            "address": None,
            "quote_effective_date": None,
            "quote_prepared_by": None
        }
        
        # Extract address - look for the specific pattern in the PDF
        address_match = re.search(r"(\d+\s+[A-Z\s]+(?:AVENUE|STREET|ROAD|DRIVE|BLVD))\s+([A-Z\s]+),\s+([A-Z]{2})\s+([A-Z0-9]{3}\s*[A-Z0-9]{3})", pdf_text)
        if address_match:
            street = address_match.group(1).strip()
            city = address_match.group(2).strip()
            province = address_match.group(3).strip()
            postal = address_match.group(4).strip()
            extracted_data["address"] = f"{street}, {city}, {province} {postal}"
        
        # Extract effective date
        effective_match = re.search(r"Effective.*?(\d{4}-\d{2}-\d{2})", pdf_text)
        if effective_match:
            extracted_data["quote_effective_date"] = effective_match.group(1)
        
        # Extract drivers using the structured format from the PDF
        # Pattern: Name License_Number Birth_Year Birth_Month Birth_Day Gender Marital_Status
        # Use finditer to get non-overlapping matches
        driver_matches = []
        
        # First pattern: Driver number + name + license + birth + gender + marital
        for match in re.finditer(r"(\d+)\s+([A-Za-z\s]+)\s+([A-Z]\d{4}-\d{5}-\d{5})\s+(\d{4})\s+(\d{1,2})\s+(\d{1,2})\s+([MF])\s+([SM])", pdf_text):
            driver_matches.append(match.groups())
        
        # Second pattern: Name + license + birth + gender + marital (without driver number)
        for match in re.finditer(r"([A-Za-z\s]+)\s+([A-Z]\d{4}-\d{5}-\d{5})\s+(\d{4})\s+(\d{1,2})\s+(\d{1,2})\s+([MF])\s+([SM])", pdf_text):
            # Check if this name is not already extracted
            name = match.group(1).strip()
            if not any(d[1].strip() == name for d in driver_matches):
                # Add a dummy driver number
                driver_matches.append(("2",) + match.groups())
        
        for driver_match in driver_matches:
            driver_num = driver_match[0]
            name = driver_match[1].strip()
            license_num = driver_match[2]
            birth_year = driver_match[3]
            birth_month = driver_match[4]
            birth_day = driver_match[5]
            gender = "Male" if driver_match[6] == "M" else "Female"
            marital = "Single" if driver_match[7] == "S" else "Married"
            
            driver_info = {
                "full_name": name,
                "birth_date": f"{birth_month}/{birth_day}/{birth_year}",
                "licence_number": license_num,
                "licence_class": None,  # Will extract separately
                "gender": gender,
                "marital_status": marital
            }
            extracted_data["drivers"].append(driver_info)
        
        # Extract vehicle information - look for the specific pattern in the PDF
        vehicle_match = re.search(r"(\d{4})\s+([A-Z\s]+)\s+([A-Z\s]+)\s+([A-Z0-9]+)\s+([A-Z\s-]+)\s+([A-Z0-9]{17})", pdf_text)
        if vehicle_match:
            year = vehicle_match.group(1)
            make = vehicle_match.group(2).strip()
            model = vehicle_match.group(3).strip()
            trim = vehicle_match.group(4).strip()
            body_type = vehicle_match.group(5).strip()
            vin = vehicle_match.group(6)
            
            vehicle_info = {
                "vin": vin,
                "vehicle_type": "Private Passenger",
                "fuel_type": "Gasoline",
                "primary_use": "Pleasure",
                "garaging_location": extracted_data.get("address", ""),
                "year": year,
                "make": make,
                "model": model,
                "trim": trim,
                "body_type": body_type
            }
            extracted_data["vehicles"].append(vehicle_info)
        
        # Also try to find VIN directly
        vin_matches = re.findall(r"([A-Z0-9]{17})", pdf_text)
        for vin in vin_matches:
            if not any(v.get("vin") == vin for v in extracted_data["vehicles"]):
                vehicle_info = {
                    "vin": vin,
                    "vehicle_type": "Private Passenger",
                    "fuel_type": "Gasoline",
                    "primary_use": "Pleasure",
                    "garaging_location": extracted_data.get("address", "")
                }
                extracted_data["vehicles"].append(vehicle_info)
        
        return extracted_data
    
    def _extract_driver_details(self, text, match):
        """Extract detailed driver information from text"""
        driver_info = {
            "full_name": None,
            "birth_date": None,
            "licence_number": None,
            "licence_class": None,
            "gender": None,
            "marital_status": None
        }
        
        # Extract name
        if len(match) >= 3:
            driver_info["full_name"] = match[2].strip()
        elif len(match) >= 1:
            driver_info["full_name"] = match[0].strip()
        
        # Look for license number near the name
        if driver_info["full_name"]:
            name_index = text.find(driver_info["full_name"])
            if name_index > 0:
                window_start = max(0, name_index - 300)
                window_end = min(len(text), name_index + 300)
                window_text = text[window_start:window_end]
                
                # Extract license number
                license_match = re.search(r"([A-Z]\d{4}\d{5}\d{5})", window_text)
                if license_match:
                    driver_info["licence_number"] = license_match.group(1)
                
                # Extract birth date
                birth_match = re.search(r"(\d{2}/\d{2}/\d{4})", window_text)
                if birth_match:
                    driver_info["birth_date"] = birth_match.group(1)
        
        return driver_info if driver_info["full_name"] else None
    
    def _find_driver_by_license(self, text, license_num):
        """Find driver information by license number"""
        license_index = text.find(license_num)
        if license_index > 0:
            window_start = max(0, license_index - 400)
            window_end = min(len(text), license_index + 400)
            window_text = text[window_start:window_end]
            
            # Look for name near license
            name_patterns = [
                r"([A-Z][a-z]+\s+[A-Z][a-z]+)",
                r"Driver.*?\|\s*([A-Za-z]+\s+[A-Za-z]+)"
            ]
            
            for pattern in name_patterns:
                name_matches = re.findall(pattern, window_text)
                for name in name_matches:
                    driver_info = {
                        "full_name": name.strip(),
                        "licence_number": license_num,
                        "birth_date": None,
                        "licence_class": None,
                        "gender": None,
                        "marital_status": None
                    }
                    
                    # Extract birth date
                    birth_match = re.search(r"(\d{2}/\d{2}/\d{4})", window_text)
                    if birth_match:
                        driver_info["birth_date"] = birth_match.group(1)
                    
                    return driver_info
        
        return None
    
    def _extract_vehicle_details(self, text, vin):
        """Extract vehicle information by VIN"""
        vin_index = text.find(vin)
        if vin_index > 0:
            window_start = max(0, vin_index - 500)
            window_end = min(len(text), vin_index + 500)
            window_text = text[window_start:window_end]
            
            vehicle_info = {
                "vin": vin,
                "vehicle_type": None,
                "fuel_type": None,
                "primary_use": None,
                "garaging_location": None
            }
            
            # Extract vehicle type
            type_patterns = [
                r"Private Passenger",
                r"Commercial",
                r"Motorcycle"
            ]
            for pattern in type_patterns:
                if pattern in window_text:
                    vehicle_info["vehicle_type"] = pattern
                    break
            
            # Extract fuel type
            fuel_patterns = [
                r"Gasoline",
                r"Diesel",
                r"Electric",
                r"Hybrid"
            ]
            for pattern in fuel_patterns:
                if pattern in window_text:
                    vehicle_info["fuel_type"] = pattern
                    break
            
            return vehicle_info
        
        return None
    
    def compare_data(self, pdf_path):
        """Main comparison function"""
        try:
            # Extract text from PDF
            pdf_text = self.extract_pdf_text(pdf_path)
            if not pdf_text:
                return {"error": "Could not extract text from PDF"}
            
            # Extract fields from PDF
            pdf_data = self.extract_pdf_fields(pdf_text)
            
            # Save extracted data for debugging
            extracted_data = {
                "pdf_text": pdf_text,
                "extracted_fields": pdf_data,
                "quote_data": self.quote_data
            }
            
            with open('application_extract.json', 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            
            print(f"Extracted data saved to application_extract.json")
            print(f"PDF text length: {len(pdf_text)} characters")
            print(f"Extracted drivers: {len(pdf_data['drivers'])}")
            print(f"Extracted vehicles: {len(pdf_data['vehicles'])}")
            
            # Compare with quote data
            comparison_results = {
                "summary": {
                    "total_drivers": len(self.quote_data.get("drivers", [])),
                    "matched_drivers": 0,
                    "total_vehicles": len(self.quote_data.get("vehicles", [])),
                    "matched_vehicles": 0,
                    "issues_found": 0
                },
                "drivers": [],
                "vehicles": [],
                "address_match": False,
                "date_match": False,
                "pdf_text_sample": pdf_text[:500] + "..." if len(pdf_text) > 500 else pdf_text
            }
            
            # Compare drivers
            for json_driver in self.quote_data.get("drivers", []):
                driver_comparison = self._compare_driver(json_driver, pdf_data["drivers"])
                comparison_results["drivers"].append(driver_comparison)
                if driver_comparison["status"] == "MATCH":
                    comparison_results["summary"]["matched_drivers"] += 1
                else:
                    comparison_results["summary"]["issues_found"] += 1
            
            # Compare vehicles
            for json_vehicle in self.quote_data.get("vehicles", []):
                vehicle_comparison = self._compare_vehicle(json_vehicle, pdf_data["vehicles"])
                comparison_results["vehicles"].append(vehicle_comparison)
                if vehicle_comparison["status"] == "MATCH":
                    comparison_results["summary"]["matched_vehicles"] += 1
                else:
                    comparison_results["summary"]["issues_found"] += 1
            
            # Compare address
            if self.quote_data.get("address") and pdf_data.get("address"):
                comparison_results["address_match"] = self._compare_address(
                    self.quote_data["address"], 
                    pdf_data["address"]
                )
            
            # Compare effective date
            if self.quote_data.get("quote_effective_date") and pdf_data.get("quote_effective_date"):
                comparison_results["date_match"] = (
                    self.quote_data["quote_effective_date"] == pdf_data["quote_effective_date"]
                )
            
            return comparison_results
            
        except Exception as e:
            return {"error": f"Comparison failed: {str(e)}"}
    
    def _compare_driver(self, json_driver, pdf_drivers):
        """Compare a JSON driver with PDF drivers"""
        comparison = {
            "json_driver": json_driver,
            "pdf_matches": [],
            "status": "NO_MATCH",
            "confidence": 0
        }
        
        for pdf_driver in pdf_drivers:
            match_score = 0
            matches = {}
            
            # Compare names
            if self._names_match(json_driver.get("full_name"), pdf_driver.get("full_name")):
                match_score += 40
                matches["name"] = "MATCH"
            else:
                matches["name"] = "MISMATCH"
            
            # Compare license numbers (handle hyphen format differences)
            json_license = json_driver.get("licence_number", "").replace("-", "")
            pdf_license = pdf_driver.get("licence_number", "").replace("-", "")
            if json_license == pdf_license:
                match_score += 40
                matches["license"] = "MATCH"
            else:
                matches["license"] = "MISMATCH"
            
            # Compare birth dates
            if json_driver.get("birth_date") == pdf_driver.get("birth_date"):
                match_score += 20
                matches["birth_date"] = "MATCH"
            else:
                matches["birth_date"] = "MISMATCH"
            
            comparison["pdf_matches"].append({
                "pdf_driver": pdf_driver,
                "match_score": match_score,
                "matches": matches
            })
            
            if match_score >= 60:  # High confidence match
                comparison["status"] = "MATCH"
                comparison["confidence"] = match_score
                break
        
        return comparison
    
    def _compare_vehicle(self, json_vehicle, pdf_vehicles):
        """Compare a JSON vehicle with PDF vehicles"""
        comparison = {
            "json_vehicle": json_vehicle,
            "pdf_matches": [],
            "status": "NO_MATCH",
            "confidence": 0
        }
        
        for pdf_vehicle in pdf_vehicles:
            match_score = 0
            matches = {}
            
            # Compare VIN
            if json_vehicle.get("vin") == pdf_vehicle.get("vin"):
                match_score += 60
                matches["vin"] = "MATCH"
            else:
                matches["vin"] = "MISMATCH"
            
            # Compare vehicle type
            if json_vehicle.get("vehicle_type") == pdf_vehicle.get("vehicle_type"):
                match_score += 20
                matches["vehicle_type"] = "MATCH"
            else:
                matches["vehicle_type"] = "MISMATCH"
            
            # Compare fuel type
            if json_vehicle.get("fuel_type") == pdf_vehicle.get("fuel_type"):
                match_score += 20
                matches["fuel_type"] = "MATCH"
            else:
                matches["fuel_type"] = "MISMATCH"
            
            comparison["pdf_matches"].append({
                "pdf_vehicle": pdf_vehicle,
                "match_score": match_score,
                "matches": matches
            })
            
            if match_score >= 60:  # High confidence match
                comparison["status"] = "MATCH"
                comparison["confidence"] = match_score
                break
        
        return comparison
    
    def _names_match(self, name1, name2):
        """Compare names with fuzzy matching"""
        if not name1 or not name2:
            return False
        
        # Normalize names
        name1 = re.sub(r'\s+', ' ', name1.strip().lower())
        name2 = re.sub(r'\s+', ' ', name2.strip().lower())
        
        return name1 == name2
    
    def _compare_address(self, address1, address2):
        """Compare addresses"""
        if not address1 or not address2:
            return False
        
        # Normalize addresses
        addr1 = re.sub(r'\s+', ' ', address1.strip().lower())
        addr2 = re.sub(r'\s+', ' ', address2.strip().lower())
        
        return addr1 == addr2

# Flask endpoint function
def compare_quote_with_pdf(pdf_file):
    """Flask endpoint function to compare PDF with quote data"""
    service = QuoteComparisonService()
    
    # Save uploaded file temporarily
    temp_path = f"uploads/temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    os.makedirs("uploads", exist_ok=True)
    
    try:
        pdf_file.save(temp_path)
        result = service.compare_data(temp_path)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return result
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return {"error": f"Processing failed: {str(e)}"} 