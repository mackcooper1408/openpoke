# OpenPoke Development Guide

## Repository Overview

OpenPoke is an AI-powered personal assistant application with a Python/FastAPI backend and Next.js frontend. The system uses tool-based agents to interact with external services like Gmail, Whoop (fitness tracking), and Hevy (workout management).

## Architecture

### Backend (Python/FastAPI)

- **Location**: `/server/`
- **Entry Point**: `server/server.py`
- **Port**: 8001 (default)
- **Framework**: FastAPI with uvicorn
- **Configuration**: `server/config.py` - loads from `.env` file

### Frontend (Next.js)

- **Location**: `/web/`
- **Entry Point**: `web/app/page.tsx`
- **Port**: 3000 (default)
- **Framework**: Next.js 14 with React, TypeScript, Tailwind CSS

### Agent System

- **Interaction Agent**: Handles user conversations (`server/agents/interaction_agent/`)
- **Execution Agent**: Executes tasks and tools (`server/agents/execution_agent/`)
- **Tools**: Located in `server/agents/execution_agent/tools/`

## Key Patterns and Conventions

### 1. Adding New External Service Integrations

Follow the pattern established by Whoop and Hevy integrations:

#### Backend Service Client (`server/services/{service_name}/client.py`)

```python
# 1. Import dependencies
from pathlib import Path
import json
import requests
from fastapi.responses import JSONResponse
from ...config import Settings, get_settings

# 2. Define storage paths
_TOKEN_FILE = Path.home() / ".openpoke" / "{service}_token.json"

# 3. Implement core functions:
# - Token/credential management (load, save, clear)
# - API request wrapper with authentication
# - Service-specific data fetch functions
# - Status check function

# 4. Export public API functions
def connect_{service}(...) -> JSONResponse:
    """Handle OAuth or API key setup"""
    pass

def get_{service}_status() -> JSONResponse:
    """Check connection status"""
    return JSONResponse(content={"connected": bool})

def get_{data_type}(...) -> Dict[str, Any]:
    """Fetch specific data from service"""
    pass
```

#### Service Routes (`server/routes/{service_name}.py`)

```python
from fastapi import APIRouter
from ..services.{service} import connect_{service}, get_{service}_status

router = APIRouter(prefix="/{service}", tags=["{service}"])

@router.get("/status")
async def status() -> JSONResponse:
    return get_{service}_status()

@router.post("/connect")
async def connect(...) -> JSONResponse:
    return connect_{service}(...)

@router.post("/disconnect")
async def disconnect() -> JSONResponse:
    return disconnect_{service}()
```

#### Register Routes (`server/routes/__init__.py`)

```python
from .{service} import router as {service}_router
api_router.include_router({service}_router, prefix="/api/v1")
```

#### Agent Tools (`server/agents/execution_agent/tools/{service}.py`)

```python
from composio import Action, action
from server.services.{service} import get_{data_type}

@action(toolname="{service}_get_{data}")
def {service}_get_{data}(start_date: str, end_date: str) -> str:
    """
    Tool description for the AI agent.

    Args:
        param: Description

    Returns:
        String representation of the data
    """
    result = get_{data_type}(start_date, end_date)
    return str(result)
```

#### Register Tools (`server/agents/execution_agent/tools/registry.py`)

```python
from .{service} import {service}_get_data
toolset.register_action({service}_get_data)
```

### 2. Frontend Integration Pattern

#### Next.js API Proxy Routes (`web/app/api/{service}/{endpoint}/route.ts`)

```typescript
export const runtime = 'nodejs';

export async function GET() {
  const serverBase = process.env.PY_SERVER_URL || 'http://localhost:8001';
  const url = `${serverBase}/api/v1/{service}/{endpoint}`;

  try {
    const resp = await fetch(url);
    const data = await resp.json().catch(() => ({}));
    return new Response(JSON.stringify(data), {
      status: resp.status,
      headers: { 'Content-Type': 'application/json; charset=utf-8' },
    });
  } catch (e: any) {
    return new Response(
      JSON.stringify({ ok: false, error: 'Upstream error', detail: e?.message }),
      { status: 502, headers: { 'Content-Type': 'application/json; charset=utf-8' } }
    );
  }
}
```

