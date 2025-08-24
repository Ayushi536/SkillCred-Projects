"""
exports/exporter.py
Export script dict to PDF bytes using fpdf2 with DejaVu Sans (Unicode).
"""
import os
import urllib.request
from fpdf import FPDF
from typing import Dict, Any

FONT_FILENAME = "DejaVuSans.ttf"
FONT_DOWNLOAD_URL = (
    "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
)

def _ensure_font(font_path: str) -> None:
    """Ensure the DejaVu TTF exists. Try to download if missing."""
    if os.path.exists(font_path):
        return
    try:
        os.makedirs(os.path.dirname(font_path), exist_ok=True)
        urllib.request.urlretrieve(FONT_DOWNLOAD_URL, font_path)
        if not os.path.exists(font_path) or os.path.getsize(font_path) == 0:
            raise IOError("Downloaded file is empty or missing.")
    except Exception as e:
        raise FileNotFoundError(
            f"Required font file not found at: {font_path}\n"
            f"Automatic download failed: {e}\n\n"
            "Please download DejaVuSans.ttf manually from:\n"
            "https://dejavu-fonts.github.io/Download.html\n"
            f"or from: {FONT_DOWNLOAD_URL}\n"
            "and place it in the same folder as this file (exports/)."
        ) from e

def script_to_pdf_bytes(script: Dict[str, Any]) -> bytes:
    """Convert script dict to PDF bytes using DejaVuSans for all styles."""
    base_dir = os.path.dirname(__file__) or "."
    font_path = os.path.join(base_dir, FONT_FILENAME)
    _ensure_font(font_path)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    family = "DejaVuSans"
    pdf.add_font(family, "", font_path, uni=True)
    pdf.add_font(family, "B", font_path, uni=True)
    pdf.add_font(family, "I", font_path, uni=True)
    pdf.add_font(family, "BI", font_path, uni=True)

    pdf.add_page()

    # Title
    pdf.set_font(family, "B", 14)
    title = script.get("title", "Explainer Script") or "Explainer Script"
    pdf.cell(0, 10, str(title), ln=True)
    pdf.ln(4)

    # Total time
    pdf.set_font(family, "", 11)
    total = script.get("total_seconds", "n/a")
    pdf.cell(0, 8, f"Estimated length: {total} seconds", ln=True)
    pdf.ln(6)

    for s in script.get("scenes", []):
        scene_num = s.get("scene", "")
        heading_text = s.get("heading", "")
        est = s.get("est_seconds", "")
        heading = f"Scene {scene_num}: {heading_text} ({est}s)".strip()

        pdf.set_font(family, "B", 12)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 8, str(heading))

        pdf.set_font(family, "I", 11)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 7, "Narration:")

        pdf.set_font(family, "", 10)
        narration = s.get("narration", "") or ""
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 7, str(narration))

        pdf.ln(2)

        pdf.set_font(family, "I", 11)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 7, "Visual Suggestions:")

        pdf.set_font(family, "", 10)
        for v in s.get("visuals", []):
            text = f"• {v}"
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 7, str(text))
        pdf.ln(6)

    # Ensure return type is bytes
    raw = pdf.output(dest="S")
    if isinstance(raw, bytearray):
        return bytes(raw)
    if isinstance(raw, str):
        return raw.encode("latin-1", errors="replace")
    return raw  # already bytes
