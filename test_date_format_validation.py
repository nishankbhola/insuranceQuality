#!/usr/bin/env python3
"""
Comprehensive test for date format validation in the comparison engine.
This test specifically validates that the engine correctly handles different date formats:
- MVR: dd/mm/yyyy
- DASH: yyyy-mm-dd  
- Quote: mm/dd/yyyy
"""

import sys
import os
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from validator.compare_engine import ValidationEngine

def test_date_format_validation():
    """Test date format validation with comprehensive test cases"""
    print("🧪 Testing Date Format Validation")
    print("=" * 50)
    print()
    
    engine = ValidationEngine()
    
    # Test data with different date formats
    test_data = {
        "extracted": {
            "quotes": [{
                "drivers": [{
                    "full_name": "John Doe",
                    "licence_number": "A123456789",
                    "birth_date": "05/15/1980",  # Quote format: MM/DD/YYYY
                    "gender": "Male",
                    "date_g1": "05/15/1998",     # Quote format: MM/DD/YYYY
                    "date_g2": "05/15/1999",     # Quote format: MM/DD/YYYY
                    "date_g": "05/15/2000",      # Quote format: MM/DD/YYYY
                }],
                "vehicles": [{
                    "garaging_location": "TORONTO ON M5V3A8"
                }]
            }],
            "mvrs": [{
                "licence_number": "A123456789",
                "name": "DOE, JOHN",
                "birth_date": "15/05/1980",      # MVR format: DD/MM/YYYY
                "gender": "M",
                "address": "123 MAIN ST\nTORONTO ON M5V3A8",
                "convictions": [],
                "expiry_date": "15/05/2025",     # MVR format: DD/MM/YYYY
                "issue_date": "15/05/1998"       # MVR format: DD/MM/YYYY
            }],
            "dashes": [{
                "dln": "A123456789",
                "name": "JOHN DOE",
                "date_of_birth": "1980-05-15",   # DASH format: YYYY-MM-DD
                "gender": "Male",
                "policies": [{
                    "policy_number": "POL123",
                    "start_date": "2024-01-01",  # DASH format: YYYY-MM-DD
                    "end_date": "2025-01-01",    # DASH format: YYYY-MM-DD
                    "company": "Test Insurance",
                    "status": "Active"
                }],
                "claims": []
            }]
        }
    }
    
    print("Test Case: Same date in different formats")
    print("  Quote birth_date: 05/15/1980 (MM/DD/YYYY)")
    print("  MVR birth_date: 15/05/1980 (DD/MM/YYYY)")
    print("  DASH birth_date: 1980-05-15 (YYYY-MM-DD)")
    print()
    
    # Run validation
    result = engine.validate_quote(test_data)
    
    print("Validation Results:")
    print(f"  Total drivers: {result['summary']['total_drivers']}")
    print(f"  Validated drivers: {result['summary']['validated_drivers']}")
    print(f"  Issues found: {result['summary']['issues_found']}")
    print(f"  Critical errors: {result['summary']['critical_errors']}")
    print(f"  Warnings: {result['summary']['warnings']}")
    print()
    
    if result["drivers"]:
        driver = result["drivers"][0]
        print(f"Driver: {driver['driver_name']}")
        print(f"Status: {driver['validation_status']}")
        print()
        
        # Check MVR validation
        mvr_val = driver["mvr_validation"]
        print("MVR Validation:")
        print(f"  Status: {mvr_val['status']}")
        print(f"  Matches: {len(mvr_val['matches'])}")
        print(f"  Errors: {len(mvr_val['critical_errors'])}")
        print(f"  Warnings: {len(mvr_val['warnings'])}")
        
        # Check if birth date matches
        birth_date_match = any("Date of birth matches" in match for match in mvr_val['matches'])
        print(f"  Birth date match: {'✓' if birth_date_match else '✗'}")
        print()
        
        # Check DASH validation
        dash_val = driver["dash_validation"]
        print("DASH Validation:")
        print(f"  Status: {dash_val['status']}")
        print(f"  Matches: {len(dash_val['matches'])}")
        print(f"  Errors: {len(dash_val['critical_errors'])}")
        print(f"  Warnings: {len(dash_val['warnings'])}")
        
        # Check if birth date matches
        birth_date_match = any("Date of birth matches" in match for match in dash_val['matches'])
        print(f"  Birth date match: {'✓' if birth_date_match else '✗'}")
        print()
        
        # Check license progression validation
        lic_val = driver["license_progression_validation"]
        print("License Progression Validation:")
        print(f"  Status: {lic_val['status']}")
        print(f"  Matches: {len(lic_val['matches'])}")
        print(f"  Errors: {len(lic_val['critical_errors'])}")
        print(f"  Warnings: {len(lic_val['warnings'])}")
        print()
        
        # Check for any critical errors
        if driver['critical_errors']:
            print("Critical Errors:")
            for error in driver['critical_errors']:
                print(f"  - {error}")
            print()
        
        # Check for any warnings
        if driver['warnings']:
            print("Warnings:")
            for warning in driver['warnings']:
                print(f"  - {warning}")
            print()
        
        # Overall assessment
        if driver['validation_status'] == 'PASS':
            print("✅ SUCCESS: All date formats handled correctly!")
        elif driver['validation_status'] == 'WARNING':
            print("⚠️  WARNING: Some issues found but dates handled correctly")
        else:
            print("❌ FAILURE: Date format handling issues detected")
        
        return driver['validation_status'] == 'PASS'
    
    return False

