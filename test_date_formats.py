#!/usr/bin/env python3
"""
Comprehensive test script for date format handling in the validation engine.
Tests the application with different date formats from MVR, DASH, and Quote sources.

Date formats by source:
- MVR: dd/mm/yyyy
- Dash: yyyy/mm/dd  
- Quote: mm/dd/yyyy
"""

import sys
import os
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from validator.compare_engine import ValidationEngine

def test_date_parsing():
    """Test date parsing with different formats"""
    print("=== Testing Date Parsing ===")
    
    engine = ValidationEngine()
    
    # Test cases with different date formats
    test_cases = [
        # MVR format (dd/mm/yyyy)
        ("04/08/1965", "mvr", "1965-08-04"),
        ("10/07/1973", "mvr", "1973-07-10"),
        ("23/10/2003", "mvr", "2003-10-23"),
        
        # DASH format (yyyy/mm/dd)
        ("1965-08-04", "dash", "1965-08-04"),
        ("1973-07-10", "dash", "1973-07-10"),
        ("2003-10-23", "dash", "2003-10-23"),
        
        # Quote format (mm/dd/yyyy)
        ("08/04/1965", "quote", "1965-08-04"),
        ("07/10/1973", "quote", "1973-07-10"),
        ("10/23/2003", "quote", "2003-10-23"),
    ]
    
    for date_str, source_type, expected in test_cases:
        # Test _parse_date
        parsed = engine._parse_date(date_str, source_type)
        parsed_str = parsed.strftime("%Y-%m-%d") if parsed else None
        
        # Test _normalize_date
        normalized = engine._normalize_date(date_str, source_type)
        
        print(f"Date: {date_str} (source: {source_type})")
        print(f"  Parsed: {parsed_str}")
        print(f"  Normalized: {normalized}")
        print(f"  Expected: {expected}")
        print(f"  ✓ Pass" if parsed_str == expected and normalized == expected else "  ✗ Fail")
        print()

def test_date_comparison():
    """Test date comparison between different formats"""
    print("=== Testing Date Comparison ===")
    
    engine = ValidationEngine()
    
    # Test cases comparing dates in different formats
    test_cases = [
        # Same date in different formats
        ("04/08/1965", "mvr", "08/04/1965", "quote", True),  # Same date
        ("10/07/1973", "mvr", "07/10/1973", "quote", True),  # Same date
        ("23/10/2003", "mvr", "10/23/2003", "quote", True),  # Same date
        
        # Different dates
        ("04/08/1965", "mvr", "08/05/1965", "quote", False),  # Different date
        ("10/07/1973", "mvr", "07/11/1973", "quote", False),  # Different date
        
        # DASH format comparisons
        ("1965-08-04", "dash", "08/04/1965", "quote", True),  # Same date
        ("1973-07-10", "dash", "07/10/1973", "quote", True),  # Same date
    ]
    
    for date1, source1, date2, source2, expected in test_cases:
        result = engine._dates_match(date1, date2, source1, source2)
        print(f"Comparing: {date1} ({source1}) vs {date2} ({source2})")
        print(f"  Expected: {expected}")
        print(f"  Result: {result}")
        print(f"  ✓ Pass" if result == expected else "  ✗ Fail")
        print()

def test_date_before_comparison():
    """Test date before comparison"""
    print("=== Testing Date Before Comparison ===")
    
    engine = ValidationEngine()
    
    # Test cases for date before comparison
    test_cases = [
        # Quote format dates (mm/dd/yyyy)
        ("01/01/2020", "quote", "01/01/2021", "quote", True),   # 2020 before 2021
        ("01/01/2021", "quote", "01/01/2020", "quote", False),  # 2021 not before 2020
        ("01/01/2020", "quote", "01/01/2020", "quote", False),  # Same date
        
        # MVR format dates (dd/mm/yyyy)
        ("01/01/2020", "mvr", "01/01/2021", "mvr", True),      # 2020 before 2021
        ("01/01/2021", "mvr", "01/01/2020", "mvr", False),      # 2021 not before 2020
        
        # Mixed formats
        ("01/01/2020", "quote", "01/01/2021", "mvr", True),     # 2020 before 2021
        ("01/01/2021", "quote", "01/01/2020", "mvr", False),    # 2021 not before 2020
    ]
    
    for date1, source1, date2, source2, expected in test_cases:
        result = engine._is_date_before(date1, date2, source1, source2)
        print(f"Comparing: {date1} ({source1}) before {date2} ({source2})")
        print(f"  Expected: {expected}")
        print(f"  Result: {result}")
        print(f"  ✓ Pass" if result == expected else "  ✗ Fail")
        print()

