"""Génère le site statique à partir de content/*.toml.

Usage : python3 tools/build.py
Produit : index.html (anglais), fr/index.html (français), 404.html, sitemap.xml, og/*.html
(gabarits des images de partage, rendus en PNG par tools/og.mjs).
Python 3.11+ (tomllib) et Pillow (dimensions des images).
"""
from __future__ import annotations

import json
import tomllib
from datetime import date
from html import escape
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://guelord-mwenderwa.github.io"
GITHUB = "https://github.com/GUELORD-MWENDERWA"
LINKEDIN = "https://linkedin.com/in/guelord-mwenderwa"
FONTS = (
    "https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500"
    "&family=Geist:wght@400;500;600;700&display=swap"
)


def e(text: str) -> str:
    return escape(str(text), quote=True)


# ---------- Icônes (SVG en ligne, 24 × 24) ----------

def icon(name: str, cls: str = "") -> str:
    stroke = 'fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"'
    paths = {
        "arrow-up-right": f'<path {stroke} d="M7 17 17 7M8 7h9v9"/>',
        "arrow-right": f'<path {stroke} d="M5 12h14M13 6l6 6-6 6"/>',
        "arrow-down": f'<path {stroke} d="M12 5v14M6 13l6 6 6-6"/>',
        "mail": f'<rect {stroke} x="3" y="5" width="18" height="14" rx="2"/><path {stroke} d="m4 7 8 6 8-6"/>',
        "sun": f'<circle {stroke} cx="12" cy="12" r="4"/><path {stroke} d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
        "moon": f'<path {stroke} d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5Z"/>',
        "menu": f'<path {stroke} d="M4 7h16M4 12h16M4 17h16"/>',
        "close": f'<path {stroke} d="M6 6l12 12M18 6 6 18"/>',
        "github": '<path fill="currentColor" d="M12 .3a12 12 0 0 0-3.8 23.4c.6.1.8-.3.8-.6v-2c-3.3.7-4-1.6-4-1.6-.6-1.4-1.4-1.8-1.4-1.8-1-.7.1-.7.1-.7 1.2 0 1.9 1.2 1.9 1.2 1 1.8 2.8 1.3 3.5 1 0-.8.4-1.3.7-1.6-2.7-.3-5.5-1.3-5.5-6 0-1.2.5-2.3 1.3-3.1-.2-.4-.6-1.6 0-3.2 0 0 1-.3 3.3 1.2a11.5 11.5 0 0 1 6 0C17.3 4.7 18.3 5 18.3 5c.7 1.6.2 2.9.1 3.2.8.8 1.3 1.9 1.3 3.2 0 4.6-2.8 5.6-5.5 5.9.5.4.9 1.1.9 2.2v3.3c0 .3.1.7.8.6A12 12 0 0 0 12 .3"/>',
        "linkedin": '<path fill="currentColor" d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13ZM7.12 20.45H3.56V9h3.56v11.45ZM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0Z"/>',
    }
    css = f' class="{cls}"' if cls else ""
    return f'<svg{css} viewBox="0 0 24 24" aria-hidden="true" focusable="false">{paths[name]}</svg>'


# Marque : une piste de circuit imprimé qui dessine un G et finit sur une pastille de cuivre.
MARK = (
    '<svg class="brand-mark" viewBox="0 0 64 64" aria-hidden="true" focusable="false">'
    '<path d="M47 17H25l-9 9v12l9 9h14l8-8v-7H35" fill="none" stroke="currentColor" stroke-width="6" '
    'stroke-linecap="round" stroke-linejoin="round"/>'
    '<circle class="via" cx="35" cy="32" r="6.5"/></svg>'
)

# Pistes décoratives du héros et du bloc contact (couleur des lignes, une pastille cuivre).
TRACES = (
    '<svg class="{cls}" viewBox="0 0 720 640" fill="none" aria-hidden="true" focusable="false">'
    '<g stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M720 96H520l-40 40v120"/><path d="M720 136H560l-24 24v176l-40 40H360"/>'
    '<path d="M720 176H600l-16 16v232l40 40h96"/><path d="M720 520H640l-40 40v80"/>'
    '<path d="M480 256v96l-56 56H300"/><path d="M720 300H660l-24 24v40"/></g>'
    '<g stroke-width="1.5"><circle class="via" cx="480" cy="256" r="6"/><circle class="via" cx="360" cy="376" r="6"/>'
    '<circle class="via" cx="300" cy="408" r="6"/><circle class="via" cx="636" cy="364" r="6"/>'
    '<circle class="via" cx="600" cy="640" r="6"/></g>'
    '<circle class="via-live" cx="424" cy="408" r="5"/></svg>'
)


