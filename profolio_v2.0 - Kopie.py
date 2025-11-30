# =====================================================================
# Portfolio Automator – PRO Version
#
# VERWENDUNG:
#
# 1) UPDATE-MODUS (Screenshots & Thumbnails aktualisieren)
#      python portfolio.py
#
#    → Durchsucht alle Wochenordner und:
#        • generiert fehlende Thumbnails (300px)
#        • aktualisiert Screenshot-Listen in allen READMEs
#        • sortiert chronologisch (neueste zuerst)
#
# 2) AUTO-INIT (Automatische Wochennummer)
#      python portfolio.py "Dein Titel"
#
#    → Findet automatisch die nächste Wochennummer und legt an:
#        • week_XX_dein-titel/ (Umlaute werden konvertiert)
#        • README.md mit Template
#        • screenshots/ + thumbnails/ Ordner
#        • Projekt-Platzhalter: <Projekt>
#
# 3) MANUELL-INIT (Woche selbst angeben)
#      python portfolio.py 05 "Smart Pointers"
#
#    → Legt Woche mit gewünschter Nummer an
#        • week_05_smart-pointers/
#        • Projekt-Platzhalter: <Projekt>
#
# 4) FULL-INIT (Woche + Titel + Projekt)
#      python portfolio.py 06 "Templates" "Generic Calculator"
#
#    → Legt alles an inkl. Projekt-Info im README
#        • week_06_templates/
#        • Projekt: Generic Calculator
#
# =====================================================================

import os
import sys
from datetime import datetime

# Optional: PIL für Thumbnails (wenn installiert)
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL nicht installiert. Thumbnails werden übersprungen.")
    print("   Installation: pip install Pillow")

THUMB_WIDTH = 300
PER_PAGE = 50
LOGFILE = "update_log.txt"

# ORDNER: weeks/ liegt eine Ebene über automation/
WEEKS_DIR = os.path.abspath(os.path.join(os.getcwd(), "..", "weeks"))

README_TEMPLATE = """ 
# Woche {week} - {title}, Projekt: {project}

![C++](https://img.shields.io/badge/C++-17%2F20-00599C?logo=cplusplus)
![Progress](https://img.shields.io/badge/Week-{week}-lightblue)

## Was ich gelernt habe

- Punkt 1
- Punkt 2
- ...
- Bsp. Global habe ich wie in .... zu sehen..

## Beispielcode

```cpp
{example_code}
```

## Was ich debugged habe

- Punkt 1
- Punkt 2
- ...

```cpp
{example_code}
```

## Projekt

- (Sinnvoll oder nicht?)
{project}

## Screenshotliste

{screenshots_markdown}
"""

# -------------------------------------------------------------
# Logging
# -------------------------------------------------------------

def log(msg: str):
    """Schreibt Log-Einträge in update_log.txt"""
    log_path = os.path.join(os.getcwd(), LOGFILE)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {msg}\n")

# -------------------------------------------------------------
# Thumbnail Generator
# -------------------------------------------------------------

def create_thumbnail(input_path, output_path):
    """Erstellt ein Thumbnail aus einem Bild"""
    if not PIL_AVAILABLE:
        return False
    
    try:
        img = Image.open(input_path)
        img.thumbnail((THUMB_WIDTH, THUMB_WIDTH))
        img.save(output_path)
        return True
    except Exception as e:
        log(f"[ERROR] Konnte Thumbnail nicht erzeugen: {input_path} → {e}")
        return False

# -------------------------------------------------------------
# Update Screenshots for ONE week folder
# -------------------------------------------------------------

def update_screenshots(folder_path):
    """Aktualisiert die Screenshot-Liste in einem Wochenordner"""
    screenshots = os.path.join(folder_path, "screenshots")
    thumbs = os.path.join(folder_path, "thumbnails")

    if not os.path.exists(screenshots):
        log(f"[SKIP] Kein screenshot-Ordner in {folder_path}")
        return None

    if PIL_AVAILABLE and not os.path.exists(thumbs):
        os.makedirs(thumbs)
        log(f"[CREATE] thumbnails/ erstellt in {folder_path}")

    # 1. Alle Bilder finden
    files = []
    for f in os.listdir(screenshots):
        ext = os.path.splitext(f)[1].lower()
        if ext in {".png", ".jpg", ".jpeg", ".gif"}:
            full = os.path.join(screenshots, f)
            mtime = os.path.getmtime(full)
            files.append((f, mtime))

    if not files:
        return "- Noch keine Screenshots"

    # ➜ neueste zuerst
    files.sort(key=lambda x: x[1], reverse=True)

    # ---------------------------------------------------------
    # 2. Thumbnails erzeugen (falls PIL verfügbar)
    # ---------------------------------------------------------
    md_pages = []
    current_page = []

    for idx, (fname, _) in enumerate(files):
        input_path = os.path.join(screenshots, fname)
        thumb_path = os.path.join(thumbs, fname) if PIL_AVAILABLE else None

        # Thumbnail erzeugen falls nicht vorhanden
        if PIL_AVAILABLE and thumb_path and not os.path.exists(thumb_path):
            create_thumbnail(input_path, thumb_path)

        # Markdown Eintrag
        if PIL_AVAILABLE and thumb_path and os.path.exists(thumb_path):
            md_line = f"- <img src=\"thumbnails/{fname}\" width=\"300\"> → [{fname}](screenshots/{fname})"
        else:
            md_line = f"- [{fname}](screenshots/{fname})"

        current_page.append(md_line)

        # Pagination
        if len(current_page) == PER_PAGE:
            md_pages.append(current_page)
            current_page = []

    if current_page:
        md_pages.append(current_page)

    # ---------------------------------------------------------
    # 3. Markdown erzeugen (mit Seiten)
    # ---------------------------------------------------------
    md_final = []

    if len(md_pages) > 1:
        # Seiten-Navigation
        page_links = " | ".join(
            [f"[Seite {i+1}](#seite-{i+1})" for i in range(len(md_pages))]
        )
        md_final.append(page_links)
        md_final.append("")

    # Inhalte der Seiten
    for i, page in enumerate(md_pages):
        if len(md_pages) > 1:
            md_final.append(f"### Seite {i+1}")
            md_final.append("")
        md_final.extend(page)
        md_final.append("")

    return "\n".join(md_final)

