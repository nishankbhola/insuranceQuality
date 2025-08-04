#!/usr/bin/env python3
"""
Debug script to test license progression validation and identify critical errors
"""

import sys
import os
import json

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from validator.compare_engine import ValidationEngine

def test_license_progression_scenarios():
    """Test different license progression scenarios"""
    
    engine = ValidationEngine()
    
    # Test scenarios that might cause critical errors
    test_scenarios = [
        {
            "name": "Future G1 date",
            "driver": {
                "date_g1": "07/10/2030",  # Future date
                "date_g2": "07/10/2031",
                "date_g": "07/10/2032",
                "licence_class": "G"
            }
        },
        {
            "name": "Invalid progression (G1 after G2)",
            "driver": {
                "date_g1": "07/10/1992",  # G1 after G2
                "date_g2": "07/10/1991",
                "date_g": "07/10/1993",
                "licence_class": "G"
            }
        },
        {
            "name": "Invalid progression (G2 after G)",
            "driver": {
                "date_g1": "07/10/1990",
                "date_g2": "07/10/1992",  # G2 after G
                "date_g": "07/10/1991",
                "licence_class": "G"
            }
        },
        {
            "name": "G2 license with G date",
            "driver": {
                "date_g1": "07/10/1990",
                "date_g2": "07/10/1991",
                "date_g": "07/10/1992",  # Should not have G date for G2 license
                "licence_class": "G2"
            }
        },
        {
            "name": "G license without G date",
            "driver": {
                "date_g1": "07/10/1990",
                "date_g2": "07/10/1991",
                "date_g": None,  # Missing G date for G license
                "licence_class": "G"
            }
        },
        {
            "name": "Very old dates",
            "driver": {
                "date_g1": "07/10/1940",  # Very old date
                "date_g2": "07/10/1941",
                "date_g": "07/10/1942",
                "licence_class": "G"
            }
        },
        {
            "name": "Valid progression",
            "driver": {
                "date_g1": "07/10/1990",
                "date_g2": "07/10/1991",
                "date_g": "07/10/1992",
                "licence_class": "G"
            }
        }
    ]
    
    print("Testing License Progression Validation Scenarios")
    print("=" * 60)
    
    for scenario in test_scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        print("-" * 40)
        
        # Create mock MVR data
        mvr_data = {
            "expiry_date": "10/07/2028",
            "birth_date": "10/07/1973",
            "issue_date": "10/07/1990"
        }
        
        # Run validation
        result = engine._validate_license_progression_enhanced(scenario['driver'], mvr_data)
        
        print(f"Status: {result['status']}")
        print(f"Critical Errors: {len(result['critical_errors'])}")
        print(f"Warnings: {len(result['warnings'])}")
        print(f"Matches: {len(result['matches'])}")
        
        if result['critical_errors']:
            print("  🟥 Critical Errors:")
            for error in result['critical_errors']:
                print(f"    • {error}")
        
        if result['warnings']:
            print("  🟧 Warnings:")
            for warning in result['warnings']:
                print(f"    • {warning}")
        
        if result['matches']:
            print("  ✅ Matches:")
            for match in result['matches']:
                print(f"    • {match}")

def test_with_real_data():
    """Test with the actual data structure"""
    
    engine = ValidationEngine()
    
    # Create test data similar to what might be causing issues
    test_data = {
        "extracted": {
            "quotes": [{
                "drivers": [{
                    "full_name": "TEST DRIVER",
                    "licence_number": "M123456789",
                    "date_g1": "07/10/2030",  # Future date - should cause critical error
                    "date_g2": "07/10/2031",   # Future date - should cause critical error
                    "date_g": "07/10/2032",    # Future date - should cause critical error
                    "licence_class": "G"
                }],
                "vehicles": [{
                    "garaging_location": "TEST LOCATION"
                }]
            }],
            "mvrs": [{
                "licence_number": "M123456789",
                "name": "TEST, DRIVER",
                "birth_date": "10/07/1973",
                "gender": "M",
                "address": "TEST ADDRESS",
                "convictions": [],
                "expiry_date": "10/07/2028",
                "issue_date": "10/07/1990"
            }],
            "dashes": []
        }
    }
    
    print("\n🧪 Testing with Real Data Structure")
    print("=" * 50)
    
    result = engine.validate_quote(test_data)
    
    if result["drivers"]:
        driver = result["drivers"][0]
        print(f"Driver: {driver['driver_name']}")
        print(f"Status: {driver['validation_status']}")
        
        # Check license progression validation
        lic_val = driver["license_progression_validation"]
        print(f"License Progression Status: {lic_val['status']}")
        print(f"License Progression Errors: {len(lic_val['critical_errors'])}")
        print(f"License Progression Warnings: {len(lic_val['warnings'])}")
        
        if lic_val['critical_errors']:
            print("  🟥 Critical Errors:")
            for error in lic_val['critical_errors']:
                print(f"    • {error}")
        
        if lic_val['warnings']:
            print("  🟧 Warnings:")
            for warning in lic_val['warnings']:
                print(f"    • {warning}")

if __name__ == "__main__":
    test_license_progression_scenarios()
    test_with_real_data() 