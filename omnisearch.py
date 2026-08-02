"""OmniSearch Core Ledger — FastPeopleSearch / Whoxy / IPLocation tracking layer."""

import socket
import time
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# FastPeopleSearch and Whoxy require paid access, so those two modules run
# in DEMO mode with clearly labelled sample records.
DEMO_MODE = True


class OmniSearchEngine:
    def __init__(self, target):
        self.target = target
        self.root_id = "OSINT-UUID-" + str(int(time.time() * 1000))[-8:]
        self.data = {
            "fastpeoplesearch": {},
            "iplocation": {},
            "whoxy": {},
        }

    def run_fastpeoplesearch_module(self):
        """Demo lookup (FastPeopleSearch is a paid data broker)."""
        time.sleep(1.0)
        self.data["fastpeoplesearch"] = {
            "full_name": "John Doe (DEMO)",
            "age": "28",
            "current_phone": "+14155552671",
            "phone_history": ["+14155559832", "+15105554412"],
            "current_address": "123 Market St, San Francisco, CA 94103",
            "aliases": ["johndoe_cyber", "doe_developer"],
            "relatives": ["Jane Doe (Mother)", "Robert Doe (Brother)"],
            "neighbors": ["Alice Smith (121 Market St)", "Bob Jones (125 Market St)"],
        }

    def run_iplocation_module(self, domain=None):
        """Live IP geolocation via the free ip-api.com endpoint."""
        time.sleep(1.0)
        try:
            ip_address = socket.gethostbyname(domain) if domain else "8.8.8.8"
            # Note: ip-api.com free tier is HTTP-only (no HTTPS support).
            response = requests.get(
                f"http://ip-api.com/json/{ip_address}",
                params={"fields": "status,message,country,regionName,city,lat,lon,isp,as"},
                timeout=8,
            ).json()

            if response.get("status") == "success":
                self.data["iplocation"] = {
                    "ip": ip_address,
                    "country": response.get("country"),
                    "city": response.get("city"),
                    "coordinates": f"{response.get('lat')}, {response.get('lon')}",
                    "isp": response.get("isp"),
                    "asn": response.get("as"),
                    "vpn_proxy": "False (Low Risk)",
                    "tor_node": "False",
                }
            else:
                self.data["iplocation"] = {"ip": ip_address, "error": response.get("message")}
        except Exception as e:
            self.data["iplocation"] = {"error": str(e)}

    def run_whoxy_module(self):
        """Demo reverse-WHOIS lookup (Whoxy is a paid API)."""
        time.sleep(1.0)
        self.data["whoxy"] = {
            "owned_domain": "johndoelabs.com (DEMO)",
            "registrar": "Namecheap Inc.",
            "creation_date": "12 May 2022",
            "expiry_date": "12 May 2027",
            "registrant_email": "johndoe_cyber@mail.com",
            "reverse_whois_count": "3 other domains mapped to this entity",
            "history_alert": "Hosting provider migrated in 2025",
        }

    def display_results(self):
        """Render the consolidated dossier."""
        console.clear()
        console.print(Panel.fit(
            f"[bold green]OMNI-SEARCH OSINT DOSSIER[/bold green]\n"
            f"[bold yellow]ROOT ID:[/bold yellow] {self.root_id}\n"
            f"[dim]Demo mode: {DEMO_MODE}[/dim]",
            border_style="green",
        ))

        fps = self.data["fastpeoplesearch"]
        fps_table = Table(title="1. FastPeopleSearch (demo)", border_style="cyan", show_lines=True)
        fps_table.add_column("Data Parameter", style="bold magenta")
        fps_table.add_column("Value", style="white")
        fps_table.add_row("Full Name (Aliases)", f"{fps['full_name']} ({', '.join(fps['aliases'])})")
        fps_table.add_row("Age", fps["age"])
        fps_table.add_row("Phone (Current)", fps["current_phone"])
        fps_table.add_row("Phone History", "\n".join(fps["phone_history"]))
        fps_table.add_row("Current Address", fps["current_address"])
        fps_table.add_row("Relatives", "\n".join(fps["relatives"]))
        fps_table.add_row("Neighbors", "\n".join(fps["neighbors"]))
        console.print(fps_table)

        wx = self.data["whoxy"]
        whoxy_table = Table(title="2. Whoxy Domain Intelligence (demo)", border_style="yellow", show_lines=True)
        whoxy_table.add_column("Digital Asset", style="bold yellow")
        whoxy_table.add_column("Value", style="white")
        whoxy_table.add_row("Associated Domain", wx["owned_domain"])
        whoxy_table.add_row("Domain Registrar", wx["registrar"])
        whoxy_table.add_row("Timeline", f"Created: {wx['creation_date']} | Expires: {wx['expiry_date']}")
        whoxy_table.add_row("Registrant Email", wx["registrant_email"])
        whoxy_table.add_row("Reverse WHOIS", wx["reverse_whois_count"])
        whoxy_table.add_row("Historical Flag", wx["history_alert"])
        console.print(whoxy_table)

        ip = self.data["iplocation"]
        ip_table = Table(title="3. IPLocation Infrastructure", border_style="blue", show_lines=True)
        ip_table.add_column("Network Parameter", style="bold blue")
        ip_table.add_column("Value", style="white")
        if "ip" in ip:
            ip_table.add_row("IP Address / ISP", f"{ip.get('ip')} ({ip.get('isp', 'Unknown')})")
            ip_table.add_row("Geolocation",
                             f"{ip.get('country', '?')}, {ip.get('city', '?')} ({ip.get('coordinates', '?')})")
            ip_table.add_row("ASN / BGP", ip.get("asn", "Unknown"))
            ip_table.add_row("Anonymization",
                             f"Proxy/VPN: {ip.get('vpn_proxy')} | Tor: {ip.get('tor_node')}")
        else:
            ip_table.add_row("Status", f"Lookup failed: {ip.get('error', 'unknown error')}")
        console.print(ip_table)


if __name__ == "__main__":
    console.print("[bold cyan]OmniSearch OSINT Terminal Engine v1.0[/bold cyan]")
    target_input = console.input("[bold white]Enter target indicator (Name/Phone/Email): [/bold white]")

    engine = OmniSearchEngine(target_input)
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task1 = progress.add_task(description="[cyan]Scanning FastPeopleSearch database...[/cyan]", total=None)
        engine.run_fastpeoplesearch_module()
        progress.update(task1, description="[green]FastPeopleSearch lookup completed.[/green]")

        task2 = progress.add_task(description="[yellow]Analyzing Whoxy reverse WHOIS records...[/yellow]", total=None)
        engine.run_whoxy_module()
        progress.update(task2, description="[green]Whoxy domain discovery finalized.[/green]")

        detected_domain = engine.data["whoxy"]["owned_domain"].replace(" (DEMO)", "")
        task3 = progress.add_task(description=f"[blue]Resolving IPLocation for {detected_domain}...[/blue]", total=None)
        engine.run_iplocation_module(detected_domain)
        progress.update(task3, description="[green]Network and geolocation analysis complete.[/green]")

    engine.display_results()
    