# -------------------------------------------------------------
# Update ALL week folders
# -------------------------------------------------------------

def update_all():
    """Aktualisiert alle Wochenordner"""
    updated = 0

    if not os.path.exists(WEEKS_DIR):
        print(f"❌ Ordner nicht gefunden: {WEEKS_DIR}")
        log(f"[ERROR] WEEKS_DIR nicht gefunden: {WEEKS_DIR}")
        return

    for folder in os.listdir(WEEKS_DIR):
        if folder.startswith("week_"):
            folder_path = os.path.join(WEEKS_DIR, folder)
            readme = os.path.join(folder_path, "README.md")

            if not os.path.exists(readme):
                continue

            md = update_screenshots(folder_path)
            if md is None:
                continue

            # README ersetzen
            with open(readme, "r", encoding="utf-8") as f:
                content = f.read()

            if "## Screenshotliste" in content:
                pre, _ = content.split("## Screenshotliste", 1)
                new_content = pre + "## Screenshotliste\n\n" + md

                with open(readme, "w", encoding="utf-8") as f:
                    f.write(new_content)

                updated += 1
                log(f"[UPDATE] README aktualisiert in {folder}")

    print(f"✔ UPDATE abgeschlossen. {updated} Ordner aktualisiert.")
    log(f"[DONE] Update abgeschlossen: {updated}")

# -------------------------------------------------------------
# Hilfsfunktionen
# -------------------------------------------------------------

def normalize_title(title: str) -> str:
    """Konvertiert Titel in saubere kebab-case Ordnernamen."""
    title = title.lower()
    title = title.strip()
    title = re.sub(r"ä", "ae", title)
    title = re.sub(r"ö", "oe", title)
    title = re.sub(r"ü", "ue", title)
    title = re.sub(r"ß", "ss", title)
    title = re.sub(r"[^a-z0-9]+", "-", title)
    title = re.sub(r"-+", "-", title)
    return title.strip("-")

def get_next_week_number():
    """Findet die höchste week_XX und gibt +1 zurück."""
    if not os.path.exists(WEEKS_DIR):
        return "01"
    max_week = 0
    for folder in os.listdir(WEEKS_DIR):
        if folder.startswith("week_"):
            parts = folder.split("_")
            if len(parts) > 1 and parts[1].isdigit():
                num = int(parts[1])
                if num > max_week:
                    max_week = num
    return f"{max_week + 1:02d}"

# -------------------------------------------------------------
# INIT: neue Woche anlegen
# -------------------------------------------------------------

def init_week(week, title, project):
    """Erstellt einen neuen Wochenordner"""
    if not os.path.exists(WEEKS_DIR):
        os.makedirs(WEEKS_DIR)
        log(f"[CREATE] weeks/ Ordner erstellt: {WEEKS_DIR}")

    folder = os.path.join(
        WEEKS_DIR,
        f"week_{week}_{title}"
    )

    if not os.path.exists(folder):
        os.makedirs(folder)

    os.makedirs(os.path.join(folder, "screenshots"), exist_ok=True)
    if PIL_AVAILABLE:
        os.makedirs(os.path.join(folder, "thumbnails"), exist_ok=True)

    readme = os.path.join(folder, "README.md")
    with open(readme, "w", encoding="utf-8") as f:
        f.write(README_TEMPLATE.format(
            week=week,
            title=title,
            project=project,
            example_code="// Beispielcode hier einfügen",
            screenshots_markdown="- Noch keine Screenshots"
        ))

    print(f"✔ INIT abgeschlossen → {folder}")
    log(f"[INIT] Ordner erstellt: {folder}")

# -------------------------------------------------------------
# MAIN
# -------------------------------------------------------------

if __name__ == "__main__":
    args = sys.argv[1:]
    
    # UPDATE MODE (keine Argumente)
    if len(args) == 0:
        update_all()
        sys.exit()
    
    # INIT: 1 Argument → nur Titel (Woche automatisch, Projekt Platzhalter)
    if len(args) == 1:
        title = args[0]
        week = get_next_week_number()
        project = "<Projekt>"
        title_norm = normalize_title(title)
        init_week(week, title_norm, project)
        sys.exit()
    
    # INIT: 2 Argumente → Woche + Titel
    if len(args) == 2:
        week, title = args
        project = "<Projekt>"
        title_norm = normalize_title(title)
        init_week(week, title_norm, project)
        sys.exit()
    
    # INIT: 3 Argumente → Woche, Titel, Projekt
    if len(args) == 3:
        week, title, project = args
        title_norm = normalize_title(title)
        init_week(week, title_norm, project)
        sys.exit()
    
    # Falls nichts passt:
    print("❌ Falsche Argumente!")
    print("Benutzung:")
    print("  python portfolio.py                        → Update aller Wochen")
    print("  python portfolio.py <Titel>                → Nächste Woche erzeugen")
    print("  python portfolio.py <Woche> <Titel>        → Projekt = <Projekt>")
    print("  python portfolio.py <Woche> <Titel> <Projekt>")