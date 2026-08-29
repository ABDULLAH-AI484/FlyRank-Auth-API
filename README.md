# 🔐 FlyRank Auth API — W2A4

Secure authentication API built with **FastAPI** and **Supabase Auth**, implementing JWT Bearer token verification, reusable auth dependencies, and interactive Swagger UI documentation.

> **FlyRank Internship · Backend Track · Week 4 · Assignment A1**  
> *Auth: Login & Protect*

---

## 🎯 What This Project Does

| Feature | Description |
|---------|-------------|
| **Sign Up** | Create user accounts via Supabase Auth (`POST /auth/signup`) |
| **Log In** | Authenticate and receive JWT access tokens (`POST /auth/login`) |
| **Log Out** | End sessions securely (`POST /auth/logout`) |
| **Protected Routes** | Verify JWTs via a single reusable `get_current_user` dependency |
| **Swagger UI** | Interactive API docs with 🔒 lock icons on protected endpoints |

---

## 🛠️ Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Auth:** [Supabase Auth](https://supabase.com/docs/guides/auth) (Identity Provider)
- **SDK:** [`supabase-py`](https://github.com/supabase/supabase-py)
- **Docs:** Swagger UI (auto-generated at `/docs`)
- **Config:** `python-dotenv` for environment variables

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/flyrank-auth-api.git
cd flyrank-auth-api
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your Supabase project credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
APP_PORT=8000
```

> **Where to find these:** [Supabase Dashboard](https://app.supabase.com) → Your Project → **Project Settings → API**
> - `SUPABASE_URL` = Project URL
> - `SUPABASE_KEY` = `anon` public key (⚠️ never use the `service_role` key)

### 5. Run the server

```bash
uvicorn main:app --reload --port 8000
```

| URL | Purpose |
|-----|---------|
| `http://localhost:8000` | API root |
| `http://localhost:8000/docs` | **Swagger UI** (interactive docs) |
| `http://localhost:8000/redoc` | ReDoc (alternative docs) |

<img width="982" height="920" alt="image" src="https://github.com/user-attachments/assets/cc026ee5-20d9-42e0-89fb-d650c688aa0a" />


## 📡 API Reference

| Method | Endpoint | Auth Required | Description | Status Codes |
|--------|----------|---------------|-------------|--------------|
| `POST` | `/auth/signup` | ❌ No | Create new account | **201**, 400 |
| `POST` | `/auth/login` | ❌ No | Authenticate, get JWT | **200**, 400, 401 |
| `POST` | `/auth/logout` | ✅ Yes | End session | **204**, 401 |
| `GET` | `/public/info` | ❌ No | Public data | **200** |
| `GET` | `/protected/profile` | ✅ Yes | Private profile | **200**, 401 |
| `GET` | `/protected/dashboard` | ✅ Yes | Private dashboard | **200**, 401 |
| `GET` | `/health` | ❌ No | Health check | **200** |

### Status Code Legend

| Code | Meaning | When It Happens |
|------|---------|-----------------|
| **201** | Created | Signup succeeds |
| **200** | OK | Login succeeds, or protected/public read succeeds |
| **204** | No Content | Logout succeeds (empty body) |
| **400** | Bad Request | Missing/invalid email or password |
| **401** | Unauthorized | Missing, malformed, or invalid/expired Bearer token |

---

## 🔒 Authentication Flow

```
┌─────────┐    POST /auth/signup     ┌──────────┐
│  Client │ ───────────────────────→ │ Supabase │
│         │ ←──── 201 + user ─────── │   Auth   │
└─────────┘                          └──────────┘

┌─────────┐    POST /auth/login      ┌──────────┐
│  Client │ ───────────────────────→ │ Supabase │
│         │ ←── 200 + access_token ──│   Auth   │
└─────────┘                          └──────────┘

┌─────────┐  GET /protected/profile  ┌──────────┐
│  Client │ ── Authorization: Bearer →│  Your    │
│         │    <access_token>         │  Server  │
│         │ ←──── 200 + user data ────│          │
└─────────┘                          └──────────┘
              (server verifies token
               with Supabase via
               supabase.auth.get_user())
```

### Step-by-Step

1. **Sign Up** → `POST /auth/signup` with `{email, password}` → **201 Created**
2. **Log In** → `POST /auth/login` with `{email, password}` → **200 OK** + `access_token`
3. **Call Protected Route** → Include header: `Authorization: Bearer <access_token>`
4. **Log Out** → `POST /auth/logout` with Bearer token → **204 No Content**

---

## 🧪 Testing with curl

### Sign Up

```bash
curl -i -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
```

**Expected:** `HTTP/1.1 201 Created`
```json
{
  "message": "User created successfully",
  "user": {
    "id": "uuid-here",
    "email": "test@example.com",
    "created_at": "2026-08-29T10:00:00Z"
  }
}
```

### Log In

```bash
curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
```

**Expected:** `HTTP/1.1 200 OK`
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "...",
  "user": {
    "id": "uuid-here",
    "email": "test@example.com"
  }
}
```

> **Copy the `access_token` value for the next steps.**

### Public Route (No Auth)

```bash
curl -i http://localhost:8000/public/info
```

**Expected:** `HTTP/1.1 200 OK`
```json
{"message": "Welcome stranger! This info is public."}
```

### Protected Route — Missing Token

```bash
curl -i http://localhost:8000/protected/profile
```

**Expected:** `HTTP/1.1 401 Unauthorized`
```json
{"detail": "Access token required"}
```

### Protected Route — Valid Token

```bash
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Expected:** `HTTP/1.1 200 OK`
```json
{
  "message": "Profile accessed successfully",
  "user": {
    "id": "uuid-here",
    "email": "test@example.com",
    "created_at": "2026-08-29T10:00:00Z"
  }
}
```

