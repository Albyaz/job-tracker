from flask import Flask, render_template, request, redirect, url_for
from concurrent.futures import ThreadPoolExecutor
import sqlite3
from datetime import date
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("RAPIDAPI_KEY")

LOCATIONS = [
    {"location": "Ireland", "remote": False},
    {"location": "Europe", "remote": True},
    {"location": "United States", "remote": True},
    {"location": "Canada", "remote": True},
    {"location": "Australia", "remote": True},
]

def get_db():
    conn = sqlite3.connect("jobs.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            location TEXT,
            salary TEXT,
            status TEXT DEFAULT 'Interested',
            date_applied TEXT,
            link TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

def fetch_jobs_for_location(query, target):
    search_query = f"{query} {target['location']}"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    params = {
        "query": search_query,
        "num_pages": 1,
        "date_posted": "month",
        "remote_jobs_only": "true" if target["remote"] else "false"
    }
    try:
        response = requests.get(
            "https://jsearch.p.rapidapi.com/search",
            headers=headers,
            params=params,
            timeout=10
        )
        data = response.json()
        if "data" in data:
            return [{
                "company": job.get("employer_name", "Unknown"),
                "role": job.get("job_title", "Unknown"),
                "location": f"{job.get('job_city') or ''}, {job.get('job_country') or ''}".strip(", "),
                "remote": "Yes" if job.get("job_is_remote") else "No",
                "salary": f"{job.get('job_min_salary', 'N/A')} - {job.get('job_max_salary', 'N/A')}",
                "link": job.get("job_apply_link", ""),
                "description": job.get("job_description", "")[:200]
            } for job in data["data"]]
    except Exception:
        return []
    return []

# ── Dashboard ──
@app.route("/")
def index():
    status_filter = request.args.get("status", "All")
    conn = get_db()
    if status_filter != "All":
        jobs = conn.execute("SELECT * FROM jobs WHERE status = ? ORDER BY id DESC", (status_filter,)).fetchall()
    else:
        jobs = conn.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", jobs=jobs, status_filter=status_filter)

# ── Add Job ──
@app.route("/add", methods=["GET", "POST"])
def add_job():
    if request.method == "POST":
        conn = get_db()
        conn.execute("""
            INSERT INTO jobs (company, role, location, salary, status, date_applied, link, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form["company"],
            request.form["role"],
            request.form["location"],
            request.form["salary"],
            request.form["status"],
            str(date.today()),
            request.form["link"],
            request.form["notes"]
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add_job.html")

# ── Update Status ──
@app.route("/update/<int:job_id>", methods=["POST"])
def update_status(job_id):
    conn = get_db()
    conn.execute("UPDATE jobs SET status = ? WHERE id = ?", (request.form["status"], job_id))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# ── Delete Job ──
@app.route("/delete/<int:job_id>")
def delete_job(job_id):
    conn = get_db()
    conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# ── Scraper ──
@app.route("/scraper", methods=["GET", "POST"])
def scraper():
    jobs = []
    query = ""
    if request.method == "POST":
        query = request.form["query"]
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(
                lambda t: fetch_jobs_for_location(query, t),
                LOCATIONS
            ))
        for result in results:
            jobs.extend(result)
    return render_template("scraper.html", jobs=jobs, query=query)