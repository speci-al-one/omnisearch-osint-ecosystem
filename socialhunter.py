"""SocialHunter — checks if a username exists across multiple social platforms."""

import requests
import sqlite3
from rich.console import Console

console = Console()


class SocialHunter:
    def __init__(self, target_id, username):
        self.target_id = target_id
        self.username = username
        self.platforms = {
            "GitHub": f"https://github.com/{username}",
            "Instagram": f"https://instagram.com/{username}",
            "Telegram": f"https://t.me/{username}",
            "Reddit": f"https://reddit.com/{username}",
            "Pinterest": f"https://pinterest.com/{username}",
            "TikTok": f"https://tiktok.com/@{username}",
            "YouTube": f"https://youtube.com/@{username}",
            "Facebook": f"https://facebook.com/{username}",
            "Twitter_X": f"https://x.com/{username}",
            "Twitch": f"https://twitch.tv/{username}",
        }
        self.found_profiles = []

    def scan_username(self):
        """Check each platform and collect profiles that return HTTP 200."""
        console.print(f"\n[*] SocialHunter: scanning @{self.username} across platforms...")

        headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/124.0 Safari/537.36")
        }

        for platform_name, url in self.platforms.items():
            try:
                response = requests.get(url, headers=headers, timeout=5)
                # 200 = topildi; 404/410 = yo'q; boshqa kodlar (403, 302) — shubhali
                if response.status_code == 200 and len(response.history) == 0:
                    self.found_profiles.append((platform_name, url))
                    console.print(f"[bold green][+] Found:[/bold green] {platform_name} -> {url}")
                elif response.status_code in (404, 410):
                    console.print(f"[red][-] Not found:[/red] {platform_name}")
                else:
                    console.print(f"[yellow][~] Uncertain ({response.status_code}):[/yellow] {platform_name}")
            except requests.RequestException as e:
                console.print(f"[yellow][!] Error scanning {platform_name}: {e}[/yellow]")

    def get_results(self):
        """Topilgan platformalarni qaytaradi (orchestrator uchun)."""
        return dict(self.found_profiles)

    def save_to_database(self):
        """Store discovered profiles in the central database."""
        if not self.found_profiles:
            console.print("[yellow][!] No profiles found, nothing to save.[/yellow]")
            return

        conn = sqlite3.connect("osint_root.db")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS social_footprints (
            target_id TEXT, platform_name TEXT, profile_url TEXT
        )""")

        for platform_name, url in self.found_profiles:
            cursor.execute(
                "INSERT INTO social_footprints (target_id, platform_name, profile_url) "
                "VALUES (?, ?, ?)",
                (self.target_id, platform_name, url),
            )

        conn.commit()
        conn.close()
        console.print("[bold green][+] Profiles stored in the central database.[/bold green]")


if __name__ == "__main__":
    hunter = SocialHunter(target_id="OSINT-UUID-TEST", username="johndoe")
    hunter.scan_username()
    hunter.save_to_database()
