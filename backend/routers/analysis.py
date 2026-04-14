import os
import uuid
import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services.document_parser import extract_text_from_file, detect_document_structure
from services.gemini_service import analyze_document, apply_correction
from services.docx_generator import generate_corrected_docx
from services.excel_service import add_score_record, update_corrected_score, export_to_excel, get_all_records

router = APIRouter(prefix="/api")

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".docx", ".pdf"}

# In-memory storage for file mappings
FILE_MAPPINGS: Dict[str, Dict[str, Any]] = {}


class ApplyFixRequest(BaseModel):
    """Request model for applying fixes to document"""
    file_id: str
    issues_to_fix: List[int]
    custom_instruction: Optional[str] = None


def _log_error(message: str):
    """Log error with timestamp to stdout"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] ERROR: {message}")


@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """
    Upload and analyze a TZ document.

    Args:
        file: Document file (.docx or .pdf)

    Returns:
        Analysis results with score, issues, and suggestions
    """
    try:
        if not file.filename:
            error_msg = "Filename is required"
            _log_error(error_msg)
            raise HTTPException(status_code=422, detail=error_msg)

        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            error_msg = f"File format not supported. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
            _log_error(f"{file.filename}: {error_msg}")
            raise HTTPException(status_code=422, detail=error_msg)

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            error_msg = "Файл слишком большой. Максимальный размер: 10 МБ"
            _log_error(f"{file.filename}: File size {len(content)} bytes exceeds {MAX_FILE_SIZE} bytes")
            raise HTTPException(status_code=422, detail=error_msg)

        if len(content) == 0:
            error_msg = "File is empty"
            _log_error(f"{file.filename}: {error_msg}")
            raise HTTPException(status_code=422, detail=error_msg)

        file_id = str(uuid.uuid4())
        saved_filename = f"{file_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, saved_filename)

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content)

        document_text = extract_text_from_file(file_path, file.filename)

        if not document_text or len(document_text.strip()) < 50:
            error_msg = "Could not extract meaningful text from the document. Please verify the file is valid."
            _log_error(f"{file.filename}: {error_msg}")
            raise HTTPException(status_code=422, detail=error_msg)

        structure = detect_document_structure(document_text)

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            error_msg = "GEMINI_API_KEY environment variable not set"
            _log_error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

        try:
            analysis_result = await analyze_document(document_text, api_key)
        except ValueError as e:
            error_str = str(e)
            if "JSON" in error_str:
                _log_error(f"{file.filename}: JSON parsing error from Gemini: {error_str}")
                raise HTTPException(
                    status_code=422,
                    detail="AI не смог обработать документ. Попробуйте ещё раз или проверьте что файл содержит читаемый текст."
                )
            else:
                _log_error(f"{file.filename}: Gemini error: {error_str}")
                raise HTTPException(status_code=500, detail=error_str)

        if not isinstance(analysis_result, dict):
            error_msg = "Invalid response from analysis service"
            _log_error(f"{file.filename}: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)

        add_score_record(
            filename=file.filename,
            original_score=analysis_result.get("original_score", 0),
            language=analysis_result.get("language", "russian")
        )

        FILE_MAPPINGS[file_id] = {
            "filename": file.filename,
            "file_path": file_path,
            "saved_filename": saved_filename,
            "text": document_text,
            "analysis": analysis_result,
            "structure": structure
        }

        return {
            "file_id": file_id,
            "filename": file.filename,
            "original_score": analysis_result.get("original_score", 0),
            "score_breakdown": analysis_result.get("score_breakdown", {}),
            "language": analysis_result.get("language", "russian"),
            "issues": analysis_result.get("issues", []),
            "suggestions": analysis_result.get("suggestions", []),
            "corrected_sections": analysis_result.get("corrected_sections", {}),
            "summary": analysis_result.get("summary", ""),
            "structure_check": structure
        }

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        _log_error(f"{file.filename if file else 'unknown'}: Unexpected error: {error_msg}")
        raise HTTPException(
            status_code=422,
            detail=f"Error processing document: {error_msg}"
        )


@router.post("/apply-fix")
async def apply_fix(request: ApplyFixRequest):
    """
    Apply fixes to a analyzed document.

    Args:
        request: Contains file_id, issues_to_fix indices, and optional custom instruction

    Returns:
        Corrected document file path and new score
    """
    try:
        if request.file_id not in FILE_MAPPINGS:
            raise HTTPException(status_code=422, detail="File ID not found. Please analyze a document first.")

        file_info = FILE_MAPPINGS[request.file_id]
        original_text = file_info["text"]
        analysis_result = file_info["analysis"]
        original_issues = analysis_result.get("issues", [])

        if not request.issues_to_fix:
            raise HTTPException(status_code=422, detail="At least one issue must be selected to fix")

        for issue_idx in request.issues_to_fix:
            if not (0 <= issue_idx < len(original_issues)):
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid issue index: {issue_idx}"
                )

        selected_issues = [original_issues[idx] for idx in request.issues_to_fix]

        user_instruction = request.custom_instruction or "Please fix the selected issues in the document."

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable not set")

        correction_result = await apply_correction(
            original_text,
            selected_issues,
            user_instruction,
            api_key
        )

        if not isinstance(correction_result, dict):
            raise HTTPException(status_code=500, detail="Invalid response from correction service")

        language = analysis_result.get("language", "russian")
        corrected_sections = {
            "corrected_text": correction_result.get("corrected_text", "")
        }

        corrected_file_path = generate_corrected_docx(
            file_info["file_path"],
            corrected_sections,
            language
        )

        new_score = correction_result.get("new_score", 0)
        update_corrected_score(file_info["filename"], new_score)

        corrected_filename = Path(corrected_file_path).name

        return {
            "corrected_file_path": corrected_file_path,
            "new_score": new_score,
            "changes_made": correction_result.get("changes_made", []),
            "download_url": f"/uploads/{corrected_filename}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Error applying fixes: {str(e)}"
        )


@router.get("/download-excel")
async def download_excel():
    """
    Download Excel file with all score records.

    Returns:
        Excel file as attachment
    """
    try:
        file_path = export_to_excel()

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Excel file generation failed")

        return FileResponse(
            path=file_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=tz_scores.xlsx"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating Excel file: {str(e)}"
        )


@router.get("/records")
async def get_records():
    """
    Get all score records.

    Returns:
        List of score records
    """
    try:
        records = get_all_records()
        return {"records": records, "total": len(records)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving records: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a file from the uploads directory.

    Args:
        filename: Name of the file to download

    Returns:
        File as response

    Security: Prevents path traversal attacks
    """
    try:
        file_path = Path(UPLOAD_DIR) / filename
        resolved_path = file_path.resolve()
        uploads_dir = Path(UPLOAD_DIR).resolve()

        if not str(resolved_path).startswith(str(uploads_dir)):
            raise HTTPException(status_code=403, detail="Access denied")

        if not resolved_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        if not resolved_path.is_file():
            raise HTTPException(status_code=403, detail="Access denied")

        return FileResponse(
            path=resolved_path,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading file: {str(e)}"
        )
