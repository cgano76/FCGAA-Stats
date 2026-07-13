import json
import re
import sys
import unicodedata
from pathlib import Path

from pypdf import PdfReader, PdfWriter


INDICATORS = [
    {"label": "Nombre d'exploitations", "aliases": ["Nombre d'exploitations"], "unit": "nombre"},
    {"label": "Unite de main d'oeuvre", "aliases": ["Unité de main d'œuvre", "Unite de main d'oeuvre"], "unit": "UMO"},
    {"label": "SAU (en ha)", "aliases": ["SAU (en ha)"], "unit": "ha"},
    {"label": "Produit brut (HT)", "aliases": ["Produit brut (HT)"], "unit": "K EUR"},
    {"label": "Dont ventes vegetales", "aliases": ["Dont ventes végétales", "Dont ventes vegetales"], "unit": "K EUR"},
    {"label": "Dont ventes animales", "aliases": ["Dont ventes animales"], "unit": "K EUR"},
    {"label": "Dont produits transformes", "aliases": ["Dont produits transformés", "Dont produits transformes"], "unit": "K EUR"},
    {"label": "Dont subventions", "aliases": ["Dont subventions"], "unit": "K EUR"},
    {"label": "Marge brute", "aliases": ["Marge brute"], "unit": "K EUR"},
    {"label": "Fermage", "aliases": ["Fermage"], "unit": "K EUR"},
    {"label": "Autres achats et charges externes", "aliases": ["Autres achats et charges externes"], "unit": "K EUR"},
    {"label": "Valeur ajoutee", "aliases": ["Valeur ajoutée", "Valeur ajoutee"], "unit": "K EUR"},
    {"label": "Charges de personnel", "aliases": ["Charges de personnel"], "unit": "K EUR"},
    {"label": "Cotisations sociales exploitants", "aliases": ["Cotisations sociales exploitants"], "unit": "K EUR"},
    {
        "label": "EBE hors remuneration exploitant",
        "aliases": ["EBE hors rému. exploitant", "EBE hors remu. exploitant", "EBE hors rémunération exploitant"],
        "unit": "K EUR",
    },
    {"label": "Amortissement et provisions", "aliases": ["Amortissement et provisions"], "unit": "K EUR"},
    {"label": "Resultat financier", "aliases": ["Résultat financier", "Resultat financier"], "unit": "K EUR"},
    {
        "label": "Resultat courant hors remuneration exploitant",
        "aliases": ["Résultat courant hors rému exploitant", "Resultat courant hors remu exploitant"],
        "unit": "K EUR",
    },
    {"label": "Total Bilan", "aliases": ["Total Bilan"], "unit": "K EUR"},
    {"label": "Immobilisations nettes", "aliases": ["Immobilisations nettes"], "unit": "K EUR"},
    {"label": "Stocks", "aliases": ["Stocks"], "unit": "K EUR"},
    {"label": "Capitaux propres avec CCA", "aliases": ["Capitaux propres avec CCA"], "unit": "K EUR"},
    {"label": "Dettes financieres", "aliases": ["Dettes financières", "Dettes financieres"], "unit": "K EUR"},
    {"label": "Dettes fournisseurs", "aliases": ["Dettes fournisseurs"], "unit": "K EUR"},
    {"label": "Fonds de roulement", "aliases": ["Fonds de roulement"], "unit": "K EUR"},
    {"label": "Endettement total", "aliases": ["Endettement total"], "unit": "K EUR"},
    {"label": "Annuites", "aliases": ["Annuités", "Annuites", "Annuités long et moyen terme"], "unit": "K EUR"},
    {"label": "Prelevements personnels", "aliases": ["Prélèvements personnels", "Prelevements personnels"], "unit": "K EUR"},
    {"label": "Autonomie financiere", "aliases": ["Autonomie financière", "Autonomie financiere"], "unit": "ratio"},
    {
        "label": "Fragilite financiere",
        "aliases": ["Fragilité financière", "Fragilite financiere", "Fragilité fin.", "Fragilite fin.", "Fragilité fin. : (Annuités+PP) / EBE", "Fragilite fin. : (Annuites+PP) / EBE"],
        "unit": "ratio",
    },
]

LABELS = [item["label"] for item in INDICATORS]

NOMENCLATURE_PATHS = [
    Path(r"S:\FCGAA\Stat Nationales\Campagnes\2026\Rapports\NOMENCLATURES.pdf"),
    Path("NOMENCLATURES.pdf"),
]


