#=====================================================================
# C++ Projektgenerator – erzeugt automatisch eine moderne Projektstruktur
#
# BESCHREIBUNG:
# Dieses Python-Script erzeugt eine komplette, moderne C++-Projektstruktur
# für VS Code, CMake, Ninja und MinGW-w64.
#
# Erstellt:
#   • CMakeLists.txt, CMakePresets.json (Debug/Release)
#   • src/main.cpp
#   • include/<projekt>/example.hpp
#   • build/{debug,release}
#   • lib/, tests/, README.md, .gitignore
#
# NAMENSVERARBEITUNG:
#   • CLI: python projectgen.py "<name>" --target <pfad>
#   • Leerzeichen/'-' → '_', lowercase, Umlaute → ASCII, erlaubt: [a-z0-9_]
#    • Projektname wird automatisch bereinigt:
#        - Leerzeichen oder '-' → '_'
#        - alles lowercase
#        - deutsche Umlaute → ascii:
#            ä → ae, ö → oe, ü → ue, ß → ss
#        - Sonderzeichen entfernt
#
# BEISPIELE:
#   python projectgen.py "Smart Pointers"
#   python projectgen.py "Erste Schritte" --target ../DEV_cpp
#   python projectgen.py Fahrzeug-System --target C:/DEV/projekte
#
# AUSGABE:
# 📂 Projektname: <projektname> wird angelegt
# 📦 Projekt wird in : <path><projektname> erzeugt
# ✅ Projekt erfolgreich in <path><projektname> erstellt!
#
# Hinweis:
#   Ohne --target wird das Projekt im aktuellen Ordner erstellt.
#
# ORDNERSKIZZE DER AUSGABE:
#
#    projektname/
#     ├── CMakeLists.txt
#     ├── CMakePresets.json
#     ├── src/
#     │    └── main.cpp
#     ├── include/
#     │    └── projektname/
#     │         └── example.hpp
#     ├── build/
#     │    ├── debug/
#     │    └── release/
#     ├── lib/
#     ├── tests/
#     ├── README.md
#     └── .gitignore
#
#=====================================================================

import os
import json
import sys
import re
import argparse

# ------------------------------------------------------------
# CLI-Argumente
# ------------------------------------------------------------
parser = argparse.ArgumentParser(description="C++ Projektgenerator",
                                add_help=False)

parser.add_argument("-h", "--help", action="store_true", help="Show help")
parser.add_argument("name", nargs="*", help="Projektname (optional)")
parser.add_argument("--target", "-t", default=".", help="Zielordner für das Projekt")

args = parser.parse_args()

script_name = os.path.basename(sys.argv[0])

GREEN = "\033[92m"
CYAN  = "\033[96m"
RESET = "\033[0m"

if args.help:
    print(f'\npy {CYAN}{script_name}{RESET} "{CYAN}<projektname>{RESET}" --target/-t {CYAN}<pfad>{RESET}')
    sys.exit(0)

# ------------------------------------------------------------
# Hilfsfunktionen
# ------------------------------------------------------------
def to_ascii(name: str) -> str:
    """Wandelt Umlaute in ASCII um."""
    replacements = {
        "ä": "ae", "ö": "oe", "ü": "ue",
        "Ä": "ae", "Ö": "oe", "Ü": "ue",
        "ß": "ss"
    }
    for src, dst in replacements.items():
        name = name.replace(src, dst)
    return name


def normalize_project_name(name: str) -> str:
    """
    Formatiert Projektname für Dateisystem:
    - Umlaute → ASCII (ä→ae...)
    - lowercase
    - mehrere Leerzeichen → _
    - nur [a-z0-9_]
    """
    name = name.strip()
    name = to_ascii(name)
    name = name.lower()
    name = re.sub(r"[-\s]+", "_", name)
    name = re.sub(r"[^a-z0-9_]", "", name)
    return name

# ------------------------------------------------------------
# Projektname bestimmen
# ------------------------------------------------------------
default_name = "my_project"

if len(args.name) > 0:
    raw_name = " ".join(args.name)
    project_name = normalize_project_name(raw_name)
else:
    raw_name = input(f"Projektname eingeben (Enter = '{default_name}'): ").strip()
    if raw_name == "":
        project_name = default_name
    else:
        project_name = normalize_project_name(raw_name)

