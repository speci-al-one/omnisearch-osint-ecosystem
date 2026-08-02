"""ImageTracker — extracts EXIF and GPS metadata from image files."""

import sqlite3
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from rich.console import Console
from rich.table import Table

console = Console()


class ImageTracker:
    def __init__(self, target_id, image_path):
        self.target_id = target_id
        self.image_path = image_path
        self.metadata = {}
        self.gps_coords = None

    @staticmethod
    def _convert_to_degrees(value):
        """Convert GPS (degrees, minutes, seconds) to decimal degrees."""
        d, m, s = float(value[0]), float(value[1]), float(value[2])
        return d + (m / 60.0) + (s / 3600.0)

    def extract_exif(self):
        """Read EXIF tags and compute GPS coordinates."""
        console.print(f"\n[*] ImageTracker: analyzing {self.image_path}...")
        try:
            image = Image.open(self.image_path)
            exif_data = image._getexif()

            if not exif_data:
                console.print("[yellow][!] No EXIF metadata found in this image.[/yellow]")
                return

            gps_info = {}
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == "GPSInfo":
                    for key in value:
                        gps_info[GPSTAGS.get(key, key)] = value[key]
                else:
                    self.metadata[tag_name] = str(value)

            if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
                lat = self._convert_to_degrees(gps_info["GPSLatitude"])
                lon = self._convert_to_degrees(gps_info["GPSLongitude"])
                if gps_info.get("GPSLatitudeRef") == "S":
                    lat = -lat
                if gps_info.get("GPSLongitudeRef") == "W":
                    lon = -lon
                self.gps_coords = f"{lat}, {lon}"
                console.print(f"[bold green][+] GPS coordinates:[/bold green] {self.gps_coords}")

            self._display_metadata_table()

        except Exception as e:
            console.print(f"[red][!] Error parsing image: {e}[/red]")

    def _display_metadata_table(self):
        """Show key metadata in a table."""
        table = Table(title="Captured Camera Metadata", border_style="magenta")
        table.add_column("Metadata Property", style="bold magenta")
        table.add_column("Value", style="white")

        table.add_row("Camera Make", self.metadata.get("Make", "Unknown"))
        table.add_row("Camera Model", self.metadata.get("Model", "Unknown"))
        table.add_row("Software Used", self.metadata.get("Software", "Unknown"))
        table.add_row("Capture DateTime", self.metadata.get("DateTime", "Unknown"))
        table.add_row("GPS Coordinates", self.gps_coords or "No GPS Data")

        console.print(table)

    def save_to_database(self):
        """Store image intelligence in the central database."""
        conn = sqlite3.connect("osint_root.db")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS image_metadata (
            target_id TEXT, image_path TEXT, camera_model TEXT,
            capture_time TEXT, gps_coordinates TEXT
        )""")
        cursor.execute(
            "INSERT INTO image_metadata (target_id, image_path, camera_model, capture_time, gps_coordinates) "
            "VALUES (?, ?, ?, ?, ?)",
            (self.target_id, self.image_path,
             self.metadata.get("Model", "Unknown"),
             self.metadata.get("DateTime", "Unknown"),
             self.gps_coords),
        )
        conn.commit()
        conn.close()
        console.print("[bold green][+] Image metadata stored in the central database.[/bold green]")


if __name__ == "__main__":
    tracker = ImageTracker(target_id="OSINT-UUID-IMAGE-TEST", image_path="test.jpg")
    tracker.extract_exif()
    tracker.save_to_database()
