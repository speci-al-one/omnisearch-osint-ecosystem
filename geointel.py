"""GeoIntel Map — renders collected coordinates on an interactive Folium map."""

import os
import sqlite3
import webbrowser
import folium
from rich.console import Console

console = Console()

# Fallback demo point (Tashkent) used when the database has no coordinates.
DEFAULT_POINT = (41.31108, 69.24056, "Demo pivot point (Tashkent)")


class GeoIntelMap:
    def __init__(self, target_id):
        self.target_id = target_id
        self.points_to_map = []
        self.output_html = f"target_map_{target_id}.html"

    def fetch_coordinates_from_db(self):
        """Load GPS coordinates collected by other modules."""
        conn = sqlite3.connect("osint_root.db")
        cursor = conn.cursor()

        # GPS points from image metadata
        try:
            cursor.execute(
                "SELECT image_path, gps_coordinates FROM image_metadata WHERE target_id = ?",
                (self.target_id,),
            )
            for path, coords in cursor.fetchall():
                if coords:
                    try:
                        lat, lon = map(float, coords.split(","))
                        self.points_to_map.append((lat, lon, f"Image capture: {path}"))
                    except ValueError:
                        continue
        except sqlite3.OperationalError:
            pass  # table does not exist yet during standalone testing

        conn.close()

    def generate_interactive_map(self):
        console.print(f"\n[*] GeoIntel: building map for {self.target_id}...")

        if not self.points_to_map:
            console.print("[yellow][!] No coordinates found, using demo pivot point.[/yellow]")
            self.points_to_map.append(DEFAULT_POINT)

        start_lat, start_lon, _ = self.points_to_map[0]
        intel_map = folium.Map(location=[start_lat, start_lon], zoom_start=12, control_scale=True)

        for lat, lon, label in self.points_to_map:
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(f"<b>Intel data:</b><br>{label}", max_width=300),
                tooltip="Click for details",
                icon=folium.Icon(color="red", icon="crosshairs", prefix="fa"),
            ).add_to(intel_map)

        # Tracking line drawn ONCE for all points (was inside the loop before)
        if len(self.points_to_map) > 1:
            path_coords = [(p[0], p[1]) for p in self.points_to_map]
            folium.PolyLine(path_coords, color="darkred", weight=3, opacity=0.7).add_to(intel_map)

        intel_map.save(self.output_html)
        console.print(f"[bold green][+] Map saved:[/bold green] {self.output_html}")

        webbrowser.open(f"file://{os.path.abspath(self.output_html)}")


if __name__ == "__main__":
    viewer = GeoIntelMap(target_id="OSINT-UUID-MAP-TEST")
    viewer.points_to_map.append(DEFAULT_POINT)
    viewer.generate_interactive_map()
