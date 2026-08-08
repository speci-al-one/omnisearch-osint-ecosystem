"""GrandOSINTOrchestrator — main entry point that chains all modules."""

import os
import re
import uuid
import sqlite3
import requests
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from database import init_db
from socialhunter import SocialHunter
from imagetracker import ImageTracker
from geointel import GeoIntelMap
from cybertrace import CyberTraceHub

console = Console()


class GrandOSINTOrchestrator:
    def __init__(self):
        init_db()
        self.console = console

    @staticmethod
    def detect_query_type(query):
        """Email / Phone / IP / Rasm / Name turlarini aniqlaydi."""
        if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", query):
            return "email"
        if re.search(r"\+?\d[\d\s\-\(\)]{7,}", query):
            return "phone"
        if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", query):
            return "ip"
        if query.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp")):
            return "image"
        return "name"

    def _save_phone_intel(self, target_id, result):
        """PhoneIntel natijasini bazaga yozadi."""
        conn = sqlite3.connect("osint_root.db")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS phone_intel_data (
            target_id TEXT, phone TEXT, valid TEXT, country TEXT,
            location TEXT, carrier TEXT, line_type TEXT
        )""")
        conn.execute(
            "INSERT INTO phone_intel_data VALUES (?, ?, ?, ?, ?, ?, ?)",
            (target_id, result.get("phone"), str(result.get("valid", "")),
             result.get("country", ""), result.get("location", ""),
             result.get("carrier", ""), result.get("line_type", "")),
        )
        conn.commit()
        conn.close()

    def run_grand_pipeline(self, query, image_dir=None):
        """Execute the full module chain under one root id."""
        self.console.clear()
        query_type = self.detect_query_type(query)
        self.console.print(f"[bold cyan][*] Detected Input Type:[/bold cyan] "
                           f"[bold yellow]{query_type.upper()}[/bold yellow]")

        self.console.print(Panel.fit(
            "[bold cyan]⚡ OMNI-SEARCH INTEGRATED OSINT ECOSYSTEM v1.1 ⚡[/bold cyan]\n"
            "[bold white]Status: Systems Operational | Mode: Deep Relational Rooting[/bold white]",
            border_style="cyan",
        ))

        session_id = f"OSINT-UUID-{str(uuid.uuid4())[:8].upper()}"
        conn = sqlite3.connect("osint_root.db")
        conn.execute("INSERT INTO targets (target_id, input_query) VALUES (?, ?)",
                     (session_id, query))
        conn.commit()
        conn.close()
        self.console.print(f"[bold green][+] Rooting active.[/bold green] "
                           f"Root ID: [bold yellow]{session_id}[/bold yellow]\n")

        discovered_emails = []

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                      console=self.console) as progress:

            # --- P1: PHONE / IP LEDGER ---
            task1 = progress.add_task(description="[cyan][P1] Seeding core registries...[/cyan]", total=None)
            if query_type == "phone":
                from phoneintel import PhoneIntel
                result = PhoneIntel(query).query()
                self._save_phone_intel(session_id, result)
                self.console.print(f"[bold green][+] PhoneIntel:[/bold green] {result.get('phone')} "
                                   f"| valid={result.get('valid', '?')} | "
                                   f"carrier={result.get('carrier', '?')}")
            elif query_type == "ip":
                try:
                    r = requests.get(f"http://ip-api.com/json/{query}",
                                     params={"fields": "status,country,city,isp,proxy"}, timeout=8)
                    data = r.json()
                    if data.get("status") == "success":
                        conn = sqlite3.connect("osint_root.db")
                        conn.execute(
                            "INSERT INTO iplocation_data (target_id, ip_address, country, city, isp, vpn_proxy) "
                            "VALUES (?, ?, ?, ?, ?, ?)",
                            (session_id, query, data.get("country"), data.get("city"),
                             data.get("isp"), str(data.get("proxy", False))))
                        conn.commit()
                        conn.close()
                        self.console.print(f"[bold green][+] IP lookup:[/bold green] {query} "
                                           f"-> {data.get('city')}, {data.get('country')}")
                except Exception as e:
                    self.console.print(f"[yellow][!] IP lookup failed: {e}[/yellow]")
            else:
                self.console.print("[dim][-] P1: phone/IP emas, skip.[/dim]")
            progress.update(task1, description="[green][P1] Core ledger seeded.[/green]")

            # --- P2: SOCIALHUNTER (name yoki email username qismi) ---
            task2 = progress.add_task(description="[yellow][P2] Running SocialHunter username audit...[/yellow]", total=None)
            search_username = query if query_type == "name" else None
            if search_username:
                hunter = SocialHunter(target_id=session_id, username=search_username)
                hunter.scan_username()
                hunter.save_to_database()
            else:
                self.console.print("[dim][-] P2: username emas, skip.[/dim]")
            progress.update(task2, description="[green][P2] Social footprint audit complete.[/green]")

            # --- P3: IMAGETRACKER (berilgan papka bo'yicha) ---
            task3 = progress.add_task(description="[magenta][P3] Extracting EXIF metadata...[/magenta]", total=None)
            if image_dir and os.path.isdir(image_dir):
                exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
                images = [p for p in os.listdir(image_dir)
                          if os.path.splitext(p)[1].lower() in exts]
                for img in images:
                    tracker = ImageTracker(target_id=session_id,
                                           image_path=os.path.join(image_dir, img))
                    tracker.extract_exif()
                    tracker.save_to_database()
            else:
                self.console.print("[yellow][!] P3: image_dir berilmagan — EXIF qadami skip.[/yellow]")
            progress.update(task3, description="[green][P3] EXIF metadata catalogued.[/green]")

            # --- P4: CYBERTRACE (email bo'lsa) ---
            task4 = progress.add_task(description="[red][P4] Auditing data-breach repositories...[/red]", total=None)
            if query_type == "email":
                discovered_emails.append(query)
            if discovered_emails:
                for email in discovered_emails:
                    cyber = CyberTraceHub(target_id=session_id, target_email=email)
                    cyber.check_data_breaches()
                    cyber.save_to_database()
            else:
                self.console.print("[yellow][!] P4: email topilmadi — breach audit skip.[/yellow]")
            progress.update(task4, description="[green][P4] Breach audit complete.[/green]")

            # --- P5: GEOINTEL MAP (har doim oxirgi) ---
            task5 = progress.add_task(description="[blue][P5] Compiling geospatial viewport...[/blue]", total=None)
            map_engine = GeoIntelMap(target_id=session_id)
            map_engine.fetch_coordinates_from_db()
            map_engine.generate_interactive_map()
            progress.update(task5, description="[green][P5] Map compiled.[/green]")

        self.console.print(f"\n[bold green]🏁 GRAND PIPELINE SUCCESSFUL FOR {session_id}! "
                           f"All data linked.[/bold green]")


if __name__ == "__main__":
    console.print("[bold white]Welcome to the Unified Grand OSINT Suite[/bold white]")
    input_data = Prompt.ask("[bold magenta]Enter target indicator (Name/Phone/Email/IP)[/bold magenta]")
    img_dir = Prompt.ask("[bold magenta]Image directory (Enter = skip)[/bold magenta]", default="").strip()
    if input_data.strip():
        GrandOSINTOrchestrator().run_grand_pipeline(
            query=input_data.strip(),
            image_dir=img_dir or None,
        )
    else:
        console.print("[red][!] Error: query parameter is required.[/red]")

