"""FaceTracker — FaceCheck.ID uslubidagi yuz qidiruv moduli.

So'rov suratidagi yuzni korpusdagi barcha suratlar bilan solishtiradi.
Topilgan mosliklarni EXIF/GPS bilan birlashtirib osint_root.db ga yozadi.
database.py dagi face_matches (6 ustun) sxemasi bilan mos keladi.
"""

import sqlite3
from pathlib import Path
import numpy as np
from rich.console import Console
from rich.table import Table
from deepface import DeepFace

from imagetracker import ImageTracker

console = Console()

# Default model — Facenet512 (aniqlik/tezlik nisbati eng yaxshi)
DEFAULT_MODEL = "Facenet512"
THRESHOLDS = {
    "VGG-Face": 0.68, "Facenet": 0.40, "Facenet512": 0.30,
    "ArcFace": 0.68, "OpenFace": 0.10, "SFace": 0.59, "GhostFaceNet": 0.65,
}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


def _cosine_similarity(a, b):
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def _area(r):
    fa = r.get("facial_area") or {}
    if "w" in fa and "h" in fa:
        return fa["w"] * fa["h"]
    return 0


class FaceTracker:
    def __init__(self, target_id, query_photo, image_dir, model=DEFAULT_MODEL,
                 detector="opencv", threshold=None):
        self.target_id = target_id
        self.query_photo = Path(query_photo)
        self.image_dir = Path(image_dir)
        self.model = model
        self.detector = detector
        self.threshold = threshold or THRESHOLDS.get(model, 0.30)
        self.matches = []
        self.query_embedding = None

    def _get_embedding(self, img_path):
        """Suratdagi eng katta yuzning embedding'ini qaytaradi (None bo'lishi mumkin)."""
        try:
            # 1) Cache'dan tekshirish — qayta hisoblamaslik
            conn = sqlite3.connect("osint_root.db")
            cur = conn.cursor()
            cur.execute(
                "SELECT embedding FROM face_embeddings WHERE image_path = ? AND model_name = ?",
                (str(img_path), self.model),
            )
            row = cur.fetchone()
            conn.close()
            if row:
                emb = np.frombuffer(row[0], dtype=np.float32)
                if emb.shape[0] > 0:
                    return emb

            # 2) DeepFace orqali hisoblash
            reps = DeepFace.represent(
                img_path=str(img_path),
                model_name=self.model,
                detector_backend=self.detector,
                enforce_detection=False,
                align=True,
            )
            if not reps:
                return None
            reps.sort(key=_area, reverse=True)  # bir nechta yuz bo'lsa — eng kattasi
            emb = np.array(reps[0]["embedding"], dtype=np.float32)

            # 3) Cache'ga saqlash
            conn = sqlite3.connect("osint_root.db")
            conn.execute(
                "INSERT OR REPLACE INTO face_embeddings (image_path, model_name, embedding) "
                "VALUES (?, ?, ?)",
                (str(img_path), self.model, emb.tobytes()),
            )
            conn.commit()
            conn.close()
            return emb
        except Exception as e:
            console.print(f"[dim][!] Embedding error: {img_path} — {e}[/dim]")
            return None

    def scan(self):
        """Korpusni skan qilib, query suratiga mos yuzlarni topadi."""
        console.print(f"\n[*] FaceTracker: scanning {self.image_dir} for matches...")
        console.print(f"    model={self.model}, detector={self.detector}, "
                       f"threshold={self.threshold:.2f}")

        # Query embedding
        self.query_embedding = self._get_embedding(self.query_photo)
        if self.query_embedding is None:
            console.print("[red][!] So'rov suratida yuz topilmadi.[/red]")
            return

        # Korpus bo'ylab yurish (query faylining o'zini chiqarib tashlash)
        all_images = sorted(
            p for p in self.image_dir.rglob("*")
            if p.suffix.lower() in IMAGE_EXTENSIONS and p != self.query_photo
        )
        if not all_images:
            console.print("[yellow][!] Korpusda rasm topilmadi.[/yellow]")
            return

        for i, img_path in enumerate(all_images, 1):
            emb = self._get_embedding(img_path)
            if emb is None:
                continue
            score = _cosine_similarity(self.query_embedding, emb)
            if score >= self.threshold:
                # EXIF/GPS ni ham bog'laymiz (imagetracker orqali)
                exif_data = self._extract_exif(img_path)
                self.matches.append({
                    "path": str(img_path),
                    "score": score,
                    **exif_data,
                })
                console.print(f"  [green][{i}/{len(all_images)}] Match: {img_path.name} "
                               f"(score={score:.4f})[/green]")
            else:
                console.print(f"  [dim][{i}/{len(all_images)}] {img_path.name} "
                               f"(score={score:.4f}) — past[/dim]")

        self._save_to_database()
        self._display_results()

    def _extract_exif(self, img_path):
        """EXIF ma'lumotlarini ImageTracker orqali chiqaradi."""
        tracker = ImageTracker(target_id=self.target_id, image_path=str(img_path))
        tracker.extract_exif()
        tracker.save_to_database()
        return {
            "camera_model": tracker.metadata.get("Model", "Unknown"),
            "capture_time": tracker.metadata.get("DateTime", "Unknown"),
            "gps_coordinates": tracker.gps_coords,
        }

    def _save_to_database(self):
        """Natijalarni face_matches (6 ustun) jadvaliga yozadi."""
        if not self.matches:
            console.print("[yellow][!] Hech qanday moslik topilmadi.[/yellow]")
            return

        conn = sqlite3.connect("osint_root.db")
        cur = conn.cursor()
        # database.py bilan bir xil sxema — CREATE yozilmaydi, init_db() yaratadi
        cur.executemany(
            "INSERT INTO face_matches "
            "(target_id, image_path, score, camera_model, capture_time, gps_coordinates) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [(self.target_id, m["path"], m["score"],
              m["camera_model"], m["capture_time"], m["gps_coordinates"])
             for m in self.matches],
        )
        conn.commit()
        conn.close()
        console.print(f"[bold green][+] {len(self.matches)} ta moslik bazaga yozildi.[/bold green]")

    def _display_results(self):
        """Natijalarni jadval ko'rinishida chiqaradi."""
        if not self.matches:
            return
        table = Table(title=f"Yuz mosliklari — {self.target_id}", border_style="green")
        table.add_column("Score", style="bold green")
        table.add_column("Rasm")
        table.add_column("Camera")
        table.add_column("GPS")
        for m in sorted(self.matches, key=lambda x: x["score"], reverse=True):
            gps = m["gps_coordinates"] or "—"
            table.add_row(f"{m['score']:.4f}", m["path"],
                          m["camera_model"], gps)
        console.print(table)

        # Geo-preview: barcha GPS koordinatalarni bir joyda ko'rsatish
        gps_points = [m["gps_coordinates"] for m in self.matches if m["gps_coordinates"]]
        if gps_points:
            console.print(f"\n[bold cyan]GPS nuqtalar ({len(gps_points)}):[/bold cyan]")
            for pt in gps_points:
                console.print(f"  {pt}")


if __name__ == "__main__":
    import sys
    from rich.prompt import Prompt

    console.print("[bold cyan]FaceTracker — mustaqil rejim[/bold cyan]")
    query = Prompt.ask("[bold]So'rov surati (path)[/bold]")
    corpus = Prompt.ask("[bold]Korpus papkasi[/bold]")
    ft = FaceTracker(target_id="OSINT-UUID-FACE-TEST",
                     query_photo=query, image_dir=corpus)
    ft.scan()
