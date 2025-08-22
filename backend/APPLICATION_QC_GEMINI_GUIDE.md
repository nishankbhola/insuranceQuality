# Application QC with Gemini AI - Implementation Guide

## Overview

This new Application QC system uses Gemini AI to perform intelligent validation of insurance application PDFs. It consists of two validation layers:

1. **Simple String Validations** (No API cost)
2. **AI-Powered Validations** (Using Gemini API)

## Architecture

### 1. Gemini Application Extractor
**File**: `backend/extractors/gemini_application_extractor.py`

**Key Features**:
- Extracts and validates application data using Gemini AI
- Performs simple string existence checks first (no API cost)
- Uses Gemini AI for complex validations (3 pages only)
- Saves `gemini_response.json` for manual review
- Tracks API usage (50 calls/day limit)

### 2. Application QC Endpoint
**Endpoint**: `/api/application-qc`
**Method**: POST
**Files Required**: `application` (PDF), `quote` (optional)

## Validation Types

### Simple Validations (No AI Required)
These check if specific strings exist anywhere in the PDF:

1. "COVERAGE NOT IN EFFECT"
2. "Optional Accident Benefits Confirmation Form"
3. "CONSENT TO RECEIVE ELECTRONIC COMMUNICATIONS"
4. "PERSONAL INFORMATION CONSENT FORM"
5. "PERSONAL INFORMATION CLIENT CONSENT FORM"

**Result**: Pass if present, Critical Error if missing.

### AI-Powered Validations (Gemini)
These use Gemini AI to analyze 3 specific pages:

1. **Ontario Application for Automobile Insurance** (first page)
2. **OPTIONAL ADDITIONAL COVERAGES/ENDORSEMENTS** page
3. **REMARKS** page

#### Validation Rules:

1. **Pleasure Use Validation**: If "Pleasure use" is checked, verify "commuting one way = 0 kms" and "business use = 0%"
2. **Business Use Remarks**: If business use % > 0, check if remarks exist
3. **Purchase Date Check**: Verify purchase date is present for each vehicle
4. **Purchase Price Check**: Verify purchase price is present for each vehicle
5. **New/Used Status**: Verify either "New" or "Used" is checked (not both, not neither)
6. **Owned/Leased Status**: Verify either "Owned" or "Leased" is checked
7. **Lease OPCF5 Check**: If leased, check for OPCF 5 on coverages page
8. **Household Vehicle Count**: Compare total household vehicles vs. policy vehicles
9. **Additional Drivers Check**: If additional licensed drivers marked YES, ensure remarks exist

## Configuration

### Environment Variables
Add to your `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
ENABLE_GEMINI_ANALYSIS=true
GEMINI_DAILY_LIMIT=45
```

### API Limits
- **Free Tier**: 50 calls per day
- **Conservative Setting**: 45 calls per day (buffer)
- **Per Request**: 1 API call (for 3 pages)

## Usage

### Backend Usage
```python
from extractors.gemini_application_extractor import extract_and_validate_application_qc

result = extract_and_validate_application_qc("path/to/application.pdf")
```

### Frontend Usage
1. Upload application PDF (required)
2. Upload quote PDF (optional)
3. System automatically runs both validation layers
4. Results displayed in existing Application QC UI

## Response Format

```json
{
  "extraction_info": {
    "original_file": "application.pdf",
    "extraction_method": "gemini_ai",
    "extraction_timestamp": "2024-..."
  },
  "simple_validations": {
    "coverage_not_in_effect": {
      "status": "pass/fail",
      "description": "Check if 'COVERAGE NOT IN EFFECT' exists in PDF",
      "error_type": "critical"
    }
  },
  "gemini_validations": {
    "validation_1_pleasure_use": "pass/fail",
    "validation_2_business_use_remarks": "pass/fail",
    "validation_3_purchase_date": "pass/fail",
    "validation_4_purchase_price": "pass/fail",
    "validation_5_new_used_status": "pass/fail",
    "validation_6_owned_leased_status": "pass/fail",
    "validation_7_lease_opcf5": "pass/fail",
    "validation_8_household_vehicle_count": "pass/fail",
    "validation_9_additional_drivers": "pass/fail",
    "details": {
      "failed_vehicles": [],
      "remarks_found": true,
      "total_vehicles_on_policy": 1,
      "total_vehicles_household": 1,
      "lease_vehicles_count": 0,
      "opcf5_found": false,
      "additional_drivers_marked": false,
      "validation_notes": "Brief explanation of any failures"
    }
  },
  "api_usage": {
    "calls_made": 1,
    "daily_limit": 50,
    "remaining_calls": 49
  }
}
```

## Files Generated

1. **`gemini_response.json`**: Raw Gemini API response for manual review
2. **`application_qc_data_[timestamp].json`**: Complete extraction results
3. **`qc_results_[timestamp].json`**: Processed results for UI compatibility

## Testing

### Manual Test
```bash
cd backend
python test_gemini_qc.py
```

### API Test
```bash
curl -X POST http://localhost:8000/api/application-qc \
  -F "application=@test/sample.pdf"
```

## Key Benefits

1. **API Efficiency**: Only 1 API call per application (3 pages only)
2. **Cost Control**: Simple validations done without API calls
3. **Comprehensive**: 9 different validation types
4. **Auditable**: Saves raw Gemini responses for review
5. **UI Compatible**: Works with existing Application QC interface
6. **Flexible**: Quote file is optional

## Error Handling

- **API Failures**: Fallback to error reporting
- **Missing Pages**: Uses first, middle, last pages if specific pages not found
- **Parsing Errors**: Returns error details with raw response
- **Rate Limiting**: Tracks API usage to prevent exceeding limits

## Future Enhancements

1. **More Validation Rules**: Easy to add new validations to Gemini prompt
2. **Page Detection**: Better logic for finding specific pages
3. **Multi-Language**: Support for French applications
4. **Caching**: Cache results to avoid duplicate API calls
5. **Batch Processing**: Process multiple applications efficiently
