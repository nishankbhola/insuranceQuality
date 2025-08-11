# Automobile Validation in Application QC

## Overview
The Application QC system includes comprehensive validation for automobile information. All 6 required automobile fields must be filled for each vehicle to pass validation.

## Required Automobile Fields

### 1. Purchase Date
- **Field**: `purchase_date`
- **Validation**: Must be present for all vehicles
- **Example**: "2020-02", "2020/02", "February 2020"
- **Fail Message**: "Purchase Date missing for: Vehicle X. Purchase Date is required for all vehicles."

### 2. Purchase Price
- **Field**: `purchase_price` or `list_price`
- **Validation**: Must be present for all vehicles
- **Example**: "15000.00", "$15,000.00", "15000"
- **Fail Message**: "Purchase Price missing for: Vehicle X. Purchase Price is required for all vehicles."

### 3. Purchase New or Used
- **Field**: `purchase_condition`
- **Validation**: Must be present for all vehicles
- **Example**: "New", "Used", "Certified Pre-Owned"
- **Fail Message**: "Purchase New or Used missing for: Vehicle X. Purchase condition is required for all vehicles."

### 4. Owned Or Leased
- **Field**: `owned` and/or `leased` (boolean)
- **Validation**: At least one must be specified (True/False)
- **Example**: `"owned": true, "leased": false`
- **Fail Message**: "Owned Or Leased missing for: Vehicle X. Ownership status is required for all vehicles."

### 5. Estimated Annual Driving Distance
- **Field**: `annual_km` or `estimated_annual_driving_distance`
- **Validation**: Must be present for all vehicles
- **Example**: "6000", "6,000 km", "6000km"
- **Fail Message**: "Annual driving distance missing for: Vehicle X. Annual driving distance is required for all vehicles."

### 6. Type of Fuel Used
- **Field**: `fuel_type` or `type_of_fuel`
- **Validation**: Must be present for all vehicles
- **Example**: "Gas", "Electric", "Hybrid", "Diesel"
- **Fail Message**: "Fuel type missing for: Vehicle X. Fuel type is required for all vehicles."

## Data Structure Example

```json
{
  "vehicles": [
    {
      "year": "2020",
      "make": "HONDA",
      "model": "CIVIC",
      "vin": "2HGFB2F50CH020785",
      "purchase_date": "2020-02",
      "purchase_price": "15000.00",
      "purchase_condition": "Used",
      "owned": true,
      "leased": false,
      "annual_km": "6000",
      "fuel_type": "Gas"
    }
  ]
}
```

## Validation Results

### PASS Scenario
When all 6 fields are properly filled:
```
✅ Purchase Date is filled for all vehicles: PASS
✅ Purchase Price is filled for all vehicles: PASS
✅ Purchase New or Used is filled for all vehicles: PASS
✅ Owned Or Leased is filled for all vehicles: PASS
✅ Estimate annual driving distance is filled for all vehicles: PASS
✅ Type of fuel used is filled for all vehicles: PASS

🎉 All automobile validations PASSED!
```

### FAIL Scenario
When any field is missing:
```
❌ Purchase Date is filled for all vehicles: FAIL
   → Purchase Date missing for: Vehicle 1. Purchase Date is required for all vehicles.
❌ Purchase Price is filled for all vehicles: FAIL
   → Purchase Price missing for: Vehicle 1. Purchase Price is required for all vehicles.
❌ Purchase New or Used is filled for all vehicles: FAIL
   → Purchase New or Used missing for: Vehicle 1. Purchase condition is required for all vehicles.
❌ Owned Or Leased is filled for all vehicles: FAIL
   → Owned Or Leased missing for: Vehicle 1. Ownership status is required for all vehicles.
❌ Estimate annual driving distance is filled for all vehicles: FAIL
   → Annual driving distance missing for: Vehicle 1. Annual driving distance is required for all vehicles.
❌ Type of fuel used is filled for all vehicles: FAIL
   → Fuel type missing for: Vehicle 1. Fuel type is required for all vehicles.
```

## Testing

### Test Complete Data (Should PASS)
```bash
python test_automobile_validation.py
```

### Test Missing Data (Should FAIL)
```bash
python test_automobile_validation_fail.py
```

## Integration

The automobile validation is automatically included in the main QC evaluation:
```python
from qc_checklist import QCChecker

qc_checker = QCChecker()
results = qc_checker.evaluate_application_qc(application_data, quote_data)

# Filter automobile results
automobile_checks = [r for r in results if r["category"] == "Automobile Section"]
```

## Notes

- All vehicles in the application must have complete automobile information
- Partial information will result in FAIL status for missing fields
- The system supports multiple vehicles per application
- Field names are flexible (e.g., `purchase_price` or `list_price` both work)
- Boolean fields like `owned`/`leased` must be explicitly set to True/False
