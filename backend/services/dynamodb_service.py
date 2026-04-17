import os
import boto3
from datetime import datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal


def _get_table():
    db = boto3.resource(
        "dynamodb",
        region_name=os.getenv("AWS_DEFAULT_REGION", "eu-north-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    table_name = os.getenv("DYNAMODB_TABLE", "TaskAnalysis")
    return db.Table(table_name)


def _to_decimal(obj):
    """Recursively convert floats to Decimal for DynamoDB compatibility."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_decimal(i) for i in obj]
    return obj


def save_analysis(analysis_id: str, filename: str, analysis_result: dict, language: str) -> None:
    """Save analysis result to DynamoDB with analysis_id as partition key."""
    table = _get_table()
    table.put_item(Item={
        "analysis_id": analysis_id,
        "filename": filename,
        "timestamp": datetime.utcnow().isoformat(),
        "original_score": _to_decimal(analysis_result.get("original_score", 0)),
        "language": language,
        "score_breakdown": _to_decimal(analysis_result.get("score_breakdown", {})),
        "summary": analysis_result.get("summary", ""),
        "issues_count": len(analysis_result.get("issues", [])),
        "corrected_score": None,
    })


def update_corrected_score(analysis_id: str, new_score: int) -> None:
    """Update corrected_score for an existing record."""
    table = _get_table()
    table.update_item(
        Key={"analysis_id": analysis_id},
        UpdateExpression="SET corrected_score = :s",
        ExpressionAttributeValues={":s": _to_decimal(new_score)},
    )


def get_all_records() -> List[Dict[str, Any]]:
    """Return all records from DynamoDB."""
    table = _get_table()
    response = table.scan()
    return response.get("Items", [])
