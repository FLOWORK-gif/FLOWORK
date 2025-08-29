```markdown
# Chapter 3: Authentication & Security

**IMPORTANT**: Currently, the Flowork v1 API requires an API Key for most endpoints. This key is configured within Flowork and must be sent with each request to ensure only authorized applications can interact with the engine.

## 3.1. How to Use the API Key
All protected requests must include the `X-API-Key` header.

**Example Request:**
```bash
curl -X GET http://localhost:8989/api/v1/presets \
     -H "X-API-Key: YOUR_API_KEY_FROM_SETTINGS"