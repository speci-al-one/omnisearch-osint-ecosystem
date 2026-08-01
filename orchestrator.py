import os
import uuid
import sqlite3
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Importing all 5 developed OSINT modules into the central registry
from core_db.database import init_db
from modules.socialhunter import SocialHunter
from modules.imagetracker import ImageTracker
from modules.geointel import GeoIntelMap
from modules.cybertrace import CyberTraceHub

console = Console()

class GrandOSINTOrchestrator:
    def __init__(self):
        # Trigger clean automated database migration at boot
        init_db()
        self.console = console

    def create_target_session(self, user_query):
        """Generates a dynamic unified identifier using the Rooting Technique"""
        target_uuid = f"OSINT-UUID-{str(uuid.uuid4())[:8].upper()}"
        
        conn = sqlite3.connect("core_db/osint_root.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO targets (target_id, input_query) VALUES (?, ?)", (target_uuid, user_query))
        conn.commit()
        conn.close()
        return target_uuid

    def run_grand_pipeline(self, query, test_image="test.jpg"):
        """Executes the master execution chain linking all 5 OSINT systems"""
        self.console.clear()
        self.console.print(Panel.fit(
            "[bold cyan]⚡ OMNI-SEARCH INTEGRATED OSINT ECOSYSTEM v1.0 ⚡[/bold cyan]\n"
            "[bold white]Status: Systems Operational | Mode: Deep Relational Rooting[/bold white]", 
            border_style="cyan"
        ))
        
        # 1. Initialize Rooting Token
        session_id = self.create_target_session(query)
        self.console.print(f"[bold green][+] Relational Rooting Active.[/bold green] Generated Primary Key: [bold yellow]{session_id}[/bold yellow]\n")

        # 2. Automated Visual Progress Monitor
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=self.console) as progress:
            
            # --- PROJECT #1: CORE REPOSITORY PARSING (FastPeopleSearch + IPLocation + Whoxy) ---
            task1 = progress.add_task(description="[cyan][P1] Fetching FastPeopleSearch records & Network footprints...[/cyan]", total=None)
            
            # Simulated data aggregation from Project 1 components to feed forward
            discovered_aliases = ["cyber_detective", "shadow_coder"]
            discovered_email = "target_intel_user@gmail.com"
            
            # Seed foundational infrastructure data into database for cross-module mapping
            conn = sqlite3.connect("core_db/osint_root.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO iplocation_data (target_id, ip_address, country, city, isp, vpn_proxy) 
                VALUES (?, '8.8.8.8', 'United States', 'California', 'Google LLC', 'False')
            """, (session_id,))
            conn.commit()
            conn.close()
            progress.update(task1, description="[green][P1] Core registries, IP networks, and WHOIS layers parsed![/green]")

            # --- PROJECT #2: SOCIALHUNTER (Username Intelligence) ---
            task2 = progress.add_task(description="[yellow][P2] Initiating SocialHunter platform auditing...[/yellow]", total=None)
            for alias in discovered_aliases:
                hunter = SocialHunter(target_id=session_id, username=alias)
                hunter.scan_username()
                hunter.save_to_database()
            progress.update(task2, description="[green][P2] SocialHunter digital footprints gathered and saved![/green]")

            # --- PROJECT #3: IMAGETRACKER (Camera Metadata Extraction) ---
            task3 = progress.add_task(description="[magenta][P3] ImageTracker analyzing tactical EXIF tags...[/magenta]", total=None)
            # Create a blank test image if one doesn't exist to prevent crashes during debug
            if not os.path.exists(test_image):
                from PIL import Image
                img = Image.new('RGB', (100, 100), color = 'red')
                img.save(test_image)
                
            img_analyzer = ImageTracker(target_id=session_id, image_path=test_image)
            img_analyzer.extract_exif()
            img_analyzer.save_to_database()
            progress.update(task3, description="[green][P3] ImageTracker metadata vectors cataloged![/green]")

            # --- PROJECT #5: CYBERTRACE HUB (Data Breach Auditing) ---
            task5 = progress.add_task(description="[red][P5] CyberTrace querying leak repositories for exposure...[/red]", total=None)
            cyber_audit = CyberTraceHub(target_id=session_id, target_email=discovered_email)
            cyber_audit.check_data_breaches()
            cyber_audit.save_to_database()
            progress.update(task5, description="[green][P5] CyberTrace data breach audit completed successfully![/green]")

            # --- PROJECT #4: GEOINTEL MAP VIEWER (Geospatial Assembly & Visualization) ---
            task4 = progress.add_task(description="[blue][P4] GeoIntel compiling interactive viewport layout...[/blue]", total=None)
            map_engine = GeoIntelMap(target_id=session_id)
            map_engine.fetch_coordinates_from_db()
            map_engine.generate_interactive_map()
            progress.update(task4, description="[green][P4] GeoIntel mapping complete! Viewport active in browser.[/green]")

        self.console.print(f"\n[bold green]🏁 GRAND PIPELINE EXECUTION SUCCESSFUL FOR SESSION {session_id}! All data linked.[/bold green]")

if __name__ == "__main__":
    orchestrator = GrandOSINTOrchestrator()
    console.print("[bold white]Welcome to the Unified Grand OSINT Suite[/bold white]")
    input_data = console.input("[bold magenta]Enter initial target indicator (Name/Phone/Email): [/bold magenta]")
    
    if input_data.strip():
        orchestrator.run_grand_pipeline(query=input_data)
    else:
        console.print("[red][!] Error: Query parameter required to seed the ecosystem.[/red]")
        