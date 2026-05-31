# Job Tracker & Scraper

A full-stack job application tracker and scraper built with Python, Flask, and SQLite.

Built by Albright Ndamati — Data Personnel and Digital Health product builder.

---

## What It Does

This platform has two core features:

**1. Job Tracker**
- Add job applications manually with full details
- View all applications in a clean dashboard
- Filter by status — Interested, Applied, Interview, Offer, Rejected
- Update application status with one click
- Delete applications
- Stats overview showing total jobs, applications, interviews, and offers

**2. Job Scraper**
- Search for jobs across Ireland (on-site), Europe, US, Canada, and Australia (remote)
- Quick search buttons for Data Engineer, Data Analyst, Digital Health, Product Analyst, Business Analyst
- Save any scraped job directly to your tracker with one click
- Powered by JSearch API via RapidAPI

---

## Tech Stack

- Python 3.11
- Flask (web framework)
- SQLite3 (database)
- Rich (CLI formatting)
- JSearch API via RapidAPI (job data)
- HTML/CSS (frontend)

---

## Project Structure
job_tracker/
├── app.py              # Flask web application
├── tracker.py          # CLI job tracker
├── scraper.py          # CLI job scraper
├── templates/
│   ├── index.html      # Dashboard
│   ├── add_job.html    # Add job form
│   └── scraper.html    # Scraper page
├── static/             # Static assets
├── .env                # API keys (not committed)
├── .gitignore
└── README.md

---

## How to Run

```bash
# Clone the repo
git clone https://github.com/Albyaz/job-tracker.git
cd job-tracker

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask requests python-dotenv rich

# Add your RapidAPI key
echo "RAPIDAPI_KEY=your_key_here" > .env

# Run the web app
python app.py
```

Then open your browser and go to **http://127.0.0.1:5000**

---

## Roadmap

- [ ] Parallel API requests for faster scraping
- [ ] Export applications to CSV
- [ ] Email alerts for new matching jobs
- [ ] Deploy online so it's accessible from anywhere
- [ ] User authentication for sharing with friends

---

## Author

**Albright Ndamati**