# ---------- Images ----------

def size(path: Path) -> tuple[int, int]:
    with Image.open(path) as im:
        return im.size


def picture(base: str, name: str, alt: str, sizes: str, cls: str = "", eager: bool = False) -> str:
    """<img> responsive à partir des fichiers assets/img/<name>-<largeur>.webp."""
    files = [
        f for f in ROOT.glob(f"assets/img/{name}-*.webp")
        if f.stem.rsplit("-", 1)[0] == name and f.stem.rsplit("-", 1)[1].isdigit()
    ]
    files.sort(key=lambda f: int(f.stem.rsplit("-", 1)[1]))
    if not files:
        raise SystemExit(f"image manquante : assets/img/{name}-*.webp")
    largest = files[-1]
    w, h = size(largest)
    srcset = ", ".join(f"{base}assets/img/{f.name} {size(f)[0]}w" for f in files)
    loading = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    css = f' class="{cls}"' if cls else ""
    return (
        f'<img{css} src="{base}assets/img/{largest.name}" srcset="{srcset}" sizes="{sizes}" '
        f'width="{w}" height="{h}" alt="{e(alt)}" {loading}>'
    )


# ---------- Morceaux de page ----------

def header(c: dict, base: str) -> str:
    n = c["nav"]
    m = c["meta"]
    links = [("work", n["work"]), ("highlights", n["highlights"]), ("open-source", n["open_source"]),
             ("teaching", n["teaching"]), ("about", n["about"])]
    desktop = "".join(f'<a href="#{i}">{e(t)}</a>' for i, t in links)
    mobile = "".join(f'<a href="#{i}">{e(t)}</a>' for i, t in links)
    alt_href = base + m["alt_path"].lstrip("/")
    return f"""
<a class="skip-link" href="#main">{e(n["skip"])}</a>
<header class="site-header" data-header>
  <div class="container header-inner">
    <a class="brand" href="./" aria-label="{e(n["home"])}">{MARK}<span class="brand-name">Guelord Mwenderwa</span></a>
    <nav class="nav-desktop" aria-label="{e(n["label"])}">{desktop}</nav>
    <div class="header-actions">
      <a class="icon-btn" href="{alt_href}" hreflang="{m["alt_lang"]}" lang="{m["alt_lang"]}" aria-label="{e(m["alt_label"])}">{m["alt_short"]}</a>
      <button class="icon-btn theme-toggle" type="button" data-theme-toggle aria-label="{e(n["theme"])}">{icon("moon", "icon-moon")}{icon("sun", "icon-sun")}</button>
      <a class="btn btn-primary btn-contact" href="#contact">{e(n["contact"])}</a>
      <button class="icon-btn menu-toggle" type="button" data-menu-toggle aria-expanded="false" aria-controls="mobile-nav" aria-label="{e(n["menu"])}">{icon("menu", "icon-menu")}{icon("close", "icon-close")}</button>
    </div>
  </div>
  <nav class="nav-mobile" id="mobile-nav" aria-label="{e(n["label"])}">{mobile}<a href="#contact">{e(n["contact"])}</a>
    <a class="btn btn-primary" href="mailto:{c["contact"]["email"]}">{icon("mail")}{e(n["email_cta"])}</a></nav>
</header>"""


