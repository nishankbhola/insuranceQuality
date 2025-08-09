from validator.compare_engine import ValidationEngine
import json

# Load the data
with open('dash_result.json', 'r') as f:
    dash_data = json.load(f)

with open('quote_result.json', 'r') as f:
    quote_data = json.load(f)

# Run validation
engine = ValidationEngine()
result = engine.validate_quote({"quotes": [quote_data], "mvrs": [], "dashes": [dash_data]})

print("=== VALIDATION TEST RESULTS ===")
print(f"Driver name in quote: {quote_data['drivers'][0]['full_name'] if quote_data.get('drivers') else 'No drivers'}")
print(f"Applicant: {quote_data.get('applicant', 'No applicant')}")
print(f"Claims validation: {result.get('claims_validation', 'No claims validation')}")
print("Validation completed successfully!")
