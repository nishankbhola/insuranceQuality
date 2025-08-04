from difflib import SequenceMatcher
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import re

class ValidationEngine:
    """
Comprehensive validation engine for comparing MVR, DASH, and Quote data with enhanced domain-specific rules
"""
    
    def __init__(self):
        self.report = {
            "summary": {
                "total_drivers": 0,
                "validated_drivers": 0,
                "issues_found": 0,
                "critical_errors": 0,
                "warnings": 0
            },
            "drivers": []
        }
    
    def validate_quote(self, data):
        """
        Main validation function that compares MVR, DASH, and Quote data
        """
        try:
            # Handle the new data structure with "extracted" wrapper
            if "extracted" in data:
                quotes = data["extracted"].get("quotes", [])
                mvrs = data["extracted"].get("mvrs", [])
                dashes = data["extracted"].get("dashes", [])
            else:
                # Legacy structure
                quotes = data.get("quotes", [])
                mvrs = data.get("mvrs", [])
                dashes = data.get("dashes", [])
            
            # Validate input data
            if not quotes:
                return {
                    "summary": {
                        "total_drivers": 0,
                        "validated_drivers": 0,
                        "issues_found": 0,
                        "critical_errors": 1,
                        "warnings": 0
                    },
                    "drivers": [],
                    "error": "No quote data found"
                }
            
            print(f"Validating {len(quotes)} quotes with {len(mvrs)} MVRs and {len(dashes)} DASH reports")
        except Exception as e:
            print(f"Error in validate_quote: {e}")
            return {
                "summary": {
                    "total_drivers": 0,
                    "validated_drivers": 0,
                    "issues_found": 1,
                    "critical_errors": 1,
                    "warnings": 0
                },
                "drivers": [],
                "error": f"Data validation error: {str(e)}"
            }
        
        # Initialize report
        self.report = {
            "summary": {
                "total_drivers": 0,
                "validated_drivers": 0,
                "issues_found": 0,
                "critical_errors": 0,
                "warnings": 0
            },
            "drivers": []
        }

        for quote in quotes:
            # Process each driver in the quote
            for driver in quote.get("drivers", []):
                self.report["summary"]["total_drivers"] += 1
                
                driver_report = self._validate_driver(driver, quote, mvrs, dashes)
                self.report["drivers"].append(driver_report)
                
                if driver_report["validation_status"] == "PASS":
                    self.report["summary"]["validated_drivers"] += 1
                elif driver_report["validation_status"] == "WARNING":
                    # Count warnings as partial validation
                    self.report["summary"]["validated_drivers"] += 0.5
                    self.report["summary"]["warnings"] += len(driver_report.get("warnings", []))
                else:
                    self.report["summary"]["issues_found"] += 1
                    self.report["summary"]["critical_errors"] += len(driver_report.get("critical_errors", []))

        return self.report

    def _validate_driver(self, driver, quote, mvrs, dashes):
        """
        Validate a single driver against MVR and DASH data with enhanced rules
        """
        try:
            # Validate input parameters
            if not driver:
                return {
                    "driver_name": "Unknown",
                    "driver_license": "Unknown",
                    "validation_status": "FAIL",
                    "critical_errors": ["Driver data is missing or invalid"],
                    "warnings": [],
                    "matches": [],
                    "mvr_validation": {"status": "ERROR", "critical_errors": ["Driver data missing"], "warnings": [], "matches": []},
                    "dash_validation": {"status": "ERROR", "critical_errors": ["Driver data missing"], "warnings": [], "matches": []},
                    "license_progression_validation": {"status": "ERROR", "critical_errors": ["Driver data missing"], "warnings": [], "matches": []},
                    "convictions_validation": {"status": "ERROR", "critical_errors": ["Driver data missing"], "warnings": [], "matches": []}
                }
            
            driver_report = {
                "driver_name": driver.get("full_name"),
                "driver_license": driver.get("licence_number"),
                "validation_status": "PASS",
                "critical_errors": [],
                "warnings": [],
                "matches": [],
                "mvr_validation": {
                    "status": "NOT_FOUND",
                    "critical_errors": [],
                    "warnings": [],
                    "matches": []
                },
                "dash_validation": {
                    "status": "NOT_FOUND", 
                    "critical_errors": [],
                    "warnings": [],
                    "matches": []
                },
                "license_progression_validation": {
                    "status": "NOT_FOUND",
                    "critical_errors": [],
                    "warnings": [],
                    "matches": []
                },
                "convictions_validation": {
                    "status": "NOT_FOUND",
                    "critical_errors": [],
                    "warnings": [],
                    "matches": []
                }
            }

            # Normalize license numbers for comparison
            quote_license_raw = driver.get("licence_number", "")
            quote_license = quote_license_raw.replace("-", "") if quote_license_raw else ""
            
            # Find matching MVR and DASH records
            matched_mvr = self._find_matching_mvr(quote_license, mvrs)
            matched_dash = self._find_matching_dash(quote_license, dashes)
            
            # Enhanced MVR validation with new rules
            if matched_mvr:
                mvr_validation = self._validate_mvr_data_enhanced(driver, matched_mvr, quote)
                driver_report["mvr_validation"] = mvr_validation
                driver_report["critical_errors"].extend(mvr_validation["critical_errors"])
                driver_report["warnings"].extend(mvr_validation["warnings"])
                driver_report["matches"].extend(mvr_validation["matches"])
                
            # Enhanced license progression validation
            if matched_mvr:
                license_validation = self._validate_license_progression_enhanced(driver, matched_mvr)
                driver_report["license_progression_validation"] = license_validation
                driver_report["critical_errors"].extend(license_validation["critical_errors"])
                driver_report["warnings"].extend(license_validation["warnings"])
                driver_report["matches"].extend(license_validation["matches"])
                
            # Enhanced convictions validation
            if matched_mvr:
                convictions_validation = self._validate_convictions_enhanced(driver, matched_mvr, quote)
                driver_report["convictions_validation"] = convictions_validation
                driver_report["critical_errors"].extend(convictions_validation["critical_errors"])
                driver_report["warnings"].extend(convictions_validation["warnings"])
                driver_report["matches"].extend(convictions_validation["matches"])
                
            # Validate DASH data  
            if matched_dash:
                dash_validation = self._validate_dash_data(driver, matched_dash, quote)
                driver_report["dash_validation"] = dash_validation
                driver_report["critical_errors"].extend(dash_validation.get("critical_errors", []))
                driver_report["warnings"].extend(dash_validation.get("warnings", []))
                driver_report["matches"].extend(dash_validation.get("matches", []))
            
            # Determine overall validation status
            driver_report["validation_status"] = self._determine_overall_status_enhanced(driver_report)
            
            return driver_report
            
        except Exception as e:
            print(f"Error validating driver {driver.get('full_name', 'Unknown')}: {e}")
            return {
                "driver_name": driver.get("full_name", "Unknown") if driver else "Unknown",
                "driver_license": driver.get("licence_number", "Unknown") if driver else "Unknown",
                "validation_status": "FAIL",
                "critical_errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "matches": [],
                "mvr_validation": {"status": "ERROR", "critical_errors": [f"Validation error: {str(e)}"], "warnings": [], "matches": []},
                "dash_validation": {"status": "ERROR", "critical_errors": [f"Validation error: {str(e)}"], "warnings": [], "matches": []},
                "license_progression_validation": {"status": "ERROR", "critical_errors": [f"Validation error: {str(e)}"], "warnings": [], "matches": []},
                "convictions_validation": {"status": "ERROR", "critical_errors": [f"Validation error: {str(e)}"], "warnings": [], "matches": []}
            }

    def _find_matching_mvr(self, quote_license, mvrs):
        """Find matching MVR record by license number"""
        for mvr in mvrs:
            mvr_license_raw = mvr.get("licence_number")
            if mvr_license_raw is None:
                continue
            mvr_license = mvr_license_raw.replace("-", "")
            if mvr_license == quote_license:
                return mvr
        return None

    def _find_matching_dash(self, quote_license, dashes):
        """Find matching DASH record by license number"""
        for dash in dashes:
            dash_license_raw = dash.get("dln")
            if dash_license_raw is None:
                continue
            dash_license = dash_license_raw.replace("-", "")
            if dash_license == quote_license:
                return dash
        return None

    def _validate_mvr_data_enhanced(self, driver, mvr, quote):
        """
        Enhanced MVR validation with critical field comparisons
        """
        validation = {
            "status": "PASS",
            "critical_errors": [],
            "warnings": [],
            "matches": []
        }
        
        # Critical field comparisons: license_number, name, address
        quote_license_raw = driver.get("licence_number", "")
        quote_license = quote_license_raw.replace("-", "") if quote_license_raw else ""
        mvr_license_raw = mvr.get("licence_number", "")
        mvr_license = mvr_license_raw.replace("-", "") if mvr_license_raw else ""
        
        if quote_license and mvr_license:
            if quote_license == mvr_license:
                validation["matches"].append("License number matches between Quote and MVR")
            else:
                validation["critical_errors"].append("License number mismatch between Quote and MVR")
                validation["status"] = "FAIL"
        
        # Name validation (fuzzy match)
        quote_name = driver.get("full_name", "")
        mvr_name = mvr.get("name", "")
        
        if self._similar(quote_name, mvr_name) or self._names_contain_same_parts(quote_name, mvr_name):
            validation["matches"].append("Name matches between Quote and MVR")
        else:
            validation["critical_errors"].append("Name mismatch between Quote and MVR")
            validation["status"] = "FAIL"
        
        # Address validation - compare MVR address with quote garaging location
        mvr_address = mvr.get("address", "")
        
        # Get garaging location from quote vehicles
        quote_garaging_location = ""
        for vehicle in quote.get("vehicles", []):
            garaging_location = vehicle.get("garaging_location", "")
            if garaging_location:
                quote_garaging_location = garaging_location
                break
        
        if mvr_address and quote_garaging_location:
            # Normalize addresses for comparison
            normalized_mvr = self._normalize_address(mvr_address)
            normalized_quote = self._normalize_address(quote_garaging_location)
            
            # Debug: Print the normalized addresses being compared
            print(f"DEBUG: Comparing addresses:")
            print(f"  MVR normalized: '{normalized_mvr}'")
            print(f"  Quote normalized: '{normalized_quote}'")
            
            if self._addresses_match(normalized_mvr, normalized_quote):
                validation["matches"].append("Address matches between MVR and Quote garaging location")
            else:
                validation["critical_errors"].append(f"Address mismatch between MVR ({mvr_address}) and Quote garaging location ({quote_garaging_location})")
                validation["status"] = "FAIL"
        elif mvr_address and not quote_garaging_location:
            validation["critical_errors"].append("MVR has address but Quote has no garaging location")
            validation["status"] = "FAIL"
        elif not mvr_address and quote_garaging_location:
            validation["warnings"].append("Quote has garaging location but MVR has no address")
        else:
            validation["warnings"].append("No address information available for comparison")
        
        # Date of birth validation
        quote_dob = driver.get("birth_date", "")
        mvr_dob = mvr.get("birth_date", "")
        
        if quote_dob and mvr_dob:
            if self._dates_match(quote_dob, mvr_dob, "quote", "mvr"):
                validation["matches"].append("Date of birth matches between Quote and MVR")
            else:
                validation["critical_errors"].append("Date of birth mismatch between Quote and MVR")
                validation["status"] = "FAIL"
        
        # Gender validation
        quote_gender = driver.get("gender", "").lower()
        mvr_gender = mvr.get("gender", "").lower()
        
        if quote_gender and mvr_gender:
            gender_mapping = {
                'm': 'male',
                'male': 'male',
                'f': 'female', 
                'female': 'female'
            }
            
            quote_gender_normalized = gender_mapping.get(quote_gender, quote_gender)
            mvr_gender_normalized = gender_mapping.get(mvr_gender, mvr_gender)
            
            if quote_gender_normalized == mvr_gender_normalized:
                validation["matches"].append("Gender matches between Quote and MVR")
            else:
                validation["warnings"].append("Gender mismatch between Quote and MVR")
        
        return validation

    def _validate_license_progression_enhanced(self, driver, mvr):
        """
        Enhanced license progression validation with G1/G2/G date logic
        Implements the business rules:
        - If DD/MM of MVR expiry date and birth date match: g1_date = issue_date, g2_date = g1_date + 1 year, g_date = g2_date + 1 year
        - If DD/MM don't match: g1_date = expiry_date - 5 years, g2_date = g1_date + 1 year, g_date = g2_date + 1 year
        """
        validation = {
            "status": "PASS",
            "critical_errors": [],
            "warnings": [],
            "matches": []
        }
        
        # Extract dates from Quote driver
        quote_g1_date = driver.get("date_g1", "")
        quote_g2_date = driver.get("date_g2", "")
        quote_g_date = driver.get("date_g", "")
        license_class = driver.get("licence_class", "")
        
        # Extract dates from MVR
        mvr_expiry_date = mvr.get("expiry_date", "")
        mvr_birth_date = mvr.get("birth_date", "")
        mvr_issue_date = mvr.get("issue_date", "")
        
        # Debug: Print the comparison details
        print(f"DEBUG: License progression validation:")
        print(f"  MVR expiry: {mvr_expiry_date}")
        print(f"  MVR birth: {mvr_birth_date}")
        print(f"  MVR issue: {mvr_issue_date}")
        print(f"  Quote G1: {quote_g1_date}")
        print(f"  Quote G2: {quote_g2_date}")
        print(f"  Quote G: {quote_g_date}")
        
        # Calculate expected G1/G2/G dates from MVR data using business rules
        calculated_dates = self._calculate_license_dates_from_mvr(mvr_expiry_date, mvr_birth_date, mvr_issue_date)
        
        if calculated_dates:
            calculated_g1, calculated_g2, calculated_g = calculated_dates
            print(f"  Calculated G1: {calculated_g1}")
            print(f"  Calculated G2: {calculated_g2}")
            print(f"  Calculated G: {calculated_g}")
            
            # Compare calculated dates with quote dates
            if quote_g1_date:
                if self._dates_match(calculated_g1, quote_g1_date, "quote", "quote"):
                    validation["matches"].append(f"G1 date matches: Quote ({quote_g1_date}) = Calculated ({calculated_g1})")
                else:
                    validation["critical_errors"].append(f"G1 date mismatch: Quote ({quote_g1_date}) ≠ Calculated ({calculated_g1})")
                    validation["status"] = "FAIL"
            else:
                validation["critical_errors"].append(f"Quote missing G1 date, expected: {calculated_g1}")
                validation["status"] = "FAIL"
            
            if quote_g2_date:
                if self._dates_match(calculated_g2, quote_g2_date, "quote", "quote"):
                    validation["matches"].append(f"G2 date matches: Quote ({quote_g2_date}) = Calculated ({calculated_g2})")
                else:
                    validation["critical_errors"].append(f"G2 date mismatch: Quote ({quote_g2_date}) ≠ Calculated ({calculated_g2})")
                    validation["status"] = "FAIL"
            else:
                validation["critical_errors"].append(f"Quote missing G2 date, expected: {calculated_g2}")
                validation["status"] = "FAIL"
            
            if quote_g_date:
                if self._dates_match(calculated_g, quote_g_date, "quote", "quote"):
                    validation["matches"].append(f"G date matches: Quote ({quote_g_date}) = Calculated ({calculated_g})")
                else:
                    validation["critical_errors"].append(f"G date mismatch: Quote ({quote_g_date}) ≠ Calculated ({calculated_g})")
                    validation["status"] = "FAIL"
            else:
                validation["critical_errors"].append(f"Quote missing G date, expected: {calculated_g}")
                validation["status"] = "FAIL"
        else:
            validation["critical_errors"].append("Could not calculate expected license dates from MVR data")
            validation["status"] = "FAIL"
        
        # Validate that the progression makes sense (additional check)
        if quote_g1_date and quote_g2_date:
            if not self._is_date_before(quote_g1_date, quote_g2_date, "quote", "quote"):
                validation["critical_errors"].append(f"G1 date ({quote_g1_date}) should be before G2 date ({quote_g2_date})")
                validation["status"] = "FAIL"
        
        if quote_g2_date and quote_g_date:
            if not self._is_date_before(quote_g2_date, quote_g_date, "quote", "quote"):
                validation["critical_errors"].append(f"G2 date ({quote_g2_date}) should be before G date ({quote_g_date})")
                validation["status"] = "FAIL"
        
        return validation
    
    def _is_date_before(self, date1_str, date2_str, source1_type=None, source2_type=None):
        """
        Check if date1 is before date2
        source1_type, source2_type: 'mvr', 'dash', 'quote', or None for auto-detection
        """
        try:
            # Normalize both dates to YYYY-MM-DD format
            norm_date1 = self._normalize_date(date1_str, source1_type)
            norm_date2 = self._normalize_date(date2_str, source2_type)
            
            if norm_date1 and norm_date2:
                return norm_date1 < norm_date2
        except Exception as e:
            print(f"DEBUG: Date comparison failed: {date1_str} vs {date2_str}: {e}")
        return False

    def _calculate_license_dates_from_mvr(self, expiry_date, birth_date, issue_date):
        """
        Calculate G1/G2/G dates from MVR data using business rules:
        - If DD/MM of expiry_date and birth_date match: g1_date = issue_date, g2_date = g1_date + 1 year, g_date = g2_date + 1 year
        - If DD/MM don't match: g1_date = expiry_date - 5 years, g2_date = g1_date + 1 year, g_date = g2_date + 1 year
        """
        if not expiry_date or not birth_date or not issue_date:
            return None
        
        try:
            # Parse dates with correct source types (MVR format: DD/MM/YYYY)
            expiry = self._parse_date(expiry_date, "mvr")
            birth = self._parse_date(birth_date, "mvr")
            issue = self._parse_date(issue_date, "mvr")
            
            if not all([expiry, birth, issue]):
                return None
            
            # Check if DD/MM of expiry_date and birth_date match
            expiry_dd_mm = (expiry.day, expiry.month)
            birth_dd_mm = (birth.day, birth.month)
            
            print(f"DEBUG: Comparing DD/MM - Expiry: {expiry_dd_mm}, Birth: {birth_dd_mm}")
            
            if expiry_dd_mm == birth_dd_mm:
                # If DD/MM match: g1_date = issue_date, g2_date = g1_date + 1 year, g_date = g2_date + 1 year
                print("DEBUG: DD/MM match - using issue_date as G1")
                g1_date = issue
                g2_date = issue + relativedelta(years=1)
                g_date = g2_date + relativedelta(years=1)
            else:
                # If DD/MM don't match: g1_date = expiry_date - 5 years, g2_date = g1_date + 1 year, g_date = g2_date + 1 year
                print("DEBUG: DD/MM don't match - using expiry_date - 5 years as G1")
                g1_date = expiry - relativedelta(years=5)
                g2_date = g1_date + relativedelta(years=1)
                g_date = g2_date + relativedelta(years=1)
            
            # Return dates in Quote format (MM/DD/YYYY)
            return (
                g1_date.strftime("%m/%d/%Y"),
                g2_date.strftime("%m/%d/%Y"),
                g_date.strftime("%m/%d/%Y")
            )
            
        except Exception as e:
            print(f"DEBUG: Error calculating license dates: {e}")
            return None

    def _calculate_license_dates(self, expiry_date, birth_date, issue_date):
        """
        Calculate G1/G2/G dates based on the specified logic
        """
        if not expiry_date or not birth_date or not issue_date:
            return None
        
        try:
            # Parse dates with correct source types
            expiry = self._parse_date(expiry_date, "mvr")
            birth = self._parse_date(birth_date, "mvr")
            issue = self._parse_date(issue_date, "mvr")
            
            if not all([expiry, birth, issue]):
                return None
            
            # Check if MM/DD of expiry_date and birthdate match
            # The rule means: if the month and day are the same (ignoring the year)
            expiry_mm_dd = (expiry.month, expiry.day)
            birth_mm_dd = (birth.month, birth.day)
            
            if expiry_mm_dd == birth_mm_dd:
                # If MM/DD match: g1_date = issue_date, g2_date = issue_date + 1 year, g_date = issue_date + 2 years
                g1_date = issue
                g2_date = issue + relativedelta(years=1)
                g_date = issue + relativedelta(years=2)
            else:
                # If MM/DD don't match: g1_date = expiry_date - 5 years, g2_date = g1_date + 1 year, g_date = g1_date + 2 years
                g1_date = expiry - relativedelta(years=5)
                g2_date = g1_date + relativedelta(years=1)
                g_date = g1_date + relativedelta(years=2)
            
            return (
                g1_date.strftime("%m/%d/%Y"),
                g2_date.strftime("%m/%d/%Y"),
                g_date.strftime("%m/%d/%Y")
            )
            
        except Exception as e:
            return None

    def _validate_convictions_enhanced(self, driver, mvr, quote):
        """
        Enhanced convictions validation with detailed matching
        """
        validation = {
            "status": "PASS",
            "critical_errors": [],
            "warnings": [],
            "matches": []
        }
        
        # Get convictions from MVR
        mvr_convictions = mvr.get("convictions", [])
        
        # Get convictions from quote
        quote_convictions = quote.get("convictions", [])
        
        if not mvr_convictions:
            validation["matches"].append("No convictions found in MVR")
            return validation
        
        # Check each MVR conviction against quote
        for mvr_conv in mvr_convictions:
            mvr_date = mvr_conv.get("offence_date", "")
            mvr_description = mvr_conv.get("description", "")
            
            # Look for matching conviction in quote
            found_match = False
            for quote_conv in quote_convictions:
                quote_date = quote_conv.get("date", "")
                quote_description = quote_conv.get("description", "")
                
                # Check if dates and descriptions match
                if (self._dates_match(mvr_date, quote_date, "mvr", "quote") and 
                    self._conviction_descriptions_match(mvr_description, quote_description)):
                    validation["matches"].append(f"Conviction matched: {mvr_date} - {mvr_description}")
                    found_match = True
                    break
            
            if not found_match:
                validation["critical_errors"].append(f"Conviction not found in quote: {mvr_date} - {mvr_description}")
                validation["status"] = "FAIL"
        
        # Check for extra convictions in quote that aren't in MVR
        for quote_conv in quote_convictions:
            quote_date = quote_conv.get("date", "")
            quote_description = quote_conv.get("description", "")
            
            found_in_mvr = False
            for mvr_conv in mvr_convictions:
                mvr_date = mvr_conv.get("offence_date", "")
                mvr_description = mvr_conv.get("description", "")
                
                if (self._dates_match(quote_date, mvr_date, "quote", "mvr") and 
                    self._conviction_descriptions_match(quote_description, mvr_description)):
                    found_in_mvr = True
                    break
            
            if not found_in_mvr:
                validation["warnings"].append(f"Extra conviction in quote not in MVR: {quote_date} - {quote_description}")
        
        return validation

    def _validate_dash_data(self, driver, dash, quote):
        """
        Validate DASH data against quote driver information
        """
        validation = {
            "status": "PASS",
            "critical_errors": [],
            "warnings": [],
            "matches": []
        }
        
        # Date of birth validation
        quote_dob = driver.get("birth_date", "")
        dash_dob = dash.get("date_of_birth", "")
        
        if quote_dob and dash_dob:
            if self._dates_match(quote_dob, dash_dob, "quote", "dash"):
                validation["matches"].append("Date of birth matches between Quote and DASH")
            else:
                validation["critical_errors"].append("Date of birth mismatch between Quote and DASH")
                validation["status"] = "FAIL"
        
        # Gender validation
        quote_gender = driver.get("gender", "").lower()
        dash_gender = dash.get("gender", "").lower()
        
        if quote_gender and dash_gender:
            gender_mapping = {
                'm': 'male',
                'male': 'male',
                'f': 'female', 
                'female': 'female'
            }
            
            quote_gender_normalized = gender_mapping.get(quote_gender, quote_gender)
            dash_gender_normalized = gender_mapping.get(dash_gender, dash_gender)
            
            if quote_gender_normalized == dash_gender_normalized:
                validation["matches"].append("Gender matches between Quote and DASH")
            else:
                validation["warnings"].append("Gender mismatch between Quote and DASH")
        
        # License number validation
        quote_license_raw = driver.get("licence_number", "")
        quote_license = quote_license_raw.replace("-", "") if quote_license_raw else ""
        dash_license_raw = dash.get("dln", "")
        dash_license = dash_license_raw.replace("-", "") if dash_license_raw else ""
        
        if quote_license and dash_license:
            if quote_license == dash_license:
                validation["matches"].append("License number matches between Quote and DASH")
            else:
                validation["critical_errors"].append("License number mismatch between Quote and DASH")
                validation["status"] = "FAIL"
        
        # Policy validation
        policies_validation = self._validate_policies(dash, quote)
        validation["critical_errors"].extend(policies_validation["critical_errors"])
        validation["warnings"].extend(policies_validation["warnings"])
        validation["matches"].extend(policies_validation["matches"])
        
        # Claims validation
        claims_validation = self._validate_claims(dash, quote)
        validation["critical_errors"].extend(claims_validation["critical_errors"])
        validation["warnings"].extend(claims_validation["warnings"])
        validation["matches"].extend(claims_validation["matches"])
        
        if validation["critical_errors"]:
            validation["status"] = "FAIL"
        
        return validation

    def _validate_policies(self, dash, quote):
        """
        Validate policy information between DASH and quote according to business rules
        """
        validation = {
            "critical_errors": [],
            "warnings": [],
            "matches": []
        }
        
        policies = dash.get("policies", [])
        active_policies = [p for p in policies if "Active" in p.get("status", "")]
        
        if not active_policies:
            validation["critical_errors"].append("No active policy found in DASH")
            return validation
        
        validation["matches"].append(f"Found {len(active_policies)} active policy(ies) in DASH")
        
        # Business rule: Compare date_insured from Quote with first policy start_date from DASH
        quote_date_insured = ""
        if quote.get("drivers"):
            quote_date_insured = quote["drivers"][0].get("date_insured", "")
        
        if quote_date_insured and active_policies:
            # Sort by start_date to get oldest (first) policy
            sorted_policies = sorted(active_policies, key=lambda x: x.get("start_date", ""))
            first_policy_start = sorted_policies[0].get("start_date", "")
            
            if self._dates_match(quote_date_insured, first_policy_start, "quote", "dash"):
                validation["matches"].append(f"Date insured ({quote_date_insured}) matches first policy start date ({first_policy_start})")
            else:
                validation["critical_errors"].append(f"Date insured ({quote_date_insured}) doesn't match first policy start date ({first_policy_start})")
        
        # Additional check: Current carrier matching (existing logic)
        quote_current_carrier = ""
        if quote.get("drivers"):
            quote_current_carrier = quote["drivers"][0].get("current_carrier", "")
        
        if quote_current_carrier:
            for policy in active_policies:
                if self._similar(quote_current_carrier, policy.get("company", "")):
                    validation["matches"].append("Current carrier matches DASH policy")
                    break
            else:
                validation["warnings"].append("Current carrier in quote doesn't match DASH policies")
        
        return validation

    def _validate_claims(self, dash, quote):
        """
        Validate claims information between DASH and quote according to business rules
        """
        validation = {
            "critical_errors": [],
            "warnings": [],
            "matches": []
        }
        
        dash_claims = dash.get("claims", [])
        quote_claims = quote.get("claims", [])
        
        # Get policyholder name from quote
        policyholder_name = ""
        if quote.get("drivers"):
            policyholder_name = quote["drivers"][0].get("full_name", "")
        
        if not dash_claims:
            validation["matches"].append("No claims found in DASH")
            return validation
        
        validation["matches"].append(f"Found {len(dash_claims)} claim(s) in DASH")
        
        for dash_claim in dash_claims:
            at_fault_percentage = dash_claim.get("at_fault_percentage", 0)
            claim_number = dash_claim.get("claim_number", "Unknown")
            dash_claim_date = dash_claim.get("date", "")
            first_party_driver = dash_claim.get("first_party_driver", "")
            
            if at_fault_percentage > 0:
                # Check if first_party_driver equals policyholder name
                if first_party_driver == policyholder_name:
                    # Check if claim date matches any quote claim
                    quote_claim_dates = [claim.get("date", "") for claim in quote_claims]
                    
                    if dash_claim_date in quote_claim_dates:
                        validation["matches"].append(f"Claim {claim_number} validated (at-fault: {at_fault_percentage}%)")
                    else:
                        validation["critical_errors"].append(f"Claim {claim_number} date mismatch - DASH: {dash_claim_date}, Quote: {quote_claim_dates}")
                else:
                    validation["warnings"].append(f"Claim {claim_number} - different driver ({first_party_driver} vs {policyholder_name})")
            else:
                # Skip claims with 0% at-fault as per business rules
                validation["matches"].append(f"Claim {claim_number} skipped (0% at-fault)")
        
        return validation

    def _names_contain_same_parts(self, name1, name2):
        """
        Check if two names contain the same key parts (first and last name)
        """
        if not name1 or not name2:
            return False
        
        # Split names into parts first, then clean each part
        name1_clean = name1.replace(",", " ") if name1 else ""
        name2_clean = name2.replace(",", " ") if name2 else ""
        parts1 = [part.strip().upper() for part in name1_clean.split() if len(part.strip()) > 2]
        parts2 = [part.strip().upper() for part in name2_clean.split() if len(part.strip()) > 2]
        
        # Check if they share key name parts
        for part1 in parts1:
            for part2 in parts2:
                if part1 == part2 or self._similar(part1, part2):
                    return True
        
        # Also check if the names are similar overall
        return self._similar(name1, name2)

    def _dates_match(self, date1, date2, source1_type=None, source2_type=None):
        """
        Compare dates in different formats
        source1_type, source2_type: 'mvr', 'dash', 'quote', or None for auto-detection
        """
        try:
            # Normalize both dates to YYYY-MM-DD format
            norm_date1 = self._normalize_date(date1, source1_type)
            norm_date2 = self._normalize_date(date2, source2_type)
            
            return norm_date1 == norm_date2
        except:
            return False

    def _parse_date(self, date_str, source_type=None):
        """
        Parse date string to datetime object
        source_type: 'mvr', 'dash', 'quote', or None for auto-detection
        
        Date formats by source:
        - MVR: dd/mm/yyyy
        - Dash: yyyy/mm/dd  
        - Quote: mm/dd/yyyy
        """
        if not date_str:
            return None
            
        try:
            # Handle different date formats based on source type
            if "/" in date_str:
                parts = date_str.split("/")
                if len(parts) == 3:
                    if source_type == "mvr":
                        # MVR dates are in DD/MM/YYYY format
                        return datetime.strptime(date_str, "%d/%m/%Y")
                    elif source_type == "dash":
                        # DASH dates are in YYYY/MM/DD format
                        return datetime.strptime(date_str, "%Y/%m/%d")
                    elif source_type == "quote":
                        # Quote dates are in MM/DD/YYYY format
                        return datetime.strptime(date_str, "%m/%d/%Y")
                    else:
                        # Auto-detection: try different formats in order of likelihood
                        # First try to determine format based on the values
                        day, month, year = parts
                        
                        # If first part is 4 digits, it's likely YYYY/MM/DD (dash format)
                        if len(day) == 4 and day.isdigit():
                            try:
                                return datetime.strptime(date_str, "%Y/%m/%d")
                            except ValueError:
                                pass
                        
                        # If second part is > 12, it's likely DD/MM/YYYY (mvr format)
                        if month.isdigit() and int(month) > 12:
                            try:
                                return datetime.strptime(date_str, "%d/%m/%Y")
                            except ValueError:
                                pass
                        
                        # If first part is <= 12, it's likely MM/DD/YYYY (quote format)
                        if day.isdigit() and int(day) <= 12:
                            try:
                                return datetime.strptime(date_str, "%m/%d/%Y")
                            except ValueError:
                                pass
                        
                        # Fallback: try different formats in order of likelihood
                        formats = [
                            "%m/%d/%Y",    # MM/DD/YYYY (quote format)
                            "%d/%m/%Y",    # DD/MM/YYYY (MVR format)
                            "%Y/%m/%d",    # YYYY/MM/DD (DASH format)
                            "%Y-%m-%d",    # YYYY-MM-DD (ISO format)
                            "%m/%d/%y",    # MM/DD/YY (2-digit year)
                            "%d/%m/%y",    # DD/MM/YY (2-digit year)
                            "%y/%m/%d"     # YY/MM/DD (2-digit year)
                        ]
                        
                        for fmt in formats:
                            try:
                                return datetime.strptime(date_str, fmt)
                            except ValueError:
                                continue
            
            elif "-" in date_str:
                # Already in YYYY-MM-DD format
                return datetime.strptime(date_str, "%Y-%m-%d")
            
            return None
        except Exception as e:
            print(f"DEBUG: Date parsing failed for '{date_str}' from {source_type}: {e}")
            return None

    def _normalize_date(self, date_str, source_type=None):
        """
        Normalize date strings to YYYY-MM-DD format for comparison
        source_type: 'mvr', 'dash', 'quote', or None for auto-detection
        
        Date formats by source:
        - MVR: dd/mm/yyyy
        - Dash: yyyy/mm/dd  
        - Quote: mm/dd/yyyy
        """
        if not date_str:
            return None
            
        # Handle different date formats based on source type
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 3:
                try:
                    if source_type == "mvr":
                        # MVR dates are in DD/MM/YYYY format
                        dt = datetime.strptime(date_str, "%d/%m/%Y")
                        return dt.strftime("%Y-%m-%d")
                    elif source_type == "dash":
                        # DASH dates are in YYYY/MM/DD format
                        dt = datetime.strptime(date_str, "%Y/%m/%d")
                        return dt.strftime("%Y-%m-%d")
                    elif source_type == "quote":
                        # Quote dates are in MM/DD/YYYY format
                        dt = datetime.strptime(date_str, "%m/%d/%Y")
                        return dt.strftime("%Y-%m-%d")
                    else:
                        # Auto-detection: try different formats in order of likelihood
                        # First try to determine format based on the values
                        day, month, year = parts
                        
                        # If first part is 4 digits, it's likely YYYY/MM/DD (dash format)
                        if len(day) == 4 and day.isdigit():
                            try:
                                dt = datetime.strptime(date_str, "%Y/%m/%d")
                                return dt.strftime("%Y-%m-%d")
                            except ValueError:
                                pass
                        
                        # If second part is > 12, it's likely DD/MM/YYYY (mvr format)
                        if month.isdigit() and int(month) > 12:
                            try:
                                dt = datetime.strptime(date_str, "%d/%m/%Y")
                                return dt.strftime("%Y-%m-%d")
                            except ValueError:
                                pass
                        
                        # If first part is <= 12, it's likely MM/DD/YYYY (quote format)
                        if day.isdigit() and int(day) <= 12:
                            try:
                                dt = datetime.strptime(date_str, "%m/%d/%Y")
                                return dt.strftime("%Y-%m-%d")
                            except ValueError:
                                pass
                        
                        # Fallback: try different formats in order of likelihood
                        formats = [
                            ("%m/%d/%Y", "quote"),    # MM/DD/YYYY (most common)
                            ("%d/%m/%Y", "mvr"),      # DD/MM/YYYY (MVR format)
                            ("%Y/%m/%d", "dash"),     # YYYY/MM/DD (DASH format)
                            ("%m/%d/%y", "quote"),    # MM/DD/YY (2-digit year)
                            ("%d/%m/%y", "mvr"),      # DD/MM/YY (2-digit year)
                            ("%y/%m/%d", "dash"),     # YY/MM/DD (2-digit year)
                        ]
                        
                        for fmt, fmt_type in formats:
                            try:
                                dt = datetime.strptime(date_str, fmt)
                                return dt.strftime("%Y-%m-%d")
                            except ValueError:
                                continue
                    
                except Exception as e:
                    print(f"DEBUG: Date normalization failed for '{date_str}' from {source_type}: {e}")
                    pass
        elif "-" in date_str:
            return date_str  # Already in YYYY-MM-DD format
            
        return None

    def _similar(self, a, b):
        """Check if two strings are similar using fuzzy matching"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio() > 0.6

    def _conviction_descriptions_match(self, desc1, desc2):
        """
        Enhanced conviction description matching with normalization and keyword matching
        """
        if not desc1 or not desc2:
            return False
        
        # Normalize descriptions
        norm1 = self._normalize_conviction_description(desc1)
        norm2 = self._normalize_conviction_description(desc2)
        
        # First try exact match on normalized descriptions
        if norm1 == norm2:
            return True
        
        # Try fuzzy matching on normalized descriptions
        if self._similar(norm1, norm2):
            return True
        
        # Try keyword matching
        if self._conviction_keywords_match(desc1, desc2):
            return True
        
        return False

    def _normalize_conviction_description(self, description):
        """
        Normalize conviction descriptions for better matching
        """
        if not description:
            return ""
        
        # Convert to lowercase
        desc = description.lower()
        
        # Remove common punctuation and extra spaces
        desc = re.sub(r'[^\w\s]', ' ', desc)
        desc = re.sub(r'\s+', ' ', desc).strip()
        
        # Common abbreviations and variations
        replacements = {
            'drv': 'drive',
            'driving': 'drive',
            'com': 'communication',
            'dev': 'device',
            'hand-held': 'handheld',
            'hand held': 'handheld',
            'prohibited': 'not allowed',
            'shall not': 'not allowed',
            'using': 'use',
            'holding': 'hold'
        }
        
        for old, new in replacements.items():
            desc = desc.replace(old, new)
        
        return desc

    def _conviction_keywords_match(self, desc1, desc2):
        """
        Check if conviction descriptions match based on key keywords
        """
        if not desc1 or not desc2:
            return False
        
        # Define keyword groups for common conviction types
        keyword_groups = {
            'handheld_device': [
                'hand-held', 'handheld', 'hand held', 'device', 'com', 'communication',
                'prohibited', 'shall not', 'using', 'holding', 'drive', 'driving'
            ],
            'speeding': [
                'speed', 'speeding', 'exceed', 'limit', 'km/h', 'mph'
            ],
            'red_light': [
                'red light', 'traffic light', 'signal', 'stop'
            ],
            'seatbelt': [
                'seatbelt', 'seat belt', 'restraint', 'safety'
            ],
            'dui': [
                'dui', 'dwi', 'impaired', 'alcohol', 'drug', 'intoxicated'
            ]
        }
        
        # Check if both descriptions contain keywords from the same group
        desc1_lower = desc1.lower()
        desc2_lower = desc2.lower()
        
        for group_name, keywords in keyword_groups.items():
            desc1_has_keywords = any(keyword in desc1_lower for keyword in keywords)
            desc2_has_keywords = any(keyword in desc2_lower for keyword in keywords)
            
            if desc1_has_keywords and desc2_has_keywords:
                return True
        
        return False

    def _normalize_address(self, address):
        """
        Normalize address for comparison by removing extra spaces, newlines, and standardizing format
        """
        if not address:
            return ""
        
        # Remove newlines and extra whitespace
        normalized = re.sub(r'\n+', ' ', address)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Convert to uppercase for comparison
        normalized = normalized.upper()
        
        # Remove common punctuation that might cause issues
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Remove extra spaces again
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized

    def _addresses_match(self, address1, address2):
        """
        Compare two normalized addresses to see if they match
        """
        if not address1 or not address2:
            return False
        
        # Exact match
        if address1 == address2:
            return True
        
        # Split addresses into parts
        parts1 = address1.split()
        parts2 = address2.split()
        
        # Look for postal code pattern (e.g., M6N1T3)
        postal_code1 = None
        postal_code2 = None
        
        for part in parts1:
            if re.match(r'^[A-Z]\d[A-Z]\d[A-Z]\d$', part):
                postal_code1 = part
                break
        
        for part in parts2:
            if re.match(r'^[A-Z]\d[A-Z]\d[A-Z]\d$', part):
                postal_code2 = part
                break
        
        # Check for city name match (e.g., TORONTO)
        city1 = None
        city2 = None
        
        for part in parts1:
            if part in ['TORONTO', 'MISSISSAUGA', 'BRAMPTON', 'VAUGHAN', 'MARKHAM', 'RICHMOND HILL', 'OAKVILLE', 'BURLINGTON', 'HAMILTON', 'LONDON', 'WINDSOR', 'OTTAWA', 'MONTREAL', 'VANCOUVER', 'CALGARY', 'EDMONTON']:
                city1 = part
                break
        
        for part in parts2:
            if part in ['TORONTO', 'MISSISSAUGA', 'BRAMPTON', 'VAUGHAN', 'MARKHAM', 'RICHMOND HILL', 'OAKVILLE', 'BURLINGTON', 'HAMILTON', 'LONDON', 'WINDSOR', 'OTTAWA', 'MONTREAL', 'VANCOUVER', 'CALGARY', 'EDMONTON']:
                city2 = part
                break
        
        # Primary match: If both have the same city and postal code, they match
        if city1 and city2 and city1 == city2 and postal_code1 and postal_code2 and postal_code1 == postal_code2:
            return True
        
        # Secondary match: If one address contains the other (e.g., full address vs city+postal)
        if len(parts1) > len(parts2):
            # address1 is longer (full address), address2 is shorter (city+postal)
            if city2 and postal_code2:
                # Check if address1 contains both city and postal code from address2
                if city2 in parts1 and postal_code2 in parts1:
                    return True
        elif len(parts2) > len(parts1):
            # address2 is longer (full address), address1 is shorter (city+postal)
            if city1 and postal_code1:
                # Check if address2 contains both city and postal code from address1
                if city1 in parts2 and postal_code1 in parts2:
                    return True
        
        # Tertiary match: If both have postal codes and they match
        if postal_code1 and postal_code2 and postal_code1 == postal_code2:
            return True
        
        # Quaternary match: If both have the same city, they likely match
        if city1 and city2 and city1 == city2:
            return True
        
        # Fuzzy match as fallback with lower threshold for addresses
        similarity = SequenceMatcher(None, address1.lower(), address2.lower()).ratio()
        return similarity > 0.4  # Lower threshold for address matching

    def _determine_overall_status_enhanced(self, driver_report):
        """
        Determine overall validation status for a driver with enhanced logic
        """
        # Count critical errors and warnings from all validation sections
        total_critical_errors = len(driver_report.get("critical_errors", []))
        total_warnings = len(driver_report.get("warnings", []))
        total_matches = len(driver_report.get("matches", []))
        
        # Also check individual validation sections
        mvr_validation = driver_report.get("mvr_validation", {})
        dash_validation = driver_report.get("dash_validation", {})
        license_validation = driver_report.get("license_progression_validation", {})
        convictions_validation = driver_report.get("convictions_validation", {})
        
        # Add critical errors from individual sections
        total_critical_errors += len(mvr_validation.get("critical_errors", []))
        total_critical_errors += len(dash_validation.get("critical_errors", []))
        total_critical_errors += len(license_validation.get("critical_errors", []))
        total_critical_errors += len(convictions_validation.get("critical_errors", []))
        
        # Add warnings from individual sections
        total_warnings += len(mvr_validation.get("warnings", []))
        total_warnings += len(dash_validation.get("warnings", []))
        total_warnings += len(license_validation.get("warnings", []))
        total_warnings += len(convictions_validation.get("warnings", []))
        
        # Add matches from individual sections
        total_matches += len(mvr_validation.get("matches", []))
        total_matches += len(dash_validation.get("matches", []))
        total_matches += len(license_validation.get("matches", []))
        total_matches += len(convictions_validation.get("matches", []))
        
        # If there are any critical errors, status is FAIL
        if total_critical_errors > 0:
            return "FAIL"
        
        # If there are warnings but no critical errors, status is WARNING
        if total_warnings > 0:
            return "WARNING"
        
        # If there are matches and no issues, status is PASS
        if total_matches > 0:
            return "PASS"
        
        # Default to FAIL if no validation was performed
        return "FAIL"

# Legacy function for backward compatibility
def validate_quote(data):
    """
    Legacy validation function - now uses the new ValidationEngine
    """
    engine = ValidationEngine()
    return engine.validate_quote(data)
