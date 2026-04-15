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
   - Минимальное количество статей в журналах КОКСНВО
   - Количество патентов с указанием патентного бюро (европейское, американское, японское, британское, или казахстанское НИИС)
   - При наличии монографий — количество и издательство
   - Все показатели должны быть числовыми

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
- ЗАПРЕЩЕНО добавлять issue типа "направление не соответствует приоритету", "направление не входит в перечень НТЗ", "необходимо привязать к утверждённому НТЗ" или любую похожую формулировку

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
1. Стратегическая релевантность (strategic_relevance): 0-20 баллов — соответствие приоритетам, наличие конкретных пунктов стратегических документов в разделе 3.
2. Цель и задачи (goals_and_tasks): 0-10 баллов — чёткость цели (раздел 2.1), конкретность и измеримость задач (раздел 2.2), соответствие SMART.
3. Научная новизна (scientific_novelty): 0-15 баллов — наличие чёткого научного вклада, отличия от существующих работ.
4. Практическая применимость (practical_applicability): 0-20 баллов — конкретные публикации WoS/Scopus с квартилем, патенты, иные прямые результаты (раздел 4.1).
5. Ожидаемые результаты (expected_results): 0-15 баллов — полнота конечного результата: экономический, экологический, социальный эффект, целевые потребители (раздел 4.2).
6. Социально-экономический эффект (socioeconomic_impact): 0-10 баллов — конкретность описания выгод для экономики и общества.
7. Реализуемость (feasibility): 0-10 баллов — обоснованность бюджета (раздел 5), разбивка по годам, соответствие лимитам, логическая согласованность цель-задачи-результаты.
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

═══════════════════════════════════════════════════════
АБСОЛЮТНЫЕ ЗАПРЕТЫ — НАРУШЕНИЕ КАЖДОГО ИЗ НИХ КРИТИЧНО
═══════════════════════════════════════════════════════

ЗАПРЕТ 1 — РАЗДЕЛ 1.2 (СПЕЦИАЛИЗИРОВАННОЕ НАПРАВЛЕНИЕ):
НИКОГДА не создавай issue о том, что специализированное направление «не соответствует», «не входит в перечень НТЗ», «требует привязки к утверждённому НТЗ» или «не совпадает с приоритетом». Раздел 1.2 проверяется ИСКЛЮЧИТЕЛЬНО на факт заполненности (поле заполнено / не заполнено). Любая другая оценка раздела 1.2 — ошибка.

ЗАПРЕТ 2 — РЕКВИЗИТЫ ВНЕШНИХ ДОКУМЕНТОВ:
НИКОГДА не указывай номера постановлений, приказов, решений, дат принятия или иных реквизитов нормативных актов, которые явно не приведены в нормативном документе выше. Если в ТЗ указан номер документа, а ты считаешь его неверным — пиши только «номер документа требует проверки», но НЕ называй «правильный» номер. Ты не можешь знать актуальные реквизиты — они меняются.

ЗАПРЕТ 3 — ПРОПОРЦИЯ ПУБЛИКАЦИЙ К ФИНАНСИРОВАНИЮ:
НИКОГДА не устанавливай норму «минимум N статей на X тыс. тенге» и не требуй увеличения числа публикаций исходя из объёма финансирования. Такой зависимости в нормативных документах нет. Оценивай только наличие/отсутствие числового показателя и квартиля — не их «достаточность» относительно бюджета.

ЗАПРЕТ 4 — ЛИМИТЫ СЛОВ И СИМВОЛОВ:
НИКОГДА не требуй сократить текст до «не более N слов» или «не более N символов», если такое требование явно не указано в нормативном документе выше. Требование краткости не означает конкретного числового лимита.

ЗАПРЕТ 5 — ГОДЫ РЕАЛИЗАЦИИ:
НИКОГДА не указывай «правильные» годы реализации программы (например, «должно быть 2024–2026») если конкретные допустимые периоды явно не указаны в нормативном документе выше. Если годы выглядят несоответствующими — отметь это как «требует уточнения у организатора», не называй конкретную замену.

ЗАПРЕТ 6 — СУММЫ В ПРЕДЕЛАХ ЛИМИТА:
Если запрашиваемая сумма НЕ превышает предельный лимит по приоритетному направлению из нормативного документа — НЕ создавай issue о финансировании. Нарушением является только ПРЕВЫШЕНИЕ лимита, а не сама по себе крупная сумма.

ЗАПРЕТ 7 — ССЫЛКИ НА НЕСУЩЕСТВУЮЩИЕ ПУНКТЫ:
Ссылайся ТОЛЬКО на те разделы и пункты нормативного документа, которые буквально присутствуют в тексте выше. Если нужного пункта там нет — не ссылайся ни на что, пиши «согласно общим требованиям конкурсной документации».

ЗАПРЕТ 8 — ДОМЫСЛЫ О СОДЕРЖАНИИ:
Цитируй ТОЛЬКО дословный текст из анализируемого документа. Если информация в документе отсутствует — пиши «информация отсутствует в документе», не додумывай.

═══════════════════════════════════════════════════════

ИНСТРУКЦИИ ПО ОЦЕНКЕ:
1. Определи язык документа (русский или казахский) и отвечай на том же языке.
2. Оцени документ по всем требованиям выше.
3. Для каждого issue СТРОГО СЛЕДУЙ ЭТОМУ ПРОЦЕССУ:
   ШАГ А: Найди в НОРМАТИВНОМ ДОКУМЕНТЕ ВЫШЕ конкретный фрагмент текста, который нарушает анализируемый ТЗ.
   ШАГ Б: Если такого фрагмента нет в нормативном документе выше — issue НЕ СОЗДАЁТСЯ. Твои знания о законодательстве, конкурсной документации или иных источниках вне предоставленного документа НЕ являются основанием для создания issue.
   ШАГ В: Только если фрагмент найден — заполни поле law_quote этим дословным текстом (max 300 символов).
