"""GrandOSINTOrchestrator — Unified OSINT Pipeline (FIXED)"""
import os, uuid, sqlite3, re, requests
from pathlib import Path
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
        if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", query):
            return "email"
        if re.search(r"\+?\d[\d\s\-\(\)]{7,}", query):
            return "phone"
        return "name"

    def _insert_ip_lookup(self, target_id, target_ip):
        """Real IP geolocation orqali core ledger'ni to'ldirish."""
        try:
            r = requests.get(f"http://ip-api.com/json/{target_ip}",
                             params={"fields": "status,country,city,isp,proxy"}, timeout=5)
            data = r.json()
            if data.get("status") == "success":
                conn = sqlite3.connect("osint_root.db")
                conn.execute(
                    "INSERT INTO iplocation_data (target_id, ip_address, country, city, isp, vpn_proxy) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (target_id, target_ip, data.get("country"), data.get("city"),
                     data.get("isp"), str(data.get("proxy", False)))
                )
                conn.commit(); conn.close()
                return data
        except Exception as e:
            console.print(f"[yellow][!] IP lookup failed: {e}[/yellow]")
        return None

    def run_grand_pipeline(self, query, image_dir=None):
        self.console.clear()
        query_type = self.detect_query_type(query)
        console.print(f"[bold cyan][*] Input type:[/bold cyan] [bold yellow]{query_type.upper()}[/bold yellow]")

        console.print(Panel.fit(
            "[bold cyan]⚡ OMNI-SEARCH INTEGRATED OSINT ECOSYSTEM v1.1 ⚡[/bold cyan]\n"
            "[bold white]Status: Systems Operational | Mode: Deep Relational Rooting[/bold white]",
            border_style="cyan",
        ))

        session_id = f"OSINT-UUID-{str(uuid.uuid4())[:8].upper()}"
        conn = sqlite3.connect("osint_root.db")
        conn.execute("INSERT INTO targets (target_id, input_query) VALUES (?, ?)", (session_id, query))
        conn.commit(); conn.close()
        console.print(f"[bold green][+] Rooting active. Root ID: [bold yellow]{session_id}[/bold yellow]\n")

        # Real lookups — yangi ob'ektlar natijalarini yig'ish uchun
        discovered_aliases = []
        discovered_emails = []

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                      console=self.console) as progress:

            # P1 — CORE LEDGER
            t1 = progress.add_task("[cyan][P1] Seeding network layer...", total=None)
            if query_type == "phone":
                from phoneintel import PhoneIntel
                pi = PhoneIntel(target_id=session_id, phone=query)
                pi.run()
            elif query_type == "email":
                discovered_emails.append(query)
            # Agar domain yoki IP berilsa, lookup qilish mumkin
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", query):
                self._insert_ip_lookup(session_id, query)
            progress.update(t1, "[green][P1] Core ledger seeded.[/green]")

            # P2 — SOCIALHUNTER
            t2 = progress.add_task("[yellow][P2] SocialHunter: username audit...", total=None)
            if query_type == "name":
                hunter = SocialHunter(target_id=session_id, username=query)
                hunter.scan_username()
                hunter.save_to_database()
                if hasattr(hunter, 'results'):
                    discovered_aliases.append(query)
            progress.update(t2, "[green][P2] Social footprint audit complete.[/green]")

            # P3 — IMAGETRACKER
            t3 = progress.add_task("[magenta][P3] EXIF metadata extraction...", total=None)
            if image_dir and Path(image_dir).exists():
                for img_file in Path(image_dir).rglob("*"):
                    if img_file.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                        img_tracker = ImageTracker(target_id=session_id, image_path=str(img_file))
                        img_tracker.extract_exif()
                        img_tracker.save_to_database()
            else:
                console.print("[yellow][!] image_dir berilmagan — ImageTracker skip qilindi.[/yellow]")
            progress.update(t3, "[green][P3] EXIF metadata catalogued.[/green]")

            # P4 — CYBERTRACE
            t4 = progress.add_task("[red][P4] Data-breach audit...", total=None)
            if discovered_emails:
                for email in discovered_emails:
                    cyber = CyberTraceHub(target_id=session_id, target_email=email)
                    cyber.check_data_breaches()
                    cyber.save_to_database()
            else:
                console.print("[yellow][!] Email topilmadi — breach audit skip qilindi.[/yellow]")
            progress.update(t4, "[green][P4] Breach audit complete.[/green]")

            # P5 — GEOINTEL MAP (always last)
            t5 = progress.add_task("[blue][P5] Compiling geospatial viewport...", total=None)
            map_engine = GeoIntelMap(target_id=session_id)
            map_engine.fetch_coordinates_from_db()
            map_engine.generate_interactive_map()
            progress.update(t5, "[green][P5] Map saved.[/green]")

        console.print(f"\n[bold green]🏁 PIPELINE SUCCESSFUL FOR {session_id}![/bold green]")

if __name__ == "__main__":
    console.print("[bold white]OmniSearch OSINT Ecosystem[/bold white]")
    query = Prompt.ask("[bold magenta]Enter target indicator (Name/Phone/Email/IP/ImageDir)[/bold magenta]")
    img_dir = Prompt.ask("[bold magenta]Image directory path (enter to skip)[/bold magenta]", default="")
    img_dir = img_dir.strip() or None
    if query.strip():
        GrandOSINTOrchestrator().run_grand_pipeline(query=query.strip(), image_dir=img_dir)
    else:
        console.print("[red][!] Query required.[/red]")