def load_profession_map() -> dict[str, str]:
    fallback = {
        "0000000": "Ferme FCGAA",
        "1100000": "GRANDES CULTURES",
        "1200000": "MARAICHAGE",
        "1300000": "VITICULTURE",
        "1302000": "VITICULTURE - Bordelais",
        "1303000": "VITICULTURE - Beaujolais",
        "1304000": "VITICULTURE - Bourgogne",
        "1306000": "VITICULTURE - Champagne",
        "2100000": "BOVINS LAIT",
        "2200000": "BOVINS VIANDE",
        "2400000": "AVICULTURE",
    }

    path = next((candidate for candidate in NOMENCLATURE_PATHS if candidate.exists()), None)
    if not path:
        return fallback

    try:
        reader = PdfReader(str(path))
        mapping = dict(fallback)
        for page in reader.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():
                clean = " ".join(line.split())
                match = re.match(
                    r"^([0-9]{7}|[0-9]{4}\+\d{2})\s+(.+?)\s+(?:0,00|30\s*000,00)\s",
                    clean,
                )
                if match:
                    mapping[match.group(1)] = clean_text(match.group(2).strip())
        return mapping
    except Exception:
        return fallback


def normalize(text: str) -> str:
    return " ".join(text.replace("\x00", " ").split())


def clean_text(value: str | None) -> str:
    if value is None:
        return ""
    replacements = {
        "€": "EUR",
        "œ": "oe",
        "Œ": "OE",
        "–": "-",
        "—": "-",
        "’": "'",
        "é": "e",
        "è": "e",
        "ê": "e",
        "à": "a",
        "ù": "u",
        "ç": "c",
    }
    text = str(value)
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return " ".join(text.split())


def detect_closure(text: str, filename: str) -> int | None:
    filename_match = re.search(r"Exercices?\s*(20\d{2})", filename, flags=re.IGNORECASE)
    if filename_match:
        return int(filename_match.group(1))

    text_match = re.search(r"exercices?\s+clos\s+en\s+(20\d{2})", text, flags=re.IGNORECASE)
    if text_match:
        return int(text_match.group(1))

    recueil = detect_recueil(filename)
    if recueil:
        return recueil - 1

    return None


def detect_harvest(text: str, closure: int | None) -> int | None:
    match = re.search(r"r[ée]colte\s+(20\d{2})", text, flags=re.IGNORECASE)
    if match:
        return int(match.group(1))

    if re.search(r"r[ée]colte\s+N-1", text, flags=re.IGNORECASE) and closure:
        return closure - 1

    if re.search(r"r[ée]colte\s+N\b", text, flags=re.IGNORECASE) and closure:
        return closure

    return closure


