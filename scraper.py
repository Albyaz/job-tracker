import requests
import os
from dotenv import load_dotenv
import sqlite3
from datetime import date
from rich.console import Console
from rich.table import Table

load_dotenv()

console = Console()

API_KEY = os.getenv("RAPIDAPI_KEY")

SEARCH_TARGETS = [
    {"location": "Ireland", "remote": False},
    {"location": "Europe", "remote": True},
    {"location": "United States", "remote": True},
    {"location": "Canada", "remote": True},
    {"location": "Australia", "remote": True},
]

def search_jobs(query, location="Ireland", remote=False):
    url = "https://jsearch.p.rapidapi.com/search"
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    search_query = f"{query} {location}"
    
    params = {
        "query": search_query,
        "num_pages": 1,
        "date_posted": "month",
        "remote_jobs_only": "true" if remote else "false"
    }
    
    console.print(f"[cyan]Searching: {search_query}...[/cyan]")
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    if "data" not in data or len(data["data"]) == 0:
        console.print(f"[yellow]No results found for {location}[/yellow]")
        return []
    
    jobs = []
    for job in data["data"]:
        jobs.append({
            "company": job.get("employer_name", "Unknown"),
            "role": job.get("job_title", "Unknown"),
            "location": f"{job.get('job_city') or ''}, {job.get('job_country') or ''}".strip(", "),
            "remote": "Yes" if job.get("job_is_remote") else "No",
            "salary": f"{job.get('job_min_salary', 'N/A')} - {job.get('job_max_salary', 'N/A')}",
            "link": job.get("job_apply_link", ""),
            "description": job.get("job_description", "")[:200]
        })
    
    return jobs

def search_all_locations(query):
    all_jobs = []
    for target in SEARCH_TARGETS:
        jobs = search_jobs(query, target["location"], target["remote"])
        all_jobs.extend(jobs)
    return all_jobs

def display_scraped_jobs(jobs):
    if not jobs:
        console.print("[yellow]No jobs to display.[/yellow]")
        return
    
    table = Table(title="Scraped Job Listings")
    table.add_column("No.", style="cyan")
    table.add_column("Company", style="magenta")
    table.add_column("Role", style="green")
    table.add_column("Location")
    table.add_column("Remote", style="yellow")
    table.add_column("Salary")
    table.add_column("Link", style="blue")

    for i, job in enumerate(jobs, 1):
        table.add_row(
            str(i),
            job["company"],
            job["role"],
            job["location"],
            job["remote"],
            job["salary"],
            job["link"][:40] + "..." if len(job["link"]) > 40 else job["link"]
        )
    
    console.print(table)

def save_job_to_tracker(job):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs (company, role, location, salary, status, date_applied, link, notes)
        VALUES (?, ?, ?, ?, 'Interested', ?, ?, ?)
    """, (
        job["company"],
        job["role"],
        job["location"],
        job["salary"],
        str(date.today()),
        job["link"],
        job["description"]
    ))
    conn.commit()
    conn.close()
    console.print(f"[green]{job['role']} at {job['company']} saved to tracker![/green]")

def handle_search(query):
    jobs = search_all_locations(query)
    display_scraped_jobs(jobs)
    if jobs:
        save = input("\nEnter job number to save to tracker (or press Enter to skip): ")
        if save.isdigit() and 1 <= int(save) <= len(jobs):
            save_job_to_tracker(jobs[int(save) - 1])

def scraper_menu():
    while True:
        console.print("\n[bold cyan]===== Job Scraper =====[/bold cyan]")
        console.print("[dim]Ireland (on-site) + Europe, US, Canada, Australia (remote)[/dim]")
        console.print("\n1. Search Data Engineer jobs")
        console.print("2. Search Data Analyst jobs")
        console.print("3. Search Digital Health jobs")
        console.print("4. Custom search")
        console.print("5. Exit")

        choice = input("\nChoose an option: ")

        if choice == "1":
            handle_search("Data Engineer")
        elif choice == "2":
            handle_search("Data Analyst")
        elif choice == "3":
            handle_search("Digital Health")
        elif choice == "4":
            query = input("Enter job title to search: ")
            handle_search(query)
        elif choice == "5":
            console.print("[green]Goodbye![/green]")
            break
        else:
            console.print("[red]Invalid option, try again.[/red]")

scraper_menu()