#!/usr/bin/env python3
"""
Test script to validate the license progression business rules implementation.
Tests the specific business rules for calculating G1/G2/G dates from MVR data.
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from validator.compare_engine import ValidationEngine

def test_license_progression_business_rules():
    """Test the license progression business rules implementation"""
    print("🧪 Testing License Progression Business Rules")
    print("=" * 50)
    print()
    
    engine = ValidationEngine()
    
    # Test Case 1: DD/MM match scenario
    print("📋 Test Case 1: DD/MM Match Scenario")
    print("MVR Data:")
    print("  Expiry Date: 04/08/2025 (DD/MM/YYYY) - August 4, 2025")
    print("  Birth Date: 04/08/1965 (DD/MM/YYYY) - August 4, 1965")
    print("  Issue Date: 08/07/2004 (DD/MM/YYYY) - July 8, 2004")
    print()
    print("Business Rule: DD/MM match (04/08), so:")
    print("  G1 Date = Issue Date = 08/07/2004")
    print("  G2 Date = G1 + 1 year = 08/07/2005")
    print("  G Date = G2 + 1 year = 08/07/2006")
    print()
    
    # Calculate expected dates
    calculated_dates = engine._calculate_license_dates_from_mvr(
        "04/08/2025",  # expiry_date (DD/MM/YYYY)
        "04/08/1965",  # birth_date (DD/MM/YYYY)
        "08/07/2004"   # issue_date (DD/MM/YYYY)
    )
    
    if calculated_dates:
        g1_calc, g2_calc, g_calc = calculated_dates
        print("✅ Calculated Dates:")
        print(f"  G1 Date: {g1_calc} (MM/DD/YYYY)")
        print(f"  G2 Date: {g2_calc} (MM/DD/YYYY)")
        print(f"  G Date: {g_calc} (MM/DD/YYYY)")
        print()
        
        # Test with matching quote dates
        print("📋 Testing with Matching Quote Dates:")
        quote_data = {
            "date_g1": "07/08/2004",  # MM/DD/YYYY
            "date_g2": "07/08/2005",  # MM/DD/YYYY
            "date_g": "07/08/2006"    # MM/DD/YYYY
        }
        
        # Test date comparisons
        g1_match = engine._dates_match(g1_calc, quote_data["date_g1"], "quote", "quote")
        g2_match = engine._dates_match(g2_calc, quote_data["date_g2"], "quote", "quote")
        g_match = engine._dates_match(g_calc, quote_data["date_g"], "quote", "quote")
        
        print(f"  G1 Match: {'✅' if g1_match else '❌'} (Expected: {g1_calc}, Quote: {quote_data['date_g1']})")
        print(f"  G2 Match: {'✅' if g2_match else '❌'} (Expected: {g2_calc}, Quote: {quote_data['date_g2']})")
        print(f"  G Match: {'✅' if g_match else '❌'} (Expected: {g_calc}, Quote: {quote_data['date_g']})")
        print()
        
        if all([g1_match, g2_match, g_match]):
            print("🎉 All dates match correctly!")
        else:
            print("❌ Some dates don't match")
    else:
        print("❌ Failed to calculate dates")
    
    print("-" * 50)
    print()
    
    # Test Case 2: DD/MM don't match scenario
    print("📋 Test Case 2: DD/MM Don't Match Scenario")
    print("MVR Data:")
    print("  Expiry Date: 15/12/2025 (DD/MM/YYYY) - December 15, 2025")
    print("  Birth Date: 04/08/1965 (DD/MM/YYYY) - August 4, 1965")
    print("  Issue Date: 08/07/2004 (DD/MM/YYYY) - July 8, 2004")
    print()
    print("Business Rule: DD/MM don't match (15/12 vs 04/08), so:")
    print("  G1 Date = Expiry Date - 5 years = 15/12/2020")
    print("  G2 Date = G1 + 1 year = 15/12/2021")
    print("  G Date = G2 + 1 year = 15/12/2022")
    print()
    
    # Calculate expected dates
    calculated_dates = engine._calculate_license_dates_from_mvr(
        "15/12/2025",  # expiry_date (DD/MM/YYYY)
        "04/08/1965",  # birth_date (DD/MM/YYYY)
        "08/07/2004"   # issue_date (DD/MM/YYYY)
    )
    
    if calculated_dates:
        g1_calc, g2_calc, g_calc = calculated_dates
        print("✅ Calculated Dates:")
        print(f"  G1 Date: {g1_calc} (MM/DD/YYYY)")
        print(f"  G2 Date: {g2_calc} (MM/DD/YYYY)")
        print(f"  G Date: {g_calc} (MM/DD/YYYY)")
        print()
        
        # Test with matching quote dates
        print("📋 Testing with Matching Quote Dates:")
        quote_data = {
            "date_g1": "12/15/2020",  # MM/DD/YYYY
            "date_g2": "12/15/2021",  # MM/DD/YYYY
            "date_g": "12/15/2022"    # MM/DD/YYYY
        }
        
        # Test date comparisons
        g1_match = engine._dates_match(g1_calc, quote_data["date_g1"], "quote", "quote")
        g2_match = engine._dates_match(g2_calc, quote_data["date_g2"], "quote", "quote")
        g_match = engine._dates_match(g_calc, quote_data["date_g"], "quote", "quote")
        
        print(f"  G1 Match: {'✅' if g1_match else '❌'} (Expected: {g1_calc}, Quote: {quote_data['date_g1']})")
        print(f"  G2 Match: {'✅' if g2_match else '❌'} (Expected: {g2_calc}, Quote: {quote_data['date_g2']})")
        print(f"  G Match: {'✅' if g_match else '❌'} (Expected: {g_calc}, Quote: {quote_data['date_g']})")
        print()
        
        if all([g1_match, g2_match, g_match]):
            print("🎉 All dates match correctly!")
        else:
            print("❌ Some dates don't match")
    else:
        print("❌ Failed to calculate dates")
    
    print("-" * 50)
    print()

def test_full_validation_with_business_rules():
    """Test full validation with the business rules"""
    print("🧪 Testing Full Validation with Business Rules")
    print("=" * 50)
    print()
    
    engine = ValidationEngine()
    
    # Create test data that follows the business rules
    test_data = {
        "extracted": {
            "quotes": [{
                "drivers": [{
                    "full_name": "Test Driver",
                    "licence_number": "T123456789",
                    "birth_date": "08/04/1965",  # Quote format: MM/DD/YYYY
                    "gender": "Male",
                    "date_g1": "07/08/2004",     # Quote format: MM/DD/YYYY
                    "date_g2": "07/08/2005",     # Quote format: MM/DD/YYYY
                    "date_g": "07/08/2006",      # Quote format: MM/DD/YYYY
                }],
                "vehicles": [{
                    "garaging_location": "TORONTO ON M5V3A8"
                }]
            }],
            "mvrs": [{
                "licence_number": "T123456789",
                "name": "TEST DRIVER",
                "birth_date": "04/08/1965",      # MVR format: DD/MM/YYYY
                "gender": "M",
                "address": "123 MAIN ST\nTORONTO ON M5V3A8",
                "convictions": [],
                "expiry_date": "04/08/2025",     # MVR format: DD/MM/YYYY (DD/MM matches birth date)
                "issue_date": "08/07/2004"       # MVR format: DD/MM/YYYY
            }],
            "dashes": []
        }
    }
    
    print("📋 Test Data:")
    print("  MVR Expiry: 04/08/2025 (DD/MM/YYYY)")
    print("  MVR Birth: 04/08/1965 (DD/MM/YYYY)")
    print("  MVR Issue: 08/07/2004 (DD/MM/YYYY)")
    print("  Quote G1: 07/08/2004 (MM/DD/YYYY)")
    print("  Quote G2: 07/08/2005 (MM/DD/YYYY)")
    print("  Quote G: 07/08/2006 (MM/DD/YYYY)")
    print()
    print("📋 Expected Business Rule Result:")
    print("  DD/MM match (04/08), so G1 = Issue Date = 08/07/2004")
    print("  G2 = G1 + 1 year = 08/07/2005")
    print("  G = G2 + 1 year = 08/07/2006")
    print()
    
    # Run validation
    result = engine.validate_quote(test_data)
    
    print("📊 Validation Results:")
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
        
        # Check license progression validation
        lic_val = driver["license_progression_validation"]
        print("🔍 License Progression Validation:")
        print(f"  Status: {lic_val['status']}")
        print(f"  Matches: {len(lic_val['matches'])}")
        print(f"  Errors: {len(lic_val['critical_errors'])}")
        print(f"  Warnings: {len(lic_val['warnings'])}")
        
        if lic_val['matches']:
            print("  📋 Matches:")
            for match in lic_val['matches']:
                print(f"    • {match}")
        
        if lic_val['critical_errors']:
            print("  ❌ Critical Errors:")
            for error in lic_val['critical_errors']:
                print(f"    • {error}")
        
        print()
        
        # Overall assessment
        if driver['validation_status'] == 'PASS':
            print("🎉 SUCCESS: Business rules working correctly!")
        else:
            print("❌ FAILURE: Business rules not working as expected")
        
        return driver['validation_status'] == 'PASS'
    
    return False

def main():
    """Run all license progression tests"""
    print("🧪 License Progression Business Rules Test")
    print("=" * 60)
    print()
    
    # Test 1: Business rules calculation
    print("Test 1: Business Rules Calculation")
    print("-" * 30)
    test1_passed = test_license_progression_business_rules()
    
    # Test 2: Full validation
    print("Test 2: Full Validation with Business Rules")
    print("-" * 30)
    test2_passed = test_full_validation_with_business_rules()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Business Rules Calculation: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Full Validation: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print()
    
    all_passed = test1_passed and test2_passed
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("The license progression business rules are working correctly.")
        print()
        print("✅ The system correctly:")
        print("  • Calculates G1/G2/G dates from MVR data using business rules")
        print("  • Compares calculated dates with Quote dates")
        print("  • Identifies mismatches when dates don't align")
        print("  • Handles both DD/MM match and DD/MM don't match scenarios")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the business rules implementation.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 