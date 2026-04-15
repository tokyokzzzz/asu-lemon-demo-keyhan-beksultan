import json
import time
from pathlib import Path
from typing import Dict, Any, List

import anthropic

CLAUDE_MODEL = "claude-sonnet-4-6"

# Load laws.pdf content at import time
_LAWS_TEXT = ""

def _load_laws_pdf() -> str:
    """Load and extract text from laws.pdf."""
    laws_path = Path(__file__).parent.parent / "laws.pdf"
    if not laws_path.exists():
        return ""
    try:
        import pdfplumber
        with pdfplumber.open(str(laws_path)) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n\n".join(pages)
    except Exception as e:
        print(f"[WARNING] Could not load laws.pdf: {e}")
        return ""

_LAWS_TEXT = _load_laws_pdf()


RULES_TEXT = """
ОФИЦИАЛЬНЫЕ ТРЕБОВАНИЯ К ТЕХНИЧЕСКОМУ ЗАДАНИЮ (ТЗ) ДЛЯ ПРОГРАММНО-ЦЕЛЕВОГО ФИНАНСИРОВАНИЯ НАУЧНЫХ ПРОГРАММ РЕСПУБЛИКИ КАЗАХСТАН

1. ОБЯЗАТЕЛЬНЫЕ РАЗДЕЛЫ: ТЗ должно содержать все следующие разделы. Отсутствие любого раздела является грубым нарушением.

2. РАЗДЕЛ 3 - СТРАТЕГИЧЕСКИЕ ДОКУМЕНТЫ: Недопустимо просто перечислять названия документов. ОБЯЗАТЕЛЬНО указывать конкретные пункты, параграфы или разделы каждого документа. Пример правильного оформления: 'Концепция развития ИИ на 2024-2029 годы, п. 30 «Проведение научных исследований в сфере ИИ»'. ТЗ без конкретных пунктов не принимается.

3. РАЗДЕЛ 4.1 - ПРЯМЫЕ РЕЗУЛЬТАТЫ: Должны быть указаны КОНКРЕТНЫЕ КОЛИЧЕСТВЕННЫЕ ПОКАЗАТЕЛИ:
   - Минимальное количество статей в журналах WoS/Scopus с указанием квартиля (Q1/Q2/Q3) или процентиля CiteScore (не менее 50)
   - Минимальное количество статей в журналах КОКНВО
   - Количество патентов с указанием патентного бюро (европейское, американское, японское, британское, или казахстанское НИИС)
   - При наличии монографий - количество и издательство
   - Все показатели должны быть числовыми, не менее чем

4. РАЗДЕЛ 5 - ФИНАНСИРОВАНИЕ: Должна быть указана общая сумма И разбивка по годам. Превышение предельных сумм является нарушением. Оплата труда не должна превышать 70% от суммы. Сторонние организации не более 30%.

5. ЛОГИЧЕСКАЯ СОГЛАСОВАННОСТЬ: Каждая задача из раздела 2.2 должна соответствовать результату в разделе 4.1. Цель раздела 2.1 должна быть достижима через перечисленные задачи.

6. КОНЕЧНЫЙ РЕЗУЛЬТАТ 4.2: Должен содержать три обязательных подраздела: экономический эффект, экологический эффект, социальный эффект. Должны быть указаны целевые потребители результатов.

СТРУКТУРА ТЗ ДОЛЖНА СОДЕРЖАТЬ ВСЕ СЛЕДУЮЩИЕ РАЗДЕЛЫ И ПОДРАЗДЕЛЫ:

РАЗДЕЛ 1: ОБЩИЕ СВЕДЕНИЯ
1.1 Наименование приоритета научно-технического развития
1.2 Наименование специализированного направления

КРИТИЧЕСКИ ВАЖНО ДЛЯ РАЗДЕЛА 1.2:
- Таблица соответствия приоритетов и направлений в конкурсной документации является ПРИМЕРНОЙ, а не исчерпывающей
- Заявитель имеет право указать ЛЮБОЕ специализированное направление независимо от приоритета
- Несовпадение направления с таблицей из документации НЕ является нарушением и НЕ должно фигурировать в issues
- ЕДИНСТВЕННОЕ что оценивается в разделе 1.2: заполнено ли поле (да/нет)
- ЗАПРЕЩЕНО добавлять issue типа "направление не соответствует приоритету" или "должно быть направление X"

РАЗДЕЛ 2: ЦЕЛИ И ЗАДАЧИ ПРОГРАММЫ
2.1 Цель программы — одна, четко сформулированная, с конкретным результатом, активный залог.
2.2 Задачи программы — SMART-критерии, минимум 2-3, каждая с измеримым результатом.

РАЗДЕЛ 3: КАКИЕ ПУНКТЫ СТРАТЕГИЧЕСКИХ И ПРОГРАММНЫХ ДОКУМЕНТОВ РЕШАЕТ
КРИТИЧНОЕ ТРЕБОВАНИЕ: ОБЯЗАТЕЛЬНО указывать конкретные номера пунктов/подпунктов.
Правильно: "Национальный план развития РК на 2025-2029 годы, раздел III, пункт 15"
Неправильно: "Национальный стратегический план" (без номера пункта)

РАЗДЕЛ 4.1: ПРЯМЫЕ РЕЗУЛЬТАТЫ — конкретные числа публикаций (WoS/Scopus с квартилем Q1/Q2/Q3), КОКСНВО, патенты (с офисом), монографии.
РАЗДЕЛ 4.2: КОНЕЧНЫЙ РЕЗУЛЬТАТ — экономический, экологический, социальный эффект + целевые потребители.

РАЗДЕЛ 5: ПРЕДЕЛЬНАЯ СУММА — общая сумма + разбивка по годам.
ВАЖНО: Суммы записывать в формате "500 000 тыс. тенге" (не 500000000).
Оплата труда ≤ 70%, сторонние организации ≤ 30%.

РУБРИКА ОЦЕНИВАНИЯ (100 баллов):
1. Полнота разделов: 25 баллов
2. Ссылки на стратегические документы (раздел 3): 20 баллов
3. Количественные результаты (раздел 4.1): 20 баллов
4. Расчет бюджета по годам (раздел 5): 15 баллов
5. Логическая согласованность цель-задачи-результат: 10 баллов
6. Ясность языка и отсутствие расплывчатых формулировок: 10 баллов
"""


