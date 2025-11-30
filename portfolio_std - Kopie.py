# =====================================================================
# Portfolio Automator step 01 – STD Version
# INIT:   python <name>.py <week> <title> <project>
# UPDATE: python <name>.py
# =====================================================================

import os
import sys

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

# Update Screenshots
def update_screenshots(folder):
    screenshots_folder = os.path.join(folder, "screenshots")
    if not os.path.exists(screenshots_folder):
        print(f"Screenshots-Ordner existiert nicht: {screenshots_folder}. Abbruch.")
        return None

    # Screenshots finden
    files = []
    for f in os.listdir(screenshots_folder):
        ext = os.path.splitext(f)[1].lower()
        if ext in {".png", ".jpg", ".jpeg", ".gif"}:
            files.append(f)

    if not files:
        return "- Noch keine Screenshots"

    # Markdown-Liste generieren (sortiert)
    files.sort()
    md_list = "\n".join([f"- [{f}](screenshots/{f})" for f in files])
    return md_list


def update_all_screenshots():
    """Aktualisiert Screenshots in allen Wochenordnern"""
    current_dir = os.getcwd()
    updated_count = 0
    
    # Alle Ordner durchsuchen, die mit "week" beginnen
    for item in os.listdir(current_dir):
        if os.path.isdir(item) and item.startswith("week"):
            readme_path = os.path.join(item, "README.md")
            
            if not os.path.exists(readme_path):
                print(f"⚠️  {item}: Keine README.md gefunden, überspringe...")
                continue
            
            screenshots_md = update_screenshots(item)
            if screenshots_md is None:
                print(f"⚠️  {item}: Kein screenshots-Ordner gefunden, überspringe...")
                continue
                
            
            # README lesen und aktualisieren
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if "## Screenshotliste" in content:
                pre, _ = content.split("## Screenshotliste", 1)
                content = pre + "## Screenshotliste\n\n" + screenshots_md + "\n"
                
                with open(readme_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                print(f"✅ {item}: Screenshots aktualisiert")
                updated_count += 1
            else:
                print(f"⚠️  {item}: '## Screenshotliste' nicht gefunden")
    
    if updated_count == 0:
        print("\n❌ Keine Ordner aktualisiert. Stelle sicher, dass Wochenordner existieren.")
    else:
        print(f"\n✅ Fertig! {updated_count} Ordner aktualisiert.")


def main():
    # ----- Template + Struktur erstellen (mit 3 Argumenten) -----
    if len(sys.argv) >= 4:
        week = sys.argv[1]
        title = sys.argv[2]
        project = sys.argv[3]
        
        folder = f"week_{week}_{title.replace(' ', '_').lower()}"
        readme_path = os.path.join(folder, "README.md")
        # Keine Argumente => nur Screenshots updaten
        # print("updating and list screenshots")
        # print("Error: missing arguments. 3 arguments required!\n"
        # "week (e.g. \"01\"), title and project\n"
        # "Usage: python <script_name>.py <week> <title> <project>")
    

        # ---- Ordner für Woche erstellen -----
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✅ Ordner erstellt: {folder}")

        # ---- Screenshots-Ordner erstellen ----
        screenshots_folder = os.path.join(folder, "screenshots")
        if not os.path.exists(screenshots_folder):
            os.makedirs(screenshots_folder)
            print(f"✅ Screenshots-Ordner erstellt: {screenshots_folder}")
       
        # ---- README schreiben ----
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(README_TEMPLATE.format(
                week=week,
                title=title,
                project=project,
                example_code="// Beispielcode hier einfügen",
                screenshots_markdown="- Noch keine Screenshots"
            ))

        print(f"✅ README erstellt: {readme_path}")
        return

    # ---- Alle Screenshots aktualisieren (ohne Argumente) -----
    elif len(sys.argv) == 1:
        print("🔄 Aktualisiere Screenshots in allen Wochenordnern...\n")
        update_all_screenshots()
    
    else:
        print("❌ Error: Falsche Anzahl an Argumenten!")
        print("Usage für Init: python <script_name>.py <week> <title> <project>")
        print("Usage für Screenshot-Update: python <script_name>.py (ohne Argumente)")


# ---- Script startet hier (bei Aufruf, nicht bei import / ohne (if __name__) start bei inmport der <name>.py dei main)
if __name__ == "__main__":
    main()
    
    