#### Settings Modal Integration (`web/components/SettingsModal.tsx`)

1. Add state variables for the service
2. Add status check useEffect hook
3. Add connection handler functions
4. Add UI section in the modal

### 3. OAuth Flow Pattern (Whoop Example)

**Flow**: Frontend → Backend → OAuth Provider → Next.js Callback → Backend Token Exchange → Frontend

1. **Initiate OAuth** (`/api/v1/{service}/connect`):

   - Generate secure state parameter (min 8 chars)
   - Save state to file for CSRF validation
   - Redirect to OAuth provider with state

2. **OAuth Callback** (`/api/{service}/callback`):

   - Next.js route receives code and state
   - Forwards to backend with both parameters
   - Backend validates state
   - Exchanges code for tokens
   - Returns success/error

3. **Frontend Detection**:
   - Check URL params on mount (`?{service}_connected=true`)
   - Update UI automatically
   - Clean up URL params

**Critical**:

- Redirect URI must point to Next.js: `http://localhost:3000/api/{service}/callback`
- Use `window.location.href` for OAuth initiation (not `window.open` or `fetch`)

### 4. Environment Variables

Add to `.env` file in project root:

```bash
# Service credentials
{SERVICE}_CLIENT_ID=your_client_id
{SERVICE}_CLIENT_SECRET=your_client_secret
{SERVICE}_REDIRECT_URI=http://localhost:3000/api/{service}/callback
{SERVICE}_API_KEY=your_api_key  # For API key-based auth
```

Update `server/config.py`:

```python
class Settings(BaseModel):
    {service}_client_id: Optional[str] = Field(default=os.getenv("{SERVICE}_CLIENT_ID"))
    {service}_client_secret: Optional[str] = Field(default=os.getenv("{SERVICE}_CLIENT_SECRET"))
```

## Common Workflows

### Starting Development Servers

**Backend**:

```bash
cd /path/to/openpoke
python -m server.server --reload
```

**Frontend**:

```bash
cd /path/to/openpoke/web
npm run dev
```

### Testing API Endpoints

**Backend Direct**:

```bash
curl http://localhost:8001/api/v1/{service}/status | python3 -m json.tool
```

**Through Next.js Proxy**:

```bash
curl http://localhost:3000/api/{service}/status | python3 -m json.tool
```

### Checking Stored Credentials

```bash
ls -la ~/.openpoke/
cat ~/.openpoke/{service}_token.json | python3 -m json.tool
```

## Troubleshooting

### Issue: "Connected" Status Not Updating

**Causes**:

1. Next.js caching - Hard refresh browser (Cmd+Shift+R)
2. Backend not restarted after .env changes
3. Next.js dev server needs restart

**Solutions**:

- Restart backend server to pick up new environment variables
- Clear Next.js cache: `rm -rf web/.next`
- Hard refresh browser

### Issue: OAuth Flow Errors

**Common Issues**:

1. "Invalid state" - State file missing or mismatch
2. "Missing code" - OAuth callback not receiving authorization code
3. "Redirect URI mismatch" - Check provider settings

**Debug Steps**:

1. Verify redirect URI matches exactly in provider settings
2. Check `~/.openpoke/{service}_oauth_state.txt` exists during flow
3. Ensure environment variables are loaded (restart server)

### Issue: 404 on API Endpoints

**Causes**:

1. Incorrect endpoint path (check API version: v1 vs v2)
2. Endpoint requires different HTTP method
3. Missing path parameters

**Solutions**:

- Check API documentation for correct endpoint paths
- Verify base URL construction in `_make_request` functions
- Test endpoint directly with curl

### Issue: Token/API Key from .env Not Recognized

**Causes**:

1. Server started before .env updated
2. .env file not in project root
3. Config not loading environment variable

**Solutions**:

