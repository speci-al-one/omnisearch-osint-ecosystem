import requests
import sqlite3
from rich.console import Console
from rich.table import Table

console = Console()

class SocialHunter:
    def __init__(self, target_id, username):
        self.target_id = target_id
        self.username = username
        # Target URLs mapping for platform lookups
        self.platforms = {
            "GitHub": f"https://github.com{username}",
            "Instagram": f"https://instagram.com{username}",
            "Telegram": f"https://t.me{username}",
            "Reddit": f"https://reddit.com{username}",
            "Pinterest": f"https://pinterest.com{username}",
            "TikTok": f"https://tiktok.com@{username}",
            "YouTube": f"https://youtube.com@{username}",
            "Facebook": f"https://facebook.com{username}",
            "Twitter_X": f"https://x.com{username}",
            "Twitch": f"https://twitch.tv{username}"
        }
        
        }
        self.found_profiles = []

    def scan_username(self):
        """Scans multiple web platforms live using HTTP status codes"""
        console.print(f"\n[*] SocialHunter: Scanning username [bold yellow]@{self.username}[/bold yellow] across platforms...")
        
        # Standard headers to prevent web servers from blocking the request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        for platform_name, url in self.platforms.items():
            try:
                # Making a live HTTP request to check if profile profile exists (Status 200)
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    self.found_profiles.append((platform_name, url))
                    console.print(f"[bold green][+] Found:[/bold green] {platform_name} -> {url}")
                else:
                    console.print(f"[red][-] Not Found:[/red] {platform_name}")
            except Exception as e:
                console.print(f"[yellow][!] Error scanning {platform_name}: {str(e)}[/yellow]")

    def save_to_database(self):
        """Saves discovered digital footprints back to the central database"""
        if not self.found_profiles:
            return

        conn = sqlite3.connect("core_db/osint_root.db")
        cursor = conn.cursor()

        # Creates the social footprint table if not exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS social_footprints (
            target_id TEXT,
            platform_name TEXT,
            profile_url TEXT
        )""")

        # Inserting each discovered platform under the unified target_id (Rooting Pipeline)
        for platform_name, url in self.found_profiles:
            cursor.execute("""
            INSERT INTO social_footprints (target_id, platform_name, profile_url)
            VALUES (?, ?, ?)
            """, (self.target_id, platform_name, url))

        conn.commit()
        conn.close()
        console.print("[bold green][+] Footprints stored in Central Database successfully![/bold green]")

if __name__ == "__main__":
    # Local module debugging test
    hunter = SocialHunter(target_id="OSINT-UUID-TEST", username="johndoe")
    hunter.scan_username()
    hunter.save_to_database()
