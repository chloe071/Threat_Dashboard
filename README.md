# Mini Threat Intel Dashboard

![tests](https://github.com/chloe071/Threat_Dashboard/actions/workflows/tests.yml/badge.svg)

A Flask-based threat intelligence dashboard that ingests indicators of compromise (IOCs) from feeds and presents them in a simple analyst-style UI with authentication.

<!-- Screenshot: add docs/dashboard.png and uncomment the line below -->
<!-- ![Dashboard screenshot](docs/dashboard.png) -->

## Example Workflow

1. Load sample indicators with `flask --app app.py init-db`.
2. Log in and filter indicators by **type** or **source**.
3. Open an indicator to inspect its score, tags, and first/last seen dates.

## Features

- Web dashboard showing threat indicators (IP, domain, URL)
- Filter by **type** and **source**
- Summary stats: total indicators, high-severity indicators (score >= 70), counts by type
- **Recent indicators** panel with severity badges
- Indicator **detail page** for drill-down
- CLI command to **ingest feeds** into the database
- **Authentication** with Flask-Login and hashed passwords

## Tech Stack

- Python / Flask
- Flask-SQLAlchemy (SQLite)
- Flask-Login (session-based auth)
- Bootstrap 5
- pytest + GitHub Actions

## Project Structure

```text
Threat_Dashboard/
├── app.py              # Flask app, routes, CLI commands
├── config.py           # Configuration helpers
├── create_user.py      # Creates a local login user
├── models/
│   ├── __init__.py     # Exports db, init_db, models
│   └── db.py           # SQLAlchemy models + init_db
├── ingestion/
│   └── feeds.py        # Feed ingestion logic
├── feeds/domains.txt   # Sample feed
├── templates/          # base, dashboard, indicator_detail, login
├── static/styles.css
├── data/threatintel.db # SQLite database
└── tests/test_auth.py  # Authentication tests
```

## Getting Started

### 1. Clone and set up a virtual environment

```bash
git clone https://github.com/chloe071/Threat_Dashboard.git
cd Threat_Dashboard
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set a secret key

```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

If `SECRET_KEY` is not set, a random key is generated at startup (sessions reset when the app restarts).

### 3. Initialize the database with sample data

```bash
flask --app app.py init-db
```

This drops and recreates the tables, then inserts sample indicators.

### 4. Create a user

```bash
python create_user.py analyst
```

You'll be prompted for a password (minimum 8 characters). Nothing is hardcoded.

### 5. Run the app

```bash
python app.py
```

Open http://127.0.0.1:5000 and log in with the account you created.

## CLI Commands

| Command | What it does |
|---|---|
| `flask --app app.py init-db` | Drops all tables and recreates them with sample indicators |
| `flask --app app.py ingest-feeds` | Calls `ingest_all_feeds_into_db(db)` to load indicators from configured feeds |

## Running Tests

```bash
pip install pytest
pytest -q
```

The tests verify that anonymous users are redirected from protected pages, wrong passwords are rejected, and valid logins succeed. They run automatically on every push via GitHub Actions.

## Security Features

- **Authentication required** on the dashboard (`/`) and indicator detail pages via `@login_required`.
- **Hashed passwords** using Werkzeug's `generate_password_hash` / `check_password_hash`.
- **Secret key from environment** instead of a hardcoded value.
- **Cookie hardening**: `SESSION_COOKIE_HTTPONLY` and `SESSION_COOKIE_SAMESITE="Lax"`. Set `SESSION_COOKIE_SECURE = True` when serving over HTTPS.
- **Debug mode off by default** (enable with `FLASK_DEBUG=1` for local development only).
- **Dependabot** checks dependencies weekly.

### Security fix log

During a review I found that the indicator detail page (`/indicator/<id>`) was reachable without logging in, even though the dashboard was protected. I added `@login_required` and a regression test (`test_indicator_detail_requires_login`) to confirm the fix. I also removed a hardcoded secret key and hardcoded demo credentials.

## Limitations

- No CSRF protection on forms yet
- No security headers (HSTS, CSP, X-Frame-Options) yet
- No roles; every logged-in user has the same access
- No audit logging of logins or ingestion
- SQLite and the Flask development server are for local use only

## Planned Improvements

- CSRF protection (Flask-WTF)
- Security headers
- Analyst vs. admin roles
- Audit log of logins and ingestion actions

## Why This Project

A small but realistic "mini SOC dashboard" that demonstrates full-stack skills (Flask, SQLAlchemy, templates, Bootstrap), security awareness (auth, hashing, session config, tests), and patterns from internal threat intel tools (feeds, indicators, stats, drill-down).
