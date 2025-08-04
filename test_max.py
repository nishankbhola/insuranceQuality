#!/usr/bin/env python3
"""
Comprehensive Test Suite for ROCKET Validation Engine
Tests all aspects of the validation engine with detailed debugging and error reporting
"""

import json
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from validator.compare_engine import ValidationEngine

class TestSuite:
    def __init__(self):
        self.engine = ValidationEngine()
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name, passed, details=""):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
        
        self.test_results.append({
            "test_name": test_name,
            "passed": passed,
            "details": details
        })
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    def test_date_normalization(self):
        """Test date normalization logic"""
        print("🧪 Testing Date Normalization Logic")
        print("=" * 50)
        
        test_cases = [
            # (input_date, expected_normalized, description)
            ("07/10/1973", "1973-07-10", "MM/DD/YYYY format"),
            ("10/07/1973", "1973-10-07", "DD/MM/YYYY format"),
            ("01/22/1975", "1975-01-22", "MM/DD/YYYY format"),
            ("22/01/1975", "1975-01-22", "DD/MM/YYYY format"),
            ("10/23/2003", "2003-10-23", "MM/DD/YYYY format"),
            ("23/10/2003", "2003-10-23", "DD/MM/YYYY format"),
            ("2023-12-25", "2023-12-25", "ISO format"),
            ("", None, "Empty string"),
            (None, None, "None value"),
        ]
        
        all_passed = True
        for input_date, expected, description in test_cases:
            try:
                result = self.engine._normalize_date(input_date)
                passed = result == expected
                details = f"Input: {input_date}, Expected: {expected}, Got: {result}"
                self.log_test(f"Date normalization - {description}", passed, details)
                if not passed:
                    all_passed = False
            except Exception as e:
                self.log_test(f"Date normalization - {description}", False, f"Exception: {e}")
                all_passed = False
        
        return all_passed
    
    def test_date_matching(self):
        """Test date matching logic"""
        print("🧪 Testing Date Matching Logic")
        print("=" * 50)
        
        test_cases = [
            # (date1, date2, should_match, description)
            ("07/10/1973", "10/07/1973", False, "Different dates (July 10 vs October 7)"),
            ("01/22/1975", "22/01/1975", True, "Same date in different formats"),
            ("10/23/2003", "23/10/2003", True, "Same date in different formats"),
            ("07/10/1973", "07/11/1973", False, "Different dates"),
            ("", "10/07/1973", False, "Empty vs valid date"),
            (None, "10/07/1973", False, "None vs valid date"),
        ]
        
        all_passed = True
        for date1, date2, should_match, description in test_cases:
            try:
                result = self.engine._dates_match(date1, date2)
                passed = result == should_match
                details = f"Date1: {date1}, Date2: {date2}, Expected: {should_match}, Got: {result}"
                self.log_test(f"Date matching - {description}", passed, details)
                if not passed:
                    all_passed = False
            except Exception as e:
                self.log_test(f"Date matching - {description}", False, f"Exception: {e}")
                all_passed = False
        
        return all_passed
    
    def test_mvr_validation(self):
        """Test MVR validation with real data"""
        print("🧪 Testing MVR Validation with Real Data")
        print("=" * 50)
        
        # Test data with known date formats
        test_data = {
            "extracted": {
                "quotes": [{
                    "quote_effective_date": "06/08/2025",
                    "applicant": {"first_name": "Paulo", "last_name": "Melo"},
                    "drivers": [{
                        "full_name": "Paulo Melo",
                        "birth_date": "07/10/1973",  # MM/DD/YYYY format (July 10, 1973)
                        "gender": "Male",
                        "licence_number": "M24156198730710",
                        "licence_class": "G",
                        "date_g": "05/07/1990",
                        "date_g2": None,
                        "date_g1": None
                    }],
                    "vehicles": [{
                        "garaging_location": "MISSISSAUGA L4Z3T3"
                    }]
                }],
                "mvrs": [{
                    "licence_number": "M24156198730710",
                    "name": "MELO, PAULO",
                    "birth_date": "10/07/1973",  # DD/MM/YYYY format (October 7, 1973)
                    "gender": "M",
                    "address": "55 HORNER AVE SUITE\nMISSISSAUGA ON L4Z3T3",
                    "convictions": [],
                    "expiry_date": "10/07/2028",
                    "issue_date": "10/07/1990"
                }],
                "dashes": [{
                    "dln": "M24156198730710",
                    "date_of_birth": "10/07/1973",  # DD/MM/YYYY format (October 7, 1973)
                    "gender": "Male"
                }]
            }
        }
        
        try:
            result = self.engine.validate_quote(test_data)
            
            # Check if validation completed
            if not result or 'drivers' not in result:
                self.log_test("MVR validation - Basic structure", False, "No drivers in result")
                return False
            
            driver_result = result['drivers'][0]
            
            # Check for birth date mismatch
            has_birth_date_error = any("Date of birth mismatch" in error for error in driver_result.get('critical_errors', []))
            
            if has_birth_date_error:
                self.log_test("MVR validation - Birth date matching", True, 
                            f"Birth date mismatch correctly detected (different dates)")
                return True
            else:
                self.log_test("MVR validation - Birth date matching", False, 
                            f"Birth date mismatch not detected when it should be")
                return False
                
        except Exception as e:
            self.log_test("MVR validation - Exception handling", False, f"Exception: {e}")
            return False
    
    def test_multiple_drivers(self):
        """Test multiple drivers validation"""
        print("🧪 Testing Multiple Drivers Validation")
        print("=" * 50)
        
        test_data = {
            "extracted": {
                "quotes": [{
                    "quote_effective_date": "06/08/2025",
                    "applicant": {"first_name": "Family", "last_name": "Test"},
                    "drivers": [
                        {
                            "full_name": "Paulo Melo",
                            "birth_date": "07/10/1973",  # MM/DD/YYYY
                            "gender": "Male",
                            "licence_number": "M24156198730710",
                            "licence_class": "G",
                            "date_g": "05/07/1990"
                        },
                        {
                            "full_name": "Dora Melo",
                            "birth_date": "01/22/1975",  # MM/DD/YYYY
                            "gender": "Female",
                            "licence_number": "M24151750755122",
                            "licence_class": "G",
                            "date_g": "01/09/2002"
                        }
                    ],
                    "vehicles": [{"garaging_location": "MISSISSAUGA L4Z3T3"}]
                }],
                "mvrs": [
                    {
                        "licence_number": "M24156198730710",
                        "name": "MELO, PAULO",
                        "birth_date": "10/07/1973",  # DD/MM/YYYY
                        "gender": "M",
                        "address": "55 HORNER AVE SUITE\nMISSISSAUGA ON L4Z3T3",
                        "convictions": []
                    },
                    {
                        "licence_number": "M24151750755122",
                        "name": "MELO, DORA",
                        "birth_date": "22/01/1975",  # DD/MM/YYYY
                        "gender": "F",
                        "address": "55 HORNER AVE SUITE\nMISSISSAUGA ON L4Z3T3",
                        "convictions": []
                    }
                ],
                "dashes": [
                    {
                        "dln": "M24156198730710",
                        "date_of_birth": "10/07/1973",
                        "gender": "Male"
                    },
                    {
                        "dln": "M24151750755122",
                        "date_of_birth": "22/01/1975",
                        "gender": "Female"
                    }
                ]
            }
        }
        
        try:
            result = self.engine.validate_quote(test_data)
            
            if not result or 'drivers' not in result:
                self.log_test("Multiple drivers - Basic structure", False, "No drivers in result")
                return False
            
            if len(result['drivers']) != 2:
                self.log_test("Multiple drivers - Count", False, 
                            f"Expected 2 drivers, got {len(result['drivers'])}")
                return False
            
            # Check each driver
            all_passed = True
            for i, driver in enumerate(result['drivers']):
                has_birth_date_error = any("Date of birth mismatch" in error for error in driver.get('critical_errors', []))
                driver_name = driver.get('driver_name', 'Unknown')
                
                if driver_name == "Paulo Melo":
                    # Paulo should have birth date mismatch (different dates)
                    if has_birth_date_error:
                        self.log_test(f"Multiple drivers - Driver {i+1} birth date", True,
                                    f"Birth date mismatch correctly detected for {driver_name}")
                    else:
                        self.log_test(f"Multiple drivers - Driver {i+1} birth date", False,
                                    f"Birth date mismatch not detected for {driver_name}")
                        all_passed = False
                else:
                    # Dora should match (same date in different formats)
                    if has_birth_date_error:
                        self.log_test(f"Multiple drivers - Driver {i+1} birth date", False,
                                    f"Birth date mismatch for {driver_name}")
                        all_passed = False
                    else:
                        self.log_test(f"Multiple drivers - Driver {i+1} birth date", True,
                                    f"Birth date matched for {driver_name}")
            
            return all_passed
            
        except Exception as e:
            self.log_test("Multiple drivers - Exception handling", False, f"Exception: {e}")
            return False
    
    def test_conviction_validation(self):
        """Test conviction validation"""
        print("🧪 Testing Conviction Validation")
        print("=" * 50)
        
        test_data = {
            "extracted": {
                "quotes": [{
                    "quote_effective_date": "06/08/2025",
                    "applicant": {"first_name": "Test", "last_name": "Driver"},
                    "drivers": [{
                        "full_name": "Test Driver",
                        "birth_date": "01/01/1990",
                        "gender": "Male",
                        "licence_number": "TEST123456",
                        "licence_class": "G"
                    }],
                    "vehicles": [{"garaging_location": "TORONTO ON"}]
                }],
                "mvrs": [{
                    "licence_number": "TEST123456",
                    "name": "DRIVER, TEST",
                    "birth_date": "01/01/1990",
                    "gender": "M",
                    "address": "TORONTO ON",
                    "convictions": []  # No convictions
                }],
                "dashes": []
            }
        }
        
        try:
            result = self.engine.validate_quote(test_data)
            
            if not result or 'drivers' not in result:
                self.log_test("Conviction validation - Basic structure", False, "No drivers in result")
                return False
            
            driver = result['drivers'][0]
            
            # Check that no false convictions are reported
            has_false_conviction = any("conviction" in error.lower() for error in driver.get('critical_errors', []))
            
            if has_false_conviction:
                self.log_test("Conviction validation - No false positives", False,
                            f"False conviction detected: {driver.get('critical_errors', [])}")
                return False
            else:
                self.log_test("Conviction validation - No false positives", True,
                            "No false convictions reported")
                return True
                
        except Exception as e:
            self.log_test("Conviction validation - Exception handling", False, f"Exception: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 ROCKET Validation Engine - Comprehensive Test Suite")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        tests = [
            ("Date Normalization", self.test_date_normalization),
            ("Date Matching", self.test_date_matching),
            ("MVR Validation", self.test_mvr_validation),
            ("Multiple Drivers", self.test_multiple_drivers),
            ("Conviction Validation", self.test_conviction_validation),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_test(test_name, False, f"Test crashed with exception: {e}")
        
        # Print summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests: {len(self.test_results)}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success rate: {(self.passed_tests / len(self.test_results) * 100):.1f}%")
        
        if self.failed_tests == 0:
            print("\n🎉 All tests passed! The validation engine is working correctly.")
            return True
        else:
            print(f"\n⚠️  {self.failed_tests} test(s) failed. Please review the issues above.")
            return False

def main():
    """Main test runner"""
    test_suite = TestSuite()
    success = test_suite.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 