print(f"📂 Projektname: {GREEN}{project_name}{RESET} wird angelegt")

# ------------------------------------------------------------
# Zielpfad berechnen
# ------------------------------------------------------------
target_path = os.path.abspath(args.target)
project_root = os.path.join(target_path, project_name)

print(f"📦 Projekt wird in : {GREEN}{project_root}{RESET} erzeugt")

# ------------------------------------------------------------
# MinGW Pfad
# ------------------------------------------------------------
mingw_path = r"C:\Program Files\mingw64\bin"

# ------------------------------------------------------------
# Ordnerstruktur
# ------------------------------------------------------------
folders = [
    project_root,
    f"{project_root}/src",
    f"{project_root}/include/{project_name}",
    f"{project_root}/build/debug",
    f"{project_root}/build/release",
    f"{project_root}/lib",
    f"{project_root}/tests"
]

# ------------------------------------------------------------
# Dateien-Inhalt
# ------------------------------------------------------------
file_header = f"""// =============================================================
// Project: {project_name}
// Generated automatically by projectgen.py
// =============================================================
"""

# ---- CMakeLists.txt ----
cmake_lists = f"""{file_header}
cmake_minimum_required(VERSION 3.16)
project({project_name} LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

file(GLOB SOURCES "src/*.cpp")

add_executable({project_name} ${{SOURCES}})
"""

# ---- CMakePresets.json ----
cmake_presets = {
    "version": 3,
    "configurePresets": [
        {
            "name": "debug",
            "generator": "Ninja",
            "binaryDir": "${{sourceDir}}/build/debug",
            "cacheVariables": {
                "CMAKE_BUILD_TYPE": "Debug",
                "CMAKE_C_COMPILER": f"{mingw_path}/gcc.exe",
                "CMAKE_CXX_COMPILER": f"{mingw_path}/g++.exe"
            }
        },
        {
            "name": "release",
            "generator": "Ninja",
            "binaryDir": "${{sourceDir}}/build/release",
            "cacheVariables": {
                "CMAKE_BUILD_TYPE": "Release",
                "CMAKE_C_COMPILER": f"{mingw_path}/gcc.exe",
                "CMAKE_CXX_COMPILER": f"{mingw_path}/g++.exe"
            }
        }
    ],
    "buildPresets": [
        {"name": "debug", "configurePreset": "debug"},
        {"name": "release", "configurePreset": "release"}
    ]
}

# ---- main.cpp ----
main_cpp = f"""{file_header}
#include <iostream>
#include "{project_name}/example.hpp"

int main() {{
    std::cout << "Hello from {project_name}!" << std::endl;

    Example ex;
    ex.say_hello();

    return 0;
}}
"""

# ---- example.hpp ----
example_hpp = f"""{file_header}
#pragma once
#include <iostream>

class Example {{
public:
    void say_hello() const {{
        std::cout << "Example.hpp says hello!" << std::endl;
    }}
}};
"""

# ---- README.md ----
readme = f"""# {project_name}

## 📦 Projektstruktur

{project_name}/
├── CMakeLists.txt
├── CMakePresets.json
├── src/
│ └── main.cpp
├── include/
│ └── {project_name}/
│  └── example.hpp
├── build/
│ ├── debug/
│ └── release/
├── lib/
└── tests/


## ▶️ Build in VS Code

1. Projektordner öffnen  
2. **CMake: Configure** starten  
3. Debug/Release auswählen  
4. **Strg + Shift + B** zum Bauen  
5. **F5** zum Starten  
"""

# ---- .gitignore ----
gitignore = """# Build
build/
*.exe
*.o
*.obj
*.log

# VS Code
.vscode/
"""

# ------------------------------------------------------------
# Ordner erstellen
# ------------------------------------------------------------
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# ------------------------------------------------------------
# Dateien erstellen
# ------------------------------------------------------------
files = {
    f"{project_root}/CMakeLists.txt": cmake_lists,
    f"{project_root}/CMakePresets.json": json.dumps(cmake_presets, indent=4),
    f"{project_root}/src/main.cpp": main_cpp,
    f"{project_root}/include/{project_name}/example.hpp": example_hpp,
    f"{project_root}/README.md": readme,
    f"{project_root}/.gitignore": gitignore
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"✅ Projekt erfolgreich in {GREEN}{project_root}{RESET} erstellt!")
