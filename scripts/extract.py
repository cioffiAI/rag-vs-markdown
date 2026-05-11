import pymupdf
import json
import os
from pathlib import Path
from tqdm import tqdm

RAW_DIR = Path("data/raw")
EXTRACTED_DIR = Path("data/extracted")
EXTRACTED_DIR.mkdir(exist_ok=True)

def extract_pdf(pdf_path: Path) -> dict:
    doc = pymupdf.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        pages.append({
            "page_num": i + 1,
            "text": text,
            "char_count": len(text),
        })
    doc.close()
    return {
        "file": pdf_path.name,
        "total_pages": len(pages),
        "total_chars": sum(p["char_count"] for p in pages),
        "pages": pages,
    }

def main():
    pdfs = sorted(RAW_DIR.glob("*.pdf"))
    print(f"Trovati {len(pdfs)} PDF in {RAW_DIR}")
    for pdf_path in tqdm(pdfs, desc="Estrazione PDF"):
        data = extract_pdf(pdf_path)
        out_path = EXTRACTED_DIR / f"{pdf_path.stem}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tqdm.write(f"  {pdf_path.name} -> {out_path.name}  ({data['total_pages']} pag, {data['total_chars']} chars)")

if __name__ == "__main__":
    main()
