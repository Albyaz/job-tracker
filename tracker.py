
import sqlite3
from datetime import date
from rich.console import Console
from rich.table import Table

console = Console()

def init_db():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            location TEXT,
            salary TEXT,
            status TEXT DEFAULT 'Applied',
            date_applied TEXT,
            link TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_job(company, role, location, salary, link, notes):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs (company, role, location, salary, status, date_applied, link, notes)
        VALUES (?, ?, ?, ?, 'Applied', ?, ?, ?)
    """, (company, role, location, salary, str(date.today()), link, notes))
    conn.commit()
    conn.close()
    console.print(f"[green]Job at {company} added successfully![/green]")

def view_jobs():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, company, role, location, salary, status, date_applied FROM jobs")
    jobs = cursor.fetchall()
    conn.close()

    if not jobs:
        console.print("[yellow]No jobs found. Start adding some![/yellow]")
        return

    table = Table(title="My Job Applications")
    table.add_column("ID", style="cyan")
    table.add_column("Company", style="magenta")
    table.add_column("Role", style="green")
    table.add_column("Location")
    table.add_column("Salary")
    table.add_column("Status", style="yellow")
    table.add_column("Date Applied")

    for job in jobs:
        table.add_row(str(job[0]), job[1], job[2], job[3] or "-", job[4] or "-", job[5], job[6] or "-")

    console.print(table)

def update_status(job_id, new_status):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET status = ? WHERE id = ?", (new_status, job_id))
    conn.commit()
    conn.close()
    console.print(f"[blue]Job {job_id} updated to '{new_status}'[/blue]")

def delete_job(job_id):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
    console.print(f"[red]Job {job_id} deleted.[/red]")

def main_menu():
    while True:
        console.print("\n[bold cyan]===== Job Tracker =====[/bold cyan]")
        console.print("1. View all jobs")
        console.print("2. Add a job")
        console.print("3. Update job status")
        console.print("4. Delete a job")
        console.print("5. Exit")

        choice = input("\nChoose an option: ")

        if choice == "1":
            view_jobs()
        elif choice == "2":
            company = input("Company name: ")
            role = input("Role: ")
            location = input("Location: ")
            salary = input("Salary: ")
            link = input("Job link: ")
            notes = input("Notes: ")
            add_job(company, role, location, salary, link, notes)
        elif choice == "3":
            view_jobs()
            job_id = int(input("Enter job ID to update: "))
            new_status = input("New status (Applied/Interview/Offer/Rejected): ")
            update_status(job_id, new_status)
        elif choice == "4":
            view_jobs()
            job_id = int(input("Enter job ID to delete: "))
            delete_job(job_id)
        elif choice == "5":
            console.print("[green]Goodbye![/green]")
            break
        else:
            console.print("[red]Invalid option, try again.[/red]")

# Run
init_db()
main_menu()