def detect_recueil(filename: str) -> int | None:
    match = re.search(r"FCGAA\s+(20\d{2})", filename, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def detect_profession(text: str, profession_map: dict[str, str]) -> tuple[str, str, bool]:
    match = re.search(r"(?:--|B-)\s*([0-9]{7}|[0-9]{4}\+\d{2})", text)
    if match:
        code = match.group(1)
        return code, clean_text(profession_map.get(code, code)), text[match.start() : match.start() + 2] == "B-"

    return "0000000", clean_text(profession_map.get("0000000", "Ferme FCGAA")), False


def safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")[:140]


def find_indicator_hits(text: str) -> list[dict]:
    hits = []
    lower = clean_text(text).lower()
    for item in INDICATORS:
        for alias in item["aliases"]:
            start = 0
            alias_lower = clean_text(alias).lower()
            while True:
                index = lower.find(alias_lower, start)
                if index == -1:
                    break
                hits.append(
                    {
                        "start": index,
                        "end": index + len(alias),
                        "label": item["label"],
                        "unit": item["unit"],
                    }
                )
                start = index + len(alias)
    filtered = []
    for hit in sorted(hits, key=lambda item: (item["start"], -(item["end"] - item["start"]))):
        if filtered and hit["start"] < filtered[-1]["end"]:
            continue
        filtered.append(hit)
    return filtered


def extract_numbers(segment: str, indicator: str) -> list[str]:
    tokens = re.findall(r"-?\d+(?:[,.]\d+)?", segment.replace("\u00a0", " "))
    if indicator in {"SAU (en ha)", "Unite de main d'oeuvre"}:
        combine_prefix_length = 0
    elif indicator == "Nombre d'exploitations":
        combine_prefix_length = 2
    else:
        combine_prefix_length = 1

    numbers = []
    index = 0
    while index < len(tokens):
        current = tokens[index]
        next_token = tokens[index + 1] if index + 1 < len(tokens) else None
        current_digits = current.lstrip("-")
        if (
            next_token
            and "," not in current
            and "." not in current
            and "," not in next_token
            and "." not in next_token
            and len(current_digits) <= combine_prefix_length
            and len(next_token) == 3
        ):
            numbers.append(f"{current} {next_token}")
            index += 2
            continue
        numbers.append(current)
        index += 1
    return numbers


def number_to_float(value: str) -> float | None:
    cleaned = value.replace("\u00a0", " ").replace(" ", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def classify_columns(numbers: list[str], table_type: str, base_unit: str) -> list[dict]:
    if table_type == "quartile":
        main_columns = ["1/4 inferieur", "Median", "1/4 superieur", "Toutes"]
    else:
        main_columns = ["Z1", "Z2", "Z3", "Toutes"]

    cells = []
    if len(numbers) >= 9:
        index = 0
        for column in main_columns:
            cells.append({"column": column, "value": numbers[index], "unit": base_unit, "value_type": "valeur"})
            cells.append({"column": column, "value": numbers[index + 1], "unit": "%", "value_type": "pourcentage"})
            index += 2
        cells.append({"column": "Moy K EUR/ha", "value": numbers[8], "unit": "K EUR/ha", "value_type": "moyenne_ha"})
        return cells

    if len(numbers) == 5:
        cells = [
            {"column": main_columns[index], "value": value, "unit": base_unit, "value_type": "valeur"}
            for index, value in enumerate(numbers[:4])
        ]
        cells.append({"column": "Moy K EUR/ha", "value": numbers[4], "unit": "K EUR/ha", "value_type": "moyenne_ha"})
        return cells

    if len(numbers) >= 4:
        return [
            {"column": main_columns[index], "value": value, "unit": base_unit, "value_type": "valeur"}
            for index, value in enumerate(numbers[:4])
        ]

    return [{"column": "Toutes", "value": value, "unit": base_unit, "value_type": "valeur"} for value in numbers]


def extract_candidates(
    reader: PdfReader,
    closure: int | None,
    file_url: str | None,
    profession_map: dict[str, str],
) -> list[dict]:
    candidates = []
    seen = set()

    for page_index, page in enumerate(reader.pages, start=1):
        text = normalize(page.extract_text() or "")
        if not text:
            continue

        harvest = detect_harvest(text, closure)
        profession_code, profession_label, bio_prefix = detect_profession(text, profession_map)
        space = "BIO" if bio_prefix or re.search(r"\bBIO\b|biologiques?", text, flags=re.IGNORECASE) else "CONVENTIONNEL"
        table_type = "quartile" if "1/4 inf" in text or "Médian" in text or "Median" in text else "zone"

        oga_match = re.search(r"Nombre d'OGA\s*:\s*(\d+)", text, flags=re.IGNORECASE)
        if oga_match:
            key = (page_index, "Nombre d'OGA", oga_match.group(1), profession_code, space, table_type)
            if key not in seen:
                seen.add(key)
                candidates.append(
                    {
                        "indicator": "Nombre d'OGA",
                        "column": "Toutes",
                        "value": oga_match.group(1),
                        "value_numeric": number_to_float(oga_match.group(1)),
                        "unit": "nombre",
                        "value_type": "valeur",
                        "page": page_index,
                        "annee_cloture": closure,
                        "annee_recolte": harvest,
                        "profession_code": profession_code,
                        "profession_label": profession_label,
                        "production_space": space,
                        "table_type": table_type,
                        "status": "a_verifier",
                        "confidence": "moyenne",
                        "source": f"Page {page_index}",
                        "pdf_url": f"{file_url}#page={page_index}" if file_url else None,
                    }
                )

        scan_text = clean_text(text)
        hits = find_indicator_hits(text)
        for idx, hit in enumerate(hits):
            segment_end = hits[idx + 1]["start"] if idx + 1 < len(hits) else min(len(scan_text), hit["end"] + 260)
            segment = scan_text[hit["end"] : segment_end]
            stop_match = re.search(
                r"\s(?:Ferme FCGAA|BIO\s+-|GRANDES CULTURES|MARAICHAGE|VITICULTURE|BOVINS|AVICULTURE|OVINS|CAPRINS|Moyennes|Repartition)\b",
                segment,
                flags=re.IGNORECASE,
            )
            if stop_match:
                segment = segment[: stop_match.start()]
            numbers = extract_numbers(segment, hit["label"])
            if not numbers:
                continue

            for cell in classify_columns(numbers, table_type, hit["unit"]):
                key = (
                    page_index,
                    hit["label"],
                    cell["column"],
                    cell["value_type"],
                    cell["value"],
                    profession_code,
                    space,
                    table_type,
                )
                if key in seen:
                    continue
                seen.add(key)
                candidates.append(
                    {
                        "indicator": hit["label"],
                        "column": cell["column"],
                        "value": cell["value"],
                        "value_numeric": number_to_float(cell["value"]),
                        "unit": cell["unit"],
                        "value_type": cell["value_type"],
                        "raw_values": numbers[:12],
                        "page": page_index,
                        "annee_cloture": closure,
                        "annee_recolte": harvest,
                        "profession_code": profession_code,
                        "profession_label": profession_label,
                        "production_space": space,
                        "table_type": table_type,
                        "status": "a_verifier",
                        "confidence": "moyenne",
                        "source": f"Page {page_index}",
                        "pdf_url": f"{file_url}#page={page_index}" if file_url else None,
                    }
                )

    return candidates


def build_reference_pdfs(
    reader: PdfReader,
    candidates: list[dict],
    output_dir: Path | None,
    url_base: str | None,
) -> list[dict]:
    groups: dict[tuple, dict] = {}
    for candidate in candidates:
        code = candidate.get("profession_code") or "0000000"
        key = (
            code,
            candidate.get("profession_label") or code,
            candidate.get("production_space") or "CONVENTIONNEL",
            candidate.get("annee_cloture") or "A_verifier",
            candidate.get("annee_recolte") or candidate.get("annee_cloture") or "A_verifier",
        )
        if key not in groups:
            groups[key] = {"pages": set(), "zone_pages": set(), "quartile_pages": set()}
        page = candidate.get("page")
        if isinstance(page, int):
            groups[key]["pages"].add(page)
            if candidate.get("table_type") == "quartile":
                groups[key]["quartile_pages"].add(page)
            else:
                groups[key]["zone_pages"].add(page)

    references = []
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    for key, data in groups.items():
        code, label, space, closure, harvest = key
        pages = sorted(data["pages"])
        filename = f"{safe_slug(str(closure))}_{safe_slug(str(harvest))}_{safe_slug(space)}_{safe_slug(code)}.pdf"
        pdf_url = None
        if output_dir and pages:
            writer = PdfWriter()
            for page_no in pages:
                writer.add_page(reader.pages[page_no - 1])
            target = output_dir / filename
            with target.open("wb") as handle:
                writer.write(handle)
            pdf_url = f"{url_base.rstrip('/')}/{filename}" if url_base else str(target)

        references.append(
            {
                "profession_code": code,
                "profession_label": label,
                "production_space": space,
                "annee_cloture": closure,
                "annee_recolte": harvest,
                "pages": pages,
                "zone_pages": sorted(data["zone_pages"]),
                "quartile_pages": sorted(data["quartile_pages"]),
                "reference_pdf_url": pdf_url,
            }
        )
    return references


def dedupe_candidates(candidates: list[dict]) -> list[dict]:
    deduped = []
    seen = set()
    for candidate in candidates:
        for field in ["indicator", "column", "unit", "value_type", "profession_label", "production_space", "source"]:
            candidate[field] = clean_text(candidate.get(field))
        key = (
            candidate.get("annee_cloture"),
            candidate.get("annee_recolte"),
            candidate.get("profession_code"),
            candidate.get("production_space"),
            candidate.get("indicator"),
            candidate.get("column"),
            candidate.get("value_type"),
            candidate.get("value"),
            candidate.get("page"),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(candidate)
    return deduped


def main() -> int:
    if len(sys.argv) not in {2, 3, 5}:
        print(json.dumps({"error": "Usage: extract_pdf.py <pdf_path> [pdf_url] [refs_dir refs_url_base]"}))
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(json.dumps({"error": "Fichier introuvable"}))
        return 2

    reader = PdfReader(str(path))
    all_text = normalize(" ".join((page.extract_text() or "")[:3000] for page in reader.pages[:5]))
    closure = detect_closure(all_text, path.name)
    file_url = sys.argv[2] if len(sys.argv) > 2 else None
    profession_map = load_profession_map()
    candidates = extract_candidates(reader, closure, file_url, profession_map)
    candidates = dedupe_candidates(candidates)
    refs_dir = Path(sys.argv[3]) if len(sys.argv) == 5 else None
    refs_url_base = sys.argv[4] if len(sys.argv) == 5 else None
    reference_pdfs = build_reference_pdfs(reader, candidates, refs_dir, refs_url_base)

    result = {
        "filename": path.name,
        "pages": len(reader.pages),
        "annee_recueil": detect_recueil(path.name),
        "annee_cloture": closure,
        "annee_recolte_default": detect_harvest(all_text, closure),
        "candidates_count": len(candidates),
        "candidates": candidates,
        "reference_pdfs": reference_pdfs,
        "warnings": [
            "Extraction automatique a verifier humainement avant integration.",
            "Les valeurs detectees sont candidates et ne sont pas validees.",
        ],
    }

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