def _call_claude(client: anthropic.Anthropic, prompt: str, max_retries: int = 5) -> str:
    """Call Anthropic Claude API with retry on rate limit errors."""
    delay = 15
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            return response.content[0].text
        except anthropic.RateLimitError:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay)
            delay *= 2
        except anthropic.APIError as e:
            if "529" in str(e) or "overloaded" in str(e).lower():
                if attempt == max_retries - 1:
                    raise
                time.sleep(delay)
                delay *= 2
            else:
                raise


def _extract_json(text: str) -> str:
    """Extract JSON object from response, handling markdown fences and stray text."""
    text = text.strip()

    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    if text.startswith("```"):
        lines = text.split("\n")
        start = 1
        end = len(lines)
        for i in range(len(lines) - 1, 0, -1):
            if lines[i].strip() == "```":
                end = i
                break
        text = "\n".join(lines[start:end]).strip()

    # If still not starting with {, find the first { and last }
    start_idx = text.find('{')
    end_idx   = text.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        text = text[start_idx:end_idx + 1]

    return text


def build_analysis_prompt(document_text: str) -> str:
    laws_section = ""
    if _LAWS_TEXT:
        laws_section = f"""
ОФИЦИАЛЬНЫЙ НОРМАТИВНЫЙ ДОКУМЕНТ (ИСТОЧНИК ИСТИНЫ):
Все оценки и рекомендации ОБЯЗАТЕЛЬНО должны ссылаться на конкретные пункты этого документа.
---
{_LAWS_TEXT}
---
"""

    prompt = f"""Ты — эксперт по оценке технических заданий (ТЗ) для научных программ Республики Казахстан.
{laws_section}
ПРАВИЛА И КРИТЕРИИ ОЦЕНКИ:
{RULES_TEXT}

ДОКУМЕНТ ДЛЯ АНАЛИЗА:
{document_text}

СТРОГИЕ ПРАВИЛА ПРОТИВ ГАЛЛЮЦИНАЦИЙ:
- НИКОГДА не выдумывай номера пунктов, статей или параграфов нормативных документов
- НИКОГДА не изобретай суммы финансирования, квартили журналов или названия патентных бюро
- Если информация отсутствует в анализируемом документе — прямо укажи "информация отсутствует"
- Ссылайся ТОЛЬКО на те пункты нормативного документа, которые реально присутствуют выше
- Цитируй ТОЛЬКО текст, который есть в документе — без домыслов и дополнений
- НИКОГДА не создавай issue о "несоответствии специализированного направления приоритету" — это не является нарушением
- Таблица приоритет→направление в laws.pdf носит информационный характер, НЕ является ограничительным перечнем
- Раздел 1.2 проверяется ТОЛЬКО на заполненность, не на соответствие какому-либо списку

ИНСТРУКЦИИ ПО ОЦЕНКЕ:
1. Определи язык документа (русский или казахский) и отвечай на том же языке.
2. Оцени документ по всем требованиям выше.
3. Для каждого нарушения укажи:
   - Раздел
   - Серьезность (high/medium/low)
   - Описание проблемы со ссылкой на конкретный пункт нормативного документа (только реально существующие пункты)
   - Точную цитату из документа (max 200 символов) — только дословный текст из документа
   - Конкретное исправление на основе нормативного документа
4. При упоминании денежных сумм ВСЕГДА используй формат "500 000 тыс. тенге" (не 500000000).
5. Рассчитай итоговый балл строго по рубрике. Сумма подбаллов ДОЛЖНА точно равняться original_score.

ФОРМАТ ВЫВОДА (ТОЛЬКО JSON, БЕЗ MARKDOWN):
{{
  "language": "russian" or "kazakh",
  "original_score": <целое число 0-100>,
  "score_breakdown": {{
    "section_completeness": <0-25>,
    "strategic_references": <0-20>,
    "quantitative_results": <0-20>,
    "budget_breakdown": <0-15>,
    "logical_consistency": <0-10>,
    "language_clarity": <0-10>
  }},
  "issues": [
    {{
      "section": "<название раздела>",
      "severity": "high" or "medium" or "low",
      "description": "<описание проблемы со ссылкой на нормативный документ>",
      "original_text": "<цитата из документа, max 200 символов>",
      "suggested_fix": "<конкретное исправление>"
    }}
  ],
  "suggestions": ["<рекомендация 1>", "<рекомендация 2>"],
  "corrected_sections": {{
    "<название_раздела>": "<полный исправленный текст раздела>"
  }},
  "summary": "<общая оценка в 2-3 предложениях>"
}}

ВАЖНО: Только JSON, без markdown, без пояснений. Сумма score_breakdown = original_score.
"""
    return prompt


