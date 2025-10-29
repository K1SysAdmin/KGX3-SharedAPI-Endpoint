# KGX3 Documentation and Testing
**Thomas Kuhn Foundation**
**Shared KGX3 API Endpoint for Members** `https://preprintwatch.com/wp-json/pw-kgx3/v1/submit`

---

## Overview

This repository provides a complete testing framework for the KGX3 Shared API, developed for and hosted on [PreprintWatch.com](https://preprintwatch.com). It is intended exclusively for authorized members of the **Thomas Kuhn Foundation**, who hold valid API credentials and approved access rights.

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
|------|---------|
| `test_api.py` | Core Python test suite. Executes all test cases, logs output, and generates reports. |
| `test_data.csv` | CSV dataset containing test case definitions and expected outcomes. |
| `test_results.log` | Plaintext execution log with timestamps, outcomes, and response bodies. |
| `API_Performance_Report_<timestamp>.html` | Automatically generated report summarizing test and performance metrics. |

---

## Authentication and Access

Every member must obtain an **API Key** and associated **usage credits** from the **Thomas Kuhn Foundation API Office** before using this test suite.

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
- Store keys in environment variables or a secrets manager; do not commit them to source control.

---

## API Request Contract (Quick Reference)

Use the following request schema when submitting to the KGX3 endpoint. Field names are snake_case in the JSON body.

Request (JSON):
- title (string) — required. Human-readable title of the submission.
- pdf_url (string) — required. Public HTTPS URL to a PDF file.
- email (string) — optional. Contact address.

Example request body:
```json
{
  "title": "On Paradigm Shifts",
  "pdf_url": "https://example.org/paper.pdf",
  "email": "research@kuhnfoundation.org"
}
```

Example success response (HTTP 200):
```json
{
  "reference_id": "kgx3-abc123",
  "status": "accepted",
  "message": "Submission queued for processing"
}
```

Common error responses:
- 400 Bad Request — missing or invalid fields.
- 401/403 Unauthorized or Forbidden — invalid or missing API key or insufficient permissions.
- 422 Unprocessable Entity — content validation failed (e.g., unreachable pdf_url).
- 500 Server Error — transient server-side failure.

When integrating, make sure to check both the HTTP status code and the returned JSON body for error details.

---

## React / Node.js Integration Guide

Developers who wish to connect frontend React applications or backend Node.js services to the KGX3 Shared API can reuse the same request schema that the Python test harness demonstrates. The examples below use native `fetch` calls available in modern browsers and Node.js 18+. For older Node releases, install [`node-fetch`](https://www.npmjs.com/package/node-fetch) or [`axios`](https://www.npmjs.com/package/axios) and replace the native call accordingly.

### Common Setup

Store the API key securely and never commit it to source control. In local development you can use an `.env` file and load it with libraries such as [`dotenv`](https://www.npmjs.com/package/dotenv).

```bash
npm install dotenv
```

```javascript
// config.js
import 'dotenv/config';

export const KGX3_ENDPOINT = 'https://preprintwatch.com/wp-json/pw-kgx3/v1/submit';
export const KGX3_API_KEY = process.env.KGX3_API_KEY;
```

Note: For Node.js 18+ the global `fetch` API is available by default. If you support Node.js versions <18, use `node-fetch` (v3 is ESM-only). Remove the `import fetch from 'node-fetch'` line when running on Node 18+.

### Node.js Service Example

This example demonstrates a server-side helper that keeps the API key on the server.

```javascript
// submitPreprint.js
import fetch from 'node-fetch'; // optional for older Node versions
import { KGX3_ENDPOINT, KGX3_API_KEY } from './config.js';

// Helper with basic timeout via AbortController
export async function submitPreprint({ title, pdfUrl, email }, { timeoutMs = 15000 } = {}) {
  const payload = {
    title,
    pdf_url: pdfUrl, // API expects snake_case
    email,
  };

  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(KGX3_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': KGX3_API_KEY,
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    clearTimeout(id);

    const text = await response.text();
    let data;
    try { data = JSON.parse(text); } catch (e) { data = { message: text }; }

    if (!response.ok) {
      const errMsg = data?.message || text || `HTTP ${response.status}`;
      throw new Error(`KGX3 submission failed (${response.status}): ${errMsg}`);
    }

    return data;
  } finally {
    clearTimeout(id);
  }
}
```

Usage example:
```javascript
submitPreprint({
  title: 'On Paradigm Shifts',
  pdfUrl: 'https://example.org/paper.pdf',
  email: 'research@kuhnfoundation.org',
})
  .then((data) => console.log('Submission accepted:', data))
  .catch((err) => console.error(err));
```

### Express Proxy Example (recommended for public apps)

For public-facing web apps, avoid shipping the raw API key to the browser. Expose a secure backend endpoint that proxies requests to KGX3 with the key stored server-side:

```javascript
// server.js (Express)
import express from 'express';
import fetch from 'node-fetch';
import 'dotenv/config';

const app = express();
app.use(express.json());

app.post('/api/submit-preprint', async (req, res) => {
  try {
    const response = await fetch(process.env.KGX3_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': process.env.KGX3_API_KEY,
      },
      body: JSON.stringify(req.body),
    });

    const data = await response.json().catch(() => ({}));
    res.status(response.status).json(data);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

app.listen(3000);
```

This keeps secrets on the server and avoids CORS/browser key exposure issues.

### React Component Example

React components can call the same helper via a backend proxy while keeping sensitive credentials on the server. When direct access is needed for trusted internal tools, runtime-injected environment variables can be used, but be aware that `process.env.REACT_APP_*` values are injected at build time and are visible in the built bundle.

```javascript
// src/components/SubmitPreprintForm.jsx
import { useState } from 'react';

const KGX3_ENDPOINT = '/api/submit-preprint'; // use proxy route for public apps

export function SubmitPreprintForm() {
  const [status, setStatus] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);

    try {
      const response = await fetch(KGX3_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: formData.get('title'),
          pdf_url: formData.get('pdf_url'),
          email: formData.get('email'),
        }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data?.message || 'Request failed');

      setStatus({ type: 'success', message: `Submission accepted. Reference: ${data.reference_id}` });
    } catch (error) {
      setStatus({ type: 'error', message: error.message });
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Title
        <input name="title" required />
      </label>
      <label>
        PDF URL
        <input name="pdf_url" type="url" required />
      </label>
      <label>
        Contact Email
        <input name="email" type="email" />
      </label>
      <button type="submit">Submit to KGX3</button>

      {status && (
        <p className={status.type === 'success' ? 'success' : 'error'}>{status.message}</p>
      )}
    </form>
  );
}
```

**Security Reminder:** For public-facing React apps, avoid shipping the raw API key to the browser. Instead, expose a secure backend endpoint that proxies requests to the KGX3 API with the key stored server-side.

---

## REST API cURL Documentation

The KGX3 Shared API accepts JSON payloads over HTTPS with an API key. The following commands demonstrate how to interact with the endpoint using `curl`.

### Base Command

```bash
curl -X POST \
  https://preprintwatch.com/wp-json/pw-kgx3/v1/submit \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $KGX3_API_KEY" \
  -d '{
    "title": "On Paradigm Shifts",
    "pdf_url": "https://example.org/paper.pdf",
    "email": "research@kuhnfoundation.org"
  }'
```

### Store Response to File

```bash
curl -sS -X POST \
  https://preprintwatch.com/wp-json/pw-kgx3/v1/submit \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $KGX3_API_KEY" \
  -d @payload.json \
  -o response.json
```

Where `payload.json` contains the JSON body and `response.json` captures the API response for auditing. Example `payload.json`:

```json
{
  "title": "On Paradigm Shifts",
  "pdf_url": "https://example.org/paper.pdf",
  "email": "research@kuhnfoundation.org"
}
```

### Include Additional Headers

If the Foundation issues supplementary headers (e.g., tracing IDs), append them with additional `-H` flags:

```bash
curl -X POST \
  https://preprintwatch.com/wp-json/pw-kgx3/v1/submit \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $KGX3_API_KEY" \
  -H "X-Trace-Id: abc123" \
  -d '{"title":"Tracing Example","pdf_url":"https://example.org/trace.pdf"}'
```

### Inspect Response Headers

Use the verbose flag to log the request/response handshake for debugging:

```bash
curl -v -X POST \
  https://preprintwatch.com/wp-json/pw-kgx3/v1/submit \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $KGX3_API_KEY" \
  -d '{"title":"Verbose Example","pdf_url":"https://example.org/verbose.pdf"}'
```

**Tip:** Wrap the commands in shell scripts or CI jobs to automate regression checks similar to the Python suite.

---

## CORS & Browser Considerations

Browser-based clients are subject to the same-origin policy and CORS. If the KGX3 endpoint does not include the appropriate Access-Control-Allow-* headers, browsers will block direct requests from frontends. In those cases, use a server-side proxy (see Express example above) to forward requests.

---

## Robustness & Best Practices

- Timeouts: Use AbortController or client-level timeouts to avoid hanging requests.
- Retries: For transient 5xx errors, implement retry with exponential backoff.
- Validation: Sanitize and validate user-provided URLs and fields before sending to the API.
- Logging: Capture request IDs or trace IDs returned by the API for incident investigation.
- Secrets: Add `.env` to `.gitignore` and prefer CI vaults or cloud secret managers for production.

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
| Success Rate | (passed / total) * 100 |
| RPS | total / duration |
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
