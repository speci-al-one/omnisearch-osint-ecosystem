"""GrandOSINTOrchestrator — main entry point that chains all 5 modules."""

import os
import uuid
import sqlite3
from rich.console import Console
import re
from phoneintel import PhoneIntel
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

    def create_target_session(self, user_query):
        """Create a unified root identifier for the target."""
        target_uuid = f"OSINT-UUID-{str(uuid.uuid4())[:8].upper()}"

        conn = sqlite3.connect("osint_root.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO targets (target_id, input_query) VALUES (?, ?)",
            (target_uuid, user_query),
        )
        conn.commit()
        conn.close()
        return target_uuid

    def run_grand_pipeline(self, query, test_image="test.jpg"):
        """Execute the full 5-module chain under one root id."""
        self.console.clear()
                def detect_query_type(query):
            if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", query):
                return "email"
            if re.search(r"\+?\d[\d\s\-\(\)]{7,}", query):
                return "phone"
            return "name"

        query_type = detect_query_type(query)
        self.console.print(f"[bold cyan][*] Detected Input Type:[/bold cyan] [bold yellow]{query_type.upper()}[/bold yellow]")

        self.console.print(Panel.fit(
            "[bold cyan]⚡ OMNI-SEARCH INTEGRATED OSINT ECOSYSTEM v1.0 ⚡[/bold cyan]\n"
            "[bold white]Status: Systems Operational | Mode: Deep Relational Rooting[/bold white]",
            border_style="cyan",
        ))

        session_id = self.create_target_session(query)
        self.console.print(f"[bold green][+] Rooting active.[/bold green] Root ID: [bold yellow]{session_id}[/bold yellow]\n")

        # Demo seeds — clearly labelled, replace with real lookups later.
        discovered_aliases = ["cyber_detective", "shadow_coder"]
        discovered_email = "target_intel_user@gmail.com"

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=self.console) as progress:
            # --- PROJECT 1: CORE LEDGER (IP seed) ---
            task1 = progress.add_task(description="[cyan][P1] Seeding core registries & network layer...[/cyan]", total=None)
            conn = sqlite3.connect("osint_root.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO iplocation_data (target_id, ip_address, country, city, isp, vpn_proxy) "
                "VALUES (?, '8.8.8.8', 'United States', 'California', 'Google LLC', 'False')",
                (session_id,),
            )
            conn.commit()
            conn.close()
            progress.update(task1, description="[green][P1] Core ledger seeded.[/green]")

            # --- PROJECT 2: SOCIALHUNTER ---
            task2 = progress.add_task(description="[yellow][P2] Running SocialHunter username audit...[/yellow]", total=None)
            for alias in discovered_aliases:
                hunter = SocialHunter(target_id=session_id, username=alias)
                hunter.scan_username()
                hunter.save_to_database()
            progress.update(task2, description="[green][P2] Social footprint audit complete.[/green]")

            # --- PROJECT 3: IMAGETRACKER ---
            task3 = progress.add_task(description="[magenta][P3] Extracting EXIF metadata...[/magenta]", total=None)
            if not os.path.exists(test_image):
                from PIL import Image
                Image.new("RGB", (100, 100), color="red").save(test_image)
            img_analyzer = ImageTracker(target_id=session_id, image_path=test_image)
            img_analyzer.extract_exif()
            img_analyzer.save_to_database()
            progress.update(task3, description="[green][P3] EXIF metadata catalogued.[/green]")

             # run_grand_pipeline() ichida, query_type == "face" bo'lganda:
from facetracker import FaceTracker

# detect_query_type() ga qo'shing:
if os.path.exists(query) and query.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
    return "face"

# P3.5 — FACE TRACKER (imagetracker'dan keyin):
task35 = progress.add_task(description="[green][P3.5] Face-tracker: yuz mosliklari qidirilmoqda...[/green]", total=None)
face_engine = FaceTracker(target_id=session_id, query_photo=query, image_dir="./corpus/")
face_engine.scan()
progress.update(task35, description="[green][P3.5] Yuz mosliklari bog'landi.[/green]")

            # --- PROJECT 5: CYBERTRACE HUB ---
            task5 = progress.add_task(description="[red][P5] Auditing data-breach repositories...[/red]", total=None)
            cyber_audit = CyberTraceHub(target_id=session_id, target_email=discovered_email)
            cyber_audit.check_data_breaches()
            cyber_audit.save_to_database()
            progress.update(task5, description="[green][P5] Breach audit complete.[/green]")

            # --- PROJECT 4: GEOINTEL MAP ---
            task4 = progress.add_task(description="[blue][P4] Compiling geospatial viewport...[/blue]", total=None)
            map_engine = GeoIntelMap(target_id=session_id)
            map_engine.fetch_coordinates_from_db()
            map_engine.generate_interactive_map()
            progress.update(task4, description="[green][P4] Map compiled and opened in browser.[/green]")

        self.console.print(f"\n[bold green]🏁 GRAND PIPELINE SUCCESSFUL FOR {session_id}! All data linked.[/bold green]")


if __name__ == "__main__":
    orchestrator = GrandOSINTOrchestrator()
    console.print("[bold white]Welcome to the Unified Grand OSINT Suite[/bold white]")
    input_data = console.input("[bold magenta]Enter initial target indicator (Name/Phone/Email): [/bold magenta]")
    if input_data.strip():
        orchestrator.run_grand_pipeline(query=input_data)
    else:
        console.print("[red][!] Error: query parameter is required.[/red]")
        
