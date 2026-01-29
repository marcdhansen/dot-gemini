# Implementation Plan - Debug WebUI Visibility

The user reports the LightRAG WebUI is not showing up. We need to verify the build artifact generation and the server's asset serving logic.

## Proposed Changes

### WebUI Build Verification
- Check `LightRAG/lightrag_webui/vite.config.ts` to see where the build output goes.
- Standardize build output to `../lightrag/api/webui` if it's not already.

### Asset Synchronization
- If the build outputs to `dist`, we need to copy it to `lightrag/api/webui` so the Python server can serve it.
- Alternatively, symlink it if suitable for the environment (though copying is safer for deployment).

## Verification Plan

### Automated Tests
- Run `curl -I http://localhost:9621/webui/index.html` to verify 200 OK.
- Check `lightrag.log` for "WebUI assets mounted" message.

### Manual Verification
- User to reload the page.
