#!/usr/bin/env python3
"""
Test script for enhanced conviction description matching
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from validator.compare_engine import ValidationEngine

def test_conviction_matching():
    """
    Test the enhanced conviction description matching
    """
    engine = ValidationEngine()
    
    print("🧪 Testing Enhanced Conviction Description Matching")
    print("=" * 60)
    
    # Test cases with different conviction descriptions
    test_cases = [
        {
            "name": "Handheld Device - Different Language",
            "desc1": "Prohibited Use of Hand-Held Device",
            "desc2": "SHALL NOT DRV HOLDING OR USING A HAND-HELD COM DEV",
            "expected": True
        },
        {
            "name": "Handheld Device - Similar Language",
            "desc1": "Using Hand-Held Device While Driving",
            "desc2": "SHALL NOT DRV HOLDING OR USING A HAND-HELD COM DEV",
            "expected": True
        },
        {
            "name": "Speeding - Different Language",
            "desc1": "Exceeding Speed Limit",
            "desc2": "SPEEDING - 20 KM/H OVER LIMIT",
            "expected": True
        },
        {
            "name": "Red Light - Different Language",
            "desc1": "Failure to Stop at Red Light",
            "desc2": "DISOBEY TRAFFIC SIGNAL",
            "expected": True
        },
        {
            "name": "Seatbelt - Different Language",
            "desc1": "No Seat Belt",
            "desc2": "FAILURE TO WEAR SEAT BELT",
            "expected": True
        },
        {
            "name": "DUI - Different Language",
            "desc1": "Driving Under the Influence",
            "desc2": "IMPAIRED DRIVING",
            "expected": True
        },
        {
            "name": "Unrelated Convictions",
            "desc1": "Prohibited Use of Hand-Held Device",
            "desc2": "FAILURE TO STOP AT STOP SIGN",
            "expected": False
        },
        {
            "name": "Empty Descriptions",
            "desc1": "",
            "desc2": "SHALL NOT DRV HOLDING OR USING A HAND-HELD COM DEV",
            "expected": False
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 50)
        print(f"Description 1: {test_case['desc1']}")
        print(f"Description 2: {test_case['desc2']}")
        print(f"Expected Match: {test_case['expected']}")
        
        # Test the enhanced matching
        result = engine._conviction_descriptions_match(test_case['desc1'], test_case['desc2'])
        print(f"Actual Match: {result}")
        
        if result == test_case['expected']:
            print("✅ PASS")
        else:
            print("❌ FAIL")
        
        # Show normalization results
        if test_case['desc1'] and test_case['desc2']:
            norm1 = engine._normalize_conviction_description(test_case['desc1'])
            norm2 = engine._normalize_conviction_description(test_case['desc2'])
            print(f"Normalized 1: {norm1}")
            print(f"Normalized 2: {norm2}")
            
            # Show fuzzy match score
            fuzzy_score = engine._similar(test_case['desc1'], test_case['desc2'])
            print(f"Fuzzy Match Score: {fuzzy_score:.2f}")
            
            # Show keyword match
            keyword_match = engine._conviction_keywords_match(test_case['desc1'], test_case['desc2'])
            print(f"Keyword Match: {keyword_match}")

def test_specific_example():
    """
    Test the specific example from the user
    """
    engine = ValidationEngine()
    
    print("\n🎯 Testing Specific User Example")
    print("=" * 40)
    
    quote_desc = "Prohibited Use of Hand-Held Device"
    mvr_desc = "SHALL NOT DRV HOLDING OR USING A HAND-HELD COM DEV"
    
    print(f"Quote Description: {quote_desc}")
    print(f"MVR Description: {mvr_desc}")
    
    # Test each matching method
    print("\n🔍 Testing Each Matching Method:")
    
    # 1. Original fuzzy matching
    fuzzy_match = engine._similar(quote_desc, mvr_desc)
    print(f"1. Fuzzy Match (0.6 threshold): {fuzzy_match}")
    
    # 2. Normalized descriptions
    norm1 = engine._normalize_conviction_description(quote_desc)
    norm2 = engine._normalize_conviction_description(mvr_desc)
    print(f"2. Normalized Descriptions:")
    print(f"   Quote: {norm1}")
    print(f"   MVR: {norm2}")
    
    # 3. Exact match on normalized
    exact_normalized = norm1 == norm2
    print(f"3. Exact Match (Normalized): {exact_normalized}")
    
    # 4. Fuzzy match on normalized
    fuzzy_normalized = engine._similar(norm1, norm2)
    print(f"4. Fuzzy Match (Normalized): {fuzzy_normalized}")
    
    # 5. Keyword matching
    keyword_match = engine._conviction_keywords_match(quote_desc, mvr_desc)
    print(f"5. Keyword Match: {keyword_match}")
    
    # 6. Final enhanced matching
    final_match = engine._conviction_descriptions_match(quote_desc, mvr_desc)
    print(f"6. Final Enhanced Match: {final_match}")
    
    if final_match:
        print("✅ SUCCESS: The enhanced matching correctly identifies these as the same conviction!")
    else:
        print("❌ FAILURE: The enhanced matching failed to identify these as the same conviction.")

if __name__ == "__main__":
    test_conviction_matching()
    test_specific_example()
    
    print("\n🎯 Summary:")
    print("• Enhanced conviction matching uses multiple strategies:")
    print("  1. Normalized description comparison")
    print("  2. Fuzzy matching on normalized descriptions")
    print("  3. Keyword-based matching for common conviction types")
    print("• This should handle the handheld device example correctly")
    print("• The system is extensible for other conviction types") 