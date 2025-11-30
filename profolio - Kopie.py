# =====================================================================
# Portfolio Automator – PRO Version
# INIT:   python <name>.py <week> <title> <project>
# UPDATE: python <name>.py
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

README_TEMPLATE = """
# Woche {week} - {title}, Projekt: {project}

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
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {msg}\n")

# -------------------------------------------------------------
# Thumbnail Generator
# -------------------------------------------------------------

def create_thumbnail(input_path, output_path):
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

def update_screenshots(folder):
    screenshots = os.path.join(folder, "screenshots")
    thumbs = os.path.join(folder, "thumbnails")

    if not os.path.exists(screenshots):
        log(f"[SKIP] Kein screenshot-Ordner in {folder}")
        return None

    if PIL_AVAILABLE and not os.path.exists(thumbs):
        os.makedirs(thumbs)
        log(f"[CREATE] thumbnails/ erstellt in {folder}")

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
            if create_thumbnail(input_path, thumb_path):
                log(f"[THUMB] Created: {thumb_path}")
            else:
                log(f"[ERROR] Thumbnail failed: {thumb_path}")

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
    base = os.getcwd()
    updated = 0

    for folder in os.listdir(base):
        if folder.startswith("week_") and os.path.isdir(folder):
            readme = os.path.join(folder, "README.md")
            if not os.path.exists(readme):
                continue

            md = update_screenshots(folder)
            if md is None:
                continue

            # README ersetzen
            with open(readme, "r", encoding="utf-8") as f:
                content = f.read()

            if "## Screenshotliste" in content:
                pre, _ = content.split("## Screenshotliste", 1)
                new_content = pre + "## Screenshotliste\n\n" + md + "\n"

                with open(readme, "w", encoding="utf-8") as f:
                    f.write(new_content)

                updated += 1
                log(f"[UPDATE] README aktualisiert in {folder}")

    print(f"✔ UPDATE abgeschlossen. {updated} Ordner aktualisiert.")
    log(f"[DONE] Update abgeschlossen: {updated} Ordner")

# -------------------------------------------------------------
# INIT: neue Woche anlegen
# -------------------------------------------------------------

def init_week(week, title, project):
    folder = f"week_{week}_{title.replace(' ', '_').lower()}"
    readme = os.path.join(folder, "README.md")

    if not os.path.exists(folder):
        os.makedirs(folder)

    os.makedirs(os.path.join(folder, "screenshots"), exist_ok=True)
    if PIL_AVAILABLE:
        os.makedirs(os.path.join(folder, "thumbnails"), exist_ok=True)

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
    # INIT MODE ----------------------------------------------
    if len(sys.argv) == 4:
        _, week, title, project = sys.argv
        init_week(week, title, project)

    # UPDATE MODE --------------------------------------------
    elif len(sys.argv) == 1:
        update_all()

    else:
        print("❌ Falsche Argumente!")
        print("INIT:   python portfolio.py <week> <title> <project>")
        print("UPDATE: python portfolio.py")
        