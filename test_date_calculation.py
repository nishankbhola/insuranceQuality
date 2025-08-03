#!/usr/bin/env python3
"""
Test script to verify G1/G2/G date calculation logic
"""

import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from validator.compare_engine import ValidationEngine

def test_date_calculation():
    """
    Test the date calculation logic with specific examples
    """
    engine = ValidationEngine()
    
    print("🧪 Testing G1/G2/G Date Calculation Logic")
    print("=" * 50)
    
    # Test Case 1: MM/YYYY match (expiry and birthdate have same month/year)
    print("\n📋 Test Case 1: MM/YYYY Match")
    print("-" * 30)
    
    expiry_date = "07/09/2027"  # July 9, 2027
    birth_date = "07/09/1991"   # July 9, 1991 (same MM/YYYY as expiry)
    issue_date = "08/29/2008"   # August 29, 2008
    
    print(f"Expiry Date: {expiry_date}")
    print(f"Birth Date: {birth_date}")
    print(f"Issue Date: {issue_date}")
    print(f"MM/YYYY Match: (7, 2027) == (7, 1991) -> False (different years)")
    
    result = engine._calculate_license_dates(expiry_date, birth_date, issue_date)
    if result:
        g1_date, g2_date, g_date = result
        print(f"✅ G1 Date: {g1_date}")
        print(f"✅ G2 Date: {g2_date}")
        print(f"✅ G Date: {g_date}")
        
        # Since MM/YYYY don't actually match (different years), should use expiry_date - 5 years
        expected_g1 = "2022-07-09"  # expiry_date - 5 years
        expected_g2 = "2023-07-09"  # g1_date + 1 year
        expected_g = "2024-07-09"   # g1_date + 2 years
        
        print(f"\nExpected G1: {expected_g1} (expiry_date - 5 years)")
        print(f"Expected G2: {expected_g2} (g1_date + 1 year)")
        print(f"Expected G: {expected_g} (g1_date + 2 years)")
        
        if g1_date == expected_g1 and g2_date == expected_g2 and g_date == expected_g:
            print("✅ All dates match expected values!")
        else:
            print("❌ Date calculation mismatch!")
    else:
        print("❌ Failed to calculate dates")
    
    # Test Case 2: MM/YYYY don't match (different months)
    print("\n📋 Test Case 2: MM/YYYY Don't Match (Different Months)")
    print("-" * 30)
    
    expiry_date = "12/15/2025"  # December 15, 2025
    birth_date = "05/15/1995"   # May 15, 1995 (different MM/YYYY from expiry)
    issue_date = "05/15/2015"   # May 15, 2015
    
    print(f"Expiry Date: {expiry_date}")
    print(f"Birth Date: {birth_date}")
    print(f"Issue Date: {issue_date}")
    print(f"MM/YYYY Match: (12, 2025) == (5, 1995) -> False (different months and years)")
    
    result = engine._calculate_license_dates(expiry_date, birth_date, issue_date)
    if result:
        g1_date, g2_date, g_date = result
        print(f"✅ G1 Date: {g1_date}")
        print(f"✅ G2 Date: {g2_date}")
        print(f"✅ G Date: {g_date}")
        
        # Should be based on expiry_date - 5 years
        expected_g1 = "2020-12-15"  # expiry_date - 5 years
        expected_g2 = "2021-12-15"  # g1_date + 1 year
        expected_g = "2022-12-15"   # g1_date + 2 years
        
        print(f"\nExpected G1: {expected_g1} (expiry_date - 5 years)")
        print(f"Expected G2: {expected_g2} (g1_date + 1 year)")
        print(f"Expected G: {expected_g} (g1_date + 2 years)")
        
        if g1_date == expected_g1 and g2_date == expected_g2 and g_date == expected_g:
            print("✅ All dates match expected values!")
        else:
            print("❌ Date calculation mismatch!")
    else:
        print("❌ Failed to calculate dates")
    
    # Test Case 3: True MM/YYYY match (same month and year)
    print("\n📋 Test Case 3: True MM/YYYY Match")
    print("-" * 30)
    
    expiry_date = "07/09/2027"  # July 9, 2027
    birth_date = "07/15/2027"   # July 15, 2027 (same MM/YYYY as expiry)
    issue_date = "08/29/2008"   # August 29, 2008
    
    print(f"Expiry Date: {expiry_date}")
    print(f"Birth Date: {birth_date}")
    print(f"Issue Date: {issue_date}")
    print(f"MM/YYYY Match: (7, 2027) == (7, 2027) -> True (same month and year)")
    
    result = engine._calculate_license_dates(expiry_date, birth_date, issue_date)
    if result:
        g1_date, g2_date, g_date = result
        print(f"✅ G1 Date: {g1_date}")
        print(f"✅ G2 Date: {g2_date}")
        print(f"✅ G Date: {g_date}")
        
        # Should be based on issue_date
        expected_g1 = "2008-08-29"  # issue_date
        expected_g2 = "2009-08-29"  # issue_date + 1 year
        expected_g = "2010-08-29"   # issue_date + 2 years
        
        print(f"\nExpected G1: {expected_g1} (issue_date)")
        print(f"Expected G2: {expected_g2} (issue_date + 1 year)")
        print(f"Expected G: {expected_g} (issue_date + 2 years)")
        
        if g1_date == expected_g1 and g2_date == expected_g2 and g_date == expected_g:
            print("✅ All dates match expected values!")
        else:
            print("❌ Date calculation mismatch!")
    else:
        print("❌ Failed to calculate dates")

