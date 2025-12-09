import requests
from datetime import datetime
from typing import List, Dict

from flask_sqlalchemy import SQLAlchemy
from flask import current_app

#Import the model dynamically to avoid circular imports
#ThreatIndicator is defined in app.py

def _now():
    return datetime.utcnow()

def fetch_feed_json_ip_list(url: str, source_name: str) -> List[Dict]:
    """
    Example JSON feed: 
    [ 
      {"ip": "1.2.3.4", "score": 50, "tags": ["botnet"]},
      ...
      ]
      Normalize to a common format used by the app.
    """

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    indicators: List[Dict] = []
    for item in data:
        ip = item.get("ip")
        if not ip:
            continue
        indicators.append(
            {
                "indicator": ip,
                "type": "ip",
                "source": source_name,
                "first_seen": _now(),
                "last_seen": _now(),
                "score": int(item.get("score", 50)),
                "tags": ",".join(item.get("tags", [])),
            }
        )
    return indicators

def fetch_feed_text_indicator_list(
    url: str, source_name: str, ind_type: str
) -> List[Dict]:
    """
    Example text feed:
      # comment
      bad-example.com
      8.8.8.8
    One indicator per line.
    """
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    lines = resp.text.splitlines()

    indicators: List[Dict] = []
    for line in lines:
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        indicators.append(
            {
                "indicator": value,
                "type": ind_type,
                "source": source_name,
                "first_seen": _now(),
                "last_seen": _now(),
                "score": 40,
                "tags": "",
            }
        )

    # IMPORTANT: this must be OUTSIDE the for-loop
    return indicators
    
from pathlib import Path

def fetch_all_feeds() -> List[Dict]:
    all_indicators: List[Dict] = []

    try:
        text_feed_url = "https://raw.githubusercontent.com/bitwire-it/ipblocklist/refs/heads/main/inbound.txt"
        all_indicators.extend(
            fetch_feed_text_indicator_list(
                text_feed_url,
                source_name="BitwireInbound",
                ind_type="ip",
            )
        )
    except Exception as exc:
        print(f"[WARN] Failed to fetch text IP feed: {exc}")

    return all_indicators
    
def ingest_all_feeds_into_db(db: SQLAlchemy):
    """
    Fetch all feeds and upsert into the database using the ThreatIndicator model defined in app.py.
    """
    from app import ThreatIndicator #local import to avoid circular dependency

    indicators = fetch_all_feeds()
    print(f"[INFO] Fetched {len(indicators)} indicators from all feeds.")

    for item in indicators:
        ind_value = item["indicator"]
        ind_type = item["type"]
        source_name = item["source"]

        #Check if this indicator already exists from this source
        existing = (
            ThreatIndicator.query.filter_by(
                indicator=ind_value,
                type=ind_type,
                source=source_name,
            )
            .order_by(ThreatIndicator.id.desc())
            .first()
        )

        if existing:
            #Update last_seen and maybe bump score
            existing.last_seen = _now()
            existing.score = max(existing.score, item["score"])
            #Merge tags
            existing_tags = set(
                filter(None, (existing.tags or "").split(","))
            )
            new_tags = set(
                filter(None, (item.get("tags") or "").split(","))
            )
            merged = existing_tags.union(new_tags)
            existing.tags = ",".join(sorted(merged))
        else:
            #insert new row
            new_row = ThreatIndicator(
                indicator=ind_value,
                type=ind_type,
                source=source_name,
                first_seen=item["first_seen"],
                last_seen=item["last_seen"],
                score=item["score"],
                tags=item.get("tags", ""),
            )
            db.session.add(new_row)

        db.session.commit()
        print("[INFO] Finished ingesting indicators into the database.")