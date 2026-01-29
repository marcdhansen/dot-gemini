# Walkthrough: Fixing WebUI Visibility

The LightRAG WebUI was failing to load due to a missing `pyproject.toml` file (broken symlink) and lack of a root URL handler.

## Changes
- **Restored `pyproject.toml`**: Replaced the broken symlink with valid content from git history.
- **Root Redirect**: Implemented a redirect in `lightrag_server.py` so requests to `/` automatically go to `/webui/`.
- **Restarted Server**: Triggered a server restart to apply changes.

## Verification Results

### 1. Server Status
The server is running at `http://localhost:9621`.

### 2. URL Redirection (UX Fix)
- `curl -I http://localhost:9621/` -> **307 Temporary Redirect** to `/webui/`.
- Users can now simply visit `http://localhost:9621` and be taken to the UI.

### 3. WebUI Accessibility
- `curl -I http://localhost:9621/webui/` -> **200 OK**
- `curl -I http://localhost:9621/webui/index.html` -> **200 OK**
- Assets are correctly served from `/webui/assets/`.

## How to Access
Open your browser to:
**[http://localhost:9621](http://localhost:9621)**
(It will automatically redirect to the WebUI)