def hero(c: dict, base: str) -> str:
    h = c["hero"]
    facts = "".join(
        f'<div class="fact"><span class="fact-value">{e(f["value"])}</span><span class="fact-label">{e(f["label"])}</span></div>'
        for f in h["facts"]
    )
    portrait = picture(base, "portrait", h["portrait_alt"], "(min-width: 1024px) 336px, (min-width: 400px) 336px, 86vw", eager=True)
    return f"""
<section class="hero" aria-labelledby="hero-title">
  {TRACES.format(cls="hero-traces")}
  <div class="container">
    <div class="hero-grid">
      <div>
        <p class="eyebrow">{e(h["eyebrow"])}</p>
        <h1 id="hero-title">{e(h["title_before"])}<em>{e(h["title_accent"])}</em></h1>
        <p class="hero-lead">{e(h["lead"])}</p>
        <div class="hero-ctas">
          <a class="btn btn-primary" href="#work">{e(h["cta_work"])}{icon("arrow-down")}</a>
          <a class="btn btn-outline" href="mailto:{c["contact"]["email"]}">{icon("mail")}{e(h["cta_email"])}</a>
        </div>
        <div class="hero-links">
          <a href="{GITHUB}" rel="me">{icon("github")}GitHub</a>
          <a href="{LINKEDIN}" rel="me">{icon("linkedin")}LinkedIn</a>
        </div>
      </div>
      <figure class="portrait-card">
        {portrait}
        <span class="status">{e(h["status"])}</span>
      </figure>
    </div>
    <div class="facts">{facts}</div>
  </div>
</section>"""


def section_head(idx: str, title: str, intro: str, hid: str) -> str:
    return f"""<div class="section-head"><p class="section-index">{e(idx)}</p><h2 id="{hid}">{e(title)}</h2><p>{e(intro)}</p></div>"""


def work(c: dict, base: str) -> str:
    w = c["work"]
    cases = []
    for k in w["cases"]:
        bullets = "".join(f"<li>{e(b)}</li>" for b in k["bullets"])
        chips = "".join(f'<span class="chip">{e(s)}</span>' for s in k["stack"])
        desktop = picture(base, k["desktop"], k["desktop_alt"], "(min-width: 1024px) 800px, 92vw")
        mobile = picture(base, k["mobile"], k["mobile_alt"], "190px")
        gallery = ""
        if k.get("gallery"):
            figs = "".join(
                f'<figure>{picture(base, g["img"], g["caption"], "(min-width: 1024px) 270px, 72vw")}<figcaption>{e(g["caption"])}</figcaption></figure>'
                for g in k["gallery"]
            )
            gallery = f'<div class="gallery" role="group" aria-label="{e(w["gallery_label"])}" tabindex="0">{figs}</div>'
        cases.append(f"""
<article class="case" id="{k["id"]}" aria-labelledby="{k["id"]}-title">
  <div class="case-visual">
    <div class="browser"><div class="browser-bar"><i></i><i></i><i></i><span>{e(k["domain"])}</span></div>{desktop}</div>
    <div class="phone">{mobile}</div>
  </div>
  <div class="case-body">
    <div class="case-intro">
      <div class="case-meta"><span class="mono">{e(k["number"])}</span><span class="status">{e(w["live"])}</span></div>
      <h3 id="{k["id"]}-title">{e(k["name"])}</h3>
      <p class="case-tagline">{e(k["tagline"])}</p>
      <p class="case-summary">{e(k["summary"])}</p>
      <div class="case-links"><a class="link-arrow" href="{k["url"]}">{e(w["visit"])} {e(k["domain"])}{icon("arrow-up-right")}</a></div>
    </div>
    <div class="case-details">
      <p class="case-role">{e(w["role_label"])} · <strong>{e(k["role"])}</strong></p>
      <p class="case-did">{e(w["did_label"])}</p>
      <ul class="case-list">{bullets}</ul>
      <div class="chips">{chips}</div>
    </div>
  </div>
  {gallery}
</article>""")
    return f"""
<section class="section" id="work" aria-labelledby="work-title">
  <div class="container">
    {section_head(w["index"], w["title"], w["intro"], "work-title")}
    <div class="cases">{"".join(cases)}</div>
  </div>
</section>"""


def highlights(c: dict) -> str:
    h = c["highlights"]
    items = "".join(
        f'<article class="highlight"><p class="mono">{e(i["project"])}</p><h3>{e(i["title"])}</h3><p>{e(i["text"])}</p></article>'
        for i in h["items"]
    )
    return f"""
<section class="section" id="highlights" aria-labelledby="highlights-title">
  <div class="container">
    {section_head(h["index"], h["title"], h["intro"], "highlights-title")}
    <div class="highlights">{items}</div>
  </div>
</section>"""


