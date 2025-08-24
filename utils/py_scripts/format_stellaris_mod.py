import os
import re

MOD_PATH = "C:\\Games\\Stellaris\\common\\solar_system_initializers"  # Ajusta la ruta

HEADER = """# ------------------------------------------
# Stellaris Mod: NombreDelMod
# Copyright (c) 2025 Francisco Javier Jiménez Mesa
# License: MIT (Non-Commercial)
# Use for personal or non-commercial purposes only.
# Commercial use is prohibited.
# ------------------------------------------
"""

def format_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Eliminar espacios dobles
    content = re.sub(r"[ ]{2,}", " ", content)

    # 2. Normalizar espacios alrededor del =
    content = re.sub(r"\s*=\s*", " = ", content)

    # 3. Insertar la cabecera si no está ya
    if not content.startswith("# ------------------------------------------"):
        content = HEADER + "\n" + content

    # 4. Guardar cambios
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

# Recorrer todos los archivos .txt del mod
for root, dirs, files in os.walk(MOD_PATH):
    for file in files:
        if file.endswith(".txt"):
            file_path = os.path.join(root, file)
            print(f"Formateando {file_path}")
            format_file(file_path)

print("Formateo y cabeceras completados.")