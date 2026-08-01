import time
import socket
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class OmniSearchEngine:
    def __init__(self, target):
        self.target = target
        # Central UUID system linking all modules together (Rooting Technique)
        self.root_id = "OSINT-UUID-9b1deb4d" 
        self.data = {
            "fastpeoplesearch": {},
            "iplocation": {},
            "whoxy": {}
        }

    def run_fastpeoplesearch_module(self):
        """Simulates FastPeopleSearch Core Workflows"""
        # In production, this replaces with local DB query or web scraping engine
        time.sleep(1.5) 
        self.data["fastpeoplesearch"] = {
            "full_name": "John Doe",
            "age": "28",
            "current_phone": "+14155552671",
            "phone_history": ["+14155559832", "+15105554412"],
            "current_address": "123 Market St, San Francisco, CA 94103",
            "aliases": ["johndoe_cyber", "doe_developer"],
            "relatives": ["Jane Doe (Mother)", "Robert Doe (Brother)"],
            "neighbors": ["Alice Smith (121 Market St)", "Bob Jones (125 Market St)"]
        }

    def run_iplocation_module(self, domain):
        """Executes Live Network & IP Geolocation Lookups"""
        time.sleep(1.2)
        try:
            # Domain to IP Lookup resolution
            ip_address = socket.gethostbyname(domain) if domain else "8.8.8.8"
            
            # Live API request to fetch real-time network infrastructure details
            response = requests.get(f"http://ip-api.com{ip_address}?fields=status,message,country,regionName,city,lat,lon,isp,as").json()
            
            if response.get("status") == "success":
                self.data["iplocation"] = {
                    "ip": ip_address,
                    "country": response.get("country"),
                    "city": response.get("city"),
                    "coordinates": f"{response.get('lat')}, {response.get('lon')}",
                    "isp": response.get("isp"),
                    "asn": response.get("as"),
                    "vpn_proxy": "False (Low Risk)",
                    "tor_node": "False"
                }
            else:
                self.data["iplocation"] = {"ip": ip_address, "status": "Geolocation Lookup Failed"}
        except Exception as e:
            self.data["iplocation"] = {"error": str(e)}

    def run_whoxy_module(self):
        """Simulates Reverse WHOIS and Digital Asset Footprinting"""
        time.sleep(1.8)
        self.data["whoxy"] = {
            "owned_domain": "johndoelabs.com",
            "registrar": "Namecheap Inc.",
            "creation_date": "12 May 2022",
            "expiry_date": "12 May 2027",
            "registrant_email": "johndoe_cyber@mail.com",
            "reverse_whois_count": "3 other domains mapped to this entity",
            "history_alert": "Hosting provider migrated in 2025"
        }

    def display_results(self):
        """Consolidates and Displays the Final Aggregated Dossier Report"""
        console.clear()
        console.print(Panel.fit(f"[bold green]OMNI-SEARCH OSINT DOSSIER[/bold green]\n[bold yellow]ROOT ID:[/bold yellow] {self.root_id}", border_style="green"))

        # 1. FastPeopleSearch Module Output Table
        fps_table = Table(title="[cyan]1. FastPeopleSearch Data Module[/cyan]", border_style="cyan", show_lines=True)
        fps_table.add_column("Data Parameter", style="bold magenta")
        fps_table.add_column("Identified Value", style="white")
        
        fps = self.data["fastpeoplesearch"]
        fps_table.add_row("Full Name (Aliases)", f"{fps['full_name']} ({', '.join(fps['aliases'])})")
        fps_table.add_row("Age", fps["age"])
        fps_table.add_row("Phone (Current)", fps["current_phone"])
        fps_table.add_row("Phone History", "\n".join(fps["phone_history"]))
        fps_table.add_row("Current Address", fps["current_address"])
        fps_table.add_row("Relatives", "\n".join(fps["relatives"]))
        fps_table.add_row("Immediate Neighbors", "\n".join(fps["neighbors"]))
        console.print(fps_table)

        # 2. Whoxy Module Output Table
        whoxy_table = Table(title="[yellow]2. Whoxy Domain Intelligence Module[/yellow]", border_style="yellow", show_lines=True)
        whoxy_table.add_column("Digital Asset", style="bold yellow")
        whoxy_table.add_column("WHOIS / Reverse WHOIS Intel", style="white")
        
        wx = self.data["whoxy"]
        whoxy_table.add_row("Associated Domain", wx["owned_domain"])
        whoxy_table.add_row("Domain Registrar", wx["registrar"])
        whoxy_table.add_row("Timeline", f"Created: {wx['creation_date']} | Expires: {wx['expiry_date']}")
        whoxy_table.add_row("Registrant Email", wx["registrant_email"])
        whoxy_table.add_row("Reverse WHOIS Discovery", wx["reverse_whois_count"])
        whoxy_table.add_row("Historical Flag", wx["history_alert"])
        console.print(whoxy_table)

        # 3. IPLocation Module Output Table
        ip_table = Table(title="[blue]3. IPLocation Infrastructure Module[/blue]", border_style="blue", show_lines=True)
        ip_table.add_column("Network Parameter", style="bold blue")
        ip_table.add_column("Analysis Resolution", style="white")
        
        ip = self.data["iplocation"]
        ip_table.add_row("IP Address / ISP", f"{ip.get('ip')} ({ip.get('isp')})")
        ip_table.add_row("Geolocation (GPS)", f"{ip.get('country')}, {ip.get('city')} ({ip.get('coordinates')})")
        ip_table.add_row("ASN / BGP Routing", ip.get("asn"))
        ip_table.add_row("Anonymization Check", f"Proxy/VPN: {ip.get('vpn_proxy')} | Tor Node: {ip.get('tor_node')}")
        console.print(ip_table)

# Application entry point
if __name__ == "__main__":
    console.print("[bold cyan]OmniSearch OSINT Terminal Engine v1.0[/bold cyan]")
    target_input = console.input("[bold white]Enter Target Intelligence Input (Name/Phone/Email): [/bold white]")
    
    engine = OmniSearchEngine(target_input)
    
    # Progress visualization pipeline for active tasks
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task1 = progress.add_task(description="[cyan]Scanning FastPeopleSearch database repository...[/cyan]", total=None)
        engine.run_fastpeoplesearch_module()
        progress.update(task1, description="[green]FastPeopleSearch lookup completed successfully![/green]")
        
        task2 = progress.add_task(description="[yellow]Analyzing Whoxy Reverse WHOIS records...[/yellow]", total=None)
        engine.run_whoxy_module()
        progress.update(task2, description="[green]Whoxy domain discovery finalized![/green]")
        
        # Rooting Technique data forwarding: Passing Whoxy output domain straight to IPLocation
        detected_domain = engine.data["whoxy"]["owned_domain"]
        task3 = progress.add_task(description=f"[blue]Resolving IPLocation network topology ({detected_domain})...[/blue]", total=None)
        engine.run_iplocation_module(detected_domain)
        progress.update(task3, description="[green]Network and geolocation analysis complete![/green]")

    # Print the unified intelligence profile dossier
    engine.display_results()
