from datetime import datetime
from typing import Optional, List, Dict, Any
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

SCORE_RECORDS: List[Dict[str, Any]] = []


def add_score_record(
    filename: str,
    original_score: int,
    language: str,
    corrected_score: Optional[int] = None
) -> Dict[str, Any]:
    """
    Add a new score record to the in-memory storage.

    Args:
        filename: Name of the analyzed file
        original_score: Score before correction (0-100)
        language: Language of document (russian or kazakh)
        corrected_score: Score after correction (optional)

    Returns:
        The created record dictionary
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    record = {
        "filename": filename,
        "original_score": original_score,
        "corrected_score": corrected_score,
        "language": language,
        "timestamp": timestamp
    }

    SCORE_RECORDS.append(record)
    return record


def update_corrected_score(filename: str, corrected_score: int) -> bool:
    """
    Update the corrected score for the most recent record with given filename.

    Args:
        filename: Name of the file to update
        corrected_score: New corrected score

    Returns:
        True if record was found and updated, False otherwise
    """
    for i in range(len(SCORE_RECORDS) - 1, -1, -1):
        if SCORE_RECORDS[i]["filename"] == filename:
            SCORE_RECORDS[i]["corrected_score"] = corrected_score
            return True

    return False


def export_to_excel() -> str:
    """
    Export all score records to an Excel file.

    Returns:
        Path to the created Excel file
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "TZ Scores"

    headers = ["Файл", "Язык", "Оценка до", "Оценка после", "Улучшение", "Дата анализа"]

    header_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
    header_font = Font(bold=True, color="000000")

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for row_num, record in enumerate(SCORE_RECORDS, 2):
        original_score = record.get("original_score", 0)
        corrected_score = record.get("corrected_score")

        ws.cell(row=row_num, column=1).value = record.get("filename", "")
        ws.cell(row=row_num, column=2).value = record.get("language", "")
        ws.cell(row=row_num, column=3).value = original_score

        if corrected_score is not None:
            ws.cell(row=row_num, column=4).value = corrected_score
            improvement = corrected_score - original_score
            ws.cell(row=row_num, column=5).value = f"+{improvement}" if improvement > 0 else str(improvement)
        else:
            ws.cell(row=row_num, column=4).value = "-"
            ws.cell(row=row_num, column=5).value = "-"

        ws.cell(row=row_num, column=6).value = record.get("timestamp", "")

        score_cell = ws.cell(row=row_num, column=3)
        if original_score < 50:
            score_cell.fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
            score_cell.font = Font(color="FFFFFF", bold=True)
        elif original_score < 75:
            score_cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
            score_cell.font = Font(color="000000", bold=True)
        else:
            score_cell.fill = PatternFill(start_color="00B050", end_color="00B050", fill_type="solid")
            score_cell.font = Font(color="FFFFFF", bold=True)

        for col in range(1, 7):
            ws.cell(row=row_num, column=col).alignment = Alignment(
                horizontal="center",
                vertical="center"
            )

    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 20

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"scores_export_{timestamp}.xlsx"
    output_path = f"uploads/{output_filename}"

    wb.save(output_path)
    return output_path


def get_all_records() -> List[Dict[str, Any]]:
    """
    Get all score records.

    Returns:
        List of all score record dictionaries
    """
    return SCORE_RECORDS.copy()


def clear_records() -> None:
    """Clear all records from memory."""
    global SCORE_RECORDS
    SCORE_RECORDS = []
