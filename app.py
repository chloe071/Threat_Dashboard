import os
from flask import Flask, render_template, request
from models import db, init_db, ThreatIndicator
from sqlalchemy import func 
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

# ---------- Config & App Setup ---------- #

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "threatintel.db")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "change-me-please-123"

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# initialize db + create tables
init_db(app)

# ---------- CLI helper to init DB with sample data ---------- #

@app.cli.command("init-db")
def init_db_command():
    """Initialize the database and add some sample indicators."""
    from models import ThreatIndicator  # ensure model is loaded

    db.drop_all()
    db.create_all()

    sample_rows = [
        ThreatIndicator(
            indicator="192.168.10.5",
            type="ip",
            source="SampleFeedA",
            score=20,
            tags="internal,suspicious",
        ),
        ThreatIndicator(
            indicator="malicious-example.com",
            type="domain",
            source="SampleFeedB",
            score=80,
            tags="phishing,high-risk",
        ),
        ThreatIndicator(
            indicator="http://bad-url.example/path",
            type="url",
            source="SampleFeedA",
            score=60,
            tags="malware,download",
        ),
    ]

    db.session.add_all(sample_rows)
    db.session.commit()
    print("Database initialized with sample data.")

# ---------- Routes ---------- #

@app.route("/")
@login_required
def dashboard():
    # Filters from query params
    indicator_type = request.args.get("type", "").strip()
    source = request.args.get("source", "").strip()

    query = ThreatIndicator.query

    if indicator_type:
        query = query.filter(ThreatIndicator.type == indicator_type)

    if source:
        query = query.filter(ThreatIndicator.source == source)

    indicators = (
        query.order_by(ThreatIndicator.score.desc())
        .limit(100)
        .all()
    )

    # For dropdowns
    distinct_types = [row[0] for row in db.session.query(ThreatIndicator.type).distinct()]
    distinct_sources = [row[0] for row in db.session.query(ThreatIndicator.source).distinct()]

    total_count = db.session.query(func.count(ThreatIndicator.id)).scalar()

    high_count = (
        db.session.query(func.count(ThreatIndicator.id))
        .filter(ThreatIndicator.score >= 70)
        .scalar()
    )

    count_by_type = (
        db.session.query(ThreatIndicator.type, func.count(ThreatIndicator.id))
        .group_by(ThreatIndicator.type)
        .all()
    )

    recent_indicators = (
        ThreatIndicator.query.order_by(ThreatIndicator.first_seen.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard.html",
        indicators=indicators,
        indicator_type=indicator_type,
        source=source,
        distinct_types=distinct_types,
        distinct_sources=distinct_sources,
        total_count=total_count,
        high_count=high_count,
        count_by_type=count_by_type,
    )

from ingestion import ingest_all_feeds_into_db

@app.cli.command("ingest-feeds")
def ingest_feeds_command():
    """Fetch threat feeds and store indicators in the database."""
    ingest_all_feeds_into_db(db)
    print("Finished ingesting feeds.")

@app.route("/indicator/<int:ind_id>")
def indicator_detail(ind_id):
    ind = ThreatIndicator.query.get_or_404(ind_id)
    return render_template("indicator_detail.html", indicator=ind)

from flask import request, redirect, url_for, flash, render_template
from flask_login import login_user
from models import User

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "danger")
        return render_template("login.html")

    return render_template("login.html")

from flask_login import logout_user, login_required

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ---------- Entry point ---------- #

if __name__ == "__main__":
    app.run(debug=True)
