# Mini Threat Intel Dashboard
A small Flask-based threat intelligence dashboard that ingests indicators of compromise (IOCs) from feeds and presents them in a simple analyst-style UI with authentication.

## Features

- Web dasboard showing threat indicators (IP, domain, URL, etc.)
- Filter by **type** and **source**
- Basic stats:
  - Total indicators
  - High-severity indicators (score >= 70)
  - Counts by type
  - **Recent indicators** panel, with severity badges and links to detail view
  - Indicator **detail page** for drill-down 
  - CLI command to **ingest feeds** into the database
  - **Authentication with Flask-Login and hashed passwords

## Tech Stack 

- Python / Flask
- Flask-SQLAlchemy (SQLite for storage)
- Flask-Login (session-based auth)
- Bootstrap 5 for styling

## Project Structure

project/
app.py # Flask app, routes, CLI commands
models/
init.py # Exports db, init_db, models
db.py # SQLAlchemy models + init_db
ingestion.py # Feed ingestion logic
templates/
base.html # Layout + navbar + flash messages
dashboard.html # Main dashboard UI
indicator_detail.html # Per-indicator view
login.html # Login form
static/
styles.css # Custom styling
data/
threatintel.db # SQLite database (created at runtime)
venv/ # Virtual environment (not committed)

## Getting Started
### 1. Clone and set up venv

git clone <your-repo-url>
cd threat_dashboard

python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt


### 2. Initialize the database with sample data

flask --app app.py init.db
This creates the SQLite DB and inserts a few sample indicators.

### 3. Create a user

Create a file `create_user.py`:

from app import app, db
from models import User

with app.app_context():
u = User(username="analyst")
u.set_password("test123")
db.session.add(u)
db.session.commit()
print("Created user:", u.username)

Run: python create_user.py

### 4. Run the app

python app.py
Then open:

- http://127.0.0.1:5000

Login with:

- username: `analyst`
- password: `test123`

## CLI Commands
### Initialize DB and sample data

flask --app app.py init-db
Drops all tables and recreates them with sample indicators.

## Ingest threat feeds

flaskk --app app.py ingest-feeds
Calls `ingest_all_feeds_into_db(db)` to pull indicators from configured feeds into the database.

## Security Features

This project intentionally includes basic security practices:

- **Authentication required**: Dashboard route (`/`) is protected with `@login_required` so anonymous users are redirected to `/login`.
- **Hashed passwords**: User passwords are stored as salted hashes using Werkzeug’s `generate_password_hash` / `check_password_hash`.
- **Session-based auth**: Flask-Login manages the user session via secure cookies.
- **Cookie hardening** (in `app.py`):

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.config["SESSION_COOKIE_SECURE"] = True # enable when using HTTPS

- **Per-user navbar**:
- Shows “Logged in as \<username\>” and a **Logout** button when authenticated
- Shows a **Login** button when logged out
- **Flash messages** for invalid logins so errors are not silently ignored.

### Future Security Improvements

Some next steps you could add:

- CSRF protection for forms
- Security headers (HSTS, CSP, X-Frame-Options)
- Simple roles (e.g., analyst vs. admin)
- Audit log of logins / ingestion actions

## Screens / UX

- **Dashboard**: shows stats, recent indicators, and a table of indicators filtered by type/source.
- **Indicator detail**: view a single IOC with metadata like first_seen, last_seen, score, and tags.
- **Login**: simple Bootstrap form; redirects to the dashboard on success.

## Why This Project

This app is meant as a small but realistic “mini SOC dashboard”:

- Demonstrates full-stack skills (Flask, SQLAlchemy, templates, Bootstrap).
- Shows security awareness (auth, hashing, session config).
- Uses real patterns you’d see in an internal threat intel tool (feeds, indicators, stats, recent items, drill-down).