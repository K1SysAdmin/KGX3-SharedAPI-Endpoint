# KGX3 Shared API Test Suite  
**Thomas Kuhn Foundation**  
**Shared KGX3 API Endpoint for Members** `https://preprintwatch.com/wp-json/pw-kgx3/v1/submit`

---

## Overview

This repository provides a complete testing framework for the KGX3 Shared API, developed for and hosted on [PreprintWatch.com](https://preprintwatch.com).  
It is intended exclusively for authorized members of the **Thomas Kuhn Foundation**, who hold valid API credentials and approved access rights.

The suite allows members to:

1. Submit controlled test requests to the KGX3 API endpoint.  
2. Validate authentication, request structure, and system performance.  
3. Generate auditable HTML performance reports and execution logs.  
4. Benchmark API reliability for integration into research automation workflows.

---

## Environment Setup

### Requirements
- **Python 3.9 or higher**
- **Installed Libraries:**
  ```bash
  pip install requests pandas
  ```

### Files in This Repository
| File | Purpose |
|------|----------|
| `test_api.py` | Core Python test suite. Executes all test cases, logs output, and generates reports. |
| `test_data.csv` | CSV dataset containing test case definitions and expected outcomes. |
| `test_results.log` | Plaintext execution log with timestamps, outcomes, and response bodies. |
| `API_Performance_Report_<timestamp>.html` | Automatically generated report summarizing test and performance metrics. |

---

## Authentication and Access

Every member must obtain an **API Key** and associated **usage credits** from the  
**Thomas Kuhn Foundation API Office** before using this test suite.  

The API key identifies you within the shared endpoint’s access registry and must be included in each request:

```python
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "<YOUR_API_KEY>"
}
```

### Important
- Do **not** share your key publicly.  
- Keys may be revoked if misused or exposed.  
- Every POST request consumes usage credits.

---

## Test Input Data (`test_data.csv`)

Each row corresponds to one POST request to the KGX3 API.

| Column | Type | Description | Example |
|---------|------|--------------|----------|
| `test_case_name` | string | Label for the test case. | `Valid Auth Submission` |
| `api_key` | string | API Key issued by the Foundation. | `tkf-12345-xyz` |
| `title` | string | Title of the preprint or metadata submission. | `On Paradigm Shifts` |
| `pdf_url` | string | Publicly accessible PDF link. | `https://example.org/paper.pdf` |
| `email` | string (optional) | Contact address. | `research@kuhnfoundation.org` |
| `expected_status` | integer | Expected HTTP status (e.g., 200, 403, 500). | `200` |

Example:

```csv
test_case_name,api_key,title,pdf_url,email,expected_status
Valid Submission,tkf-12345-xyz,"Scientific Revolutions","https://preprints.org/doc1.pdf","analyst@kuhnfoundation.org",200
Invalid Key,,"Unauthorized Attempt","https://preprints.org/doc2.pdf","",403
```

---

## Python Script Logic (`test_api.py`)

1. Loads configuration constants and CSV file path.  
2. Logs progress with timestamps using `log_message()`.  
3. Iterates through test cases, constructs JSON payloads, and sends POST requests.  
4. Records status codes, response times, and outcomes.  
5. Generates HTML report summarizing statistics.

---

## Log File (`test_results.log`)

Example:
```
[2025-10-08 14:00:02] [INFO] Running Test: Valid Submission
[2025-10-08 14:00:03] [SUCCESS] PASS: Status code matches for 'Valid Submission'
[2025-10-08 14:00:04] [ERROR] FAIL: Status code MISMATCH for 'Invalid Key'
```

Levels: `INFO`, `SUCCESS`, `ERROR`.

---

## Performance Report (`API_Performance_Report_<timestamp>.html`)

### Sections
1. **Overall Summary:** Total tests, success rate, duration, and RPS.  
2. **Response Time Stats:** min, max, average.  
3. **Status Code Distribution:** histogram of results.  
4. **Detailed Results:** PASS/FAIL per test, color-coded.

---

## Metrics

| Metric | Formula |
|---------|----------|
| Success Rate | $\frac{passed}{total} \times 100$ |
| RPS | $\frac{total}{duration}$ |
| Average Response Time | Mean(response times) |

---

## Running Tests

### Google Colab
1. Upload `test_data.csv`.  
2. Paste the Python script in a new cell.  
3. Run the cell.  
4. HTML report opens automatically.

### Local
```bash
python test_api.py
```

---

## Member License

**License:** Thomas Kuhn Foundation Members-Only License  
- Use restricted to registered members.  
- Redistribution prohibited.  
- All outputs remain property of the Foundation.

---

## Credits

The KGX3 and all its symbolic IP, trademarks, branding are the sole property of the **Thomas Kuhn Foundation**. Hosting and management by KNOWDYN LTD.

For inquiries: `membership@kuhnfoundation.org`
