# Validation Engine Documentation

## Overview

The enhanced `compare_engine.py` provides comprehensive validation logic for comparing auto insurance documents by analyzing data from three sources:

- **MBR (Motor Vehicle Record) Extractor** → Driver history details (convictions, license dates)
- **DASH Extractor** → Claims and policy history  
- **Quote Extractor** → Details entered by insurance broker

## Architecture

### ValidationEngine Class

The core validation logic is encapsulated in the `ValidationEngine` class, which provides:

- **Modular Design**: Separate validation methods for each data source
- **Comprehensive Reporting**: Detailed status tracking with matches, warnings, and issues
- **Scalable Structure**: Easy to extend with additional validation rules

### Key Features

#### 1. MBR Validation
- **Name Matching**: Fuzzy string comparison for driver names
- **Date of Birth Validation**: Cross-format date comparison
- **Gender Validation**: Simple character matching
- **Convictions Analysis**: Identifies missing convictions in quote data

#### 2. DASH Validation  
- **Policy Status**: Validates active/cancelled policies
- **Policy Periods**: Checks start/end dates
- **Company Names**: Matches current carrier information
- **Claims History**: Identifies and reports all claims

#### 3. License Progression Validation
- **Issue Date Calculation**: Derives G1, G2, G dates from MBR issue date
- **Progression Logic**: 
  - G1 date = issue date
  - G2 date = G1 + 1 year  
  - G date = G2 + 1 year
- **Canadian Experience**: Validates birth month/year alignment

## Output Format

### Summary Section
```json
{
  "summary": {
    "total_drivers": 1,
    "validated_drivers": 0,
    "issues_found": 1
  }
}
```

### Driver Validation Results
Each driver gets a comprehensive validation report with:

- **Overall Status**: PASS/FAIL/NO_DATA
- **MBR Validation**: Name, DOB, gender, convictions
- **DASH Validation**: Policies, claims, carrier information  
- **License Progression**: G1/G2/G date validation

### Status Indicators
- ✅ **Matches**: Successfully validated fields
- ⚠️ **Warnings**: Data found but requires verification
- ❌ **Issues**: Validation failures requiring attention

## Usage Example

```python
from validator.compare_engine import ValidationEngine

# Prepare data
data = {
    "quotes": [quote_data],
    "mvrs": [mvr_data], 
    "dashes": [dash_data]
}

# Run validation
engine = ValidationEngine()
result = engine.validate_quote(data)

# Access results
print(f"Total drivers: {result['summary']['total_drivers']}")
print(f"Validated: {result['summary']['validated_drivers']}")
print(f"Issues: {result['summary']['issues_found']}")

# Process driver results
for driver in result['drivers']:
    print(f"Driver: {driver['driver_name']}")
    print(f"Status: {driver['validation_status']}")
    
    # Check MBR issues
    for issue in driver['mbr_validation']['issues']:
        print(f"MBR Issue: {issue}")
```

## Validation Rules

### MBR Validation Rules
1. **Name Matching**: 80% similarity threshold using fuzzy matching
2. **Date Formats**: Handles MM/DD/YYYY and DD/MM/YYYY formats
3. **Convictions**: Lists all MBR convictions for quote verification
4. **Gender**: Simple first character comparison

### DASH Validation Rules  
1. **Active Policies**: Identifies policies with "Active" status
2. **Carrier Matching**: Fuzzy matching for company names
3. **Claims Reporting**: Lists all claims with dates and amounts
4. **Date Normalization**: Converts between YYYY-MM-DD and MM/DD/YYYY

### License Progression Rules
1. **Issue Date**: Extracted from MBR (requires implementation)
2. **Progression Calculation**: Automatic G1→G2→G progression
3. **Experience Validation**: Birth date vs. issue date analysis

## Error Handling

The engine gracefully handles:
- Missing data sources (NOT_FOUND status)
- Date format mismatches
- Incomplete records
- Fuzzy matching failures

## Extensibility

### Adding New Validation Rules
1. Create new validation method in ValidationEngine class
2. Add validation call in `_validate_driver()` method
3. Update status determination logic

### Custom Validation Logic
```python
def _validate_custom_field(self, driver, mvr, dash):
    validation = {
        "status": "PASS",
        "issues": [],
        "warnings": [],
        "matches": []
    }
    
    # Custom validation logic here
    
    return validation
```

## Backward Compatibility

The original `validate_quote()` function is preserved for backward compatibility:

```python
# Legacy usage still works
from validator.compare_engine import validate_quote
result = validate_quote(data)
```

## Performance Considerations

- **Efficient Matching**: License number normalization for quick lookups
- **Fuzzy Matching**: Configurable similarity thresholds
- **Date Handling**: Optimized date format conversion
- **Memory Usage**: Streamlined data structures

## Future Enhancements

1. **Issue Date Extraction**: Implement MBR issue date extraction
2. **Conviction Matching**: Direct conviction comparison logic
3. **Policy Period Validation**: Detailed policy overlap analysis
4. **Risk Scoring**: Automated risk assessment based on validation results
5. **Batch Processing**: Support for multiple quotes/drivers 