def test_date_comparison_functions():
    """Test individual date comparison functions"""
    print("\n🔍 Testing Individual Date Comparison Functions")
    print("=" * 50)
    
    engine = ValidationEngine()
    
    # Test cases for date comparison
    test_cases = [
        # Same date in different formats
        ("05/15/1980", "quote", "15/05/1980", "mvr", True, "Same date, different formats"),
        ("05/15/1980", "quote", "1980-05-15", "dash", True, "Same date, different formats"),
        ("15/05/1980", "mvr", "1980-05-15", "dash", True, "Same date, different formats"),
        
        # Different dates
        ("05/15/1980", "quote", "15/05/1981", "mvr", False, "Different years"),
        ("05/15/1980", "quote", "16/05/1980", "mvr", False, "Different days"),
        ("05/15/1980", "quote", "05/16/1980", "quote", False, "Different days"),
        
        # Edge cases
        ("", "quote", "15/05/1980", "mvr", False, "Empty date"),
        ("05/15/1980", "quote", "", "mvr", False, "Empty date"),
        ("invalid", "quote", "15/05/1980", "mvr", False, "Invalid date"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for date1, source1, date2, source2, expected, description in test_cases:
        result = engine._dates_match(date1, date2, source1, source2)
        status = "✓" if result == expected else "✗"
        print(f"{status} {description}")
        print(f"    {date1} ({source1}) vs {date2} ({source2})")
        print(f"    Expected: {expected}, Got: {result}")
        if result == expected:
            passed += 1
        print()
    
    print(f"Date comparison tests: {passed}/{total} passed")
    return passed == total

def test_date_parsing_functions():
    """Test individual date parsing functions"""
    print("\n🔍 Testing Individual Date Parsing Functions")
    print("=" * 50)
    
    engine = ValidationEngine()
    
    # Test cases for date parsing
    test_cases = [
        # Quote format (MM/DD/YYYY)
        ("05/15/1980", "quote", "1980-05-15", "Quote format"),
        ("12/31/1999", "quote", "1999-12-31", "Quote format"),
        ("01/01/2000", "quote", "2000-01-01", "Quote format"),
        
        # MVR format (DD/MM/YYYY)
        ("15/05/1980", "mvr", "1980-05-15", "MVR format"),
        ("31/12/1999", "mvr", "1999-12-31", "MVR format"),
        ("01/01/2000", "mvr", "2000-01-01", "MVR format"),
        
        # DASH format (YYYY-MM-DD)
        ("1980-05-15", "dash", "1980-05-15", "DASH format"),
        ("1999-12-31", "dash", "1999-12-31", "DASH format"),
        ("2000-01-01", "dash", "2000-01-01", "DASH format"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for date_str, source_type, expected, description in test_cases:
        # Test _parse_date
        parsed = engine._parse_date(date_str, source_type)
        parsed_str = parsed.strftime("%Y-%m-%d") if parsed else None
        
        # Test _normalize_date
        normalized = engine._normalize_date(date_str, source_type)
        
        success = parsed_str == expected and normalized == expected
        status = "✓" if success else "✗"
        print(f"{status} {description}")
        print(f"    Input: {date_str} ({source_type})")
        print(f"    Parsed: {parsed_str}")
        print(f"    Normalized: {normalized}")
        print(f"    Expected: {expected}")
        if success:
            passed += 1
        print()
    
    print(f"Date parsing tests: {passed}/{total} passed")
    return passed == total

def main():
    """Run all date format validation tests"""
    print("🧪 Comprehensive Date Format Validation Test")
    print("=" * 60)
    print()
    
    # Test 1: Full validation with different date formats
    print("Test 1: Full Validation with Different Date Formats")
    print("-" * 50)
    test1_passed = test_date_format_validation()
    
    # Test 2: Individual date comparison functions
    print("Test 2: Individual Date Comparison Functions")
    print("-" * 50)
    test2_passed = test_date_comparison_functions()
    
    # Test 3: Individual date parsing functions
    print("Test 3: Individual Date Parsing Functions")
    print("-" * 50)
    test3_passed = test_date_parsing_functions()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Test 1 (Full Validation): {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"Test 2 (Date Comparison): {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    print(f"Test 3 (Date Parsing): {'✓ PASSED' if test3_passed else '✗ FAILED'}")
    print()
    
    all_passed = test1_passed and test2_passed and test3_passed
    if all_passed:
        print("🎉 ALL TESTS PASSED! Date format handling is working correctly.")
        print()
        print("✅ The comparison engine correctly handles:")
        print("   - MVR dates in DD/MM/YYYY format")
        print("   - DASH dates in YYYY-MM-DD format")
        print("   - Quote dates in MM/DD/YYYY format")
        print()
        print("✅ Date comparisons work correctly across all formats")
        print("✅ The application will not fail due to date format mismatches")
    else:
        print("❌ SOME TESTS FAILED! Date format handling needs attention.")
        print()
        print("⚠️  Please check the failed tests above and fix the issues")
        print("⚠️  The application may fail when comparing dates across different formats")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 