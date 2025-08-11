"""
QC Checklist Evaluation Module
Evaluates application and quote data against predefined QC checklist
"""
import json
from typing import Dict, List, Any
from datetime import datetime
import re

class QCChecker:
    def __init__(self):
        self.checklist_items = [
            # Forms
            {"id": "coverage_not_in_effect", "category": "Forms", "name": "COVERAGE NOT IN EFFECT form attached", "required": True},
            {"id": "consent_electronic_communications", "category": "Forms", "name": "CONSENT TO RECEIVE ELECTRONIC COMMUNICATIONS form attached", "required": True},
            {"id": "personal_info_consent", "category": "Forms", "name": "PERSONAL INFORMATION CONSENT FORM attached", "required": True},
            {"id": "personal_info_client_consent", "category": "Forms", "name": "PERSONAL INFORMATION CLIENT CONSENT FORM attached", "required": True},
            {"id": "optional_accident_benefits", "category": "Forms", "name": "Optional Accident Benefits Confirmation Form attached", "required": True},
            {"id": "privacy_consent", "category": "Forms", "name": "Privacy Consent Form signed", "required": True},
            
            # Date Validation
            {"id": "effective_date_match", "category": "Date Validation", "name": "Quote effective date matches application effective date", "required": True},
            
            # Automobile Section Validations
            {"id": "purchase_date_filled", "category": "Automobile Section", "name": "Purchase Date is filled for all vehicles", "required": True},
            {"id": "purchase_price_filled", "category": "Automobile Section", "name": "Purchase Price is filled for all vehicles", "required": True},
            {"id": "purchase_new_used_filled", "category": "Automobile Section", "name": "Purchase New or Used is filled for all vehicles", "required": True},
            {"id": "owned_leased_filled", "category": "Automobile Section", "name": "Owned Or Leased is filled for all vehicles", "required": True},
            {"id": "annual_driving_distance_filled", "category": "Automobile Section", "name": "Estimate annual driving distance is filled for all vehicles", "required": True},
            {"id": "fuel_type_filled", "category": "Automobile Section", "name": "Type of fuel used is filled for all vehicles", "required": True},
            
            # Other Requirements
            {"id": "payment_method_valid", "category": "Other Requirements", "name": "Valid payment method provided", "required": True}
        ]
    
    def evaluate_application_qc(self, application_data: Dict, quote_data: Dict) -> List[Dict]:
        """
        Evaluate application and quote data against QC checklist
        Returns list of QC results with simple PASS/FAIL format
        """
        results = []
        
        for item in self.checklist_items:
            result = {
                "check_description": item["name"],
                "status": "PASS",
                "remarks": "",
                "category": item["category"],
                "required": item["required"]
            }
            
            # Evaluate each checklist item
            try:
                if item["id"] == "coverage_not_in_effect":
                    result = self._check_coverage_not_in_effect(application_data, result)
                elif item["id"] == "consent_electronic_communications":
                    result = self._check_consent_electronic_communications(application_data, result)
                elif item["id"] == "personal_info_consent":
                    result = self._check_personal_info_consent(application_data, result)
                elif item["id"] == "personal_info_client_consent":
                    result = self._check_personal_info_client_consent(application_data, result)
                elif item["id"] == "optional_accident_benefits":
                    result = self._check_optional_accident_benefits(application_data, result)
                elif item["id"] == "privacy_consent":
                    result = self._check_privacy_consent(application_data, result)
                elif item["id"] == "effective_date_match":
                    result = self._check_effective_date_match(application_data, quote_data, result)
                elif item["id"] == "purchase_date_filled":
                    result = self._check_purchase_date_filled(application_data, result)
                elif item["id"] == "purchase_price_filled":
                    result = self._check_purchase_price_filled(application_data, result)
                elif item["id"] == "purchase_new_used_filled":
                    result = self._check_purchase_new_used_filled(application_data, result)
                elif item["id"] == "owned_leased_filled":
                    result = self._check_owned_leased_filled(application_data, result)
                elif item["id"] == "annual_driving_distance_filled":
                    result = self._check_annual_driving_distance_filled(application_data, result)
                elif item["id"] == "fuel_type_filled":
                    result = self._check_fuel_type_filled(application_data, result)
                elif item["id"] == "payment_method_valid":
                    result = self._check_payment_method_valid(application_data, result)
                    
            except Exception as e:
                result["status"] = "FAIL"
                result["remarks"] = f"Error evaluating item: {str(e)}"
            
            results.append(result)
        
        return results
    
    def _check_coverage_not_in_effect(self, application_data: Dict, result: Dict) -> Dict:
        """Check if COVERAGE NOT IN EFFECT form is attached"""
        # Check if the form is present in the extracted forms data
        forms = application_data.get("forms", {})
        if forms.get("coverage_not_in_effect", False):
            result["status"] = "PASS"
            result["remarks"] = "COVERAGE NOT IN EFFECT form verified as attached"
        else:
            # Fallback to text search if forms data not available
            if self._form_text_present(application_data, "COVERAGE NOT IN EFFECT"):
                result["status"] = "PASS"
                result["remarks"] = "COVERAGE NOT IN EFFECT form verified as attached"
            else:
                result["status"] = "FAIL"
                result["remarks"] = "COVERAGE NOT IN EFFECT form not found - must be attached. This form is required to confirm that coverage is not currently in effect for the applicant."
        return result
    
    def _check_consent_electronic_communications(self, application_data: Dict, result: Dict) -> Dict:
        """Check if CONSENT TO RECEIVE ELECTRONIC COMMUNICATIONS form is attached"""
        # Check if the form is present in the extracted forms data
        forms = application_data.get("forms", {})
        if forms.get("consent_electronic_communications", False):
            result["status"] = "PASS"
            result["remarks"] = "CONSENT TO RECEIVE ELECTRONIC COMMUNICATIONS form verified as attached"
        else:
            # Fallback to text search if forms data not available
            if self._form_text_present(application_data, "CONSENT TO RECEIVE ELECTRONIC COMMUNICATIONS"):
                result["status"] = "PASS"
                result["remarks"] = "CONSENT TO RECEIVE ELECTRONIC COMMUNICATIONS form verified as attached"
            else:
                result["status"] = "FAIL"
                result["remarks"] = "CONSENT TO RECEIVE ELECTRONIC COMMUNICATIONS form not found - must be attached. This form is required to authorize electronic communications with the client."
        return result
    
    def _check_personal_info_consent(self, application_data: Dict, result: Dict) -> Dict:
        """Check if PERSONAL INFORMATION CONSENT FORM is attached"""
        # Check if the form is present in the extracted forms data
        forms = application_data.get("forms", {})
        if forms.get("personal_info_consent", False):
            result["status"] = "PASS"
            result["remarks"] = "PERSONAL INFORMATION CONSENT FORM verified as attached"
        else:
            # Fallback to text search if forms data not available
            if self._form_text_present(application_data, "PERSONAL INFORMATION CONSENT FORM"):
                result["status"] = "PASS"
                result["remarks"] = "PERSONAL INFORMATION CONSENT FORM verified as attached"
            else:
                result["status"] = "FAIL"
                result["remarks"] = "PERSONAL INFORMATION CONSENT FORM not found - must be attached. This form is required to authorize the collection and use of personal information."
        return result
    
    def _check_personal_info_client_consent(self, application_data: Dict, result: Dict) -> Dict:
        """Check if PERSONAL INFORMATION CLIENT CONSENT FORM is attached"""
        # Check if the form is present in the extracted forms data
        forms = application_data.get("forms", {})
        if forms.get("personal_info_client_consent", False):
            result["status"] = "PASS"
            result["remarks"] = "PERSONAL INFORMATION CLIENT CONSENT FORM verified as attached"
        else:
            # Fallback to text search if forms data not available
            if self._form_text_present(application_data, "PERSONAL INFORMATION CLIENT CONSENT FORM"):
                result["status"] = "PASS"
                result["remarks"] = "PERSONAL INFORMATION CLIENT CONSENT FORM verified as attached"
            else:
                result["status"] = "FAIL"
                result["remarks"] = "PERSONAL INFORMATION CLIENT CONSENT FORM not found - must be attached. This form is required to authorize the sharing of personal information with third parties."
        return result
    
    def _check_optional_accident_benefits(self, application_data: Dict, result: Dict) -> Dict:
        """Check if Optional Accident Benefits Confirmation Form is attached"""
        # Check if the form is present in the extracted forms data
        forms = application_data.get("forms", {})
        if forms.get("optional_accident_benefits", False):
            result["status"] = "PASS"
            result["remarks"] = "Optional Accident Benefits Confirmation Form verified as attached"
        else:
            # Fallback to text search if forms data not available
            if self._form_text_present(application_data, "Optional Accident Benefits Confirmation Form"):
                result["status"] = "PASS"
                result["remarks"] = "Optional Accident Benefits Confirmation Form verified as attached"
            else:
                result["status"] = "FAIL"
                result["remarks"] = "Optional Accident Benefits Confirmation Form not found - must be attached. This form is required to confirm the client's selection of optional accident benefits coverage."
        return result
    
    def _form_text_present(self, application_data: Dict, form_name: str) -> bool:
        """Helper method to check if a specific form text is present in the application data"""
        # Convert application data to string for text search
        app_text = str(application_data).upper()
        form_text = form_name.upper()
        
        # Check if the form name is present in the application text
        return form_text in app_text
    
    def _check_privacy_consent(self, application_data: Dict, result: Dict) -> Dict:
        """Check if privacy consent form is signed"""
        # Check if the form is present in the extracted forms data
        forms = application_data.get("forms", {})
        if forms.get("privacy_consent", False):
            result["status"] = "PASS"
            result["remarks"] = "Privacy consent form verified as attached"
        else:
            # Fallback to text search if forms data not available
            if self._form_text_present(application_data, "Privacy Consent"):
                result["status"] = "PASS"
                result["remarks"] = "Privacy consent form verified as signed in application"
            else:
                result["status"] = "FAIL"
                result["remarks"] = "Privacy consent form not found - must be attached. This form is required to authorize the collection, use, and disclosure of personal information in accordance with privacy laws."
        return result
    
    def _check_effective_date_match(self, application_data: Dict, quote_data: Dict, result: Dict) -> Dict:
        """Check if quote effective date matches application effective date"""
        app_effective_date_str = application_data.get("policy_info", {}).get("effective_date")
        quote_effective_date_str = quote_data.get("quote_effective_date")

        if not app_effective_date_str or not quote_effective_date_str:
            result["status"] = "FAIL"
            result["remarks"] = "Application or Quote effective date missing."
            return result

        app_effective_date = self._normalize_date(app_effective_date_str)
        quote_effective_date = self._normalize_date(quote_effective_date_str)

        if app_effective_date == quote_effective_date:
            result["status"] = "PASS"
            result["remarks"] = "Quote effective date matches application effective date."
        else:
            result["status"] = "FAIL"
            result["remarks"] = f"Quote effective date ({quote_effective_date}) does not match application effective date ({app_effective_date}). This is a required validation."
        return result
    
    def _check_payment_method_valid(self, application_data: Dict, result: Dict) -> Dict:
        """Check if valid payment method is provided"""
        policy_info = application_data.get("policy_info", {})
        
        if not policy_info.get("payment_frequency"):
            result["status"] = "FAIL"
            result["remarks"] = "No payment method specified"
        else:
            payment_method = policy_info.get("payment_frequency")
            result["status"] = "PASS"
            result["remarks"] = f"Payment method verified: {payment_method}"
        
        return result
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string for comparison"""
        if not date_str:
            return ""
        
        # Handle various date formats
        date_str = str(date_str).strip()
        
        # Try to parse and normalize common formats
        try:
            # Handle MM/DD/YYYY format - normalize to consistent format
            if re.match(r'\d{1,2}/\d{1,2}/\d{4}', date_str):
                # Split the date and normalize month/day to 2 digits
                parts = date_str.split('/')
                if len(parts) == 3:
                    month = parts[0].zfill(2)  # Add leading zero if needed
                    day = parts[1].zfill(2)    # Add leading zero if needed
                    year = parts[2]
                    return f"{month}/{day}/{year}"
            
            # Handle other formats as needed
            return date_str
        except:
            return date_str

    def _check_purchase_date_filled(self, application_data: Dict, result: Dict) -> Dict:
        """Check if Purchase Date is filled for all vehicles"""
        vehicles = application_data.get("vehicles", [])
        if not vehicles:
            result["status"] = "FAIL"
            result["remarks"] = "No vehicles found in application - Purchase Date validation cannot be performed"
            return result
        
        missing_dates = []
        for i, vehicle in enumerate(vehicles):
            vehicle_num = i + 1
            purchase_date = vehicle.get("purchase_date")
            if not purchase_date:
                missing_dates.append(f"Vehicle {vehicle_num}")
        
        if missing_dates:
            result["status"] = "FAIL"
            result["remarks"] = f"Purchase Date missing for: {', '.join(missing_dates)}. Purchase Date is required for all vehicles."
        else:
            result["status"] = "PASS"
            result["remarks"] = "Purchase Date verified for all vehicles"
        
        return result
    
    def _check_purchase_price_filled(self, application_data: Dict, result: Dict) -> Dict:
        """Check if Purchase Price is filled for all vehicles"""
        vehicles = application_data.get("vehicles", [])
        if not vehicles:
            result["status"] = "FAIL"
            result["remarks"] = "No vehicles found in application - Purchase Price validation cannot be performed"
            return result
        
        missing_prices = []
        for i, vehicle in enumerate(vehicles):
            vehicle_num = i + 1
            purchase_price = vehicle.get("purchase_price") or vehicle.get("list_price")
            if not purchase_price:
                missing_prices.append(f"Vehicle {vehicle_num}")
        
        if missing_prices:
            result["status"] = "FAIL"
            result["remarks"] = f"Purchase Price missing for: {', '.join(missing_prices)}. Purchase Price is required for all vehicles."
        else:
            result["status"] = "PASS"
            result["remarks"] = "Purchase Price verified for all vehicles"
        
        return result
    
    def _check_purchase_new_used_filled(self, application_data: Dict, result: Dict) -> Dict:
        """Check if Purchase New or Used is filled for all vehicles"""
        vehicles = application_data.get("vehicles", [])
        if not vehicles:
            result["status"] = "FAIL"
            result["remarks"] = "No vehicles found in application - Purchase New or Used validation cannot be performed"
            return result
        
        missing_conditions = []
        for i, vehicle in enumerate(vehicles):
            vehicle_num = i + 1
            purchase_condition = vehicle.get("purchase_condition")
            if not purchase_condition:
                missing_conditions.append(f"Vehicle {vehicle_num}")
        
        if missing_conditions:
            result["status"] = "FAIL"
            result["remarks"] = f"Purchase New or Used missing for: {', '.join(missing_conditions)}. Purchase condition is required for all vehicles."
        else:
            result["status"] = "PASS"
            result["remarks"] = "Purchase New or Used verified for all vehicles"
        
        return result
    
    def _check_owned_leased_filled(self, application_data: Dict, result: Dict) -> Dict:
        """Check if Owned Or Leased is filled for all vehicles"""
        vehicles = application_data.get("vehicles", [])
        if not vehicles:
            result["status"] = "FAIL"
            result["remarks"] = "No vehicles found in application - Owned Or Leased validation cannot be performed"
            return result
        
        missing_ownership = []
        for i, vehicle in enumerate(vehicles):
            vehicle_num = i + 1
            owned = vehicle.get("owned")
            leased = vehicle.get("leased")
            if owned is None and leased is None:
                missing_ownership.append(f"Vehicle {vehicle_num}")
        
        if missing_ownership:
            result["status"] = "FAIL"
            result["remarks"] = f"Owned Or Leased missing for: {', '.join(missing_ownership)}. Ownership status is required for all vehicles."
        else:
            result["status"] = "PASS"
            result["remarks"] = "Owned Or Leased verified for all vehicles"
        
        return result
    
    def _check_annual_driving_distance_filled(self, application_data: Dict, result: Dict) -> Dict:
        """Check if Estimate annual driving distance is filled for all vehicles"""
        vehicles = application_data.get("vehicles", [])
        if not vehicles:
            result["status"] = "FAIL"
            result["remarks"] = "No vehicles found in application - Annual driving distance validation cannot be performed"
            return result
        
        missing_distances = []
        for i, vehicle in enumerate(vehicles):
            vehicle_num = i + 1
            annual_km = vehicle.get("annual_km") or vehicle.get("estimated_annual_driving_distance")
            if not annual_km:
                missing_distances.append(f"Vehicle {vehicle_num}")
        
        if missing_distances:
            result["status"] = "FAIL"
            result["remarks"] = f"Annual driving distance missing for: {', '.join(missing_distances)}. Annual driving distance is required for all vehicles."
        else:
            result["status"] = "PASS"
            result["remarks"] = "Annual driving distance verified for all vehicles"
        
        return result
    
    def _check_fuel_type_filled(self, application_data: Dict, result: Dict) -> Dict:
        """Check if Type of fuel used is filled for all vehicles"""
        vehicles = application_data.get("vehicles", [])
        if not vehicles:
            result["status"] = "FAIL"
            result["remarks"] = "No vehicles found in application - Fuel type validation cannot be performed"
            return result
        
        missing_fuel_types = []
        for i, vehicle in enumerate(vehicles):
            vehicle_num = i + 1
            fuel_type = vehicle.get("fuel_type") or vehicle.get("type_of_fuel")
            if not fuel_type:
                missing_fuel_types.append(f"Vehicle {vehicle_num}")
        
        if missing_fuel_types:
            result["status"] = "FAIL"
            result["remarks"] = f"Fuel type missing for: {', '.join(missing_fuel_types)}. Fuel type is required for all vehicles."
        else:
            result["status"] = "PASS"
            result["remarks"] = "Fuel type verified for all vehicles"
        
        return result
