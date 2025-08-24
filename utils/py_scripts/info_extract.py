import os
import glob
import re
import yaml

# ----------------------------
# Configuración del mod
# ----------------------------
mod_folder = "ruta/a/tu/mod"  # <-- Cambiar a la ruta de tu mod
wiki_folder = os.path.join(mod_folder, "wiki")
exclude_folders = ["gfx", "sound", "temp"]  # Carpetas a excluir

os.makedirs(wiki_folder, exist_ok=True)

# Tipos de lore a extraer
lore_types = {
    "SPECIES_TRAIT": "Traits de Especies",
    "LEADER_TRAIT": "Traits de Líderes",
    "EVENT": "Eventos"
}

# Diccionario para almacenar el lore
wiki_content = {key: [] for key in lore_types.keys()}

# ----------------------------
# Funciones auxiliares
# ----------------------------
def extract_sections(lore_block):
    """
    Divide un bloque de lore en secciones:
    narrativa, mecánicas, aplicación, rareza, sinergias, afecta
    """
    sections = {
        "narrativa": "",
        "beneficios": "",
        "aplicacion": "",
        "rareza": "",
        "sinergias": "",
        "afecta": ""
    }
    current_section = None
    for line in lore_block.splitlines():
        line_clean = line.strip().lstrip("# ").rstrip()
        if not line_clean:
            continue
        header_map = {
            "Descripci": "narrativa",
            "Narrativa": "narrativa",
            "Mecánicas": "beneficios",
            "Aplicación": "aplicacion",
            "Rareza": "rareza",
            "Sinergias": "sinergias",
            "Afecta": "afecta"
        }
        for key, section_name in header_map.items():
            if line_clean.startswith(key):
                current_section = section_name
                break
        else:
            if current_section:
                sections[current_section] += line_clean + "\n"
    return sections

def extract_yaml(file_content):
    """
    Extrae pares key: "value" simples de archivos YAML de Stellaris
    """
    pattern = r'^(\S+):\s*"(.*?)"$'
    entries = {}
    for line in file_content.splitlines():
        match = re.match(pattern, line.strip())
        if match:
            key, val = match.groups()
            entries[key] = val
    return entries

# ----------------------------
# Recorrer archivos del mod
# ----------------------------
file_paths = [f for f in glob.glob(os.path.join(mod_folder, "**", "*.*"), recursive=True)
              if all(excl not in f for excl in exclude_folders)]

# Primero extraemos los bloques de lore
for file_path in file_paths:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    for lore_type in lore_types.keys():
        pattern = rf"# BEGIN_LORE_{lore_type}_(.+?)\n(.*?)# END_LORE_{lore_type}_\1"
        matches = re.findall(pattern, content, re.DOTALL)
        for name, lore_block in matches:
            sections = extract_sections(lore_block)
            wiki_content[lore_type].append({
                "name": name.strip(),
                "sections": sections,
                "source_file": os.path.relpath(file_path, mod_folder),
                "yaml": {}
            })

# Luego buscamos archivos YAML para vincularlos
for file_path in file_paths:
    if not file_path.endswith((".yml", ".yaml")):
        continue
    with open(file_path, "r", encoding="utf-8") as f:
        yaml_content = f.read()
    yaml_entries = extract_yaml(yaml_content)

    # Asignar YAML a traits/events existentes
    for lore_type in wiki_content.keys():
        for entry in wiki_content[lore_type]:
            if entry["name"] in yaml_entries:
                entry["yaml"] = yaml_entries

# ----------------------------
# Generar Markdown
# ----------------------------
md_lines = ["# Wiki del Mod", ""]

# Tabla de contenidos
md_lines.append("## Tabla de Contenidos\n")
toc_lines = []
for lore_type, section_title in lore_types.items():
    md_lines.append(f"### {section_title}")
    toc_lines.append(f"- [{section_title}](#{section_title.lower().replace(' ', '-')})")
    for entry in wiki_content[lore_type]:
        anchor = entry['name'].lower().replace(' ', '-')
        toc_lines.append(f"  - [{entry['name']}](#{anchor})")
md_lines.extend(toc_lines)
md_lines.append("\n---\n")

# Contenido detallado
for lore_type, section_title in lore_types.items():
    md_lines.append(f"## {section_title}\n")
    for entry in wiki_content[lore_type]:
        anchor = entry['name'].lower().replace(' ', '-')
        md_lines.append(f"### {entry['name']}")
        md_lines.append(f"*Archivo origen:* `{entry['source_file']}`\n")
        # Secciones de lore
        for sec_title, content in entry['sections'].items():
            if content.strip():
                md_lines.append(f"**{sec_title.capitalize()}:**\n{content.strip()}\n")
        # Datos YAML si existen
        if entry.get("yaml"):
            md_lines.append("**Datos Stellaris (YAML):**\n")
            for key, val in entry['yaml'].items():
                md_lines.append(f"- `{key}`: \"{val}\"")
        md_lines.append("\n---\n")

# Guardar Markdown
output_file = os.path.join(wiki_folder, "wiki_mod.md")
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"Wiki generada correctamente en: {output_file}")
