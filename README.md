# AI-Driven Hyper-Local Business Advisory and Financial Structuring Assistant for Rural Micro-Entrepreneurs

A complete, server-rendered **Python & Django** web application designed to help rural micro-entrepreneurs, Self-Help Groups (SHGs), and Farmer Producer Organizations (FPOs) evaluate hyper-local business opportunities, structure accurate financial plans using `Decimal` arithmetic, log local mandi/market observations, explore verified government funding schemes, and generate print-ready & PDF-exportable project dossiers.

---

## 1. Architecture & Technology Stack

- **Backend**: Python 3.11+, Django 4.2+ / 5.x, Django ORM, Django Authentication System, ReportLab (PDF generation)
- **Database**: SQLite (`db.sqlite3`) by default for development; PostgreSQL-ready via environment variables
- **Frontend**: Server-rendered Django Templates (`.html`) using Django Template Language (DTL), semantic HTML5, modern CSS3 (`Flexbox` & `Grid` in `main.css`, `dashboard.css`, `responsive.css`), and optional progressive-enhancement Vanilla JavaScript (`main.js`)
- **Zero SPA / Zero Frontend Build Dependencies**: No React, Vue, Angular, Tailwind, Vite, or Node.js build chain

### Project Structure

```text
rural_business_advisor/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/               # Registration, login, logout, password reset, UserProfile
├── dashboard/              # Dynamic Entrepreneur Dashboard & public landing page
├── business_advisor/       # AI provider service layer + deterministic Rule-Based Fallback Engine
├── financial_planning/     # Decimal financial calculation engine, break-even, EMI, 3-scenario stress test
├── market_insights/        # Hyper-local field observations CRUD + 6 verified Govt schemes + seed command
├── reports/                # Saved reports, scenario comparison tool, print view, ReportLab PDF export
├── templates/              # Shared base.html, reusable components/, and app template directories
├── static/                 # CSS (main.css, dashboard.css, responsive.css), JS (main.js), SVG logo
├── requirements.txt
├── .env.example
└── README.md
```

---

## 2. Setup & Installation Instructions

### Step 1: Clone or Extract the Project & Create a Virtual Environment

```bash
cd rural_business_advisor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables (Optional)

Copy `.env.example` to `.env` and adjust settings as needed:

```bash
cp .env.example .env
```

- **Database Configuration**: Uses SQLite (`db.sqlite3`) out of the box. To use PostgreSQL in production, set `DB_ENGINE=django.db.backends.postgresql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`.
- **External AI Provider Configuration**: By default, `AI_PROVIDER_ENABLED=False`, and the application uses its built-in **Rule-Based Hyper-Local Advisory Engine** (explicitly labelled in the UI). To enable an OpenAI-compatible LLM provider, set:
  ```ini
  AI_PROVIDER_ENABLED=True
  AI_API_KEY=your-api-key
  AI_API_URL=https://api.openai.com/v1/chat/completions
  AI_MODEL_NAME=gpt-4o-mini
  AI_TIMEOUT_SECONDS=12
  AI_RATE_LIMIT_PER_HOUR=15
  ```
  If the external AI API times out, returns malformed JSON, or hits the per-user hourly rate limit, the service layer automatically falls back to the Rule-Based Engine without crashing.

### Step 3: Run Database Migrations

```bash
python3 manage.py migrate
```

### Step 4: Seed Verified Government Schemes & Optional Demo Data

To seed the 6 official central government schemes (PMEGP, PMMY-MUDRA, PMFME, DAY-NRLM, Stand-Up India, AIF) and a complete demo rural entrepreneur account (`demo_kisan` / `RuralPass@2026`):

```bash
python3 manage.py seed_demo_data
```

To seed only the government schemes without the demo user:

```bash
python3 manage.py seed_demo_data --schemes-only
```

### Step 5: Run the Automated Test Suite

```bash
python3 manage.py check
python3 manage.py test
```

### Step 6: Start the Development Server

```bash
python3 manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.
- **Demo Credentials**: Username `demo_kisan` | Password `RuralPass@2026`