def open_source(c: dict, base: str, contributions: list[dict]) -> str:
    o = c["open_source"]
    cards = "".join(f"""
<a class="project" href="{GITHUB}/{p["repo"]}">
  <div class="project-figure">{picture(base, p["img"], p["alt"], "(min-width: 1024px) 380px, (min-width: 768px) 46vw, 92vw")}</div>
  <div class="project-body">
    <span class="project-kind">{e(p["kind"])}</span>
    <h3>{e(p["name"])}</h3>
    <p>{e(p["text"])}</p>
    <div class="chips">{"".join(f'<span class="chip">{e(t)}</span>' for t in p["tags"])}</div>
    <span class="project-cta">{e(o["view"])}{icon("arrow-up-right")}</span>
  </div>
</a>""" for p in o["featured"])
    contrib = ""
    if contributions:
        states = {"merged": o["merged"], "open": o["open"], "closed": o["closed"]}
        rows = "".join(f"""
<a class="contrib" href="{x["url"]}">
  <span class="contrib-top"><span class="contrib-repo">{e(x["repo"])}</span><span class="contrib-state{' is-merged' if x["state"] == "merged" else ''}">{e(states[x["state"]])}</span></span>
  <span class="contrib-title">{e(x["title"])}</span>
</a>""" for x in contributions)
        contrib = f"""
<div class="contribs" id="contributions">
  <div class="contribs-head"><h3>{e(o["contrib_title"])}</h3><p>{e(o["contrib_intro"])}</p></div>
  {rows}
</div>"""
    return f"""
<section class="section" id="open-source" aria-labelledby="open-source-title">
  <div class="container">
    {section_head(o["index"], o["title"], o["intro"], "open-source-title")}
    <div class="projects">{cards}</div>
    <p class="all-repos"><a class="btn btn-outline" href="{GITHUB}?tab=repositories">{icon("github")}{e(o["all_repos"])}{icon("arrow-up-right")}</a></p>
    {contrib}
  </div>
</section>"""


def teaching(c: dict) -> str:
    t = c["teaching"]
    courses = "".join(f"""
<a class="course" href="{GITHUB}/{k["repo"]}">
  <h3>{e(k["name"])}</h3><p>{e(k["text"])}</p>
  <div class="chips">{"".join(f'<span class="chip">{e(x)}</span>' for x in k["tags"])}</div>
  <span class="project-cta">{e(c["open_source"]["view"])}{icon("arrow-up-right")}</span>
</a>""" for k in t["courses"])
    return f"""
<section class="section" id="teaching" aria-labelledby="teaching-title">
  <div class="container">
    {section_head(t["index"], t["title"], t["intro"], "teaching-title")}
    <div class="teaching">{courses}</div>
  </div>
</section>"""


def about(c: dict, base: str) -> str:
    a = c["about"]
    paras = "".join(f"<p>{e(p)}</p>" for p in a["paragraphs"])
    edu = "".join(
        f'<li><strong>{e(x["school"])}</strong><span>{e(x["program"])}</span><span class="mono">{e(x["when"])}</span></li>'
        for x in a["education"]
    )
    principles = "".join(f'<li><strong>{e(p["title"])}</strong> {e(p["text"])}</li>' for p in a["principles"])
    skills = "".join(f'<div><dt>{e(s["area"])}</dt><dd>{e(s["items"])}</dd></div>' for s in a["skills"])
    return f"""
<section class="section" id="about" aria-labelledby="about-title">
  <div class="container">
    <div class="section-head"><p class="section-index">{e(a["index"])}</p><h2 id="about-title">{e(a["title"])}</h2></div>
    <div class="about">
      <div class="about-text">
        {paras}
        <h3 class="subhead">{e(a["education_title"])}</h3>
        <ul class="timeline">{edu}</ul>
      </div>
      <div class="about-side">
        <h3 class="subhead">{e(a["principles_title"])}</h3>
        <ul class="principles">{principles}</ul>
        <h3 class="subhead">{e(a["skills_title"])}</h3>
        <dl class="skills">{skills}</dl>
      </div>
    </div>
  </div>
</section>"""


