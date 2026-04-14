#!/usr/bin/env python3
"""
Integration test script for TZ Analyzer
Tests the full analyze flow with a sample TZ document
"""

import asyncio
import os
import json
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.gemini_service import analyze_document

# Sample bad TZ document for testing
SAMPLE_TZ = """
ТЕХНИЧЕСКОЕ ЗАДАНИЕ

Раздел 1: Общие сведения
1.1 Приоритет: Развитие информационных технологий
1.2 Направление: ИТ и искусственный интеллект

Раздел 2: Цели и задачи
2.1 Цель программы: Проведение исследований в области ИТ
2.2 Задачи:
- Провести исследования
- Разработать технологии
- Опубликовать результаты

Раздел 3: Стратегические документы
Государственная программа развития информационно-коммуникационных технологий
Национальный стратегический план

Раздел 4: Результаты
4.1 Прямые результаты:
Будут опубликованы научные статьи
Получены патенты
Разработаны новые алгоритмы

4.2 Конечный результат:
Результаты будут применены в промышленности
Улучшение качества технологий
Развитие специалистов

Раздел 5: Финансирование
Общая сумма: 5,000,000 тенге
"""

async def run_integration_test():
    """Run the integration test"""
    print("=" * 70)
    print("TZ ANALYZER - INTEGRATION TEST")
    print("=" * 70)

    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not set in environment")
        return False

    print("✓ GEMINI_API_KEY found")
    print()

    # Test document length
    print(f"Sample TZ document length: {len(SAMPLE_TZ)} characters")
    print()

    # Call analyze_document
    print("Calling gemini_service.analyze_document()...")
    try:
        result = await analyze_document(SAMPLE_TZ, api_key)
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

    # Verify result is dict
    if not isinstance(result, dict):
        print(f"❌ ERROR: Expected dict, got {type(result)}")
        return False

    print("✓ Received response from Gemini API")
    print()

    # Check required fields
    required_fields = [
        'language', 'original_score', 'score_breakdown',
        'issues', 'suggestions', 'summary'
    ]

    missing_fields = [f for f in required_fields if f not in result]
    if missing_fields:
        print(f"❌ ERROR: Missing required fields: {missing_fields}")
        return False

    print("✓ All required fields present")
    print()

    # Display score and breakdown
    score = result.get('original_score', 0)
    print(f"Original Score: {score}/100")

    breakdown = result.get('score_breakdown', {})
    print("Score Breakdown:")
    for key, value in breakdown.items():
        print(f"  - {key}: {value}")
    print()

    # Display first 3 issues
    issues = result.get('issues', [])
    print(f"Total Issues Found: {len(issues)}")
    print()

    if issues:
        print("First 3 Issues:")
        for i, issue in enumerate(issues[:3], 1):
            section = issue.get('section', 'Unknown')
            severity = issue.get('severity', 'unknown')
            description = issue.get('description', '')[:80]
            print(f"  {i}. [{severity.upper()}] {section}")
            print(f"     {description}...")
        print()

    # Display summary
    summary = result.get('summary', '')
    if summary:
        print("Summary:")
        print(f"  {summary[:150]}...")
        print()

    # Verify JSON structure
    try:
        json_str = json.dumps(result)
        print(f"✓ JSON structure valid ({len(json_str)} characters)")
    except Exception as e:
        print(f"❌ ERROR: Invalid JSON structure: {str(e)}")
        return False

    print()
    print("=" * 70)
    print("✅ INTEGRATION TEST PASSED")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = asyncio.run(run_integration_test())
    sys.exit(0 if success else 1)
