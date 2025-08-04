#!/usr/bin/env python3
"""
Test script to verify that the application can handle multiple MVRs and multiple drivers
without the AttributeError that was occurring before.
"""

import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from validator.compare_engine import ValidationEngine

def test_multiple_mvrs():
    """Test the validation engine with multiple MVRs and drivers"""
    
    # Create test data with multiple MVRs and drivers
    test_data = {
        "extracted": {
            "quotes": [
                {
                    "drivers": [
                        {
                            "full_name": "John Doe",
                            "licence_number": "A123456789",
                            "birth_date": "01/15/1990",
                            "gender": "Male"
                        },
                        {
                            "full_name": "Jane Smith", 
                            "licence_number": "B987654321",
                            "birth_date": "05/20/1985",
                            "gender": "Female"
                        }
                    ],
                    "vehicles": [
                        {
                            "garaging_location": "TORONTO ON"
                        }
                    ]
                }
            ],
            "mvrs": [
                {
                    "licence_number": "A123456789",
                    "name": "DOE, JOHN",
                    "birth_date": "01/15/1990",
                    "gender": "M",
                    "address": "123 MAIN ST\nTORONTO ON M6N1T3"
                },
                {
                    "licence_number": "B987654321", 
                    "name": "SMITH, JANE",
                    "birth_date": "05/20/1985",
                    "gender": "F",
                    "address": "456 OAK AVE\nTORONTO ON M6N1T3"
                },
                {
                    # This MVR has None values to test the fix
                    "licence_number": None,
                    "name": None,
                    "birth_date": None,
                    "gender": None,
                    "address": None
                }
            ],
            "dashes": [
                {
                    "dln": "A123456789",
                    "date_of_birth": "01/15/1990",
                    "gender": "Male"
                },
                {
                    "dln": "B987654321",
                    "date_of_birth": "05/20/1985", 
                    "gender": "Female"
                }
            ]
        }
    }
    
    print("Testing validation engine with multiple MVRs and drivers...")
    
    try:
        # Create validation engine
        engine = ValidationEngine()
        
        # Run validation
        result = engine.validate_quote(test_data)
        
        print("✅ Validation completed successfully!")
        print(f"Total drivers: {result['summary']['total_drivers']}")
        print(f"Validated drivers: {result['summary']['validated_drivers']}")
        print(f"Issues found: {result['summary']['issues_found']}")
        
        # Print driver results
        for i, driver in enumerate(result['drivers']):
            print(f"\nDriver {i+1}: {driver['driver_name']}")
            print(f"  Status: {driver['validation_status']}")
            print(f"  Critical errors: {len(driver['critical_errors'])}")
            print(f"  Warnings: {len(driver['warnings'])}")
            print(f"  Matches: {len(driver['matches'])}")
            
            if driver['critical_errors']:
                print("  Critical errors:")
                for error in driver['critical_errors']:
                    print(f"    - {error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_null_handling():
    """Test that the engine properly handles None values"""
    
    print("\nTesting null value handling...")
    
    test_data = {
        "extracted": {
            "quotes": [
                {
                    "drivers": [
                        {
                            "full_name": "Test Driver",
                            "licence_number": "C111111111",
                            "birth_date": "01/01/1990",
                            "gender": "Male"
                        }
                    ],
                    "vehicles": []
                }
            ],
            "mvrs": [
                {
                    # MVR with None values
                    "licence_number": None,
                    "name": None,
                    "birth_date": None,
                    "gender": None,
                    "address": None
                }
            ],
            "dashes": []
        }
    }
    
    try:
        engine = ValidationEngine()
        result = engine.validate_quote(test_data)
        
        print("✅ Null value handling test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Null value handling test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Multiple MVRs and Drivers Support")
    print("=" * 50)
    
    success1 = test_multiple_mvrs()
    success2 = test_null_handling()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The application should now handle multiple MVRs and drivers correctly.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1) 