4. При упоминании денежных сумм ВСЕГДА используй формат "500 000 тыс. тенге" (не 500000000).
5. Рассчитай итоговый балл строго по рубрике. Сумма подбаллов ДОЛЖНА точно равняться original_score.

ФОРМАТ ВЫВОДА (ТОЛЬКО JSON, БЕЗ MARKDOWN):
{{
  "language": "russian" or "kazakh",
  "original_score": <целое число 0-100>,
  "score_breakdown": {{
    "strategic_relevance": <0-20>,
    "goals_and_tasks": <0-10>,
    "scientific_novelty": <0-15>,
    "practical_applicability": <0-20>,
    "expected_results": <0-15>,
    "socioeconomic_impact": <0-10>,
    "feasibility": <0-10>
  }},
  "issues": [
    {{
      "section": "<название раздела ТЗ>",
      "severity": "high" or "medium" or "low",
      "description": "<описание проблемы>",
      "original_text": "<дословная цитата из анализируемого ТЗ, max 200 символов>",
      "law_quote": "<ОБЯЗАТЕЛЬНО: дословная цитата из нормативного документа выше, которая подтверждает нарушение, max 300 символов. Если не можешь процитировать — не создавай этот issue>",
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


def _filter_hallucinated_issues(result: dict) -> dict:
    """
    Two-layer filter against hallucinated issues.

    Layer 1 — law_quote check:
        Remove issues with no documentary basis (empty law_quote).

    Layer 2 — known false-positive patterns:
        Hard-coded business rules that the AI consistently violates.
        Enforced in code because prompt prohibitions alone are insufficient
        when the AI fabricates supporting quotes.
    """
    # ── Layer 2 patterns ──────────────────────────────────────────────────────
    # (description_keywords, section_keywords, reason)
    # Blocked if ANY desc keyword matches AND (no sec filter OR any sec keyword matches).
    FALSE_POSITIVE_PATTERNS = [
        # Section 1.2: direction ↔ НТЗ / Appendix 2 binding — never a violation
        (
            ["нтз", "приложени", "привязать", "привязан",
             "не охваченн", "новому направлению", "утверждённ",
             "согласовать с организатором", "новое направление"],
            ["1.2", "1.1", "специализированн", "направлен"],
            "Section 1.2 direction matching is not a violation"
        ),
        # Publication count tied to funding amount (invented ratio)
        (
            ["для соответствия уровню нтз", "для соответствия уровню",
             "соответствия уровню, установленному в нтз",
             "для программы стоимость", "на сумму финансирован"],
            [],
            "Publication-to-funding ratio is not in normative docs"
        ),
        # Recommending to replace specific decree numbers
        (
            ["заменить постановлени", "замените постановлени",
             "вместо постановлени", "исправить реквизиты постановлени"],
            [],
            "Replacing decree numbers is hallucination"
        ),
        # Word/character count limit on goal text
        (
            ["не более 100 слов", "не более 150 слов", "не более 200 слов",
             "сократить до ", "лимит слов"],
            [],
            "Word count limit is not in normative docs"
        ),
    ]

    issues = result.get("issues", [])
    filtered = []
    removed_count = 0

    for issue in issues:
        desc    = issue.get("description", "").lower()
        section = issue.get("section", "").lower()
        law_q   = issue.get("law_quote", "").strip()

        # Layer 1: must have a non-trivial law_quote
        if not law_q or len(law_q) < 10:
            print(f"[FILTER-L1] No law_quote: {issue.get('section','')} — {desc[:80]}")
            removed_count += 1
            continue

        # Layer 2: known false-positive patterns
        blocked = False
        for (desc_kws, sec_kws, reason) in FALSE_POSITIVE_PATTERNS:
            desc_hit = any(kw in desc for kw in desc_kws)
            sec_hit  = (not sec_kws) or any(kw in section for kw in sec_kws)
            if desc_hit and sec_hit:
                print(f"[FILTER-L2] {reason}: {issue.get('section','')} — {desc[:80]}")
                removed_count += 1
                blocked = True
                break

        if not blocked:
            filtered.append(issue)

    if removed_count:
        print(f"[FILTER] Total removed: {removed_count} issue(s).")

    result["issues"] = filtered
    return result


async def analyze_document(document_text: str, api_key: str) -> dict:
    try:
        client = anthropic.Anthropic(api_key=api_key)
        prompt = build_analysis_prompt(document_text)
        response_text = _call_claude(client, prompt)
        response_text = _extract_json(response_text)

        try:
            result = json.loads(response_text)
            result = _fix_score(result)
            return _filter_hallucinated_issues(result)
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
    api_key: str,
    original_score: int = 0
) -> dict:
    try:
        client = anthropic.Anthropic(api_key=api_key)

        prompt = build_correction_prompt(document_text, issues, user_instruction)
        response_text = _call_claude(client, prompt)
        response_text = _extract_json(response_text)

        try:
            correction_result = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse Claude response as JSON. "
                f"Parse error: {str(e)}. "
                f"Raw response: {response_text[:500]}"
            )

        # Don't score the corrected document — just return it for download.
        correction_result["new_score"] = original_score
        return correction_result

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Error calling Anthropic API: {str(e)}")
