"""FaceTracker — yuz embedding'lari orqali suratlar korpusidan odamni topib,
EXIF/GPS ma'lumotlarini bitta target UUID ostida bog'laydi (Relational Rooting)."""
import sqlite3
from pathlib import Path
import numpy as np
from rich.console import Console
from rich.table import Table
from deepface import DeepFace
from imagetracker import ImageTracker

console = Console()
MODEL = "Facenet512"   # orchestrator bilan bir xil model ishlating

def _cos(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

class FaceTracker:
    def __init__(self, target_id, query_photo, image_dir, threshold=0.30):
        self.target_id = target_id
        self.query_photo = query_photo
        self.image_dir = image_dir
        self.threshold = threshold
        self.matches = []

    def _embed(self, path):
        reps = DeepFace.represent(img_path=str(path), model_name=MODEL,
                                  detector_backend="opencv",
                                  enforce_detection=False, align=True)
        return reps[0]["embedding"] if reps else None

    def scan(self):
        q = self._embed(self.query_photo)
        if q is None:
            console.print("[red][!] So'rov suratida yuz topilmadi.[/red]")
            return
        console.print(f"[*] FaceTracker: {self.image_dir} korpusi skan qilinmoqda...")
        exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
        for f in sorted(Path(self.image_dir).rglob("*")):
            if f.suffix.lower() not in exts:
                continue
            try:
                emb = self._embed(f)
            except Exception:
                continue
            if emb is None:
                continue
            score = _cos(q, emb)
            if score >= self.threshold:
                self.matches.append({"path": str(f), "score": score})
                # Topilgan rasmning EXIF/GPS'ini ham bog'laymiz
                tracker = ImageTracker(target_id=self.target_id, image_path=str(f))
                tracker.extract_exif()
                tracker.save_to_database()
        self._save_matches()
        self._show()

    def _save_matches(self):
        conn = sqlite3.connect("osint_root.db")
        conn.execute("""CREATE TABLE IF NOT EXISTS face_matches (
            target_id TEXT, image_path TEXT, score REAL)""")
        conn.executemany("INSERT INTO face_matches VALUES (?, ?, ?)",
                         [(self.target_id, m["path"], m["score"]) for m in self.matches])
        conn.commit(); conn.close()

    def _show(self):
        table = Table(title=f"Yuz mosliklari ({self.target_id})", border_style="green")
        table.add_column("Score", style="bold green"); table.add_column("Rasm")
        for m in self.matches:
            table.add_row(f"{m['score']:.4f}", m["path"])
        console.print(table if self.matches else "[yellow][!] Moslik topilmadi.[/yellow]")

if __name__ == "__main__":
    FaceTracker("OSINT-UUID-FACE-TEST", "query.jpg", "./photos/").scan()
