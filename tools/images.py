"""Prépare les images du portfolio en WebP (deux largeurs par image).

Usage : python3 tools/images.py <dossier-des-sources>
Chaque image source donne <nom>-<largeur>.webp dans assets/img/.
"""
from pathlib import Path
import sys

from PIL import Image

SRC = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent.parent / "assets" / "img"
OUT.mkdir(parents=True, exist_ok=True)

# nom de sortie : (fichier source, largeurs, proportion largeur/hauteur imposée ou None)
IMAGES = {
    "mwangaza-site": ("mwangaza-desktop.png", (1200, 720), None),
    "mwangaza-site-mobile": ("mwangaza-mobile.png", (390, 260), None),
    "mwangaza-cash-desk": ("mz-gestion-caisse-encaissement.webp", (1184, 592), None),
    "mwangaza-dashboard": ("mz-gestion-tableau-de-bord.webp", (1184, 592), None),
    "mwangaza-grades": ("mz-gestion-notes-saisie.webp", (1184, 592), None),
    "mwangaza-unpaid": ("mz-gestion-impayes.webp", (1184, 592), None),
    "mwangaza-portal": ("mz-portail-accueil-mobile.webp", (390, 260), None),
    "afronova-site": ("afronova-desktop.png", (1200, 720), None),
    "afronova-site-mobile": ("afronova-mobile.png", (390, 260), None),
    "dtms-site": ("dtms-desktop.png", (1200, 720), None),
    "dtms-site-mobile": ("dtms-mobile.png", (390, 260), None),
    "edge-ai": ("tech-edge-ai-motor-fault-detector-confusion_matrix.png", (800, 400), 16 / 10),
    "oscilloscope": ("tech-esp32-web-oscilloscope-web_ui.png", (800, 400), 16 / 10),
    "circuit-solver": ("tech-circuit-solver-bode.png", (800, 400), 16 / 10),
    "pid": ("tech-dc-motor-pid-controller-step_response.png", (800, 400), 16 / 10),
    "ml": ("tech-ml-from-scratch-decision_boundaries.png", (800, 400), 16 / 10),
    "scheduler": ("tech-os-scheduling-simulator-gantt.png", (800, 400), 16 / 10),
    "portrait": ("avatar.jpg", (460, 240), 1.0),
    "goma": ("goma-lac-kivu.webp", (1200, 600), 3 / 2),
}


def fit(im: Image.Image, ratio: float) -> Image.Image:
    """Met l'image à la proportion voulue en complétant les bords avec la couleur du coin."""
    w, h = im.size
    edge = im.getpixel((1, 1))
    if abs(w / h - ratio) < 0.01:
        return im
    if w / h > ratio:  # trop large : on garde toute la largeur et on ajoute du blanc en haut et en bas
        canvas = Image.new("RGB", (w, round(w / ratio)), edge)
        canvas.paste(im, (0, (canvas.height - h) // 2))
        return canvas
    canvas = Image.new("RGB", (round(h * ratio), h), edge)
    canvas.paste(im, ((canvas.width - w) // 2, 0))
    return canvas


for name, (src, widths, ratio) in IMAGES.items():
    im = Image.open(SRC / src).convert("RGB")
    if ratio:
        im = fit(im, ratio)
    for width in widths:
        out = im.copy()
        if out.width > width:
            out = out.resize((width, round(out.height * width / out.width)), Image.LANCZOS)
        path = OUT / f"{name}-{width}.webp"
        out.save(path, "WEBP", quality=80, method=6)
        print(f"{path.name:32} {out.width}×{out.height}  {path.stat().st_size // 1024} Ko")
