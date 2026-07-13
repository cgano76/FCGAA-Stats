import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile


NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def clean_text(value):
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return " ".join(text.split())


def read_xlsx_rows(path):
    with ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall(NS + "si"):
                strings.append("".join(node.text or "" for node in item.findall(".//" + NS + "t")))

        def cell_value(cell):
            value = cell.find(NS + "v")
            if value is None:
                return ""
            text = value.text or ""
            if cell.attrib.get("t") == "s":
                return strings[int(text)]
            return text

        root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        rows = []
        for row in root.findall(".//" + NS + "row"):
            rows.append([cell_value(cell) for cell in row])
        return rows


def dictionary_columns(path):
    rows = read_xlsx_rows(path)
    columns = []
    for row in rows:
        if not row or not str(row[0]).isdigit():
            continue
        position = int(float(row[0]))
        label = clean_text(row[1] if len(row) > 1 else "")
        value_type = clean_text(row[2] if len(row) > 2 else "")
        columns.append({"position": position, "label": label, "type": value_type})
    return columns


INDICATOR_ALIASES = {
    "Nombre d'exploitations": "Nombre d'exploitations",
    "Surface agricole utile (ha)": "SAU (en ha)",
    "Produit Brut (HT)": "Produit brut (HT)",
    "EBE hors remuneration de l'exploitant": "EBE hors remuneration exploitant",
    "Resultat courant avant remuneration des associes": "Resultat courant hors remuneration exploitant",
    "Total du bilan": "Total Bilan",
    "Fragilite financiere": "Fragilite financiere",
    "Fond de roulement": "Fonds de roulement",
    "Annuites long et moyen terme": "Annuites",
    "Prelevements personnels": "Prelevements personnels",
    "Valeur ajoutee": "Valeur ajoutee",
    "Marge brute": "Marge brute",
    "Dont production vegetale": "Dont ventes vegetales",
    "Dont production animale": "Dont ventes animales",
    "Dont production transformee": "Dont produits transformes",
    "Dont subventions": "Dont subventions",
}


META_POSITIONS = set(range(1, 9))
DATE_RE = re.compile(r"^(20\d{2})")


def money_indicator(label):
    lower = label.lower()
    if "fragilite" in lower or "autonomie" in lower or "taux" in lower:
        return False
    if "nombre d'exploitations" in lower or "surface agricole" in lower or "unite de main" in lower:
        return False
    return True


def parse_number(text):
    if text in {"", None}:
        return None
    try:
        return float(str(text).replace(",", "."))
    except ValueError:
        return None


def format_value(number):
    if number is None:
        return ""
    if abs(number - round(number)) < 0.00001:
        return str(int(round(number)))
    return f"{number:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def zone_column(zone):
    return {"0": "Toutes", "1": "Z1", "2": "Z2", "3": "Z3"}.get(str(zone), f"Z{zone}")


def tranche_column(tranche):
    return {"0": None, "1": "1/4 inferieur", "2": "Median", "3": "1/4 superieur"}.get(str(tranche), f"Tranche {tranche}")


def parse_txt(txt_path, dictionary_path):
    columns = dictionary_columns(dictionary_path)
    path = Path(txt_path)
    candidates = []
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        values = line.rstrip("\n").split(";")
        meta = {}
        for column in columns[:8]:
            index = column["position"] - 1
            meta[column["label"]] = values[index] if index < len(values) else ""

        raw_code = meta.get("Code nomenclature", "")
        production_space = "BIO" if raw_code.startswith("B-") else "CONVENTIONNEL"
        profession_code = raw_code.replace("B-", "").replace("--", "")
        closure = int(meta.get("Annee de production") or 0) or None
        harvest = closure
        zone = meta.get("Numero de zone", "0")
        tranche = meta.get("Numero de tranche", "0")
        column_label = tranche_column(tranche) or zone_column(zone)
        table_type = "quartile" if tranche_column(tranche) else "zone"

        for column in columns:
            if column["position"] in META_POSITIONS:
                continue
            index = column["position"] - 1
            raw_value = values[index] if index < len(values) else ""
            numeric = parse_number(raw_value)
            if numeric is None:
                continue

            base_label = clean_text(column["label"])
            indicator = INDICATOR_ALIASES.get(base_label, base_label)
            unit = "K EUR" if column["type"] == "INTEGER" and money_indicator(base_label) else ""
            if "surface agricole" in base_label.lower():
                unit = "ha"
            elif "unite de main" in base_label.lower():
                unit = "UMO"
            elif "nombre d'exploitations" in base_label.lower():
                unit = "nombre"
            elif "fragilite" in base_label.lower() or "autonomie" in base_label.lower() or "taux" in base_label.lower():
                unit = "ratio"

            value_numeric = numeric / 1000 if unit == "K EUR" else numeric
            candidates.append(
                {
                    "indicator": indicator,
                    "column": column_label,
                    "value": format_value(value_numeric),
                    "value_numeric": value_numeric,
                    "unit": unit or "valeur",
                    "value_type": "valeur",
                    "page": None,
                    "line": line_number,
                    "annee_cloture": closure,
                    "annee_recolte": harvest,
                    "profession_code": profession_code,
                    "profession_label": profession_code,
                    "production_space": production_space,
                    "table_type": table_type,
                    "status": "a_verifier",
                    "confidence": "haute",
                    "source": f"TXT ligne {line_number} / position {column['position']}",
                    "pdf_url": None,
                }
            )

    return {
        "filename": path.name,
        "source_type": "txt",
        "pages": None,
        "annee_recueil": None,
        "annee_cloture": None,
        "annee_recolte_default": None,
        "candidates_count": len(candidates),
        "candidates": candidates,
        "reference_pdfs": [],
    }


if __name__ == "__main__":
    txt = sys.argv[1]
    dictionary = sys.argv[2]
    print(json.dumps(parse_txt(txt, dictionary), ensure_ascii=False))
