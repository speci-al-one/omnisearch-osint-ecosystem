"""PhoneIntel — free phone-number validation via numverify API.

Free tier: 100 requests/month after a free API key (https://numverify.com).
Returns validity, country, carrier and line type — NOT the owner's identity.
"""

import os
import sqlite3
import requests
from rich.console import Console
from rich.table import Table

console = Console()


class PhoneIntel:
    def __init__(self, phone, target_id="STANDALONE"):
        self.phone = phone
        self.target_id = target_id
        self.result = {}

    def query(self):
        """numverify API yoki demo rejim — natijani qaytaradi."""
        api_key = os.environ.get("NUMVERIFY_API_KEY", "")
        if not api_key:
            self.result = {
                "phone": self.phone,
                "valid": "demo",
                "error": "No NUMVERIFY_API_KEY set — demo mode. Get a free key at https://numverify.com",
            }
            return self.result

        url = "https://apilayer.net/api/validate"
        params = {"access_key": api_key, "number": self.phone}
        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get("valid"):
                self.result = {
                    "phone": self.phone,
                    "valid": True,
                    "country": data.get("country_name", "Unknown"),
                    "location": data.get("location", "N/A"),
                    "carrier": data.get("carrier", "Unknown"),
                    "line_type": data.get("line_type", "Unknown"),
                }
            else:
                self.result = {"phone": self.phone, "valid": False,
                               "error": data.get("error", {}).get("info", "invalid number")}
        except Exception as e:
            self.result = {"phone": self.phone, "valid": False, "error": str(e)}
        return self.result

    def display(self):
        """Natijani jadval ko'rinishida chiqaradi."""
        table = Table(title=f"Phone Intelligence — {self.phone}", border_style="cyan")
        table.add_column("Parameter", style="bold cyan")
        table.add_column("Value", style="white")
        for k, v in self.result.items():
            table.add_row(k, str(v))
        console.print(table)

    def save_to_database(self):
        """Natijani osint_root.db ga yozadi."""
        conn = sqlite3.connect("osint_root.db")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS phone_intel_data (
            target_id TEXT, phone TEXT, valid TEXT, country TEXT,
            location TEXT, carrier TEXT, line_type TEXT
        )""")
        conn.execute(
            "INSERT INTO phone_intel_data VALUES (?, ?, ?, ?, ?, ?, ?)",
            (self.target_id, self.result.get("phone"),
             str(self.result.get("valid", "")), self.result.get("country", ""),
             self.result.get("location", ""), self.result.get("carrier", ""),
             self.result.get("line_type", "")),
        )
        conn.commit()
        conn.close()
        console.print("[bold green][+] PhoneIntel stored in the central database.[/bold green]")


if __name__ == "__main__":
    phone = input("Enter phone number: ").strip()
    engine = PhoneIntel(phone)
    engine.query()
    engine.display()
    engine.save_to_database()
