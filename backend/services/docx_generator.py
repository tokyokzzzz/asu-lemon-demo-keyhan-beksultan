from datetime import datetime
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def generate_corrected_docx(original_file_path: str, corrected_sections: dict, language: str) -> str:
    """
    Generate a corrected DOCX file from original and corrected sections.

    Args:
        original_file_path: Path to original file (DOCX or PDF)
        corrected_sections: Dictionary of section names to corrected text
        language: Document language (russian or kazakh)

    Returns:
        Path to the saved corrected DOCX file
    """
    original_filename = Path(original_file_path).name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"corrected_{timestamp}_{original_filename.rsplit('.', 1)[0]}.docx"
    output_path = f"uploads/{output_filename}"

    if original_filename.lower().endswith('.docx'):
        doc = _modify_existing_docx(original_file_path, corrected_sections)
    else:
        doc = _create_docx_from_corrected_sections(corrected_sections, language)

    doc.save(output_path)
    return output_path


def _modify_existing_docx(docx_path: str, corrected_sections: dict) -> Document:
    """Modify existing DOCX with corrected sections."""
    doc = Document(docx_path)

    section_mapping = {
        "Section 1": "общие сведения",
        "Section 2": "цели и задачи",
        "Section 3": "стратегических",
        "Section 4.1": "прямые результаты",
        "Section 4.2": "конечный результат",
        "Section 5": "предельная сумма"
    }

    for corrected_section_name, corrected_text in corrected_sections.items():
        keyword = section_mapping.get(corrected_section_name, "")
        if not keyword:
            continue

        keyword_lower = keyword.lower()
        found_index = -1

        for i, paragraph in enumerate(doc.paragraphs):
            if keyword_lower in paragraph.text.lower():
                found_index = i
                break

        if found_index >= 0 and found_index + 1 < len(doc.paragraphs):
            next_para = doc.paragraphs[found_index + 1]
            next_para.text = corrected_text

    return doc


def _create_docx_from_corrected_sections(corrected_sections: dict, language: str) -> Document:
    """Create DOCX from scratch with corrected sections."""
    doc = Document()

    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    if language == "kazakh":
        doc_language = "kk"
    else:
        doc_language = "ru"

    set_document_language(doc, doc_language)

    for section_name, section_text in corrected_sections.items():
        heading = doc.add_heading(section_name, level=2)
        heading.runs[0].font.color.rgb = RGBColor(0, 51, 102)

        paragraphs = section_text.split('\n')
        for para_text in paragraphs:
            if para_text.strip():
                p = doc.add_paragraph(para_text)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT

        doc.add_paragraph()

    return doc


def create_docx_from_text(text: str, filename: str, language: str) -> str:
    """
    Create a DOCX document from plain text.

    Args:
        text: Document text content
        filename: Original filename to derive output name
        language: Document language (russian or kazakh)

    Returns:
        Path to the saved DOCX file
    """
    doc = Document()

    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    if language == "kazakh":
        doc_language = "kk"
    else:
        doc_language = "ru"

    set_document_language(doc, doc_language)

    lines = text.split('\n')
    for line in lines:
        if line.strip():
            if any(keyword in line.lower() for keyword in [
                "раздел", "раздел", "1.", "2.", "3.", "4.", "5.",
                "бөлім", "1.", "2.", "3.", "4.", "5."
            ]):
                heading = doc.add_heading(line, level=2)
                heading.runs[0].font.color.rgb = RGBColor(0, 51, 102)
            else:
                p = doc.add_paragraph(line)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        else:
            doc.add_paragraph()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = filename.rsplit('.', 1)[0]
    output_filename = f"document_{timestamp}_{base_name}.docx"
    output_path = f"uploads/{output_filename}"

    doc.save(output_path)
    return output_path


def set_document_language(doc: Document, language_code: str) -> None:
    """
    Set the document language in metadata.

    Args:
        doc: Document object
        language_code: ISO language code (e.g., 'ru', 'kk')
    """
    try:
        core_props = doc.core_properties
        core_props.language = language_code
    except Exception:
        pass
