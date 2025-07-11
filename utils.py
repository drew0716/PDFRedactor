
import fitz  # PyMuPDF
import os

def extract_pages(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        image_path = f"/tmp/page_{i+1}.png"
        pix = page.get_pixmap(dpi=150)
        pix.save(image_path)
        pages.append({
            "number": i + 1,
            "text": text,
            "image_path": image_path
        })
    return pages

def redact_terms(pdf_path, redactions):
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        page_redactions = [r["Text"] for r in redactions if int(r["Page #"]) == i + 1]
        for term in page_redactions:
            if not term:
                continue
            areas = page.search_for(term, hit_max=16)
            for area in areas:
                page.add_redact_annot(area, fill=(0, 0, 0))
        page.apply_redactions()
    output_path = pdf_path.replace(".pdf", "_redacted.pdf")
    doc.save(output_path)
    return output_path
