"""CyberTrace Hub — checks an email against known data-breach sources.

Default: clearly-labelled DEMO (simulated) response.
Optional: set the HIBP_API_KEY environment variable to query the real
HaveIBeenPwned API (free key at https://haveibeenpwned.com/API/Key).
"""

import os
import sqlite3
import requests
from rich.console import Console
from rich.table import Table

console = Console()

# Simulated data keeps the pipeline runnable without any API key.
DEMO_BREACHES = [
    {"source": "LinkedIn Mega-Leak (simulated)", "date": "2021-05-12",
     "leaked_info": "Passwords, emails, professional titles"},
    {"source": "Canva Database Breach (simulated)", "date": "2019-11-24",
     "leaked_info": "Bcrypt hashes, usernames"},
    {"source": "Adobe Leak Archive (simulated)", "date": "2013-10-04",
     "leaked_info": "Password hints, names, plaintext passwords"},
]


class CyberTraceHub:
    def __init__(self, target_id, target_email):
        self.target_id = target_id
        self.target_email = target_email
        self.breach_results = []

    def check_data_breaches(self):
        console.print(f"\n[*] CyberTrace: auditing breaches for {self.target_email}...")
        api_key = os.environ.get("HIBP_API_KEY", "")

        if api_key:
            self._query_hibp(api_key)
        else:
            console.print("[yellow][!] No HIBP_API_KEY set — using simulated demo data.[/yellow]")
            self._load_simulated()

        self._display_security_report()

    def _query_hibp(self, api_key):
        """Query the real HaveIBeenPwned API."""
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{self.target_email}"
        headers = {"hibp-api-key": api_key, "user-agent": "OmniSearch-OSINT"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                for breach in response.json():
                    self.breach_results.append({
                        "source": breach.get("Name", "Unknown Source"),
                        "date": breach.get("BreachDate", "Unknown Date"),
                        "leaked_info": ", ".join(breach.get("DataClasses", ["Unknown"])),
                    })
            elif response.status_code == 404:
                console.print("[green][+] No known breaches for this email.[/green]")
            else:
                console.print(f"[yellow][!] HIBP returned {response.status_code} — using simulated data.[/yellow]")
                self._load_simulated()
        except requests.RequestException as e:
            console.print(f"[yellow][!] HIBP error ({e}) — using simulated data.[/yellow]")
            self._load_simulated()

    def _load_simulated(self):
        self.breach_results = list(DEMO_BREACHES)

    def _display_security_report(self):
        table = Table(title="Data Breach Audit", border_style="red")
        table.add_column("Leaked Data Source", style="bold red")
        table.add_column("Breach Date", style="yellow")
        table.add_column("Exposed Info", style="white")
        for breach in self.breach_results:
            table.add_row(breach["source"], breach["date"], breach["leaked_info"])
        console.print(table)

    def save_to_database(self):
        conn = sqlite3.connect("osint_root.db")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cyber_leaks (
            target_id TEXT, leak_source TEXT, breach_date TEXT, exposed_data TEXT
        )""")
        for breach in self.breach_results:
            cursor.execute(
                "INSERT INTO cyber_leaks (target_id, leak_source, breach_date, exposed_data) "
                "VALUES (?, ?, ?, ?)",
                (self.target_id, breach["source"], breach["date"], breach["leaked_info"]),
            )
        conn.commit()
        conn.close()
        console.print("[bold green][+] Breach data stored in the central database.[/bold green]")


if __name__ == "__main__":
    tracker = CyberTraceHub(target_id="OSINT-UUID-LEAK-TEST", target_email="test_target@gmail.com")
    tracker.check_data_breaches()
    tracker.save_to_database()
