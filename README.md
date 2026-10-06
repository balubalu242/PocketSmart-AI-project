# PocketSmart AI

PocketSmart AI is a FastAPI + Jinja2 web application that turns a user's budget and preferences into structured recommendations for:

- Home interior planning
- Party/event planning
- Jewelry planning, including an optional outfit image
- Recommendation history and saved planning sessions
- User registration/login with JWT-backed session cookies
- Gemini-powered recommendation generation with a deterministic mock fallback

The project follows the architecture described in the supplied project documentation: FastAPI routes, modular services, Jinja2 templates, authentication/session endpoints, three planner endpoints, history, and a Gemini utility/service layer.

## Important implementation note

The supplied document names "Gemini 1.5 Flash Pro". Model availability changes over time, so the application does not hard-code that model. Set `GEMINI_MODEL` in `.env` to the model available to your Gemini API key. The default is `gemini-2.5-flash`, which supports text and image input and structured JSON output.

The app also includes a mock catalog layer. It does NOT pretend to have live Amazon/Flipkart/IKEA/Swiggy/Zomato/OYO inventory. When real provider APIs are available, replace the catalog adapter with those integrations.

## Features

- Responsive browser UI
- Home, Party and Jewelry planners
- Budget validation and sensible budget allocation
- Optional image upload for Jewelry Planner
- Structured Gemini output using Pydantic
- Fallback recommendations when Gemini is unavailable
- SQLite persistence with no external database server
- Password hashing using PBKDF2-HMAC
- JWT access tokens stored in an HttpOnly cookie
- Protected dashboard/history/API routes
- API endpoint `/recommendations-details`
- API endpoint `/session-info`
- API endpoint `/session-data`
- API endpoint `/history`
- `/startup` health/config endpoint
- Automated API tests
- `.env` configuration
- No API keys committed to source control

## Project structure

```text
PocketSmartAI/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── auth.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── pages.py
│   │   ├── planners.py
│   │   └── session.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── catalog.py
│   │   ├── gemini_service.py
│   │   └── planner_service.py
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── history.html
│       ├── home_planner.html
│       ├── party_planner.html
│       ├── jewelry_planner.html
│       └── recommendations.html
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── data/
├── uploads/
├── .env.example
├── .gitignore
├── requirements.txt
└── run.py
```

## VS Code setup

### 1. Requirements

Install:

- Python 3.11 or newer
- VS Code
- VS Code Python extension

A Gemini API key is optional for the first local test because the application automatically falls back to mock recommendations.

### 2. Open the project

Open the `PocketSmartAI` folder in VS Code.

### 3. Create a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure environment

Copy `.env.example` to `.env`.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

For Gemini-powered responses, put your key in:

```env
GEMINI_API_KEY=your_key_here
```

If no key is supplied, leave it blank. The fallback catalog still makes the application usable.

### 6. Run

```bash
python run.py
```

Or:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

### 7. Test

```bash
pytest -q
```

The tests use the application without requiring a Gemini API key.

## Gemini configuration

`.env` supports:

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
```

The service requests structured JSON and validates it with Pydantic. If Gemini fails, the planner service returns deterministic fallback recommendations instead of crashing the application.

## Planner API examples

### Home

```http
POST /generate-home
Content-Type: application/json

{
  "budget": 50000,
  "rooms": [
    {
      "room_type": "Living Room",
      "quantity": 1,
      "items": ["sofa", "lighting", "rug"]
    }
  ],
  "style": "modern",
  "city": "Chennai",
  "notes": "Warm neutral colors"
}
```

### Party

```http
POST /generate-party
Content-Type: application/json

{
  "budget": 30000,
  "guest_count": 30,
  "event_type": "birthday",
  "venue": "home",
  "city": "Chennai",
  "food_preference": "vegetarian",
  "notes": "Evening event"
}
```

### Jewelry

Use multipart form data:

```text
budget=15000
occasion=wedding
style=traditional
metal_preference=gold-tone
notes=Prefer lightweight pieces
image=<optional image file>
```

## Security notes

This is a portfolio/academic application, not a production financial service.

Before production deployment:

- Use HTTPS.
- Set a strong `SECRET_KEY`.
- Use a managed database.
- Add CSRF protection if using cookie-authenticated state-changing browser forms.
- Add rate limiting.
- Store uploads outside the application process and validate/scan them.
- Add provider-specific API authentication and terms-compliant integrations.
- Use a production ASGI process manager.
- Add structured logging and monitoring.

## Troubleshooting

### Gemini errors

The application catches Gemini errors and uses fallback recommendations. Check:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- API quota
- network access

### Port already in use

```bash
uvicorn app.main:app --reload --port 8001
```

Then open `http://127.0.0.1:8001`.

### Database reset

Stop the server and delete:

```text
data/pocketsmart.db
```

Then restart the application.
