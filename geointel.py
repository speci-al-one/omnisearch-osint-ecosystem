import os
import folium
import sqlite3
import webbrowser
from rich.console import Console

console = Console()

class GeoIntelMap:
    def __init__(self, target_id):
        self.target_id = target_id
        self.points_to_map = []  # List to store tuples of (lat, lon, label)
        self.output_html = f"core_db/target_map_{target_id}.html"

    def fetch_coordinates_from_db(self):
        """Extracts all discovered geographic location points from the central database"""
        conn = sqlite3.connect("core_db/osint_root.db")
        cursor = conn.cursor()

        # 1. Pull GPS coordinates from image metadata module
        try:
            cursor.execute("SELECT image_path, gps_coordinates FROM image_metadata WHERE target_id = ?", (self.target_id,))
            image_records = cursor.fetchall()
            for rec in image_records:
                if rec[1]:  # If coordinates exist
                    lat, lon = map(float, rec[1].split(","))
                    self.points_to_map.append((lat, lon, f"Image Capture: {rec[0]}"))
        except sqlite3.OperationalError:
            pass  # Table might not exist yet during standalone testing

        # 2. Pull GPS coordinates from IPLocation infrastructure module
        try:
            cursor.execute("SELECT ip_address, country, city FROM iplocation_data WHERE target_id = ?", (self.target_id,))
            ip_records = cursor.fetchall()
            # Note: For testing standalone, we can simulate an IP location point if database is fresh
            for rec in ip_records:
                # In production, pull real lat/lon fields or parse them from a coordinates field
                pass
        except sqlite3.OperationalError:
            pass

        conn.close()

    def generate_interactive_map(self):
        """Generates an HTML-based OpenStreetMap with custom markers and automated viewport anchoring"""
        console.print(f"\n[*] GeoIntel: Generating intelligence map tracking for Target Session [bold yellow]{self.target_id}[/bold yellow]...")
        
        # Fallback default location (Tashkent, Uzbekistan) if no live data is found in the database yet
        if not self.points_to_map:
            console.print("[yellow][!] No live intelligence points found in database. Using default test coordinates.[/yellow]")
            self.points_to_map.append((41.31108, 69.24056, "Default Pivot Intel Point"))

        # Initialize the base map styled layer using OpenStreetMap
        start_lat, start_lon, _ = self.points_to_map[0]
        intel_map = folium.Map(location=[start_lat, start_lon], zoom_start=12, control_scale=True)

        # Plot all extracted threat intelligence coordinates onto the map layer
        for lat, lon, label in self.points_to_map:
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(f"<b>Intel Data:</b><br>{label}", max_width=300),
                tooltip="Click for Core Intelligence",
                icon=folium.Icon(color="red", icon="crosshairs", prefix="fa")
            ).add_to(intel_map)

            # Draw a tracking pathway connecting the movements if multiple points exist
            if len(self.points_to_map) > 1:
                path_coords = [(p[0], p[1]) for p in self.points_to_map]
                folium.PolyLine(path_coords, color="darkred", weight=3, opacity=0.7).add_to(intel_map)

        # Compile and export to the local database file directory
        intel_map.save(self.output_html)
        console.print(f"[bold green][+] Interactive map successfully generated at:[/bold green] {self.output_html}")
        
        # Automatically launch the generated map file inside the default web browser
        abs_path = os.path.abspath(self.output_html)
        webbrowser.open(f"file://{abs_path}")
        console.print("[*] Launching system default browser viewport...")

if __name__ == "__main__":
    # Local engine standalone debugging test
    geo_viewer = GeoIntelMap(target_id="OSINT-UUID-MAP-TEST")
    # Manually append a simulated point for standalone verification
    geo_viewer.points_to_map.append((41.31108, 69.24056, "Simulated Target Signal Base"))
    geo_viewer.generate_interactive_map()