def test_mock_data_validation():
    """Test validation with mock data using different date formats"""
    print("=== Testing Mock Data Validation ===")
    
    engine = ValidationEngine()
    
    # Create mock data with different date formats
    mock_data = {
        "extracted": {
            "quotes": [{
                "drivers": [{
                    "full_name": "MELO, PAULO",
                    "licence_number": "M24156198730710",
                    "birth_date": "07/10/1973",  # Quote format: mm/dd/yyyy
                    "gender": "Male",
                    "date_g1": "07/10/1990",     # Quote format: mm/dd/yyyy
                    "date_g2": "07/10/1991",     # Quote format: mm/dd/yyyy
                    "date_g": "07/10/1992",      # Quote format: mm/dd/yyyy
                }],
                "vehicles": [{
                    "garaging_location": "MISSISSAUGA ON L4Z3T3"
                }]
            }],
            "mvrs": [{
                "licence_number": "M24156198730710",
                "name": "MELO, PAULO",
                "birth_date": "10/07/1973",      # MVR format: dd/mm/yyyy
                "gender": "M",
                "address": "55 HORNER AVE SUITE\nMISSISSAUGA ON L4Z3T3",
                "convictions": [],
                "expiry_date": "10/07/2028",     # MVR format: dd/mm/yyyy
                "issue_date": "10/07/1990"       # MVR format: dd/mm/yyyy
            }],
            "dashes": [{
                "dln": "M24156198730710",
                "name": "PAULO MELO",
                "date_of_birth": "1973-07-10",   # DASH format: yyyy-mm-dd
                "gender": "Male",
                "address": "55 HORNER AVE SUITE MISSISSAUGA ON L4Z3T3",
                "policies": [{
                    "policy_number": "1",
                    "start_date": "2024-05-03",  # DASH format: yyyy-mm-dd
                    "end_date": "2025-05-03",    # DASH format: yyyy-mm-dd
                    "company": "The Wawanesa Mutual Insurance Company",
                    "status": "Active"
                }],
                "claims": []
            }]
        }
    }
    
    # Run validation
    result = engine.validate_quote(mock_data)
    
    print("Validation Result:")
    print(json.dumps(result, indent=2))
    
    # Check specific validations
    if result["drivers"]:
        driver = result["drivers"][0]
        print(f"\nDriver: {driver['driver_name']}")
        print(f"Status: {driver['validation_status']}")
        
        # Check MVR validation
        mvr_val = driver["mvr_validation"]
        print(f"MVR Status: {mvr_val['status']}")
        print(f"MVR Matches: {len(mvr_val['matches'])}")
        print(f"MVR Errors: {len(mvr_val['critical_errors'])}")
        print(f"MVR Warnings: {len(mvr_val['warnings'])}")
        
        # Check DASH validation
        dash_val = driver["dash_validation"]
        print(f"DASH Status: {dash_val['status']}")
        print(f"DASH Matches: {len(dash_val['matches'])}")
        print(f"DASH Errors: {len(dash_val['critical_errors'])}")
        print(f"DASH Warnings: {len(dash_val['warnings'])}")
        
        # Check license progression validation
        lic_val = driver["license_progression_validation"]
        print(f"License Progression Status: {lic_val['status']}")
        print(f"License Progression Matches: {len(lic_val['matches'])}")
        print(f"License Progression Errors: {len(lic_val['critical_errors'])}")
        print(f"License Progression Warnings: {len(lic_val['warnings'])}")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("=== Testing Edge Cases ===")
    
    engine = ValidationEngine()
    
    # Test invalid dates
    invalid_dates = [
        ("", "quote"),
        (None, "quote"),
        ("invalid", "quote"),
        ("13/01/2020", "quote"),  # Invalid month
        ("01/32/2020", "quote"),  # Invalid day
        ("02/30/2020", "quote"),  # Invalid day for February
    ]
    
    for date_str, source_type in invalid_dates:
        parsed = engine._parse_date(date_str, source_type)
        normalized = engine._normalize_date(date_str, source_type)
        print(f"Invalid date: '{date_str}' (source: {source_type})")
        print(f"  Parsed: {parsed}")
        print(f"  Normalized: {normalized}")
        print(f"  ✓ Pass" if parsed is None and normalized is None else "  ✗ Fail")
        print()
    
    # Test date comparison with invalid dates
    print("Testing date comparison with invalid dates:")
    result = engine._dates_match("invalid", "01/01/2020", "quote", "quote")
    print(f"Invalid vs Valid: {result} (should be False)")
    
    result = engine._dates_match("01/01/2020", "invalid", "quote", "quote")
    print(f"Valid vs Invalid: {result} (should be False)")

def main():
    """Run all tests"""
    print("Testing Date Format Handling in Validation Engine")
    print("=" * 50)
    print()
    
    test_date_parsing()
    test_date_comparison()
    test_date_before_comparison()
    test_mock_data_validation()
    test_edge_cases()
    
    print("All tests completed!")

if __name__ == "__main__":
    main() 