def build_correction_prompt(document_text: str, issues: list, user_instruction: str) -> str:
    laws_section = ""
    if _LAWS_TEXT:
        laws_section = f"""
ОФИЦИАЛЬНЫЙ НОРМАТИВНЫЙ ДОКУМЕНТ (ИСТОЧНИК ИСТИНЫ):
---
{_LAWS_TEXT}
---
"""

    issues_text = "\n".join([
        f"- Раздел: {issue.get('section', '')}, Серьезность: {issue.get('severity', '')}, Проблема: {issue.get('description', '')}"
        for issue in issues
    ])

    prompt = f"""Ты — эксперт-редактор технических заданий (ТЗ) для научных программ Республики Казахстан.
{laws_section}
ИСХОДНЫЙ ДОКУМЕНТ:
{document_text}

ВЫЯВЛЕННЫЕ ПРОБЛЕМЫ:
{issues_text}

ИНСТРУКЦИЯ ПОЛЬЗОВАТЕЛЯ:
{user_instruction}

СТРОГИЕ ПРАВИЛА ПРОТИВ ГАЛЛЮЦИНАЦИЙ:
- НИКОГДА не выдумывай номера пунктов стратегических документов — используй только те, что есть в нормативном документе выше
- НИКОГДА не изобретай суммы финансирования — исправляй только формат записи существующих сумм
- НИКОГДА не добавляй несуществующие результаты или патенты — только улучшай формулировки имеющихся
- Если в оригинале нет данных по какому-то разделу — укажи "[требуется заполнить]", не выдумывай
- Опирайся исключительно на нормативный документ выше, не на общие знания

ЗАДАЧА:
1. Исправь все указанные проблемы согласно нормативному документу.
2. Структурируй исправленный ТЗ по разделам и подразделам.
3. При указании денежных сумм ВСЕГДА используй формат "500 000 тыс. тенге" (не 500000000).
4. Все ссылки на стратегические документы должны содержать конкретные номера пунктов (только реально существующие).
5. Все показатели результатов должны быть числовыми с квартилями/перцентилями.
6. После исправления пересчитай балл (0-100).

ФОРМАТ corrected_text (СТРОГО СОБЛЮДАЙ):
- Используй заголовки разделов: "РАЗДЕЛ 1: ОБЩИЕ СВЕДЕНИЯ", "РАЗДЕЛ 2: ЦЕЛИ И ЗАДАЧИ" и т.д.
- Используй заголовки подразделов: "1.1 Наименование", "2.1 Цель программы" и т.д.
- НИКОГДА не используй символ | (вертикальная черта) в тексте
- НИКОГДА не используй markdown таблицы или форматирование с |
- Только обычный текст с заголовками разделов

ФОРМАТ ВЫВОДА (ТОЛЬКО JSON, БЕЗ MARKDOWN):
{{
  "corrected_text": "<полный исправленный текст без символов | >",
  "new_score": <целое число 0-100>,
  "changes_made": ["<описание изменения 1>", "<описание изменения 2>"]
}}

ВАЖНО: Только JSON, без markdown, без пояснений. В corrected_text запрещён символ |.
"""
    return prompt