### Protected Route — Tampered Token

Change **one character** of your token and retry:

```bash
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs...X"
```

**Expected:** `HTTP/1.1 401 Unauthorized`
```json
{"detail": "Invalid or expired token"}
```

> 🔥 **You just watched a forged pass get rejected.**

### Log Out

```bash
curl -i -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Expected:** `HTTP/1.1 204 No Content` (empty body)

---

## 🧠 Key Concepts

### The Trust Triangle

```
     Client
      / \
     /   \
    /     \
   /       \
  /    ✓    \
 /  verified  \
Supabase ←——→ Your Server
  (IdP)      (verifies token)
```

1. **Client** sends credentials → **Supabase** (Identity Provider)
2. **Supabase** validates and returns a **JWT access token**
3. **Client** sends token → **Your Server** in `Authorization: Bearer <token>` header
4. **Your Server** asks Supabase: *"Is this token real?"* → opens or refuses the door

### 401 vs 403

| Code | Meaning | Use Case |
|------|---------|----------|
| **401** | Unauthorized | *"I don't know who you are."* — Missing, malformed, or invalid token |
| **403** | Forbidden | *"I know exactly who you are, and you still may not."* — Valid token, but insufficient permissions |

> This project demonstrates **401** on all auth failures. A **403** would be used for an admin-only route that rejects regular authenticated users.

### Why We Don't Hash Passwords Ourselves

> *"Rolling your own auth is how careers end."*

Supabase Auth handles:
- ✅ Password hashing (bcrypt)
- ✅ Account storage
- ✅ JWT signing & verification
- ✅ Email confirmation (optional)
- ✅ Session management

Your server only does what matters: **receive a token, verify it, decide whether to open the door.**

---

## 🏗️ Architecture

```
flyrank-auth-api/
├── main.py              # FastAPI app + all routes
├── dependencies.py      # Reusable auth guard (get_current_user)
├── supabase_client.py   # Supabase client initialization
├── requirements.txt     # Python dependencies
├── .env.example         # Template for environment variables (committed)
├── .gitignore           # Ensures .env never reaches GitHub
└── README.md            # This file
```

### The Auth Guard (`dependencies.py`)

The `get_current_user` dependency is the heart of the security system:

1. **Extracts** the token from `Authorization: Bearer <token>`
2. **Verifies** the token with Supabase via `supabase.auth.get_user(token)`
3. **Injects** the user metadata into the route handler
4. **Rejects** forgeries with **401 Unauthorized**

Applied to any protected route with a single line:

```python
@app.get("/protected/profile")
def protected_profile(user: Annotated[dict, Depends(get_current_user)]):
    ...
```

---

## 📝 Commit History

| Stage | Commit Message | What It Covers |
|-------|----------------|----------------|
| 0 | `Stage 0: setup server and supabase client` | Project init, `.env`, `.gitignore`, Supabase client |
| 1 | `Stage 1: signup and login routes working` | `POST /auth/signup` + `POST /auth/login` |
| 2 | `Stage 2: public route and unverified protected route` | `GET /public/info` + `GET /protected/profile` (token check only) |
| 3 | `Stage 3: profile route token verification` | Full Supabase token verification on protected route |
| 4 | `Stage 4: auth middleware and logout endpoint` | Reusable `get_current_user` dependency + `POST /auth/logout` + `GET /protected/dashboard` |
| 5 | `Stage 5: Swagger UI documentation with bearer auth` | HTTPBearer security scheme + lock icons on `/docs` |
| 6 | `Stage 6: publish to GitHub and write README` | Public repo + comprehensive README |

---

## 🎁 Stretch Goals (Optional)

- [ ] **403 Forbidden** — Add an admin-only route that returns 403 for non-admin users
- [ ] **Refresh Token** — Add `POST /auth/refresh` to exchange a refresh token for a new access token
- [ ] **Rate Limiting** — Limit `POST /auth/login` to N attempts per minute, return 429 on brute-force
- [ ] **Token Expiry Experiment** — Wait 1 hour (Supabase default), call `/protected/profile` with stale token, observe 401
- [ ] **AI Rematch** — Prompt an AI to build the same API, diff it against yours, write an "AI vs Me" analysis

---

## 📄 License

MIT — Built for the **FlyRank Backend Internship, Week 4, Assignment 1**.

---

*"You never store a password and you never hash anything yourself. Supabase does that. Your code only ever sends credentials to Supabase and verifies the tokens it hands back."*