def contact(c: dict) -> str:
    k = c["contact"]
    return f"""
<section class="section" id="contact" aria-labelledby="contact-title">
  <div class="container">
    <div class="contact">
      {TRACES.format(cls="contact-traces")}
      <p class="eyebrow">{e(k["eyebrow"])}</p>
      <h2 id="contact-title">{e(k["title"])}</h2>
      <p>{e(k["text"])}</p>
      <div class="contact-actions">
        <a class="btn btn-copper" href="mailto:{k["email"]}">{icon("mail")}{e(k["email_cta"])}</a>
        <a class="btn btn-outline" href="{LINKEDIN}" rel="me">{icon("linkedin")}{e(k["linkedin"])}</a>
        <a class="btn btn-outline" href="{GITHUB}" rel="me">{icon("github")}{e(k["github"])}</a>
      </div>
      <p class="contact-email">{e(k["email"])}</p>
    </div>
  </div>
</section>"""


def footer() -> str:
    return f"""
<footer class="site-footer">
  <div class="container"><div class="footer-inner"><p>© {date.today().year} Guelord Mwenderwa</p></div></div>
</footer>"""


THEME_BOOT = (
    "<script>try{var t=localStorage.getItem('theme');if(t==='dark'||t==='light')"
    "document.documentElement.dataset.theme=t}catch(e){}</script>"
)


def head(c: dict, base: str, *, title: str, description: str, canonical: str, index: bool = True) -> str:
    m = c["meta"]
    og = f"{SITE}/assets/og-{m['lang']}.png"
    alternates = (
        f'<link rel="alternate" hreflang="en" href="{SITE}/">'
        f'<link rel="alternate" hreflang="fr" href="{SITE}/fr/">'
        f'<link rel="alternate" hreflang="x-default" href="{SITE}/">'
    )
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Guelord Mwenderwa",
        "url": f"{SITE}/",
        "image": f"{SITE}/assets/img/portrait-460.webp",
        "jobTitle": "Software engineer" if m["lang"] == "en" else "Ingénieur logiciel",
        "email": f"mailto:{c['contact']['email']}",
        "address": {"@type": "PostalAddress", "addressLocality": "Goma", "addressCountry": "CD"},
        "alumniOf": [
            {"@type": "CollegeOrUniversity", "name": "Institut Supérieur d'Informatique et de Gestion (ISIG Goma)"},
            {"@type": "HighSchool", "name": "Institut Technique Industriel de Goma (ITIG Don Bosco)"},
        ],
        "knowsAbout": ["Django", "React", "TypeScript", "PostgreSQL", "ESP32", "Embedded systems", "Machine learning"],
        "sameAs": [GITHUB, LINKEDIN],
    }
    robots = "" if index else '<meta name="robots" content="noindex">'
    return f"""<!doctype html>
<html lang="{m["lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="author" content="Guelord Mwenderwa">
{robots}
<link rel="canonical" href="{canonical}">
{alternates if index else ""}
<meta name="theme-color" content="#fbfaf8" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#11100f" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="profile">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{m["og_locale"]}">
<meta property="profile:first_name" content="Guelord">
<meta property="profile:last_name" content="Mwenderwa">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{base}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{base}assets/icons/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{base}assets/icons/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{base}assets/site.css">
{THEME_BOOT}
<script type="application/ld+json">{json.dumps(person, ensure_ascii=False)}</script>
</head>
<body>"""


def page(c: dict, base: str, contributions: list[dict]) -> str:
    m = c["meta"]
    canonical = SITE + m["path"]
    return (
        head(c, base, title=m["title"], description=m["description"], canonical=canonical)
        + header(c, base)
        + '\n<main id="main">'
        + hero(c, base)
        + work(c, base)
        + highlights(c)
        + open_source(c, base, contributions)
        + teaching(c)
        + about(c, base)
        + contact(c)
        + "\n</main>"
        + footer()
        + f'\n<script src="{base}assets/site.js" defer></script>\n</body>\n</html>\n'
    )


