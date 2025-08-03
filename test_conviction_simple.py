#!/usr/bin/env python3
"""
Simple test script for enhanced conviction description matching
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from validator.compare_engine import ValidationEngine

def test_specific_example():
    """
    Test the specific example from the user
    """
    engine = ValidationEngine()
    
    print("Testing Specific User Example")
    print("=" * 40)
    
    quote_desc = "Prohibited Use of Hand-Held Device"
    mvr_desc = "SHALL NOT DRV HOLDING OR USING A HAND-HELD COM DEV"
    
    print(f"Quote Description: {quote_desc}")
    print(f"MVR Description: {mvr_desc}")
    
    # Test each matching method
    print("\nTesting Each Matching Method:")
    
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
        print("SUCCESS: The enhanced matching correctly identifies these as the same conviction!")
    else:
        print("FAILURE: The enhanced matching failed to identify these as the same conviction.")

def test_other_examples():
    """
    Test other conviction examples
    """
    engine = ValidationEngine()
    
    print("\nTesting Other Conviction Examples")
    print("=" * 40)
    
    test_cases = [
        ("Exceeding Speed Limit", "SPEEDING - 20 KM/H OVER LIMIT"),
        ("Failure to Stop at Red Light", "DISOBEY TRAFFIC SIGNAL"),
        ("No Seat Belt", "FAILURE TO WEAR SEAT BELT"),
        ("Driving Under the Influence", "IMPAIRED DRIVING"),
        ("Prohibited Use of Hand-Held Device", "FAILURE TO STOP AT STOP SIGN")  # Should not match
    ]
    
    for desc1, desc2 in test_cases:
        print(f"\nTesting: '{desc1}' vs '{desc2}'")
        result = engine._conviction_descriptions_match(desc1, desc2)
        print(f"Match: {result}")

if __name__ == "__main__":
    test_specific_example()
    test_other_examples()
    
    print("\nSummary:")
    print("- Enhanced conviction matching uses multiple strategies:")
    print("  1. Normalized description comparison")
    print("  2. Fuzzy matching on normalized descriptions")
    print("  3. Keyword-based matching for common conviction types")
    print("- This should handle the handheld device example correctly")
    print("- The system is extensible for other conviction types") 