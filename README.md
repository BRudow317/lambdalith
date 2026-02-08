# Cloud Voyages Lambda - Multi-Service Auth Platform

## Key Updates

- Removed CDK/CloudFormation app scaffolding in favor of SAM.
- SAM-based local dev and deployment.
- Added `pdoc` for documentation generation.
- Refactored auth service with consistent docstrings and structure.
- Secrets Manager for JWT signing key.

## Tech Stack

- **Runtime**: Python 3.13
- **Framework**: FastAPI + Mangum (ASGI adapter for Lambda)
- **Infrastructure**: AWS SAM (`template.yaml`)
- **Compute**: AWS Lambda with Function URLs (no API Gateway)
- **Database**: DynamoDB (PAY_PER_REQUEST)
- **Secrets**: AWS Secrets Manager (JWT signing key)
- **Dev Environment**: Windows 11, VS Code, Docker Desktop, AWS CLI
- **Linting**: ruff
- **Docs**: pdoc (Google-style docstrings)
- ToDo Later: SQS, SES, SNS, CloudWatch Events

## Dependencies

### Runtime (`requirements.txt`)

Shipped to Lambda via `sam build`:

- **fastapi** + starlette, pydantic, python-multipart — web framework
- **mangum** — ASGI adapter translating Lambda events to FastAPI
- **boto3** + botocore — AWS SDK (DynamoDB, Secrets Manager)
- **jwt** (PyJWT) — JWT token signing/verification
- **cryptography** + cffi — used by scrypt password hashing
- **httpx** + httpcore, h11, anyio — async HTTP client
- **beautifulsoup4** + soupsieve — HTML parsing
- **Jinja2** + MarkupSafe — template rendering
- **markdown2** — Markdown to HTML conversion
- **pydantic-settings** + python-dotenv — config from env vars
- **email-validator** + dnspython — Pydantic `EmailStr` support
- **sentry-sdk** — error tracking
- **s3transfer** — S3 upload/download support
- **certifi**, **idna**, **urllib3**, **six** — standard networking deps

### Dev only (`requirements-dev.txt`)

Not deployed — local tooling:

- **uvicorn** + httptools, watchfiles, websockets — local dev server
- **pytest** — test runner
- **ruff** — linter and formatter
- **pdoc** + Pygments — documentation generator
- **rich** — pretty terminal output

### Planned (not yet installed)

- aws-lambda-powertools — structured logging, tracing, metrics
- structlog — structured logging alternative

## Commands

### Local Development

```bash
# Run locally with hot reload
uvicorn app.app:app --reload

# Open Swagger UI
# http://localhost:8000/docs

# Run tests
pytest tests/

# Lint and format
ruff check app/ handler.py
ruff format app/ handler.py

# Generate docs
pdoc app --output-directory docs
```

### SAM (Build & Deploy)

```bash
# Build the Lambda package
sam build

# Deploy (first time — interactive setup)
sam deploy --guided

# Deploy (subsequent — uses samconfig.toml)
sam deploy

# Test locally in Docker
sam local start-api

# Tail live logs
sam logs --stack-name <your-stack> --tail

# Validate template
sam validate
```

### Environment Variables

For local dev, set these in a `.env` file or export them:

```bash
JWT_SECRET=your-local-dev-secret    # used when JWT_SECRET_NAME is not set
USERS_TABLE=Users                   # defaults in config.py
BLACKLIST_TABLE=TokenBlacklist
PASSWORD_RESET_TABLE=PasswordResetTokens
LOGIN_ATTEMPTS_TABLE=LoginAttempts
```

In production, `template.yaml` wires these automatically via `!Ref`.

## Lambda Usage

- **CloudWatch Logs** — every `print()` and exception traceback goes here automatically.
- **CloudWatch Metrics** — invocation count, duration, errors, throttles (all free).
- **/docs endpoint** — Function URL + `/docs` gives you Swagger UI to test endpoints live.
- **sam logs** — tails CloudWatch from your terminal: `sam logs --stack-name <your-stack> --tail`
- **sam local invoke** / **sam local start-api** — runs Lambda locally in Docker.

## Links