def _fix_score(result: dict) -> dict:
    """Recalculate original_score from breakdown to prevent math errors."""
    breakdown = result.get("score_breakdown", {})
    if breakdown:
        real_sum = sum(breakdown.values())
        result["original_score"] = real_sum
    return result


async def analyze_document(document_text: str, api_key: str) -> dict:
    try:
        client = anthropic.Anthropic(api_key=api_key)
        prompt = build_analysis_prompt(document_text)
        response_text = _call_claude(client, prompt)
        response_text = _extract_json(response_text)

        try:
            result = json.loads(response_text)
            return _fix_score(result)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parse failed: {e}")
            print(f"[ERROR] Raw response (first 1000 chars):\n{response_text[:1000]}")
            raise ValueError(
                f"Failed to parse Claude response as JSON. "
                f"Parse error: {str(e)}. "
                f"Raw response: {response_text[:500]}"
            )

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Error calling Anthropic API: {str(e)}")


async def apply_correction(
    document_text: str,
    issues: list,
    user_instruction: str,
    api_key: str
) -> dict:
    try:
        client = anthropic.Anthropic(api_key=api_key)
        prompt = build_correction_prompt(document_text, issues, user_instruction)
        response_text = _call_claude(client, prompt)
        response_text = _extract_json(response_text)

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse Claude response as JSON. "
                f"Parse error: {str(e)}. "
                f"Raw response: {response_text[:500]}"
            )

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Error calling Anthropic API: {str(e)}")
