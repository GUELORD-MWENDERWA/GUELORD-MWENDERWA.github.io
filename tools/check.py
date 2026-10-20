"""Garde-fou du site : refuse ce qui fait dériver le design.

Usage : python3 tools/check.py   (code de sortie 1 au moindre problème)
- assets/site.css : couleur, taille de texte ou rayon écrits en dur hors définition de jeton (--nom: valeur) ;
- pages générées : attribut style="…" en ligne, image sans texte alternatif, lien vers le dépôt mwangaza.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
problems: list[str] = []

COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgb|rgba|hsl|hsla|oklch)\(")
for number, line in enumerate((ROOT / "assets" / "site.css").read_text(encoding="utf-8").splitlines(), 1):
    code = re.sub(r"/\*.*?\*/", "", line).strip()
    if not code or re.match(r"--[\w-]+\s*:", code):
        continue  # définition de jeton : c'est le seul endroit où une valeur brute est permise
    where = f"site.css:{number}"
    if COLOR.search(code):
        problems.append(f"{where} couleur hors jeton : {code}")
    size = re.search(r"font-size:\s*([^;]+)", code)
    if size and not re.fullmatch(r"var\(--t-[\w-]+\)|inherit", size.group(1).strip()):
        problems.append(f"{where} taille de texte hors échelle : {code}")
    radius = re.search(r"border(?:-[a-z]+)*-radius:\s*([^;]+)", code)
    if radius and not re.fullmatch(r"(var\(--r-[\w-]+\)|50%|0)( (var\(--r-[\w-]+\)|50%|0))*", radius.group(1).strip()):
        problems.append(f"{where} rayon hors jetons : {code}")

for page in ("index.html", "fr/index.html", "404.html"):
    html = (ROOT / page).read_text(encoding="utf-8")
    if re.search(r"<(?!svg|path|rect|circle|g\b)[a-z]+[^>]*\sstyle=", html):
        problems.append(f"{page} : attribut style en ligne")
    for img in re.findall(r"<img\b[^>]*>", html):
        if not re.search(r'\salt="[^"]+"', img):
            problems.append(f"{page} : image sans texte alternatif : {img[:80]}")
    if "github.com/GUELORD-MWENDERWA/mwangaza" in html:
        problems.append(f"{page} : lien vers le dépôt mwangaza (Mwangaza se présente par son site)")

for p in problems:
    print("✘", p)
print(f"{len(problems)} problème(s)")
sys.exit(1 if problems else 0)