- [SAM CLI Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/using-sam-cli-configure.html)
- [SAM Template Reference](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-specification.html)
- [AWS Lambda Powertools](https://awslabs.github.io/aws-lambda-powertools-python/latest/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Mangum](https://mangum.fastapiexpert.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [Python Cryptography](https://cryptography.io/en/latest/)
- [PyJWT](https://pyjwt.readthedocs.io/en/stable/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [httpx](https://www.python-httpx.org/)
- [Pytest](https://docs.pytest.org/en/stable/)
- [pdoc](https://pdoc.dev/)
- [ruff](https://docs.astral.sh/ruff/)

## Project Setup

1. Configure AWS CLI credentials: `aws configure`
2. Install dependencies: `pip install -r requirements-dev.txt`
3. Build: `sam build`
4. Deploy: `sam deploy --guided`

The first `sam deploy --guided` creates a `samconfig.toml` with your stack name, region, and S3 bucket. After that, just `sam deploy`.

---

# User Journey: Admin
- Here’s the exact admin journey, hop‑by‑hop, with file/function references.
- 
## Admin logs in (gets JWT)
- Client calls POST /auth/login
- Routed in app/auth/routes.py → login handler.
- app/auth/login.py::login()
- Validates body with LoginRequest in app/auth/models.py.
- Resolves tenant from x-api-key via get_tenant() in app/auth/dependencies.py.
- Reads user from DynamoDB via users_table() in app/db.py.
- Verifies password with verify_password() in app/auth/passwords.py.
- Signs JWT with get_jwt_secret() in app/config.py.
- Returns token.
## Admin loads the admin page (GET /admin/users)
- HTTP request hits Lambda entry: handler in handler.py.
- Mangum forwards to FastAPI app in app/app.py → app instance.
- Router match: /admin/users → users_form() in app/admin/routes.py.
- Dependency: Depends(get_current_user) runs first.
- get_current_user() in app/auth/dependencies.py
- Extracts Authorization: Bearer <token>
- jwt.decode(...) verifies signature + exp using secret from app/config.py
- Checks blacklist in DynamoDB via blacklist_table() in app/db.py
- Returns decoded JWT payload as user.
- users_form() renders HTML with Jinja2 template:
- Template file templates/admin/users_form.html.
- Response is HTML back to browser.
## Admin submits the form (POST /admin/users)
- Same routing and dependency chain as above.
- submit_user_form() in app/admin/routes.py
- Uses JWT claims (user) for tenant context.
- Calls real auth handler register() in app/auth/register_user.py
- Writes to DynamoDB via app/db.py.
- Renders result HTML in templates/admin/result.html.
- That’s the full loop: login → get JWT → send JWT to admin page → auth dependency verifies token → admin page renders. If you want the admin journey to start from a dedicated admin login page instead of the API login, I can add that.

# Project Goals

## Phase 1: Foundation

Get the monolith deployed and working

- Project structure setup (done)
- FastAPI + Mangum basic handler (done)
- SAM template.yaml configuration (done)
- Local dev environment with uvicorn
- First deploy to AWS — "hello world" endpoint

## Phase 2: Auth Service

Central authentication for all your sites

- User table in DynamoDB (done)
- Registration endpoint with scrypt password hashing (done)
- Login endpoint returning JWT (done)
- JWT validation via FastAPI dependencies (done)
- Protected route example — `GET /user/me` (done)
- Token refresh, logout/blacklist, password reset (done)
- Integrate with one of your sites

## Phase 3: Secret Messages

Encrypted dead-drop for yourself

- Generate pub/priv keypair
- Store private key encrypted with your password in DynamoDB
- Public endpoint: accepts encrypted message, stores in DynamoDB
- Authenticated endpoint: fetches encrypted key, decrypts with password, decrypts message
- Auto-delete after read (optional)
- TTL expiration on messages

## Phase 4: Email Service

SQS-triggered email generation

- SQS queue setup
- Lambda trigger on queue
- SES integration for sending
- Email templates (welcome, notifications, etc.)
- API endpoint to queue emails from your other services

## Phase 5: Scheduled Scraper

Cron-based web scraping

- CloudWatch scheduled event
- BeautifulSoup + httpx scraper logic
- Store results in S3 or DynamoDB
- Notification on completion (SNS or email yourself)

## Phase 6: Markdown to Deploy

Auto-publish markdown docs to your sites

- S3 bucket for markdown uploads
- Lambda trigger on upload
- Markdown to HTML conversion
- Push to GitHub repo via API
- GitHub Pages or Netlify auto-deploys from there

## Phase 7: Logging / Admin Dashboard

Central visibility into your backend

- Log storage (DynamoDB or S3)
- Simple FastAPI admin routes
- Protected with your auth service
- View logs, messages, scraper results

### Nice-to-haves (later)

- AI API
- SES (Simple Email Service) integration
- OAuth2 support (Google, GitHub logins)
- Rate limiting with DynamoDB
- API keys for external access
- Plotly charts for scraper data visualization
- Multi-device key sync for secret messages

## Current Structure

```text
lambdalith/
├── handler.py              # Lambda entrypoint (Mangum wraps FastAPI)
├── template.yaml           # SAM infrastructure definition
├── Makefile                # Dev workflow targets (docs, serve, lint, test)
├── requirements.txt        # Runtime dependencies (shipped to Lambda)
├── requirements-dev.txt    # Dev tools (uvicorn, pytest, ruff, pdoc)
├── ruff.toml
├── README.md
├── plan.md
│
├── app/
│   ├── __init__.py
│   ├── app.py              # FastAPI app + route registration
│   ├── config.py           # Centralized config, secrets, API keys
│   ├── db.py               # DynamoDB table accessors
│   │
│   ├── auth/
│   │   ├── routes.py           # Router combining all auth endpoints
│   │   ├── dependencies.py     # get_tenant(), get_current_user()
│   │   ├── models.py           # Pydantic request models
│   │   ├── passwords.py        # scrypt hash/verify (stdlib only)
│   │   ├── login.py            # POST /auth/login
│   │   ├── logout.py           # POST /auth/logout
│   │   ├── register_user.py    # POST /auth/register
│   │   ├── pw_reset.py         # POST /auth/password-reset
│   │   ├── pw_reset_confirm.py # POST /auth/password-reset/confirm
│   │   └── token_refresh.py    # POST /auth/token/refresh
│   │
│   ├── entity/
│   │   ├── routes.py           # Router combining entity endpoints
│   │   └── user_profile.py     # GET /user/me
│   │
│   └── health/
│       ├── routes.py           # GET /health, /health/live, /health/ready
│       ├── cv_health.py        # (placeholder)
│       ├── ll_health.py        # (placeholder)
│       └── mlm_health.py       # (placeholder)
│
└── tests/
    ├── __init__.py
    └── unit/
        └── __init__.py
```

## DynamoDB Tables

Defined in `template.yaml`. All tables use PAY_PER_REQUEST billing.

### Users (`${StackName}-Users`)

| Key | Type | Notes |
|-----|------|-------|
| `user_id` (PK) | S | Composite: `{client_id}#{site_id}#{email}` |
| `email` (GSI) | S | `email-index` — not queried yet, for future use |

Other attributes: `password_hash`, `name`, `client_id`, `site_id`, `created_at`, `updated_at`, `last_login`

### TokenBlacklist (`${StackName}-TokenBlacklist`)

| Key | Type | Notes |
|-----|------|-------|
| `token_jti` (PK) | S | UUID from JWT `jti` claim |
| `ttl` | N | Epoch seconds, DynamoDB auto-deletes expired records |

Other attributes: `blacklisted_at`

### PasswordResetTokens (`${StackName}-PasswordResetTokens`)

| Key | Type | Notes |
|-----|------|-------|
| `reset_token` (PK) | S | URL-safe random token |
| `ttl` | N | Epoch seconds (1 hour from creation), auto-deletes |

Other attributes: `user_id`, `used`

### LoginAttempts (`${StackName}-LoginAttempts`)

| Key | Type | Notes |
|-----|------|-------|
| `identifier` (PK) | S | Email or IP for rate limiting |
| `ttl` | N | Epoch seconds, auto-deletes |

**Not yet implemented** — table exists in template.yaml but no route logic uses it.

### Future Tables (planned)

- **Secret Messages** — encrypted dead-drop (Phase 3)
- **Scraper Results** — web scraping output (Phase 5)
- **Email Queue** — or use SQS instead (Phase 4)

## Other Repo Examples

- Zappa
- maybe-finance/maybe
- actualbudget/actualbudget
- firefly-iii
- teller.io - screen scraper

# Front End Usage
```ts
// api.ts
const API_BASE = "https://your-api.example.com";
const API_KEY = "site_a_key_abc123";

type LoginResponse = {
  token: string;
  user: { user_id: string; email: string; name: string };
};

export async function registerUser(email: string, password: string, name = "") {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": API_KEY,
    },
    body: JSON.stringify({ email, password, name }),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

export async function loginUser(email: string, password: string) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": API_KEY,
    },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }
  const data = (await res.json()) as LoginResponse;
  return data;
}

export async function getProfile(token: string) {
  const res = await fetch(`${API_BASE}/user/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

export async function requestPasswordReset(email: string) {
  const res = await fetch(`${API_BASE}/auth/password-reset`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": API_KEY,
    },
    body: JSON.stringify({ email }),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

export async function confirmPasswordReset(token: string, newPassword: string) {
  const res = await fetch(`${API_BASE}/auth/password-reset/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password: newPassword }),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}
```

## Component Example
```tsx
import { useState } from "react";
import { loginUser, getProfile } from "./api";

export function LoginExample() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function onLogin() {
    const { token } = await loginUser(email, password);
    // Store token in memory or storage; then use it for auth requests
    const profile = await getProfile(token);
    console.log(profile);
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onLogin().catch(console.error);
      }}
    >
      <input value={email} onChange={(e) => setEmail(e.target.value)} />
      <input
        value={password}
        type="password"
        onChange={(e) => setPassword(e.target.value)}
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

## Frontend Usage of cookie-based auth
```ts
// login (cookie-based)
await fetch("/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json", "x-api-key": API_KEY },
  credentials: "include", // send/receive cookies
  body: JSON.stringify({ email, password }),
});

// subsequent request
await fetch("/user/me", {
  method: "GET",
  credentials: "include",
});
```

# CORS Header Examples (Backend + Frontend)

## Option A: Cookie-Based Auth (recommended)

Backend response headers (CORS + cookie):

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
Access-Control-Allow-Headers: Content-Type, X-Api-Key
Access-Control-Allow-Methods: GET, POST, OPTIONS
Set-Cookie: auth_token=<JWT>; HttpOnly; Secure; SameSite=None; Path=/
```

Frontend request headers (browser sets Cookie automatically):

```http
Origin: https://app.example.com
```

Frontend fetch example:

```ts
await fetch("https://api.example.com/auth/login", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "x-api-key": API_KEY,
  },
  credentials: "include",
  body: JSON.stringify({ email, password }),
});
```

## Option B: Bearer Token (Authorization Header)

Backend response headers (CORS):

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Headers: Content-Type, Authorization, X-Api-Key
Access-Control-Allow-Methods: GET, POST, OPTIONS
```

Frontend request headers:

```http
Origin: https://app.example.com
Authorization: Bearer <JWT>
```

Frontend fetch example:

```ts
await fetch("https://api.example.com/user/me", {
  method: "GET",
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

BASE_URL=example.com;

# Routes

## GET /
Example endpoint:
`GET ${BASE_URL}/`

Example headers:
```http
Accept: application/json
```

Example React TypeScript request:
```ts
await fetch(`${BASE_URL}/`);
```

Example backend response:
```json
{ "ok": true }
```

## GET /health
Example endpoint:
`GET ${BASE_URL}/health`

Example headers:
```http
Accept: application/json
```

Example React TypeScript request:
```ts
await fetch(`${BASE_URL}/health`);
```

Example backend response:
```json
{ "status": "ok" }
```

## GET /health/live
Example endpoint:
`GET ${BASE_URL}/health/live`

Example headers:
```http
Accept: application/json
```

Example React TypeScript request:
```ts
await fetch(`${BASE_URL}/health/live`);
```

Example backend response:
```json
{ "status": "live" }
```

## GET /health/ready
Example endpoint:
`GET ${BASE_URL}/health/ready`

Example headers:
```http
Accept: application/json
```

Example React TypeScript request:
```ts
await fetch(`${BASE_URL}/health/ready`);
```

Example backend response:
```json
{ "status": "ready" }
```

## POST /auth/register
Example endpoint:
`POST ${BASE_URL}/auth/register`

Example headers:
```http
Content-Type: application/json
x-api-key: site_a_key_abc123
```

Example React TypeScript request:
```ts
await fetch(`${BASE_URL}/auth/register`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "x-api-key": "site_a_key_abc123",
  },
  body: JSON.stringify({
    email: "user@example.com",
    password: "S3cur3Pass!",
    name: "Example User",
  }),
});
```

Example backend response:
```json
{
  "message": "Registration successful",
  "user": {
    "user_id": "ClientCustomerC#SiteA#user@example.com",
    "email": "user@example.com",
    "name": "Example User"
  }
}
```

## POST /auth/login
Example endpoint:
`POST ${BASE_URL}/auth/login`

Example headers:
```http
Content-Type: application/json
x-api-key: site_a_key_abc123
```

Example React TypeScript request:
```ts
await fetch(`${BASE_URL}/auth/login`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "x-api-key": "site_a_key_abc123",
  },
  body: JSON.stringify({
    email: "user@example.com",
    password: "S3cur3Pass!",
  }),
});
```

Example backend response:
```json
{
  "token": "<JWT>",
  "user": {
    "user_id": "ClientCustomerC#SiteA#user@example.com",
    "email": "user@example.com",
    "name": "Example User"
  }
}
```

## POST /auth/logout
Example endpoint:
`POST ${BASE_URL}/auth/logout`

Example headers:
```http
Authorization: Bearer <JWT>
```

Example React TypeScript request:
```ts
await fetch(`${BASE_URL}/auth/logout`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

Example backend response:
```json
{ "message": "Logged out successfully" }
```

## POST /auth/password-reset
Example endpoint:
`POST ${BASE_URL}/auth/password-reset`

Example headers:
```http
Content-Type: application/json
x-api-key: site_a_key_abc123
```

Example React TypeScript request:
```ts
await fetch(`${BASE_URL}/auth/password-reset`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "x-api-key": "site_a_key_abc123",
  },
  body: JSON.stringify({ email: "user@example.com" }),
});
```

Example backend response:
```json
{ "message": "If account exists, reset email sent" }
```

## POST /auth/password-reset/confirm
Example endpoint:
`POST ${BASE_URL}/auth/password-reset/confirm`

Example headers:
```http
Content-Type: application/json
```

Example React TypeScript request:
```ts
await fetch(`${BASE_URL}/auth/password-reset/confirm`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    token: "<reset_token>",
    new_password: "N3wPassw0rd!",
  }),
});
```

Example backend response:
```json
{ "message": "Password reset successful" }
```

## POST /auth/token/refresh
Example endpoint:
`POST ${BASE_URL}/auth/token/refresh`

Example headers:
```http
Authorization: Bearer <JWT>
```

Example React TypeScript request:
```ts
await fetch(`${BASE_URL}/auth/token/refresh`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

Example backend response:
```json
{ "token": "<JWT>" }
```

## GET /user/me
Example endpoint:
`GET ${BASE_URL}/user/me`

Example headers:
```http
Authorization: Bearer <JWT>
```

Example React TypeScript request:
```ts
await fetch(`${BASE_URL}/user/me`, {
  method: "GET",
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

Example backend response:
```json
{
  "user": {
    "user_id": "ClientCustomerC#SiteA#user@example.com",
    "email": "user@example.com",
    "client_id": "ClientCustomerC",
    "site_id": "SiteA"
  }
}
```

## GET /admin/users
Example endpoint:
`GET ${BASE_URL}/admin/users`

Example headers:
```http
Authorization: Bearer <JWT>
Accept: text/html
```

Example React TypeScript request:
```ts
await fetch(`${BASE_URL}/admin/users`, {
  method: "GET",
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

Example backend response:
```http
Content-Type: text/html
```

## POST /admin/users
Example endpoint:
`POST ${BASE_URL}/admin/users`

Example headers:
```http
Authorization: Bearer <JWT>
Content-Type: application/x-www-form-urlencoded
```

Example React TypeScript request:
```ts
const body = new URLSearchParams({
  email: "user@example.com",
  api_key: "site_a_key_abc123",
  password: "S3cur3Pass!",
  name: "Example User",
});

await fetch(`${BASE_URL}/admin/users`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/x-www-form-urlencoded",
  },
  body,
});
```

Example backend response:
```http
Content-Type: text/html
```

## GET /admin/password-reset
Example endpoint:
`GET ${BASE_URL}/admin/password-reset`

Example headers:
```http
Authorization: Bearer <JWT>
Accept: text/html
```

Example React TypeScript request:
```ts
await fetch(`${BASE_URL}/admin/password-reset`, {
  method: "GET",
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

Example backend response:
```http
Content-Type: text/html
```

## POST /admin/password-reset
Example endpoint:
`POST ${BASE_URL}/admin/password-reset`

Example headers:
```http
Authorization: Bearer <JWT>
Content-Type: application/x-www-form-urlencoded
```

Example React TypeScript request:
```ts
const body = new URLSearchParams({
  email: "user@example.com",
  api_key: "site_a_key_abc123",
});

await fetch(`${BASE_URL}/admin/password-reset`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/x-www-form-urlencoded",
  },
  body,
});
```

Example backend response:
```http
Content-Type: text/html
```

