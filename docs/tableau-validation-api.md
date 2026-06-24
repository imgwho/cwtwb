# Tableau REST API — Workbook Validation Endpoints
[refer](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_workbooks_and_views.htm#validate_uploaded_workbook)

> Source: Tableau REST API Reference (API 3.29+, Tableau Cloud June 2026 / Server 2026.2)
> Saved: 2026-06-24

---

## 1. Validate Workbook

Validates a TWB file against the TWB XSD schema and verifies it can be loaded in Tableau.
**Does NOT store the file on the server.**

### URI

```
POST /api/{api-version}/sites/{site-id}/workbooks/validateWorkbook
```

### Permissions
- Any authenticated user
- Access Scope: `tableau:workbooks:read`

### Request Header
```
Accept: application/json
```

### Request Body

Multipart form data. **Only .twb files** (not .twbx).

- `name` parameter: `tableau_workbook`
- `filename` parameter: TWB filename (must end with `.twb`)
- File content: raw TWB XML

cURL example:
```bash
curl --location \
  'https://example.com/api/3.29/sites/{site-id}/workbooks/validateWorkbook' \
  --header 'X-Tableau-Auth: {auth-token}' \
  --header 'Accept: application/json' \
  --form 'tableau_workbook=@"path/to/file.twb"'
```

### Response

**200** — Valid (may have warnings):
```json
{
  "timestamp": "2026-06-10T14:32:18.456Z",
  "warnings": [
    {
      "severity": "WARNING",
      "message": "Unknown map source is used",
      "line": 245,
      "column": 18,
      "elementName": "map"
    }
  ]
}
```

**422** — Validation errors found:
```json
{
  "timestamp": "2026-06-10T14:32:18.456Z",
  "errors": [
    {
      "severity": "ERROR",
      "message": "Missing required closing tag for element",
      "line": 127,
      "column": 5,
      "elementName": "preferences"
    }
  ],
  "warnings": [...]
}
```

### Error Codes

| HTTP | Condition | Details |
|------|-----------|---------|
| 400 | Missing required parameter | `tableau_workbook` parameter not present |
| 400 | Invalid file type or content | Not valid TWB or filename doesn't end with `.twb` |
| 406 | No acceptable response | Must use `Accept: application/json` header |
| 422 | Unprocessable entity | Validation errors detected |

---

## 2. Validate Workbook and Upload

Validates a TWB file AND stores it in **temporary storage** on the server if validation succeeds.
The stored file can then be validated again via "Validate Uploaded Workbook".

### URI

```
POST /api/{api-version}/sites/{site-id}/workbooks/validateWorkbookAndUpload
```

### Permissions
- Any authenticated user
- Access Scope: `tableau:workbooks:create`

### Request Header
```
Accept: application/json
```

### Request Body

Same format as "Validate Workbook" — multipart form data, `.twb` only.

cURL example:
```bash
curl --location \
  'https://example.com/api/3.29/sites/{site-id}/workbooks/validateWorkbookAndUpload' \
  --header 'X-Tableau-Auth: {auth-token}' \
  --header 'Accept: application/json' \
  --form 'tableau_workbook=@"path/to/file.twb"'
```

### Response

**200** — Valid, file stored in temporary storage:
```json
{
  "timestamp": "2026-06-10T14:32:18.456Z",
  "uploadId": "12345:12ab34cd56ef78ab90cd12ef34ab56cd-0:0",
  "warnings": [...]
}
```

**422** — Validation errors found (file NOT stored):
```json
{
  "timestamp": "2026-06-10T14:32:18.456Z",
  "errors": [...],
  "warnings": [...]
}
```

### Error Codes

| HTTP | Condition | Details |
|------|-----------|---------|
| 400 | Missing required parameter | `tableau_workbook` parameter not present |
| 400 | Invalid file type or content | Not valid TWB or filename doesn't end with `.twb` |
| 406 | No acceptable response | Must use `Accept: application/json` header |
| 422 | Unprocessable entity | Validation errors detected |

---

## 3. Validate Uploaded Workbook

Validates a TWB file that **already exists in temporary storage** (uploaded via
"Validate Workbook and Upload" or the file upload API).

### URI

```
POST /api/{api-version}/sites/{site-id}/workbooks/validateUploadedWorkbook?uploadSessionId={upload-session-id}
```

### Permissions
- Any authenticated user
- Access Scope: `tableau:workbooks:create`

### Request Header
```
Accept: application/json
```

### Request Body

None. The TWB is retrieved from temporary storage using the `uploadSessionId`.

cURL example:
```bash
curl --location --request POST \
  'https://example.com/api/3.29/sites/{site-id}/workbooks/validateUploadedWorkbook?uploadSessionId=12345:12ab34cd56ef78ab90cd12ef34ab56cd-0:0' \
  --header 'X-Tableau-Auth: {auth-token}' \
  --header 'Accept: application/json'
```

### Response

**200** — Valid:
```json
{
  "timestamp": "2026-06-10T14:32:18.456Z",
  "uploadId": "12345:12ab34cd56ef78ab90cd12ef34ab56cd-0:0",
  "warnings": [...]
}
```

**422** — Validation errors found:
```json
{
  "timestamp": "2026-06-10T14:32:18.456Z",
  "errors": [...],
  "warnings": [...]
}
```

### Error Codes

| HTTP | Condition | Details |
|------|-----------|---------|
| 400 | Missing uploadSessionId parameter | `uploadSessionId` not in querystring |
| 404 | Resource not found | `uploadSessionId` couldn't be found |
| 422 | Unprocessable entity | Validation errors detected |

---

## Common: Error/Warning Object Format

```json
{
  "severity": "ERROR" | "WARNING",
  "message": "Human-readable description",
  "line": 127,
  "column": 5,
  "elementName": "preferences"
}
```

## Common: Validation Semantics

- **Syntactic validation**: TWB conforms to the XSD schema
- **Semantic validation**: Content can be interpreted by Tableau (guarantees the workbook will open)
- **Errors** = will prevent the workbook from loading in Tableau
- **Warnings** = advisory, won't prevent loading
