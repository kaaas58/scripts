#=====================================================================
# C++ Projektgenerator – automatisch Ordnerstruktur & Basisdateien
#
# BESCHREIBUNG:
# Dieses Python-Script erzeugt eine komplette, moderne C++-Projektstruktur
# für VS Code, CMake, Ninja und MinGW-w64.
#
# Das Script legt automatisch an:
#      CMakeLists.txt
#      CMakePresets.json (Debug + Release)
#      src/main.cpp
#      include/<projektname>/example.hpp
#      build/debug + build/release
#      lib/      (für externe Libraries)
#      tests/    (für Unit-Tests)
#      README.md
#      .gitignore
#
# NAMENSVERARBEITUNG:
#    • Script kann ohne oder mit Projektname ausgeführt werden:
#         python create_project_full.py
#         python create_project_full.py My Projekt Name
#
#    • Projektname wird automatisch bereinigt:
#        - Leerzeichen oder '-' → '_'
#        - alles lowercase
#        - deutsche Umlaute → ascii:
#            ä → ae, ö → oe, ü → ue, ß → ss
#        - Sonderzeichen entfernt
#
# BEISPIELE:
#
#    python create_project_full.py
#        → erzeugt: my_project/.....
#
#    python create_project_full.py "Erste Schritte"
#        → erzeugt: erste_schritte/.......
#
#    python project_gen.py Fahrzeug-System
#        → erzeugt: fahrzeug_system/
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
# HINWEIS:
#   • Dieses Script wird außerhalb aller Projektordner ausgeführt
#     (z. B. im DEV-Ordner → erzeugt dort Unterordner).
#   • Für jeden neuen Projektnamen einfach erneut ausführen.
#
#=====================================================================


import os
import json
import sys
import re

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

if len(sys.argv) > 1:
    raw_name = " ".join(sys.argv[1:])
    project_name = normalize_project_name(raw_name)
else:
    raw_name = input(f"Projektname eingeben (Enter = '{default_name}'): ").strip()
    if raw_name == "":
        project_name = default_name
    else:
        project_name = normalize_project_name(raw_name)

print(f"📂 Projektname verwendet: {project_name}")

# ------------------------------------------------------------
# MinGW Pfad — EINMAL bei dir anpassen
# ------------------------------------------------------------
mingw_path = "C:/mingw64/bin"

# ------------------------------------------------------------
# Ordnerstruktur
# ------------------------------------------------------------
folders = [
    project_name,
    f"{project_name}/src",
    f"{project_name}/include/{project_name}",
    f"{project_name}/build/debug",
    f"{project_name}/build/release",
    f"{project_name}/lib",
    f"{project_name}/tests"
]

# ------------------------------------------------------------
# Dateien
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
│ └── example.hpp
├── build/
│ ├── debug/
│ └── release/
├── lib/
└── tests/

bash
Code kopieren

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
# Ordner erzeugen
# ------------------------------------------------------------
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# ------------------------------------------------------------
# Dateien erzeugen
# ------------------------------------------------------------
files = {
    f"{project_name}/CMakeLists.txt": cmake_lists,
    f"{project_name}/CMakePresets.json": json.dumps(cmake_presets, indent=4),
    f"{project_name}/src/main.cpp": main_cpp,
    f"{project_name}/include/{project_name}/example.hpp": example_hpp,
    f"{project_name}/README.md": readme,
    f"{project_name}/.gitignore": gitignore
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"✅ Projekt '{project_name}' erfolgreich erstellt!")