- Restart backend server (uvicorn --reload doesn't reload .env)
- Verify .env location (should be in `/openpoke/` root)
- Check `server/config.py` for correct env variable names

## API Endpoint Patterns

### Whoop API v2

- Base URL: `https://api.prod.whoop.com/developer/v2/`
- Auth: Bearer token
- Date params: ISO datetime strings (YYYY-MM-DDTHH:MM:SS.SSSZ)
- Endpoints:
  - `/v2/recovery` - Recovery data
  - `/v2/activity/sleep` - Sleep data
  - `/v2/activity/workout` - Workout data
  - `/v2/cycle` - Physiological cycles

### Hevy API

- Base URL: `https://api.hevyapp.com/v1/`
- Auth: X-API-Key header
- Endpoints:
  - `/v1/workouts` - Workout history
  - `/v1/routines` - Training routines
  - `/v1/routine_folders` - Routine organization

## File Structure Reference

```
openpoke/
├── .env                          # Environment variables
├── server/
│   ├── config.py                 # Configuration management
│   ├── server.py                 # FastAPI app entry point
│   ├── agents/
│   │   └── execution_agent/
│   │       ├── system_prompt.md  # Agent persona/instructions
│   │       └── tools/
│   │           ├── registry.py   # Tool registration
│   │           ├── whoop.py      # Whoop agent tools
│   │           └── hevy.py       # Hevy agent tools
│   ├── routes/
│   │   ├── __init__.py          # Route registration
│   │   ├── whoop.py             # Whoop API routes
│   │   └── hevy.py              # Hevy API routes
│   └── services/
│       ├── whoop/
│       │   └── client.py        # Whoop service client
│       └── hevy/
│           └── client.py        # Hevy service client
├── web/
│   ├── app/
│   │   ├── page.tsx             # Main chat interface
│   │   └── api/                 # Next.js API routes (proxies)
│   │       ├── whoop/
│   │       │   ├── status/route.ts
│   │       │   ├── connect/route.ts
│   │       │   ├── callback/route.ts
│   │       │   └── disconnect/route.ts
│   │       └── hevy/
│   │           └── ...
│   └── components/
│       └── SettingsModal.tsx    # Integration UI
└── ~/.openpoke/                 # User data directory
    ├── whoop_token.json
    ├── whoop_oauth_state.txt
    └── hevy_api_key.json
```

## Best Practices

1. **Always use environment variables** for sensitive credentials (never hardcode)
2. **Follow the established patterns** when adding new integrations
3. **Test both backend and frontend proxy** endpoints
4. **Handle errors gracefully** with appropriate HTTP status codes
5. **Update system_prompt.md** when adding new agent capabilities
6. **Document API quirks** (like Whoop requiring datetime strings)
7. **Use TypeScript types** for frontend API responses
8. **Validate inputs** before making external API calls
9. **Clear credentials on disconnect** for security
10. **Auto-reload servers** during development (--reload flag)

## Security Notes

- Tokens stored in `~/.openpoke/` directory (user home)
- OAuth state parameter must be ≥8 characters for CSRF protection
- Environment-sourced credentials are trusted (skip validation)
- User-provided credentials are validated via test API calls
- Never expose API keys or tokens in logs or responses

## Performance Considerations

- Token refresh happens automatically when expired
- Cache status checks to avoid redundant API calls
- Use pagination for large data sets (Whoop: max 25 per page)
- Date range queries are more efficient than full history pulls
- Next.js API routes cache responses (may need hard refresh)

## Extension Points

To extend OpenPoke:

1. **New Tools**: Add to `server/agents/execution_agent/tools/`
2. **New Services**: Follow the integration pattern above
3. **New Agent Behaviors**: Update `system_prompt.md`
4. **New UI Components**: Add to `web/components/`
5. **New API Routes**: Add to `server/routes/` and `web/app/api/`

## Reference Documentation

- [Whoop API Docs](https://developer.whoop.com/api)
- [Hevy API Docs](https://hevyapp.com/api-docs) (if available)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Composio Tools](https://composio.dev/tools)
