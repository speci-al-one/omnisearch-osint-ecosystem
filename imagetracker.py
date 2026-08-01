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

    def _convert_to_degrees(self, value):
        """Helper function to convert the GPS coordinates to decimal degrees"""
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)

    def extract_exif(self):
        """Extracts live EXIF and GPS metadata from the target image"""
        console.print(f"\n[*] ImageTracker: Analyzing image file [bold yellow]{self.image_path}[/bold yellow]...")
        try:
            image = Image.open(self.image_path)
            exif_data = image._getexif()
            
            if not exif_data:
                console.print("[yellow][!] Warning: No EXIF metadata found in this image.[/yellow]")
                return

            gps_info = {}
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == "GPSInfo":
                    for key in value:
                        sub_tag_name = GPSTAGS.get(key, key)
                        gps_info[sub_tag_name] = value[key]
                else:
                    self.metadata[tag_name] = str(value)

            # Process GPS Coordinates if they exist
            if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
                lat = self._convert_to_degrees(gps_info["GPSLatitude"])
                lon = self._convert_to_degrees(gps_info["GPSLongitude"])
                
                # Check for South Latitude or West Longitude
                if gps_info.get("GPSLatitudeRef") == "S":
                    lat = -lat
                if gps_info.get("GPSLongitudeRef") == "W":
                    lon = -lon
                    
                self.gps_coords = f"{lat}, {lon}"
                console.print(f"[bold green][+] GPS Coordinates Found:[/bold green] {self.gps_coords}")
            
            self._display_metadata_table()

        except Exception as e:
            console.print(f"[red][!] Error parsing image: {str(e)}[/red]")

    def _display_metadata_table(self):
        """Displays technical camera metadata in a structured layout"""
        table = Table(title="Captured Camera Metadata", border_style="magenta")
        table.add_column("Metadata Property", style="bold magenta")
        table.add_column("Resolution Value", style="white")

        # Display key parameters if they exist in the metadata dictionary
        table.add_row("Camera Make", self.metadata.get("Make", "Unknown"))
        table.add_row("Camera Model", self.metadata.get("Model", "Unknown"))
        table.add_row("Software Used", self.metadata.get("Software", "Unknown"))
        table.add_row("Capture DateTime", self.metadata.get("DateTime", "Unknown"))
        table.add_row("GPS Coordinates", self.gps_coords if self.gps_coords else "No GPS Data")
        
        console.print(table)

    def save_to_database(self):
        """Stores image intelligence details back into the central ecosystem"""
        conn = sqlite3.connect("core_db/osint_root.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS image_metadata (
            target_id TEXT,
            image_path TEXT,
            camera_model TEXT,
            capture_time TEXT,
            gps_coordinates TEXT
        )""")

        cursor.execute("""
        INSERT INTO image_metadata (target_id, image_path, camera_model, capture_time, gps_coordinates)
        VALUES (?, ?, ?, ?, ?)
        """, (
            self.target_id, 
            self.image_path, 
            self.metadata.get("Model", "Unknown"), 
            self.metadata.get("DateTime", "Unknown"), 
            self.gps_coords
        ))

        conn.commit()
        conn.close()
        console.print("[bold green][+] Image intelligence cached in Central Database successfully![/bold green]")

if __name__ == "__main__":
    # Local debugging execution block
    # Note: Replace 'test.jpg' with a real smartphone photo to see full GPS/Camera details
    tracker = ImageTracker(target_id="OSINT-UUID-IMAGE-TEST", image_path="test.jpg")
    tracker.extract_exif()
    tracker.save_to_database()