def not_found(en: dict, fr: dict) -> str:
    base = "/"
    body = "".join(
        f"""<div lang="{c["meta"]["lang"]}"><h1>{e(c["not_found"]["title"])}</h1><p>{e(c["not_found"]["text"])}</p>
<p class="not-found-actions"><a class="btn btn-primary" href="{c["meta"]["path"]}">{e(c["not_found"]["back"])}{icon("arrow-right")}</a></p></div>"""
        for c in (en, fr)
    )
    return (
        head(en, base, title="404 · Guelord Mwenderwa", description=en["meta"]["description"], canonical=f"{SITE}/404.html", index=False)
        + f"""
<header class="site-header"><div class="container header-inner"><a class="brand" href="/" aria-label="{e(en["nav"]["home"])}">{MARK}<span class="brand-name">Guelord Mwenderwa</span></a></div></header>
<main id="main"><div class="container not-found">{body}</div></main>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""
    )


def og_card(c: dict) -> str:
    """Gabarit 1200 × 630 de l'image de partage (rendu par tools/og.mjs)."""
    h = c["hero"]
    facts = "".join(f'<div class="f"><b>{e(f["value"])}</b><span>{e(f["label"])}</span></div>' for f in h["facts"])
    return f"""<!doctype html><html lang="{c["meta"]["lang"]}"><head><meta charset="utf-8">
<link rel="stylesheet" href="{FONTS}">
<style>
*{{box-sizing:border-box;margin:0}}
body{{width:1200px;height:630px;background:#11100f;color:#f3efea;font-family:Geist,sans-serif;overflow:hidden;position:relative}}
.wrap{{position:absolute;inset:0;padding:64px 72px;display:grid;grid-template-columns:1fr 300px;gap:56px;align-items:center}}
.k{{font-family:'Geist Mono',monospace;font-size:20px;letter-spacing:.08em;text-transform:uppercase;color:#a39a91;display:flex;align-items:center;gap:14px}}
.k::before{{content:"";width:32px;height:3px;background:#e79a6b;border-radius:2px}}
h1{{margin-top:22px;font-size:58px;line-height:1.05;letter-spacing:-.03em;font-weight:600}}
h1 em{{font-style:normal;color:#e79a6b}}
.facts{{display:flex;gap:40px;margin-top:40px}}
.f{{display:grid;gap:4px;max-width:200px}} .f b{{font-family:'Geist Mono',monospace;font-size:36px;font-weight:500}} .f span{{font-size:17px;color:#cfc7bf;line-height:1.3}}
img{{width:300px;height:300px;object-fit:cover;border-radius:20px;border:1px solid #2d2926}}
.name{{margin-top:16px;font-weight:600;font-size:22px}} .url{{font-family:'Geist Mono',monospace;color:#a39a91;font-size:16px;margin-top:4px}}
svg.t{{position:absolute;right:-60px;top:-40px;width:720px;color:#2d2926}} svg.t .via{{fill:#11100f;stroke:#3a3531}} svg.t .via-live{{fill:#e79a6b}}
</style></head><body>{TRACES.format(cls="t")}
<div class="wrap"><div><p class="k">{e(h["eyebrow"])}</p><h1>{e(h["title_before"])}<em>{e(h["title_accent"])}</em></h1><div class="facts">{facts}</div></div>
<div><img src="../assets/img/portrait-460.webp" alt=""><p class="name">Guelord Mwenderwa</p><p class="url">guelord-mwenderwa.github.io</p></div></div>
</body></html>"""


def main() -> None:
    load = lambda lang: tomllib.loads((ROOT / "content" / f"{lang}.toml").read_text(encoding="utf-8"))
    en, fr = load("en"), load("fr")
    contrib_file = ROOT / "content" / "contributions.toml"
    contributions = tomllib.loads(contrib_file.read_text(encoding="utf-8")).get("pr", []) if contrib_file.exists() else []

    (ROOT / "index.html").write_text(page(en, "", contributions), encoding="utf-8")
    (ROOT / "fr").mkdir(exist_ok=True)
    (ROOT / "fr" / "index.html").write_text(page(fr, "../", contributions), encoding="utf-8")
    (ROOT / "404.html").write_text(not_found(en, fr), encoding="utf-8")
    (ROOT / "og").mkdir(exist_ok=True)
    for c in (en, fr):
        (ROOT / "og" / f"{c['meta']['lang']}.html").write_text(og_card(c), encoding="utf-8")
    urls = "".join(
        f"<url><loc>{SITE}{p}</loc>"
        f'<xhtml:link rel="alternate" hreflang="en" href="{SITE}/"/>'
        f'<xhtml:link rel="alternate" hreflang="fr" href="{SITE}/fr/"/></url>'
        for p in ("/", "/fr/")
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
        f"{urls}</urlset>\n",
        encoding="utf-8",
    )
    print("index.html, fr/index.html, 404.html, sitemap.xml, og/*.html générés")


if __name__ == "__main__":
    main()
