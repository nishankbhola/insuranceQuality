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
    
    def validate_quote(self, data, no_dash_report=False):
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
                
                driver_report = self._validate_driver(driver, quote, mvrs, dashes, no_dash_report)
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

    def generate_compact_report(self, data, no_dash_report=False):
        """
        Generate a compact, one-page professional validation report with charts and analytics
        """
        # First get the full validation report
        full_report = self.validate_quote(data, no_dash_report=no_dash_report)
        
        # Extract summary statistics
        summary = full_report.get("summary", {})
        drivers = full_report.get("drivers", [])
        
        # Calculate analytics
        total_drivers = summary.get("total_drivers", 0)
        validated_drivers = summary.get("validated_drivers", 0)
        critical_errors = summary.get("critical_errors", 0)
        warnings = summary.get("warnings", 0)
        
        # Calculate percentages for charts
        validation_rate = (validated_drivers / total_drivers * 100) if total_drivers > 0 else 0
        error_rate = (critical_errors / total_drivers * 100) if total_drivers > 0 else 0
        warning_rate = (warnings / total_drivers * 100) if total_drivers > 0 else 0
        
        # Analyze driver statuses
        status_counts = {"PASS": 0, "WARNING": 0, "FAIL": 0}
        for driver in drivers:
            status = driver.get("validation_status", "FAIL")
            status_counts[status] += 1
        
        # Analyze validation categories
        validation_categories = {
            "MVR Validation": {"pass": 0, "warning": 0, "fail": 0},
            "DASH Validation": {"pass": 0, "warning": 0, "fail": 0},
            "License Progression": {"pass": 0, "warning": 0, "fail": 0},
            "Convictions": {"pass": 0, "warning": 0, "fail": 0},
            "Driver Training": {"pass": 0, "warning": 0, "fail": 0},
            "Report Age": {"pass": 0, "warning": 0, "fail": 0}
        }
        
        for driver in drivers:
            # MVR Validation
            mvr_status = driver.get("mvr_validation", {}).get("status", "FAIL")
            if mvr_status == "PASS":
                validation_categories["MVR Validation"]["pass"] += 1
            elif mvr_status == "WARNING":
                validation_categories["MVR Validation"]["warning"] += 1
            else:
                validation_categories["MVR Validation"]["fail"] += 1
            
            # DASH Validation
            dash_status = driver.get("dash_validation", {}).get("status", "FAIL")
            if dash_status == "PASS":
                validation_categories["DASH Validation"]["pass"] += 1
            elif dash_status == "WARNING":
                validation_categories["DASH Validation"]["warning"] += 1
            else:
                validation_categories["DASH Validation"]["fail"] += 1
            
            # License Progression
            license_status = driver.get("license_progression_validation", {}).get("status", "FAIL")
            if license_status == "PASS":
                validation_categories["License Progression"]["pass"] += 1
            elif license_status == "WARNING":
                validation_categories["License Progression"]["warning"] += 1
            else:
                validation_categories["License Progression"]["fail"] += 1
            
            # Convictions
            convictions_status = driver.get("convictions_validation", {}).get("status", "FAIL")
            if convictions_status == "PASS":
                validation_categories["Convictions"]["pass"] += 1
            elif convictions_status == "WARNING":
                validation_categories["Convictions"]["warning"] += 1
            else:
                validation_categories["Convictions"]["fail"] += 1
            
            # Driver Training
            training_status = driver.get("driver_training_validation", {}).get("status", "FAIL")
            if training_status == "PASS":
                validation_categories["Driver Training"]["pass"] += 1
            elif training_status == "WARNING":
                validation_categories["Driver Training"]["warning"] += 1
            else:
                validation_categories["Driver Training"]["fail"] += 1
            
            # Report Age
            report_age_status = driver.get("report_age_validation", {}).get("status", "FAIL")
            if report_age_status == "PASS":
                validation_categories["Report Age"]["pass"] += 1
            elif report_age_status == "WARNING":
                validation_categories["Report Age"]["warning"] += 1
            else:
                validation_categories["Report Age"]["fail"] += 1
        
        # Generate compact driver summaries
        driver_summaries = []
        for driver in drivers:
            driver_summary = {
                "name": driver.get("driver_name", "Unknown"),
                "license": driver.get("driver_license", "Unknown"),
                "status": driver.get("validation_status", "FAIL"),
                "mvr_found": driver.get("mvr_found", False),
                "dash_found": driver.get("dash_found", False),
                "critical_errors": len(driver.get("critical_errors", [])),
                "warnings": len(driver.get("warnings", [])),
                "matches": len(driver.get("matches", []))
            }
            driver_summaries.append(driver_summary)
        
        # Create compact report
        compact_report = {
            "report_metadata": {
                "generated_at": self._get_current_timestamp(),
                "total_drivers": total_drivers,
                "overall_status": self._get_overall_status(summary)
            },
            "summary_statistics": {
                "validation_rate": round(validation_rate, 1),
                "error_rate": round(error_rate, 1),
                "warning_rate": round(warning_rate, 1),
                "total_critical_errors": critical_errors,
                "total_warnings": warnings,
                "total_matches": sum(len(d.get("matches", [])) for d in drivers)
            },
            "status_distribution": status_counts,
            "validation_categories": validation_categories,
            "driver_summaries": driver_summaries,
            "charts": {
                "validation_pie_chart": {
                    "labels": ["Pass", "Warning", "Fail"],
                    "data": [status_counts["PASS"], status_counts["WARNING"], status_counts["FAIL"]],
                    "colors": ["#28a745", "#ffc107", "#dc3545"]
                },
                "category_radar_chart": {
                    "labels": list(validation_categories.keys()),
                    "pass_data": [validation_categories[cat]["pass"] for cat in validation_categories],
                    "warning_data": [validation_categories[cat]["warning"] for cat in validation_categories],
                    "fail_data": [validation_categories[cat]["fail"] for cat in validation_categories]
                },
                "validation_bar_chart": {
                    "labels": ["Validation Rate", "Error Rate", "Warning Rate"],
                    "data": [validation_rate, error_rate, warning_rate],
                    "colors": ["#28a745", "#dc3545", "#ffc107"]
                }
            },
            "key_insights": self._generate_key_insights(summary, drivers, validation_categories),
            "recommendations": self._generate_recommendations(summary, drivers)
        }
        
        return compact_report

    def _get_current_timestamp(self):
        """Get current timestamp in a readable format"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _get_overall_status(self, summary):
        """Determine overall status based on summary"""
        if summary.get("critical_errors", 0) > 0:
            return "FAIL"
        elif summary.get("warnings", 0) > 0:
            return "WARNING"
        else:
            return "PASS"

    def _generate_key_insights(self, summary, drivers, validation_categories):
        """Generate key insights from the validation data"""
        insights = []
        
        total_drivers = summary.get("total_drivers", 0)
        validation_rate = (summary.get("validated_drivers", 0) / total_drivers * 100) if total_drivers > 0 else 0
        
        if validation_rate >= 90:
            insights.append("Excellent validation rate - most drivers are properly documented")
        elif validation_rate >= 70:
            insights.append("Good validation rate - some drivers need attention")
        else:
            insights.append("Low validation rate - significant documentation issues detected")
        
        # Check MVR coverage
        mvr_found_count = sum(1 for d in drivers if d.get("mvr_found", False))
        mvr_coverage = (mvr_found_count / total_drivers * 100) if total_drivers > 0 else 0
        if mvr_coverage < 100:
            insights.append(f"MVR coverage: {mvr_coverage:.1f}% - missing MVR reports for {total_drivers - mvr_found_count} drivers")
        
        # Check DASH coverage
        dash_found_count = sum(1 for d in drivers if d.get("dash_found", False))
        dash_coverage = (dash_found_count / total_drivers * 100) if total_drivers > 0 else 0
        if dash_coverage < 100:
            insights.append(f"DASH coverage: {dash_coverage:.1f}% - missing DASH reports for {total_drivers - dash_found_count} drivers")
        
        # Check for critical issues
        critical_errors = summary.get("critical_errors", 0)
        if critical_errors > 0:
            insights.append(f"Critical issues detected: {critical_errors} errors require immediate attention")
        
        return insights

    def _generate_recommendations(self, summary, drivers):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check for missing MVRs
        missing_mvrs = sum(1 for d in drivers if not d.get("mvr_found", False))
        if missing_mvrs > 0:
            recommendations.append(f"Upload MVR reports for {missing_mvrs} driver(s)")
        
        # Check for missing DASH reports
        missing_dash = sum(1 for d in drivers if not d.get("dash_found", False))
        if missing_dash > 0:
            recommendations.append(f"Upload DASH reports for {missing_dash} driver(s)")
        
        # Check for critical errors
        critical_errors = summary.get("critical_errors", 0)
        if critical_errors > 0:
            recommendations.append("Review and resolve critical validation errors")
        
        # Check for warnings
        warnings = summary.get("warnings", 0)
        if warnings > 0:
            recommendations.append("Review warnings for potential data inconsistencies")
        
        # Check validation rate
        validation_rate = (summary.get("validated_drivers", 0) / summary.get("total_drivers", 1) * 100)
        if validation_rate < 80:
            recommendations.append("Improve data quality to achieve higher validation rates")
        
        return recommendations

    def _validate_driver(self, driver, quote, mvrs, dashes, no_dash_report=False):
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
                    "convictions_validation": {"status": "ERROR", "critical_errors": ["Driver data missing"], "warnings": [], "matches": []},
                    "report_age_validation": {"status": "ERROR", "critical_errors": ["Driver data missing"], "warnings": [], "matches": []}
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
                },
                "report_age_validation": {
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
            matched_dash = self._find_matching_dash(quote_license, dashes) if not no_dash_report else None
            
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
                
            # Validate DASH data only if noDashReport is false
            if not no_dash_report and matched_dash:
                dash_validation = self._validate_dash_data(driver, matched_dash, quote)
                driver_report["dash_validation"] = dash_validation
                driver_report["critical_errors"].extend(dash_validation.get("critical_errors", []))
                driver_report["warnings"].extend(dash_validation.get("warnings", []))
                driver_report["matches"].extend(dash_validation.get("matches", []))
            elif no_dash_report:
                # Set DASH validation status to indicate it was skipped
                driver_report["dash_validation"] = {
                    "status": "SKIPPED",
                    "critical_errors": [],
                    "warnings": ["DASH validation skipped - no DASH report available"],
                    "matches": []
                }
            
            # Validate driver training
            if matched_mvr:
                driver_training_validation = self._validate_driver_training(driver, quote)
                driver_report["driver_training_validation"] = driver_training_validation
                driver_report["critical_errors"].extend(driver_training_validation["critical_errors"])
                driver_report["warnings"].extend(driver_training_validation["warnings"])
                driver_report["matches"].extend(driver_training_validation["matches"])
            
            # Validate report age (DASH and MVR report dates)
            report_age_validation = self._validate_report_age(matched_dash, matched_mvr, quote)
            driver_report["report_age_validation"] = report_age_validation
            driver_report["critical_errors"].extend(report_age_validation["critical_errors"])
            driver_report["warnings"].extend(report_age_validation["warnings"])
            driver_report["matches"].extend(report_age_validation["matches"])
            
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
                "convictions_validation": {"status": "ERROR", "critical_errors": [f"Validation error: {str(e)}"], "warnings": [], "matches": []},
                "report_age_validation": {"status": "ERROR", "critical_errors": [f"Validation error: {str(e)}"], "warnings": [], "matches": []}
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

    def _validate_driver_training(self, driver, quote):
        """
        Validate driver training requirements and add warnings for DTC attachment
        """
        validation = {
            "status": "PASS",
            "critical_errors": [],
            "warnings": [],
            "matches": []
        }
        
        # Check if driver has driver training
        driver_training = driver.get("driver_training", "")
        
        if driver_training and driver_training.lower() == "yes":
            validation["warnings"].append("Please make sure to attach the DTC on file")
            validation["matches"].append("Driver training detected - DTC attachment reminder added")
        elif driver_training and driver_training.lower() == "no":
            validation["matches"].append("No driver training required")
        else:
            # No driver training information found
            validation["matches"].append("No driver training information available")
        
        return validation

    def _validate_report_age(self, matched_dash, matched_mvr, quote):
        """
        Validate that DASH and MVR reports are generated within acceptable timeframes:
        - DASH report should be generated within 45 days of quote_effective_date
        - MVR report should be generated within 30 days of quote_effective_date
        """
        validation = {
            "status": "PASS",
            "critical_errors": [],
            "warnings": [],
            "matches": []
        }
        
        # Get quote effective date
        quote_effective_date = quote.get("quote_effective_date", "")
        if not quote_effective_date:
            validation["warnings"].append("Quote effective date not available for report age validation")
            return validation
        
        # Parse quote effective date (MM/DD/YYYY format)
        try:
            quote_date = self._parse_date(quote_effective_date, "quote")
            if not quote_date:
                validation["warnings"].append(f"Could not parse quote effective date: {quote_effective_date}")
                return validation
        except Exception as e:
            validation["warnings"].append(f"Error parsing quote effective date: {quote_effective_date}")
            return validation
        
        # Validate DASH report age
        if matched_dash and matched_dash.get("report_date"):
            dash_report_date = matched_dash.get("report_date")
            try:
                # Parse DASH report date (YYYY-MM-DD HH:MM:SS format)
                dash_date = self._parse_date_dash_format(dash_report_date)
                if dash_date:
                    # Calculate days difference
                    days_diff = (quote_date - dash_date).days
                    
                    if days_diff < 0:
                        # DASH report is in the future relative to quote effective date
                        validation["matches"].append(f"DASH report date {dash_report_date} is after quote effective date {quote_effective_date}")
                    elif days_diff <= 45:
                        # DASH report is within acceptable timeframe
                        validation["matches"].append(f"DASH report age is acceptable: {days_diff} days (≤45 days limit)")
                    else:
                        # DASH report is too old
                        validation["critical_errors"].append(
                            f"DASH report is too old: {days_diff} days since generation (>{45} days limit). "
                            f"Report date: {dash_report_date}, Quote effective: {quote_effective_date}"
                        )
                        validation["status"] = "FAIL"
                else:
                    validation["warnings"].append(f"Could not parse DASH report date: {dash_report_date}")
            except Exception as e:
                validation["warnings"].append(f"Error validating DASH report age: {str(e)}")
        else:
            validation["warnings"].append("DASH report date not available for age validation")
        
        # Validate MVR report age
        if matched_mvr and matched_mvr.get("release_date"):
            mvr_release_date = matched_mvr.get("release_date")
            try:
                # Parse MVR release date (DD/MM/YYYY format)
                mvr_date = self._parse_date(mvr_release_date, "mvr")
                if mvr_date:
                    # Calculate days difference
                    days_diff = (quote_date - mvr_date).days
                    
                    if days_diff < 0:
                        # MVR report is in the future relative to quote effective date
                        validation["matches"].append(f"MVR release date {mvr_release_date} is after quote effective date {quote_effective_date}")
                    elif days_diff <= 30:
                        # MVR report is within acceptable timeframe
                        validation["matches"].append(f"MVR report age is acceptable: {days_diff} days (≤30 days limit)")
                    else:
                        # MVR report is too old
                        validation["critical_errors"].append(
                            f"MVR report is too old: {days_diff} days since release (>{30} days limit). "
                            f"Release date: {mvr_release_date}, Quote effective: {quote_effective_date}"
                        )
                        validation["status"] = "FAIL"
                else:
                    validation["warnings"].append(f"Could not parse MVR release date: {mvr_release_date}")
            except Exception as e:
                validation["warnings"].append(f"Error validating MVR release age: {str(e)}")
        else:
            validation["warnings"].append("MVR release date not available for age validation")
        
        return validation

    def _parse_date_dash_format(self, date_str):
        """
        Parse DASH report date which is in format: "YYYY-MM-DD HH:MM:SS EDT"
        """
        if not date_str:
            return None
        
        try:
            # Extract just the date part if it includes time and timezone
            if " " in date_str:
                date_part = date_str.split(" ")[0]  # Get YYYY-MM-DD part
            else:
                date_part = date_str
            
            # Parse YYYY-MM-DD format
            return datetime.strptime(date_part, "%Y-%m-%d")
        except Exception as e:
            print(f"DEBUG: Error parsing DASH date '{date_str}': {e}")
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
                validation["matches"].append(f"License number matches: Quote '{quote_license_raw}' vs MVR '{mvr_license_raw}'")
            else:
                validation["critical_errors"].append(f"License number mismatch: Quote '{quote_license_raw}' vs MVR '{mvr_license_raw}'")
                validation["status"] = "FAIL"
        
        # Name validation (fuzzy match) - More lenient matching
        quote_name = driver.get("full_name", "")
        mvr_name = mvr.get("name", "")
        
        # First validate name order
        is_valid_order, order_error = self._validate_name_order(quote_name, mvr_name)
        if not is_valid_order:
            validation["critical_errors"].append(f"Name order error: {order_error}")
            validation["status"] = "FAIL"
        
        # Then check if names match (existing logic)
        if self._similar(quote_name, mvr_name) or self._names_contain_same_parts(quote_name, mvr_name):
            validation["matches"].append(f"Name matches: Quote '{quote_name}' vs MVR '{mvr_name}'")
        else:
            # More lenient name matching - treat as warning instead of critical error
            # Check if names might be the same person with different formatting
            if self._names_might_be_same_person(quote_name, mvr_name):
                validation["warnings"].append(f"Name format difference: Quote '{quote_name}' vs MVR '{mvr_name}' (likely same person)")
            else:
                validation["warnings"].append(f"Name mismatch: Quote '{quote_name}' vs MVR '{mvr_name}'")
            # Note: No longer setting status to FAIL for name mismatches
        
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
                validation["matches"].append(f"Address matches: MVR '{mvr_address}' vs Quote garaging '{quote_garaging_location}'")
            else:
                validation["critical_errors"].append(f"Address mismatch: MVR '{mvr_address}' vs Quote garaging location '{quote_garaging_location}'")
                validation["status"] = "FAIL"
        elif mvr_address and not quote_garaging_location:
            validation["critical_errors"].append(f"MVR has address '{mvr_address}' but Quote has no garaging location")
            validation["status"] = "FAIL"
        elif not mvr_address and quote_garaging_location:
            validation["warnings"].append(f"Quote has garaging location '{quote_garaging_location}' but MVR has no address")
        
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
        
        # Status validation - must be "LICENCED"
        mvr_status = mvr.get("status", "")
        if mvr_status:
            if mvr_status.upper() == "LICENCED":
                validation["matches"].append(f"License status is valid: {mvr_status}")
            else:
                validation["critical_errors"].append(f"License status is not valid: '{mvr_status}' (must be 'LICENCED')")
                validation["status"] = "FAIL"
        else:
            validation["warnings"].append("No license status found in MVR")
        
        return validation

    def _validate_license_progression_enhanced(self, driver, mvr):
        """
        Enhanced license progression validation with G1/G2/G date logic
        Implements the business rules:
        - If DD/MM of MVR expiry date and birth date match: g1_date = issue_date, g2_date = g1_date + 1 year, g_date = g2_date + 1 year
        - If DD/MM don't match: g1_date = expiry_date - 5 years, g2_date = g1_date + 1 year, g_date = g2_date + 1 year
        - SPECIAL RULE: If MVR issue date is before April 1, 1994, issue_date becomes G date and G1/G2 dates are not required
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
        
        # If no issue date found, try to infer it from available dates
        if not mvr_issue_date:
            mvr_issue_date = self._infer_license_issue_date(mvr)
            if mvr_issue_date:
                print(f"DEBUG: Using inferred issue date: {mvr_issue_date}")
        
        # Debug: Print the comparison details
        print(f"DEBUG: License progression validation:")
        print(f"  MVR expiry: {mvr_expiry_date}")
        print(f"  MVR birth: {mvr_birth_date}")
        print(f"  MVR issue: {mvr_issue_date}")
        print(f"  Quote G1: {quote_g1_date}")
        print(f"  Quote G2: {quote_g2_date}")
        print(f"  Quote G: {quote_g_date}")
        print(f"  License Class: {license_class}")
        
        # Additional debugging for date parsing
        if mvr_expiry_date:
            parsed_expiry = self._parse_date(mvr_expiry_date, "mvr")
            print(f"  Parsed expiry: {parsed_expiry}")
        
        if mvr_birth_date:
            parsed_birth = self._parse_date(mvr_birth_date, "mvr")
            print(f"  Parsed birth: {parsed_birth}")
        
        if mvr_issue_date:
            parsed_issue = self._parse_date(mvr_issue_date, "mvr")
            print(f"  Parsed issue: {parsed_issue}")
            if parsed_issue:
                april_1994 = datetime(1994, 4, 1)
                is_pre_1994 = parsed_issue < april_1994
                print(f"  Issue date {mvr_issue_date} is before April 1, 1994: {is_pre_1994}")
        
        # Note: Higher-level license classes (A, C, D, etc.) still require G1 → G2 → G progression
        # They don't skip the G1/G2 stages - they just mean the driver can already drive G vehicles
        # Only pre-April 1, 1994 licenses skip G1/G2 progression
        if license_class:
            print(f"DEBUG: License class '{license_class}' detected - will validate G1/G2/G progression as normal")
        
        # Check if MVR issue date is before April 1, 1994
        april_1994 = datetime(1994, 4, 1)
        
        if mvr_issue_date:
            issue_date_parsed = self._parse_date(mvr_issue_date, "mvr")
            
            if issue_date_parsed and issue_date_parsed < april_1994:
                print(f"DEBUG: MVR issue date {mvr_issue_date} is before April 1, 1994 - applying special rules")
                
                # Special rule: Issue date becomes G date, G1/G2 not required
                # Convert MVR date format (DD/MM/YYYY) to Quote format (MM/DD/YYYY) for comparison
                expected_g_date = self._convert_mvr_date_to_quote_format(mvr_issue_date)
                
                validation["matches"].append(f"Pre-April 1, 1994 license detected - issue date {mvr_issue_date} becomes G date")
                validation["matches"].append("G1 and G2 dates not required for licenses issued before April 1, 1994")
                
                # Validate G date only
                if quote_g_date:
                    if self._dates_match(expected_g_date, quote_g_date, "quote", "quote"):
                        validation["matches"].append(f"G date matches: Expected '{expected_g_date}' vs Quote '{quote_g_date}'")
                    else:
                        validation["critical_errors"].append(f"G date mismatch: Expected '{expected_g_date}' vs Quote '{quote_g_date}'")
                        validation["status"] = "FAIL"
                else:
                    validation["critical_errors"].append(f"Quote missing G date, expected: '{expected_g_date}'")
                    validation["status"] = "FAIL"
                
                # Don't validate G1/G2 dates for pre-April 1, 1994 licenses
                if quote_g1_date:
                    validation["warnings"].append(f"G1 date '{quote_g1_date}' provided but not required for pre-April 1, 1994 licenses")
                
                if quote_g2_date:
                    validation["warnings"].append(f"G2 date '{quote_g2_date}' provided but not required for pre-April 1, 1994 licenses")
                
                return validation
        else:
            # No issue date found - try to infer from other available dates
            print(f"DEBUG: No MVR issue date found - attempting to infer from available dates")
            
            # Try to use the earliest available date as a potential issue date
            available_dates = []
            if mvr_expiry_date:
                available_dates.append(("expiry", mvr_expiry_date))
            if mvr_birth_date:
                available_dates.append(("birth", mvr_birth_date))
            
            if available_dates:
                # Parse all available dates and find the earliest
                parsed_dates = []
                for date_type, date_str in available_dates:
                    try:
                        parsed_date = self._parse_date(date_str, "mvr")
                        if parsed_date:
                            parsed_dates.append((parsed_date, date_str, date_type))
                    except:
                        continue
                
                if parsed_dates:
                    # Sort by date and take the earliest
                    parsed_dates.sort(key=lambda x: x[0])
                    earliest_date = parsed_dates[0][1]
                    earliest_type = parsed_dates[0][2]
                    
                    print(f"DEBUG: Using earliest available date as potential issue date: {earliest_date} (from {earliest_type})")
                    
                    # Check if this earliest date is before April 1, 1994
                    earliest_parsed = parsed_dates[0][0]
                    if earliest_parsed < april_1994:
                        print(f"DEBUG: Earliest date {earliest_date} is before April 1, 1994 - applying special rules")
                        
                        # Use this as the G date
                        expected_g_date = self._convert_mvr_date_to_quote_format(earliest_date)
                        
                        validation["matches"].append(f"Pre-April 1, 1994 license inferred - earliest date {earliest_date} becomes G date")
                        validation["matches"].append("G1 and G2 dates not required for licenses issued before April 1, 1994")
                        
                        # Validate G date only
                        if quote_g_date:
                            if self._dates_match(expected_g_date, quote_g_date, "quote", "quote"):
                                validation["matches"].append(f"G date matches: Expected '{expected_g_date}' vs Quote '{quote_g_date}'")
                            else:
                                validation["critical_errors"].append(f"G date mismatch: Expected '{expected_g_date}' vs Quote '{quote_g_date}'")
                                validation["status"] = "FAIL"
                        else:
                            validation["critical_errors"].append(f"Quote missing G date, expected: '{expected_g_date}'")
                            validation["status"] = "FAIL"
                        
                        # Don't validate G1/G2 dates for pre-April 1, 1994 licenses
                        if quote_g1_date:
                            validation["warnings"].append(f"G1 date '{quote_g1_date}' provided but not required for pre-April 1, 1994 licenses")
                        
                        if quote_g2_date:
                            validation["warnings"].append(f"G2 date '{quote_g2_date}' provided but not required for pre-April 1, 1994 licenses")
                        
                        return validation
            
            # If we still can't determine, add a helpful warning
            validation["warnings"].append("Unable to determine if license is pre or post-April 1, 1994 - issue date not found")
            validation["warnings"].append("License progression validation may be incomplete without the license issue date")
        
        # Standard logic for post-April 1, 1994 licenses
        # Calculate expected G1/G2/G dates from MVR data using business rules
        calculated_dates = self._calculate_license_dates_from_mvr(mvr_expiry_date, mvr_birth_date, mvr_issue_date)
        
        if calculated_dates:
            calculated_g1, calculated_g2, calculated_g = calculated_dates
            print(f"  Calculated G1: {calculated_g1}")
            print(f"  Calculated G2: {calculated_g2}")
            print(f"  Calculated G: {calculated_g}")
            
            # Check for special case: If quote G date matches issue date AND this is a pre-April 1994 license
            # This can happen when someone got their G license before the graduated system was fully enforced
            if quote_g_date and mvr_issue_date:
                quote_g_parsed = self._parse_date(quote_g_date, "quote")
                issue_parsed = self._parse_date(mvr_issue_date, "mvr")
                
                # Only apply special case if the issue date is before April 1, 1994
                if quote_g_parsed and issue_parsed and issue_parsed < april_1994:
                    if self._dates_match(quote_g_date, mvr_issue_date, "quote", "mvr"):
                        print(f"DEBUG: Special case detected - Pre-April 1994 license with G date matching issue date")
                        print(f"DEBUG: This suggests the driver got their G license directly without G1/G2 progression")
                        
                        # Add special case handling
                        validation["matches"].append(f"Special case detected: Pre-April 1994 license with G date '{quote_g_date}' matching issue date '{mvr_issue_date}'")
                        validation["matches"].append("This suggests the driver obtained their G license directly (before graduated licensing was fully enforced)")
                        
                        # Validate G date
                        validation["matches"].append(f"G date matches: Quote '{quote_g_date}' vs MVR issue date '{mvr_issue_date}'")
                        
                        # For pre-April 1994 licenses, G1/G2 dates are not required
                        if quote_g1_date:
                            validation["warnings"].append(f"G1 date '{quote_g1_date}' provided but not required for pre-April 1994 licenses")
                        else:
                            validation["matches"].append("G1 date not required for pre-April 1994 licenses")
                        
                        if quote_g2_date:
                            validation["warnings"].append(f"G2 date '{quote_g2_date}' provided but not required for pre-April 1994 licenses")
                        else:
                            validation["matches"].append("G2 date not required for pre-April 1994 licenses")
                        
                        # Set status to PASS since this is a valid special case
                        validation["status"] = "PASS"
                        return validation
                else:
                    # Post-April 1994 license with G date matching issue date - this is suspicious
                    if self._dates_match(quote_g_date, mvr_issue_date, "quote", "mvr"):
                        print(f"DEBUG: Suspicious case detected - Post-April 1994 license with G date matching issue date")
                        print(f"DEBUG: This suggests the driver got their G license directly, but G1/G2 progression is still required")
                        
                        # Add warning about suspicious case
                        validation["warnings"].append(f"Suspicious case: Post-April 1994 license with G date '{quote_g_date}' matching issue date '{mvr_issue_date}'")
                        validation["warnings"].append("This suggests the driver got their G license directly, but G1/G2 progression is still required for post-April 1994 licenses")
                        
                        # Continue with normal validation (G1/G2 dates are still required)
            
            # Standard validation for normal G1/G2/G progression
            # Compare calculated dates with quote dates
            if quote_g1_date:
                if self._dates_match(calculated_g1, quote_g1_date, "calculated", "quote"):
                    validation["matches"].append(f"G1 date matches: Calculated '{calculated_g1}' vs Quote '{quote_g1_date}'")
                else:
                    validation["critical_errors"].append(f"G1 date mismatch: Calculated '{calculated_g1}' vs Quote '{quote_g1_date}'")
                    validation["status"] = "FAIL"
            else:
                validation["critical_errors"].append(f"Quote missing G1 date, expected: '{calculated_g1}'")
                validation["status"] = "FAIL"
            
            if quote_g2_date:
                if self._dates_match(calculated_g2, quote_g2_date, "calculated", "quote"):
                    validation["matches"].append(f"G2 date matches: Calculated '{calculated_g2}' vs Quote '{quote_g2_date}'")
                else:
                    validation["critical_errors"].append(f"G2 date mismatch: Calculated '{calculated_g2}' vs Quote '{quote_g2_date}'")
                    validation["status"] = "FAIL"
            else:
                validation["critical_errors"].append(f"Quote missing G2 date, expected: '{calculated_g2}'")
                validation["status"] = "FAIL"
            
            if quote_g_date:
                if self._dates_match(calculated_g, quote_g_date, "calculated", "quote"):
                    validation["matches"].append(f"G date matches: Calculated '{calculated_g}' vs Quote '{quote_g_date}'")
                else:
                    validation["critical_errors"].append(f"G date mismatch: Calculated '{calculated_g}' vs Quote '{quote_g_date}'")
                    validation["status"] = "FAIL"
            else:
                validation["critical_errors"].append(f"Quote missing G date, expected: '{calculated_g}'")
                validation["status"] = "FAIL"
        else:
            # Provide more helpful error message
            missing_fields = []
            if not mvr_expiry_date:
                missing_fields.append("expiry date")
            if not mvr_birth_date:
                missing_fields.append("birth date")
            if not mvr_issue_date:
                missing_fields.append("issue date")
            
            error_msg = f"Could not calculate expected license dates from MVR data. Missing: {', '.join(missing_fields)}"
            validation["critical_errors"].append(error_msg)
            validation["status"] = "FAIL"
            
            # Add helpful guidance
            if not mvr_issue_date:
                validation["warnings"].append("MVR issue date not found - this is required for license progression validation")
                validation["warnings"].append("Consider checking if the MVR document contains the license issue date in a different format")
                validation["warnings"].append("The system will attempt to infer the issue date from other available dates")
            
            if not mvr_expiry_date or not mvr_birth_date:
                validation["warnings"].append("MVR expiry date and birth date are required for calculating G1/G2/G progression")
            
            # Try to provide specific guidance based on what's available
            if mvr_expiry_date and mvr_birth_date and not mvr_issue_date:
                validation["warnings"].append("Have expiry and birth dates but missing issue date - this prevents accurate G1/G2/G calculation")
                validation["warnings"].append("Consider manually reviewing the MVR document for the license issue date")
        
        # Validate that the progression makes sense (additional check) - only for post-April 1, 1994
        if quote_g1_date and quote_g2_date:
            if not self._is_date_before(quote_g1_date, quote_g2_date, "quote", "quote"):
                validation["critical_errors"].append(f"G1 date '{quote_g1_date}' should be before G2 date '{quote_g2_date}'")
                validation["status"] = "FAIL"
        
        if quote_g2_date and quote_g_date:
            if not self._is_date_before(quote_g2_date, quote_g_date, "quote", "quote"):
                validation["critical_errors"].append(f"G2 date '{quote_g2_date}' should be before G date '{quote_g_date}'")
                validation["status"] = "FAIL"
        
        return validation
    
    def _convert_mvr_date_to_quote_format(self, mvr_date):
        """
        Convert MVR date format (DD/MM/YYYY) to Quote format (MM/DD/YYYY)
        """
        if not mvr_date or '/' not in mvr_date:
            return mvr_date
        
        try:
            parts = mvr_date.split('/')
            if len(parts) == 3:
                day, month, year = parts
                return f"{month}/{day}/{year}"
        except:
            pass
        
        return mvr_date
    
    def _infer_license_issue_date(self, mvr_data):
        """
        Try to infer the license issue date from available MVR data
        This is a fallback when the explicit issue date is not found
        """
        available_dates = []
        
        # Collect all available dates from MVR
        if mvr_data.get("expiry_date"):
            available_dates.append(("expiry", mvr_data.get("expiry_date")))
        if mvr_data.get("birth_date"):
            available_dates.append(("birth", mvr_data.get("birth_date")))
        if mvr_data.get("release_date"):
            available_dates.append(("release", mvr_data.get("release_date")))
        
        if not available_dates:
            return None
        
        # Parse all available dates and find the earliest one
        parsed_dates = []
        for date_type, date_str in available_dates:
            try:
                parsed_date = self._parse_date(date_str, "mvr")
                if parsed_date:
                    parsed_dates.append((parsed_date, date_str, date_type))
            except:
                continue
        
        if parsed_dates:
            # Sort by date and take the earliest
            parsed_dates.sort(key=lambda x: x[0])
            earliest_date = parsed_dates[0][1]
            earliest_type = parsed_dates[0][2]
            
            print(f"DEBUG: Inferred license issue date from {earliest_type}: {earliest_date}")
            return earliest_date
        
        return None

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
        Enhanced convictions validation with detailed comparison information
        """
        validation = {
            "status": "PASS",
            "critical_errors": [],
            "warnings": [],
            "matches": []
        }
        
        # Get convictions from MVR and quote
        mvr_convictions = mvr.get("convictions", [])
        quote_convictions = quote.get("convictions", [])
        
        validation["matches"].append(f"Found {len(mvr_convictions)} conviction(s) in MVR, {len(quote_convictions)} in Quote")
        
        # If no convictions in MVR, this is acceptable
        if not mvr_convictions:
            validation["matches"].append("No convictions found in MVR - this is acceptable")
            return validation
        
        # Check each MVR conviction against quote convictions
        for mvr_conviction in mvr_convictions:
            # MVR uses 'offence_date' field, Quote uses 'date' field
            mvr_date = mvr_conviction.get("offence_date", mvr_conviction.get("date", ""))
            mvr_description = mvr_conviction.get("description", "")
            mvr_code = mvr_conviction.get("code", "")
            
            # Look for matching conviction in quote
            conviction_found = False
            
            for quote_conviction in quote_convictions:
                quote_date = quote_conviction.get("date", "")
                quote_description = quote_conviction.get("description", "")
                quote_code = quote_conviction.get("code", "")
                
                # Check if dates match
                if mvr_date and quote_date and self._dates_match(mvr_date, quote_date, "mvr", "quote"):
                    # Check if descriptions match
                    if self._conviction_descriptions_match(mvr_description, quote_description):
                        validation["matches"].append(f"Conviction validated: MVR '{mvr_description}' on '{mvr_date}' vs Quote '{quote_description}' on '{quote_date}'")
                        conviction_found = True
                        break
                    else:
                        validation["warnings"].append(f"Conviction date match but description mismatch: MVR '{mvr_description}' vs Quote '{quote_description}' on '{mvr_date}'")
            
            if not conviction_found:
                validation["critical_errors"].append(f"Conviction not declared in Quote: '{mvr_description}' on '{mvr_date}' (Code: {mvr_code})")
                validation["status"] = "FAIL"
        
        return validation

    def _validate_dash_data(self, driver, dash, quote):
        """
        Validate DASH data against quote data according to business rules
        """
        validation = {
            "status": "PASS",
            "critical_errors": [],
            "warnings": [],
            "matches": []
        }
        
        # Use the driver parameter that was passed in (correct driver for this validation)
        quote_name = driver.get("full_name", "")
        quote_license = driver.get("licence_number", "")
        quote_dob = driver.get("birth_date", "")
        
        # Get DASH info
        dash_name = dash.get("name", "")
        dash_license = dash.get("dln", "")
        dash_dob = dash.get("date_of_birth", "")
        
        # Name comparison - More lenient matching
        if quote_name and dash_name:
            # First validate name order (DASH names might also be in LASTNAME,FIRSTNAME format)
            is_valid_order, order_error = self._validate_name_order(quote_name, dash_name)
            if not is_valid_order:
                validation["critical_errors"].append(f"Name order error: {order_error}")
                validation["status"] = "FAIL"
            
            # Then check if names match (existing logic)
            if self._similar(quote_name, dash_name) or self._names_contain_same_parts(quote_name, dash_name):
                validation["matches"].append(f"Name matches: Quote '{quote_name}' vs DASH '{dash_name}'")
            else:
                # More lenient name matching - treat as warning instead of critical error
                # Check if names might be the same person with different formatting
                if self._names_might_be_same_person(quote_name, dash_name):
                    validation["warnings"].append(f"Name format difference: Quote '{quote_name}' vs DASH '{dash_name}' (likely same person)")
                else:
                    validation["warnings"].append(f"Name mismatch: Quote '{quote_name}' vs DASH '{dash_name}'")
                # Note: No longer setting status to FAIL for name mismatches
        elif quote_name and not dash_name:
            # DASH name is missing - this is not a critical error, just a warning
            validation["warnings"].append("DASH name not available for comparison")
        elif not quote_name and dash_name:
            # Quote name is missing - this is not a critical error, just a warning
            validation["warnings"].append("Quote name not available for comparison")
        elif not quote_name and not dash_name:
            # Both names are missing - this is not a critical error, just a warning
            validation["warnings"].append("No names available for comparison")
        
        # License number comparison
        if quote_license and dash_license:
            if self._similar(quote_license, dash_license):
                validation["matches"].append(f"License number matches: Quote '{quote_license}' vs DASH '{dash_license}'")
            else:
                validation["critical_errors"].append(f"License number mismatch: Quote '{quote_license}' vs DASH '{dash_license}'")
                validation["status"] = "FAIL"
        
        # Date of birth comparison
        if quote_dob and dash_dob:
            if self._dates_match(quote_dob, dash_dob, "quote", "dash"):
                validation["matches"].append(f"Date of birth matches: Quote '{quote_dob}' vs DASH '{dash_dob}'")
            else:
                validation["critical_errors"].append(f"Date of birth mismatch: Quote '{quote_dob}' vs DASH '{dash_dob}'")
                validation["status"] = "FAIL"
        
        # Validate policies and claims
        policies_validation = self._validate_policies(dash, quote)
        claims_validation = self._validate_claims(dash, quote)
        
        # Combine results
        validation["matches"].extend(policies_validation["matches"])
        validation["warnings"].extend(policies_validation["warnings"])
        validation["critical_errors"].extend(policies_validation["critical_errors"])
        
        validation["matches"].extend(claims_validation["matches"])
        validation["warnings"].extend(claims_validation["warnings"])
        validation["critical_errors"].extend(claims_validation["critical_errors"])
        
        # Update status if there are critical errors
        if validation["critical_errors"]:
            validation["status"] = "FAIL"
        elif validation["warnings"]:
            validation["status"] = "WARNING"
        
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
        
        if not policies:
            validation["critical_errors"].append("No policies found in DASH")
            return validation
        
        # Business rule: Find first insurance policy ever held (not just active)
        # Sort by start_date to get the oldest policy
        sorted_policies = sorted(policies, key=lambda x: x.get("start_date", ""))
        first_policy = sorted_policies[0]
        first_policy_start = first_policy.get("start_date", "")
        
        validation["matches"].append(f"Found {len(policies)} total policies in DASH")
        validation["matches"].append(f"First policy ever held: {first_policy_start} ({first_policy.get('company', 'Unknown')})")
        
        # Business rule: Check for gaps between policy end and next policy start
        policy_gaps = dash.get("policy_gaps", [])
        if policy_gaps:
            for gap in policy_gaps:
                gap_days = gap.get("gap_days", 0)
                previous_end = gap.get("previous_policy_end", "")
                next_start = gap.get("next_policy_start", "")
                cancellation_reason = gap.get("cancellation_reason", "Unknown")
                
                validation["warnings"].append(
                    f"Policy gap detected: {gap_days} days between {previous_end} and {next_start}. "
                    f"Reason: {cancellation_reason}"
                )
        else:
            validation["matches"].append("No policy gaps detected")
        
        # Additional check: Current carrier matching (existing logic)
        active_policies = [p for p in policies if "Active" in p.get("status", "")]
        if active_policies:
            validation["matches"].append(f"Found {len(active_policies)} active policy(ies)")
            
            quote_current_carrier = ""
            if quote.get("drivers"):
                quote_current_carrier = quote["drivers"][0].get("current_carrier", "")
            
            if quote_current_carrier:
                for policy in active_policies:
                    if self._similar(quote_current_carrier, policy.get("company", "")):
                        validation["matches"].append("Current carrier matches DASH policy")
                        break
        
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
        
        # If no claims in DASH, this is a pass condition
        if not dash_claims:
            validation["matches"].append("No claims found in DASH - this is acceptable")
            return validation
        
        validation["matches"].append(f"Found {len(dash_claims)} claim(s) in DASH")
        
        for dash_claim in dash_claims:
            at_fault_percentage = dash_claim.get("at_fault_percentage", 0)
            claim_number = dash_claim.get("claim_number", "Unknown")
            dash_claim_date = dash_claim.get("date", "")
            first_party_driver = dash_claim.get("first_party_driver", "")
            
            # NEW BUSINESS RULE: Check if claim is less than 9 years old
            claim_age_check = self._is_claim_less_than_9_years_old(dash_claim_date)
            if not claim_age_check["is_recent"]:
                validation["matches"].append(
                    f"Claim {claim_number} skipped (age: {claim_age_check['age_years']:.1f} years, older than 9 years)"
                )
                continue
            
            # NEW BUSINESS RULE: For claims less than 9 years old, validate ALL claims (including 0% at-fault)
            # Enhanced driver matching - check if the claim involves the policyholder
            driver_matches = False
            
            # Check if first_party_driver equals policyholder name (exact match)
            if first_party_driver and policyholder_name:
                if (self._similar(first_party_driver, policyholder_name) or 
                    self._names_contain_same_parts(first_party_driver, policyholder_name)):
                    driver_matches = True
            
            # If no first_party_driver info, assume it's the policyholder (common case)
            if not first_party_driver:
                driver_matches = True
            
            if driver_matches:
                # Check if claim is declared in quote
                claim_found_in_quote = False
                
                # Look for matching claim date in quote claims
                if dash_claim_date:
                    for quote_claim in quote_claims:
                        quote_claim_date = quote_claim.get("date", "")
                        if self._dates_match(dash_claim_date, quote_claim_date, "dash", "quote"):
                            claim_found_in_quote = True
                            validation["matches"].append(
                                f"Claim {claim_number} validated (at-fault: {at_fault_percentage}%, date: {dash_claim_date}, age: {claim_age_check['age_years']:.1f} years)"
                            )
                            break
                
                if not claim_found_in_quote:
                    # CRITICAL ERROR: Claim not declared in quote (regardless of at-fault percentage)
                    validation["critical_errors"].append(
                        f"Claim {claim_number} ({at_fault_percentage}% at-fault) on {dash_claim_date} "
                        f"involving {first_party_driver or policyholder_name} not declared in quote "
                        f"(claim age: {claim_age_check['age_years']:.1f} years)"
                    )
            else:
                validation["warnings"].append(
                    f"Claim {claim_number} - different driver ({first_party_driver} vs {policyholder_name})"
                )
        
        return validation

    def _names_might_be_same_person(self, name1, name2):
        """
        More lenient name matching that can detect when names are likely the same person
        despite different formatting, order, or slight variations
        Examples:
        - "Navid Tahmasebian" vs "TAHMASEBIAN-MALAYERI,NAVID" -> True
        - "John Smith" vs "SMITH,JOHN" -> True
        - "Mary Jane Wilson" vs "WILSON,MARY JANE" -> True
        - "Matthew Silva" vs "SILVA,MATTHEW" -> True
        """
        if not name1 or not name2:
            return False
        
        # Clean and normalize names
        name1_clean = name1.replace(",", " ").replace("  ", " ").replace("-", " ").strip()
        name2_clean = name2.replace(",", " ").replace("  ", " ").replace("-", " ").strip()
        
        # Convert to lowercase for comparison
        name1_lower = name1_clean.lower()
        name2_lower = name2_clean.lower()
        
        # Split names into parts
        parts1 = name1_lower.split()
        parts2 = name2_lower.split()
        
        # If either name has less than 2 parts, use exact matching
        if len(parts1) < 2 or len(parts2) < 2:
            return self._names_contain_same_parts(name1, name2)
        
        # Check for exact match after normalization
        if self._names_contain_same_parts(name1, name2):
            return True
        
        # More lenient matching: check if most name parts are present in both names
        # This handles cases like "Navid Tahmasebian" vs "TAHMASEBIAN-MALAYERI,NAVID"
        
        # Create sets of name parts
        set1 = set(parts1)
        set2 = set(parts2)
        
        # Find common parts
        common_parts = set1.intersection(set2)
        
        # Calculate match percentage
        total_unique_parts = len(set1.union(set2))
        if total_unique_parts == 0:
            return False
        
        match_percentage = len(common_parts) / total_unique_parts
        
        # If we have at least 60% match, consider them the same person
        if match_percentage >= 0.6:
            return True
        
        # Additional check: look for partial matches (e.g., "tahmasebian" in "tahmasebian-malayeri")
        for part1 in parts1:
            for part2 in parts2:
                # Check if one part contains the other (for compound names)
                if len(part1) > 3 and len(part2) > 3:  # Only for substantial parts
                    if part1 in part2 or part2 in part1:
                        # If we have at least one substantial match, check overall similarity
                        remaining_parts1 = [p for p in parts1 if p != part1]
                        remaining_parts2 = [p for p in parts2 if p != part2]
                        
                        # If remaining parts also match well, consider it a match
                        if len(remaining_parts1) > 0 and len(remaining_parts2) > 0:
                            remaining_set1 = set(remaining_parts1)
                            remaining_set2 = set(remaining_parts2)
                            remaining_common = remaining_set1.intersection(remaining_set2)
                            remaining_total = len(remaining_set1.union(remaining_set2))
                            
                            if remaining_total > 0 and len(remaining_common) / remaining_total >= 0.5:
                                return True
        
        return False

    def _validate_name_order(self, quote_name, mvr_name):
        """
        Validate that quote name follows correct order: FIRSTNAME LASTNAME or FIRSTNAME MIDDLENAME LASTNAME
        MVR format is: LASTNAME,FIRSTNAME,MIDDLENAME
        
        Returns: (is_valid_order, error_message)
        """
        if not quote_name or not mvr_name:
            return True, None  # Skip validation if either name is missing
        
        # Parse MVR name (LASTNAME,FIRSTNAME,MIDDLENAME)
        mvr_parts = [part.strip() for part in mvr_name.split(',')]
        
        if len(mvr_parts) < 2:
            return True, None  # Can't validate if MVR name doesn't have at least 2 parts
        
        mvr_lastname = mvr_parts[0]
        mvr_firstname = mvr_parts[1]
        mvr_middlename = mvr_parts[2] if len(mvr_parts) > 2 else ""
        
        # Parse quote name (should be FIRSTNAME LASTNAME or FIRSTNAME MIDDLENAME LASTNAME)
        quote_parts = quote_name.split()
        
        if len(quote_parts) < 2:
            return False, f"Quote name '{quote_name}' must have at least first and last name"
        
        # Check if quote name starts with first name
        quote_firstname = quote_parts[0]
        if quote_firstname.lower() != mvr_firstname.lower():
            return False, f"Quote name '{quote_name}' should start with first name '{mvr_firstname}' from MVR"
        
        # Check if quote name ends with last name
        quote_lastname = quote_parts[-1]
        if quote_lastname.lower() != mvr_lastname.lower():
            return False, f"Quote name '{quote_name}' should end with last name '{mvr_lastname}' from MVR"
        
        # If MVR has middle name, check if quote has it in the right position
        if mvr_middlename and len(quote_parts) > 2:
            quote_middlename = quote_parts[1]  # Middle name should be second
            if quote_middlename.lower() != mvr_middlename.lower():
                return False, f"Quote name '{quote_name}' should have middle name '{mvr_middlename}' in correct position"
        
        return True, None

    def _names_contain_same_parts(self, name1, name2):
        """
        Check if two names contain the same parts (handles different name orders and formats)
        Examples:
        - "nadeen thomas" vs "thomas nadeen" -> True
        - "nadeen thomas" vs "thomas,nadeen" -> True
        - "john smith" vs "smith,john" -> True
        - "mary jane wilson" vs "wilson,mary jane" -> True
        - "matthew f silva" vs "silva,matthew,freitas" -> True (F vs FREITAS, different order)
        """
        if not name1 or not name2:
            return False
        
        # Clean and normalize names
        name1_clean = name1.replace(",", " ").replace("  ", " ").strip()
        name2_clean = name2.replace(",", " ").replace("  ", " ").strip()
        
        # Split names into parts and normalize
        parts1 = name1_clean.lower().split()
        parts2 = name2_clean.lower().split()
        
        # Convert to sets for comparison
        set1 = set(parts1)
        set2 = set(parts2)
        
        # Check if they contain the same parts (exact match)
        if set1 == set2:
            return True
        
        # Handle middle initial vs full middle name with different orders
        # Create sets that consider initials as matches
        set1_with_initials = set()
        set2_with_initials = set()
        
        # Add all parts to sets, including initial variations
        for part in parts1:
            set1_with_initials.add(part)
            if len(part) == 1:  # If it's an initial, add possible full names
                for other_part in parts2:
                    if other_part.startswith(part):
                        set1_with_initials.add(other_part)
        
        for part in parts2:
            set2_with_initials.add(part)
            if len(part) == 1:  # If it's an initial, add possible full names
                for other_part in parts1:
                    if other_part.startswith(part):
                        set2_with_initials.add(other_part)
        
        # Check if sets match with initial handling
        if set1_with_initials == set2_with_initials:
            return True
        
        # More flexible matching: check if most parts match
        matches = 0
        total_parts = max(len(parts1), len(parts2))
        
        # Check each part in parts1 against parts2
        for part1 in parts1:
            for part2 in parts2:
                if part1 == part2 or (len(part1) == 1 and part2.startswith(part1)) or (len(part2) == 1 and part1.startswith(part2)):
                    matches += 1
                    break
        
        # If we have enough matches (allowing for one mismatch), consider it a match
        if matches >= min(len(parts1), len(parts2)) and matches >= total_parts - 1:
            return True
        
        return False

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

    def _is_claim_less_than_9_years_old(self, claim_date_str):
        """
        Check if a claim is less than 9 years old from the current date
        
        Args:
            claim_date_str (str): Claim date string in various formats
            
        Returns:
            dict: {
                "is_recent": bool,      # True if claim is less than 9 years old
                "age_years": float,     # Age of claim in years
                "claim_date": datetime, # Parsed claim date
                "current_date": datetime # Current date used for comparison
            }
        """
        if not claim_date_str:
            return {
                "is_recent": False,
                "age_years": float('inf'),
                "claim_date": None,
                "current_date": datetime.now()
            }
        
        try:
            # Parse the claim date using existing utility method
            claim_date = self._parse_date(claim_date_str, "dash")
            if not claim_date:
                return {
                    "is_recent": False,
                    "age_years": float('inf'),
                    "claim_date": None,
                    "current_date": datetime.now()
                }
            
            # Get current date
            current_date = datetime.now()
            
            # Calculate age in years
            age_delta = current_date - claim_date
            age_years = age_delta.days / 365.25  # Account for leap years
            
            # Check if claim is less than 9 years old
            is_recent = age_years < 9.0
            
            return {
                "is_recent": is_recent,
                "age_years": age_years,
                "claim_date": claim_date,
                "current_date": current_date
            }
            
        except Exception as e:
            print(f"DEBUG: Error calculating claim age for '{claim_date_str}': {e}")
            return {
                "is_recent": False,
                "age_years": float('inf'),
                "claim_date": None,
                "current_date": datetime.now()
            }

    def _similar(self, a, b):
        """Check if two strings are similar using fuzzy matching"""
        if not a or not b:
            return False
        
        # Normalize strings for comparison
        a_normalized = a.lower().strip()
        b_normalized = b.lower().strip()
        
        # Exact match after normalization
        if a_normalized == b_normalized:
            return True
        
        # Check if names are the same but in different order
        if self._names_contain_same_parts(a_normalized, b_normalized):
            return True
        
        # Use fuzzy matching for other cases
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, a_normalized, b_normalized).ratio()
        return similarity >= 0.8

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
        driver_training_validation = driver_report.get("driver_training_validation", {})
        report_age_validation = driver_report.get("report_age_validation", {})
        
        # Add critical errors from individual sections
        total_critical_errors += len(mvr_validation.get("critical_errors", []))
        total_critical_errors += len(dash_validation.get("critical_errors", []))
        total_critical_errors += len(license_validation.get("critical_errors", []))
        total_critical_errors += len(convictions_validation.get("critical_errors", []))
        total_critical_errors += len(driver_training_validation.get("critical_errors", []))
        total_critical_errors += len(report_age_validation.get("critical_errors", []))
        
        # Add warnings from individual sections
        total_warnings += len(mvr_validation.get("warnings", []))
        total_warnings += len(dash_validation.get("warnings", []))
        total_warnings += len(license_validation.get("warnings", []))
        total_warnings += len(convictions_validation.get("warnings", []))
        total_warnings += len(driver_training_validation.get("warnings", []))
        total_warnings += len(report_age_validation.get("warnings", []))
        
        # Add matches from individual sections
        total_matches += len(mvr_validation.get("matches", []))
        total_matches += len(dash_validation.get("matches", []))
        total_matches += len(license_validation.get("matches", []))
        total_matches += len(convictions_validation.get("matches", []))
        total_matches += len(driver_training_validation.get("matches", []))
        total_matches += len(report_age_validation.get("matches", []))
        
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
def validate_quote(data, no_dash_report=False):
    """
    Legacy validation function - now uses the new ValidationEngine
    """
    engine = ValidationEngine()
    return engine.validate_quote(data, no_dash_report=no_dash_report)
        