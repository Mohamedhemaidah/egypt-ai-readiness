import sqlite3, json, uuid
from datetime import datetime, timezone
from pathlib import Path
DB = Path(__file__).resolve().parent / "data" / "assessments.db"

def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    return sqlite3.connect(DB,timeout=20)

def initialize_database():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS assessments(
        id TEXT PRIMARY KEY, submitted_at TEXT NOT NULL, profile TEXT NOT NULL,
        answers TEXT NOT NULL, results TEXT NOT NULL)""")
        c.commit()

def save_submission(profile,answers,results):
    aid=str(uuid.uuid4())
    timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect() as c:
        c.execute("INSERT INTO assessments VALUES(?,?,?,?,?)",
        (aid,timestamp,json.dumps(profile,ensure_ascii=False),
         json.dumps(answers,ensure_ascii=False),json.dumps(results,ensure_ascii=False)))
        c.commit()
    return aid

def get_all_assessments():
    with connect() as c:
        c.row_factory=sqlite3.Row
        rows=c.execute("SELECT * FROM assessments ORDER BY submitted_at DESC").fetchall()
    return [dict(r) for r in rows]