def test_parse_date():
    """
    Test the date parsing function
    """
    engine = ValidationEngine()
    
    print("\n🧪 Testing Date Parsing")
    print("=" * 30)
    
    test_dates = [
        "07/09/1991",
        "2027-07-09",
        "08/29/2008",
        "12/15/2025"
    ]
    
    for date_str in test_dates:
        parsed = engine._parse_date(date_str)
        if parsed:
            print(f"✅ '{date_str}' -> {parsed.strftime('%Y-%m-%d')}")
        else:
            print(f"❌ '{date_str}' -> Failed to parse")

def test_mm_yyyy_logic():
    """
    Test the MM/YYYY comparison logic specifically
    """
    engine = ValidationEngine()
    
    print("\n🧪 Testing MM/YYYY Comparison Logic")
    print("=" * 40)
    
    test_cases = [
        {
            "expiry": "07/09/2027",
            "birth": "07/15/2027",
            "description": "Same month and year (should match)"
        },
        {
            "expiry": "07/09/2027", 
            "birth": "07/09/1991",
            "description": "Same month, different year (should not match)"
        },
        {
            "expiry": "12/15/2025",
            "birth": "05/15/1995", 
            "description": "Different month and year (should not match)"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {case['description']}")
        print("-" * 40)
        
        expiry = engine._parse_date(case['expiry'])
        birth = engine._parse_date(case['birth'])
        
        if expiry and birth:
            expiry_mm_yyyy = (expiry.month, expiry.year)
            birth_mm_yyyy = (birth.month, birth.year)
            
            print(f"Expiry MM/YYYY: {expiry_mm_yyyy}")
            print(f"Birth MM/YYYY: {birth_mm_yyyy}")
            print(f"Match: {expiry_mm_yyyy == birth_mm_yyyy}")
            
            if expiry_mm_yyyy == birth_mm_yyyy:
                print("✅ Should use issue_date as base")
            else:
                print("✅ Should use expiry_date - 5 years as base")

if __name__ == "__main__":
    test_date_calculation()
    test_parse_date()
    test_mm_yyyy_logic()
    
    print("\n🎯 Summary:")
    print("• MM/YYYY match means same month AND same year")
    print("• If MM/YYYY match: use issue_date as base")
    print("• If MM/YYYY don't match: use expiry_date - 5 years as base")
    print("• G2 license class skips G date validation")
    print("• Date parsing handles multiple formats") 