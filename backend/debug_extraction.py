#!/usr/bin/env python3
"""
Debug script to test PDF extraction patterns
"""

import re

# Sample text from the PDF
sample_text = "1 Nancy Freitas F7330-57777-85612 1978 6 12 F S Matthew F Silva S4403-52930-21023 2002 10 23 M S"

print("Testing driver extraction pattern...")
print(f"Sample text: {sample_text}")

# Test the pattern
pattern = r"(\d+)\s+([A-Za-z\s]+)\s+([A-Z]\d{4}-\d{5}-\d{5})\s+(\d{4})\s+(\d{1,2})\s+(\d{1,2})\s+([MF])\s+([SM])"

matches = re.findall(pattern, sample_text)
print(f"Found {len(matches)} matches:")
for i, match in enumerate(matches):
    print(f"Match {i+1}:")
    print(f"  Driver #: {match[0]}")
    print(f"  Name: {match[1].strip()}")
    print(f"  License: {match[2]}")
    print(f"  Birth Year: {match[3]}")
    print(f"  Birth Month: {match[4]}")
    print(f"  Birth Day: {match[5]}")
    print(f"  Gender: {match[6]}")
    print(f"  Marital: {match[7]}")

# Test individual parts
print("\nTesting individual parts:")
name_pattern = r"([A-Za-z\s]+)\s+([A-Z]\d{4}-\d{5}-\d{5})"
name_matches = re.findall(name_pattern, sample_text)
print(f"Name matches: {name_matches}")

# Test with the actual PDF text
with open('application_extract.json', 'r', encoding='utf-8') as f:
    import json
    data = json.load(f)
    pdf_text = data['pdf_text']
    
    # Find the driver section
    driver_section = re.search(r"(\d+)\s+([A-Za-z\s]+)\s+([A-Z]\d{4}-\d{5}-\d{5})\s+(\d{4})\s+(\d{1,2})\s+(\d{1,2})\s+([MF])\s+([SM])", pdf_text)
    if driver_section:
        print(f"\nFound driver section: {driver_section.group(0)}")
        print(f"Driver name: {driver_section.group(2).strip()}")
        
        # Look for more drivers after this one
        remaining_text = pdf_text[driver_section.end():]
        next_driver = re.search(r"(\d+)\s+([A-Za-z\s]+)\s+([A-Z]\d{4}-\d{5}-\d{5})\s+(\d{4})\s+(\d{1,2})\s+(\d{1,2})\s+([MF])\s+([SM])", remaining_text)
        if next_driver:
            print(f"Found second driver: {next_driver.group(0)}")
            print(f"Second driver name: {next_driver.group(2).strip()}")
        else:
            print("No second driver found in remaining text")
            
            # Look for Matthew Silva specifically
            matthew_match = re.search(r"Matthew F Silva", remaining_text)
            if matthew_match:
                print(f"Found 'Matthew F Silva' at position {matthew_match.start()}")
                # Show context around Matthew Silva
                start = max(0, matthew_match.start() - 50)
                end = min(len(remaining_text), matthew_match.end() + 50)
                print(f"Context: {remaining_text[start:end]}")
            else:
                print("'Matthew F Silva' not found in remaining text") 