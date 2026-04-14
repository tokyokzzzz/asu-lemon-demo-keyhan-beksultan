from typing import List, Optional, Dict
from pydantic import BaseModel
from enum import Enum


class SeverityEnum(str, Enum):
    """Severity levels for issues"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Issue(BaseModel):
    """Issue found during analysis"""
    section: str
    severity: SeverityEnum
    description: str
    original_text: str
    suggested_fix: str


class AnalysisResult(BaseModel):
    """Result of document analysis"""
    filename: str
    original_score: int
    language: str
    issues: List[Issue]
    suggestions: List[str]
    corrected_sections: Dict[str, str]
    summary: str


class VersionEntry(BaseModel):
    """Version history entry"""
    version_number: int
    score: int
    timestamp: str
    changes_made: List[str]


class ScoreRecord(BaseModel):
    """Score record for a document"""
    filename: str
    original_score: int
    corrected_score: Optional[int] = None
    language: str
    timestamp: str
