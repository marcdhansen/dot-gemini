# Walkthrough - LightRAG Timeout Fix

I have investigated the `httpx.ReadTimeout` issue when uploading `final_report BCBC.pdf` and resolved it by successfully implementing a 1-hour timeout configuration.

## Root Cause
The `final_report BCBC.pdf` file is computationally intensive for the Ollama LLM to process.
- **Initial failure**: Occurred at 3 minutes (`DEFAULT_LLM_TIMEOUT=180`).
- **Second failure**: Occurred at 10 minutes (`DEFAULT_LLM_TIMEOUT=600`).
The processing time for a single chunk exceeds 10 minutes, requiring a significantly larger timeout.

## Changes

### 1. Increased Default Timeout to 1 Hour
I updated `lightrag/constants.py` to increase the `DEFAULT_LLM_TIMEOUT` to **3600 seconds** (1 hour).

```python
# lightrag/constants.py
-DEFAULT_LLM_TIMEOUT = 600
+DEFAULT_LLM_TIMEOUT = 3600
```

### 2. Implementation & Configuration
- Updated `lightrag/constants.py`
- Updated `.env` to set `LLM_TIMEOUT=3600`
- Updated `env.example` to reflect the new recommendation.
- Added `tests/test_ollama_timeout.py` to prevent regression.

## Verification

### Real-world Verification
I ran a full verification using the actual `final_report BCBC.pdf` file with the 3600s check:
1.  **Metric**: The processing previously failed at **3 minutes** and **10 minutes** with `httpx.ReadTimeout`.
2.  **Result**: With the 3600s setting, the processing **continued successfully beyond 25 minutes** without error.
3.  **Status**: The server remained healthy and the document status remained `PROCESSING`.

The fix allows the server to accommodate the long processing times required by large/complex PDF files without prematurely cutting off the connection.
