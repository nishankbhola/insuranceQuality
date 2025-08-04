#!/usr/bin/env python3
"""
Test the validation engine with real quote and MVR data
"""

import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from validator.compare_engine import ValidationEngine

def test_real_data_validation():
    """Test the validation engine with real quote and MVR data"""
    
    # Create test data with the correct quote data that matches our MVR mock data
    quote_data = {
        "quote_effective_date": "06/08/2025",
        "quote_prepared_by": "Nishank Bhola",
        "applicant": {
            "first_name": "Paulo",
            "last_name": "Melo"
        },
        "drivers": [
            {
                "full_name": "Paulo Melo",
                "birth_date": "07/10/1973",  # MM/DD/YYYY format
                "single": "No",
                "marital_status": "Married",
                "male": "Yes",
                "gender": "Male",
                "insured": "Yes",
                "relationship_to_applicant": None,
                "driver_training": "No",
                "driver_training_date": None,
                "out_of_province_country_driver": "No",
                "licence_class": "G",
                "date_g": "05/07/1990",
                "date_g2": None,
                "date_g1": None,
                "licence_number": "M24156198730710",
                "licence_province": "ON",
                "occupation": None,
                "date_insured": "05/06/1992",
                "current_carrier": "",
                "date_with_company": "06/08/2020",
                "brokerage_insured": None,
                "owner_principal": "No",
                "applicant_lives_with_parents": "No",
                "student_away_at_school_km": "No",
                "retired": "No"
            },
            {
                "full_name": "Dora Melo",
                "birth_date": "01/22/1975",  # MM/DD/YYYY format
                "single": "No",
                "marital_status": "Married",
                "male": "No",
                "gender": "Female",
                "insured": "Yes",
                "relationship_to_applicant": None,
                "driver_training": "No",
                "driver_training_date": None,
                "out_of_province_country_driver": "No",
                "licence_class": "G",
                "date_g": "01/09/2002",
                "date_g2": "01/08/2001",
                "date_g1": "01/06/2000",
                "licence_number": "M24151750755122",
                "licence_province": "ON",
                "occupation": None,
                "date_insured": "02/08/2001",
                "current_carrier": "",
                "date_with_company": "06/08/2020",
                "brokerage_insured": None,
                "owner_principal": "No",
                "applicant_lives_with_parents": "No",
                "student_away_at_school_km": "No",
                "retired": "No"
            },
            {
                "full_name": "Emily Melo",
                "birth_date": "10/23/2003",  # MM/DD/YYYY format
                "single": "Yes",
                "marital_status": "Single",
                "male": "No",
                "gender": "Female",
                "insured": "Yes",
                "relationship_to_applicant": None,
                "driver_training": "No",
                "driver_training_date": None,
                "out_of_province_country_driver": "No",
                "licence_class": "G",
                "date_g": "05/10/2022",
                "date_g2": "05/03/2021",
                "date_g1": "11/15/2019",
                "licence_number": "M24152246036023",
                "licence_province": "ON",
                "occupation": None,
                "date_insured": "06/08/2020",
                "current_carrier": "",
                "date_with_company": "06/08/2020",
                "brokerage_insured": None,
                "owner_principal": "Yes",
                "applicant_lives_with_parents": "Yes",
                "student_away_at_school_km": "No",
                "retired": "No"
            }
        ],
        "vehicles": [
            {
                "vehicle_type": "Private Passenger",
                "vin": "1FTFW3L5XRFB60639",
                "body_style": "Gasoline\nFuel Type\nNo\nHybrid\nPleasure\nPrimary Use",
                "fuel_type": "Gasoline",
                "hybrid": "No",
                "primary_use": "Pleasure",
                "annual_km": 15000,
                "business_km": 10,
                "daily_km": 10,
                "garaging_location": "MISSISSAUGA L4Z3T3",
                "single_vehicle_mvd": "No",
                "leased": "No",
                "cylinders": 6,
                "anti_theft_device_type": None,
                "anti_theft_manufacturer": None,
                "anti_theft_engraving": None,
                "purchase_condition": "New",
                "purchase_date": "07/17/2024",
                "km_at_purchase": 74209,
                "list_price_new": None,
                "purchase_price": None,
                "winter_tires": "No",
                "parking_at_night": None
            }
        ],
        "convictions": [],
        "suspensions": [],
        "coverages": [],
        "address": "55 Horner Ave, Suite"
    }
    
    # Create test data with real quote and mock MVR data
    test_data = {
        "extracted": {
            "quotes": [quote_data],
            "mvrs": [
                {
                    "licence_number": "M24156198730710",  # Paulo's license
                    "name": "MELO, PAULO",
                    "birth_date": "10/07/1973",  # DD/MM/YYYY format (July 10, 1973)
                    "gender": "M",
                    "address": "55 HORNER AVE SUITE\nMISSISSAUGA ON L4Z3T3",
                    "convictions": [],
                    "expiry_date": "10/07/2028",  # DD/MM/YYYY format
                    "issue_date": "10/07/1990"  # DD/MM/YYYY format
                },
                {
                    "licence_number": "M24151750755122",  # Dora's license
                    "name": "MELO, DORA",
                    "birth_date": "22/01/1975",  # DD/MM/YYYY format (January 22, 1975)
                    "gender": "F",
                    "address": "55 HORNER AVE SUITE\nMISSISSAUGA ON L4Z3T3",
                    "convictions": [],
                    "expiry_date": "22/01/2028",  # DD/MM/YYYY format
                    "issue_date": "06/01/2000"  # DD/MM/YYYY format
                },
                {
                    "licence_number": "M24152246036023",  # Emily's license
                    "name": "MELO, EMILY",
                    "birth_date": "23/10/2003",  # DD/MM/YYYY format (October 23, 2003)
                    "gender": "F",
                    "address": "55 HORNER AVE SUITE\nMISSISSAUGA ON L4Z3T3",
                    "convictions": [],
                    "expiry_date": "23/10/2028",  # DD/MM/YYYY format
                    "issue_date": "15/11/2019"  # DD/MM/YYYY format
                }
            ],
            "dashes": [
                {
                    "dln": "M24156198730710",  # Paulo's license
                    "date_of_birth": "1973-07-10",  # DASH format: YYYY-MM-DD
                    "gender": "Male"
                },
                {
                    "dln": "M24151750755122",  # Dora's license
                    "date_of_birth": "1975-01-22",  # DASH format: YYYY-MM-DD
                    "gender": "Female"
                },
                {
                    "dln": "M24152246036023",  # Emily's license
                    "date_of_birth": "2003-10-23",  # DASH format: YYYY-MM-DD
                    "gender": "Female"
                }
            ]
        }
    }
    
    print("Testing validation engine with real quote and MVR data...")
    print("Date format test:")
    print("  Quote dates: MM/DD/YYYY format")
    print("  MVR dates: DD/MM/YYYY format") 
    print("  DASH dates: YYYY-MM-DD format")
    print()
    
    try:
        # Create validation engine
        engine = ValidationEngine()
        
        # Run validation
        result = engine.validate_quote(test_data)
        
        print("✅ Validation completed successfully!")
        print(f"Total drivers: {result['summary']['total_drivers']}")
        print(f"Validated drivers: {result['summary']['validated_drivers']}")
        print(f"Issues found: {result['summary']['issues_found']}")
        print(f"Critical errors: {result['summary']['critical_errors']}")
        print(f"Warnings: {result['summary']['warnings']}")
        print()
        
        # Print driver results
        for i, driver in enumerate(result['drivers']):
            print(f"Driver {i+1}: {driver['driver_name']}")
            print(f"  Status: {driver['validation_status']}")
            print(f"  License: {driver['driver_license']}")
            print(f"  Critical errors: {len(driver['critical_errors'])}")
            print(f"  Warnings: {len(driver['warnings'])}")
            print(f"  Matches: {len(driver['matches'])}")
            
            # Print MVR validation details
            mvr_validation = driver.get('mvr_validation', {})
            print(f"  MVR Status: {mvr_validation.get('status', 'UNKNOWN')}")
            
            # Print license progression validation details
            license_validation = driver.get('license_progression_validation', {})
            print(f"  License Progression Status: {license_validation.get('status', 'UNKNOWN')}")
            
            # Print DASH validation details
            dash_validation = driver.get('dash_validation', {})
            print(f"  DASH Status: {dash_validation.get('status', 'UNKNOWN')}")
            
            if driver['critical_errors']:
                print("  Critical errors:")
                for error in driver['critical_errors']:
                    print(f"    - {error}")
            
            if driver['warnings']:
                print("  Warnings:")
                for warning in driver['warnings']:
                    print(f"    - {warning}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Real Data Validation")
    print("=" * 50)
    
    success = test_real_data_validation()
    
    if success:
        print("🎉 Real data validation test passed!")
    else:
        print("❌ Real data validation test failed.")
        sys.exit(1) 