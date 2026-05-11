import json
import re
from pathlib import Path

EXTRACTED_DIR = Path("data/extracted")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(exist_ok=True)

def is_section_header(line: str) -> bool:
    patterns = [
        r"^\d+(\.\d+)*\s+[A-Z]",     # "1 Introduction", "2.1 Related Work"
        r"^[A-Z][A-Z\s\-]{2,}$",     # "ABSTRACT", "REFERENCES"
        r"^[A-Z][a-z]+(\s[A-Z][a-z]+)+$",  # "Related Work"
        r"^[IVX]+\.\s+[A-Z]",         # "I. Introduction"
    ]
    return any(re.match(p, line.strip()) for p in patterns)

def is_bibliographic_ref(line: str) -> bool:
    return bool(re.match(r"^\[\d+\]", line.strip()))

def contains_table_marker(line: str) -> bool:
    markers = ["table", "figure", "tabella"],
    return any(m in line.lower() for m in markers[0])

def line_heuristic_is_header(line: str, prev_line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if s.isupper() and len(s) > 4 and len(s) < 80:
        return True
    if re.match(r"^\d+(\.\d+)*\s", s) and len(s) < 100:
        return True
    if prev_line and prev_line.strip() == "" and s[0].isupper() and len(s) < 100:
        if any(kw in s.lower() for kw in ["introduction", "related", "method", "experiment", "result", "conclusion", "abstract", "reference"]):
            return True
    return False

def page_to_markdown(page: dict, page_num: int) -> str:
    text = page.get("text", "")
    lines = text.split("\n")
    md_lines = []
    prev_line = ""

    md_lines.append(f"\n--- PAGE {page_num} ---\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            md_lines.append("")
            prev_line = line
            continue

        if is_bibliographic_ref(stripped):
            md_lines.append(f"> {stripped}")
        elif line_heuristic_is_header(stripped, prev_line):
            md_lines.append(f"## {stripped}")
        else:
            md_lines.append(stripped)

        prev_line = line

    return "\n".join(md_lines)

def extract_section_name(text: str, page_num: int) -> str:
    lines = text.split("\n")
    for line in lines:
        s = line.strip()
        if re.match(r"^\d+\.?\s+(Introduction|Abstract|Related|Method|Experiment|Result|Conclusion|Background)", s, re.IGNORECASE):
            return s[:60]
    return f"page_{page_num}"

def compile_document(data: dict) -> str:
    title = data["file"].replace(".json", ".pdf")
    md = [f"# {title}\n"]
    md.append(f"*Total pages: {data['total_pages']} | Total chars: {data['total_chars']}*\n")

    current_section = "preamble"
    for p in data["pages"]:
        sec = extract_section_name(p["text"], p["page_num"])
        if sec != f"page_{p['page_num']}" and sec != current_section:
            md.append(f"\n## Section: {sec}\n")
            current_section = sec
        md.append(page_to_markdown(p, p["page_num"]))

    return "\n".join(md)

def main():
    files = sorted(EXTRACTED_DIR.glob("*.json"))
    print(f"Compilazione {len(files)} documenti estratti in Markdown...")
    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        md_content = compile_document(data)
        out_path = PROCESSED_DIR / f"{fpath.stem}.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"  {fpath.stem}.json -> {out_path.name}  ({len(md_content)} chars)")

if __name__ == "__main__":
    main()
