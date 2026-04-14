import json
import google.generativeai as genai
from typing import Dict, Any, List

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

4. РАЗДЕЛ 5 - ФИНАНСИРОВАНИЕ: Должна быть указана общая сумма И разбивка по годам. Превышение предельных сумм является нарушением. Оплата труда не должна превышать 70% от суммы.

5. ЛОГИЧЕСКАЯ СОГЛАСОВАННОСТЬ: Каждая задача из раздела 2.2 должна соответствовать результату в разделе 4.1. Цель раздела 2.1 должна быть достижима через перечисленные задачи.

6. КОНЕЧНЫЙ РЕЗУЛЬТАТ 4.2: Должен содержать три обязательных подраздела: экономический эффект, экологический эффект, социальный эффект. Должны быть указаны целевые потребители результатов.

СТРУКТУРА ТЗ ДОЛЖНА СОДЕРЖАТЬ ВСЕ СЛЕДУЮЩИЕ РАЗДЕЛЫ И ПОДРАЗДЕЛЫ:

РАЗДЕЛ 1: ОБЩИЕ СВЕДЕНИЯ
1.1 Наименование приоритета научно-технического развития
1.2 Наименование специализированного направления

Требование: Оба подраздела должны быть заполнены четко и однозначно. Приоритет должен соответствовать государственной политике в области науки и технологий Казахстана.

РАЗДЕЛ 2: ЦЕЛИ И ЗАДАЧИ ПРОГРАММЫ
2.1 Цель программы
Требование: Цель должна быть одна, четко сформулирована, описывать конечный результат, который будет достигнут. Использование активного залога обязательно. Цель должна быть достижимой в установленные сроки.

2.2 Задачи программы
Требование: Задачи должны быть специфичными и измеримыми (SMART-критерии). Каждая задача должна:
- содержать конкретный результат (не просто "проведение исследований")
- быть привязана к временному периоду
- содержать указание на измеримый результат
- напрямую способствовать достижению цели (2.1)
Минимум 2-3 задачи обязательны.

РАЗДЕЛ 3: КАКИЕ ПУНКТЫ СТРАТЕГИЧЕСКИХ И ПРОГРАММНЫХ ДОКУМЕНТОВ РЕШАЕТ
Требование (КРИТИЧНОЕ): Этот раздел ДОЛЖЕН содержать:
- Названия конкретных государственных стратегических документов (Государственная программа развития образования, Национальный план развития РК и т.д.)
- КОНКРЕТНЫЕ НОМЕРА ПУНКТОВ, ПОДПУНКТОВ ИЛИ ПАРАГРАФОВ этих документов
- Прямое цитирование текста соответствующего пункта

ПРИМЕРЫ ПРАВИЛЬНЫХ ССЫЛОК:
✓ "Государственная программа развития образования Республики Казахстан на 2016-2019 годы, пункт 3.2.4"
✓ "Национальный план развития РК на 2025-2029 годы, раздел III, подраздел 'Инновационная экономика', пункт 15"

ПРИМЕРЫ НЕПРАВИЛЬНЫХ ССЫЛОК (НЕДОПУСТИМО):
✗ "Государственная программа развития образования"
✗ "Национальный стратегический план"
✗ "Пятилетний план развития"
БЕЗ УКАЗАНИЯ КОНКРЕТНЫХ НОМЕРОВ ПУНКТОВ/ПОДПУНКТОВ

Отсутствие конкретных номеров пунктов - это КРИТИЧЕСКАЯ ОШИБКА!

РАЗДЕЛ 4: РЕЗУЛЬТАТЫ ПРОГРАММЫ

4.1 Прямые результаты
Требование: Этот раздел должен содержать КОНКРЕТНЫЕ, ИЗМЕРИМЫЕ показатели результатов:

Публикационная активность (если применимо):
- МИНИМАЛЬНОЕ количество публикаций в журналах, индексированных в Web of Science (WoS) с указанием квартиля (Q1, Q2, Q3, Q4) или перцентиля
- МИНИМАЛЬНОЕ количество публикаций в журналах, индексированных в Scopus с указанием квартиля или перцентиля
- МИНИМАЛЬНОЕ количество публикаций в журналах списка KOKSNVO (Комитет по контролю в сфере образования и науки)
- Примеры неправильных формулировок:
  ✗ "Будут подготовлены научные статьи" (не указано количество)
  ✗ "Публикации в рецензируемых журналах" (не указана база индексирования)
  ✗ "Статьи в научных журналах" (не указаны квартили)

Примеры правильных формулировок:
✓ "Минимум 3 статьи в журналах WoS с Q1 или Q2 квартилем"
✓ "Минимум 2 статьи в журналах Scopus первого и второго квартилей"
✓ "Минимум 5 статей в журналах KOKSNVO"

Интеллектуальная собственность:
- КОЛИЧЕСТВО патентов и КОНКРЕТНЫЕ патентные офисы (Евразийский патентный офис EPO, Национальный патентный центр Казахстана, USPTO, WIPO и т.д.)
- Примеры неправильно:
  ✗ "Получение патентов" (не указано количество и офис)
  ✗ "Защита интеллектуальной собственности" (неконкретно)
- Примеры правильно:
  ✓ "Минимум 2 патента в Национальном патентном центре Республики Казахстан"
  ✓ "Минимум 1 евразийский патент в Евразийском патентном офисе"

Другие результаты:
- Количество монографий (если требуется)
- Количественные KPI индикаторы с конкретными числами

4.2 Конечный результат
Требование: Должна быть описана практическое применение результатов через указание:

Экономический эффект:
- Увеличение производительности
- Снижение затрат
- Рост дохода
- Привлечение инвестиций
- Или другие экономические показатели
- Примеры: "Снижение себестоимости производства на 15%", "Увеличение выпуска продукции на 20%"

Экологический эффект (если применимо):
- Снижение выбросов
- Улучшение качества воды, воздуха
- Экономия ресурсов
- Примеры: "Снижение выбросов CO2 на 30%", "Сокращение отходов на 25%"

Социальный эффект:
- Создание рабочих мест
- Улучшение качества жизни
- Здоровье и безопасность
- Образование и развитие
- Примеры: "Создание 50 новых рабочих мест", "Подготовка 100 специалистов"

Целевые потребители:
- Указание конкретных категорий пользователей или организаций, которые будут использовать результаты
- Примеры: "Министерство энергетики РК", "Производители сельскохозяйственной продукции", "Строительные компании"

РАЗДЕЛ 5: ПРЕДЕЛЬНАЯ СУММА ПРОГРАММЫ
Требование: Раздел должен содержать:
- ОБЩУЮ СУММУ финансирования на весь период программы в тенге
- ПОДРОБНЫЙ РАСЧЕТ ПО ГОДАМ (обязательно показать распределение по годам)
- Соответствие установленным лимитам (для программ в сфере энергетики и ИТ максимум 500,000 тенге в год)
- Обоснование распределения средств

Примеры правильного формата:
✓ "Предельная сумма программы: 1,500,000 тенге
   2024 год: 400,000 тенге
   2025 год: 550,000 тенге
   2026 год: 550,000 тенге"

Примеры неправильного:
✗ "Бюджет программы: 1,500,000 тенге" (нет разбивки по годам)
✗ "Финансирование: 500,000 тенге в год" (не ясно сколько лет, нет явной разбивки)

РУБРИКА ОЦЕНИВАНИЯ (ТАБЛИЦА БАЛЛОВ):

1. ПОЛНОТА РАЗДЕЛОВ (25 баллов):
   - Все 6 разделов присутствуют и содержат существенную информацию: +25 баллов
   - Отсутствует или пусто одно или более требуемое поле: -5 баллов за каждое отсутствующее/пустое поле
   - Максимум может быть снижено до 0 баллов

2. ССЫЛКИ НА СТРАТЕГИЧЕСКИЕ ДОКУМЕНТЫ (20 баллов):
   - Раздел 3 содержит конкретные номера пунктов/подпунктов стратегических документов: +20 баллов
   - Содержит названия документов, но без номеров пунктов или номера неполные: +5 баллов
   - Отсутствуют ссылки на стратегические документы: 0 баллов

3. КОЛИЧЕСТВЕННЫЕ ИЗМЕРИМЫЕ РЕЗУЛЬТАТЫ (20 баллов):
   - Раздел 4.1 содержит конкретные числовые показатели для всех видов результатов (публикации, патенты, монографии): +20 баллов
   - Содержит числовые показатели, но не для всех видов результатов: +10 баллов
   - Содержит только описательные формулировки без чисел: +5 баллов
   - Отсутствуют результаты или они полностью неконкретны: 0 баллов

4. РАСЧЕТ БЮДЖЕТА ПО ГОДАМ (15 баллов):
   - Раздел 5 содержит четкую разбивку бюджета по годам с явным распределением: +15 баллов
   - Содержит общую сумму с частичной разбивкой по годам: +8 баллов
   - Содержит общую сумму без разбивки по годам: +3 баллов
   - Отсутствует информация о бюджете: 0 баллов

5. ЛОГИЧЕСКАЯ СОГЛАСОВАННОСТЬ ЦЕЛЬ-ЗАДАЧИ-РЕЗУЛЬТАТ (10 баллов):
   - Задачи (2.2) напрямую приводят к достижению цели (2.1), результаты (4.1) соответствуют задачам, конечный результат (4.2) демонстрирует практическое применение: +10 баллов
   - Связь есть, но не полная: +5 баллов
   - Связь между разделами слабая или отсутствует: 0 баллов

6. ЯСНОСТЬ ЯЗЫКА И ОТСУТСТВИЕ РАСПЛЫВЧАТЫХ ФОРМУЛИРОВОК (10 баллов):
   - Четкий, конкретный язык, отсутствуют неопределенные выражения типа "и т.д.", "в том числе", "возможно": +10 баллов
   - Язык в целом понятен, но есть незначительные неточности: +7 баллов
   - Язык неясен, много расплывчатых формулировок: +3 баллов
   - Документ невозможно понять из-за неясности: 0 баллов

ТИПИЧНЫЕ КРИТИЧЕСКИЕ ОШИБКИ И ДЕНЬГИ БАЛЛОВ:

1. Раздел 3: Перечисление названий документов БЕЗ конкретных номеров пунктов
   → ВЫСОКАЯ серьезность
   → Снижение на значительное количество баллов
   → Описание: "Раздел 3 содержит только названия стратегических документов без ссылки на конкретные пункты или подпункты"

2. Раздел 4.1: Формулировки "будут опубликованы статьи" БЕЗ указания минимального количества
   → ВЫСОКАЯ серьезность
   → Описание: "Раздел 4.1 упоминает будущие публикации без указания конкретного количества"

3. Раздел 4.1: Упоминание публикаций БЕЗ указания квартиля WoS/Scopus или перцентиля
   → ВЫСОКАЯ серьезность
   → Описание: "Раздел 4.1 указывает на публикации в WoS/Scopus, но без уточнения квартиля или перцентиля"

4. Раздел 4.1: Упоминание патентов БЕЗ указания количества и патентного офиса
   → ВЫСОКАЯ серьезность
   → Описание: "Раздел 4.1 говорит о защите интеллектуальной собственности, но не указывает количество патентов и офис"

5. Раздел 2.2: Расплывчатые задачи типа "проведение исследований" БЕЗ измеримого результата
   → СРЕДНЯЯ серьезность
   → Описание: "Раздел 2.2 содержит неконкретные задачи, не отвечающие критериям SMART"

6. Раздел 4.2: Отсутствие одного из трех эффектов (экономический, экологический, социальный)
   → СРЕДНЯЯ серьезность
   → Описание: "Раздел 4.2 не содержит описания экономического/экологического/социального эффекта"

7. Раздел 5: Наличие общей суммы БЕЗ разбивки по годам
   → ВЫСОКАЯ серьезность
   → Описание: "Раздел 5 указывает сумму, но отсутствует разбивка по годам программы"

8. Раздел 5: Бюджет НЕ соответствует лимиту 500,000 тенге в год для программ энергетики/ИТ
   → СРЕДНЯЯ серьезность
   → Описание: "Раздел 5 показывает бюджет, превышающий лимит 500,000 тенге в год"

9. Раздел 2.1: Цель сформулирована пассивным залогом БЕЗ указания конкретного результата
   → НИЗКАЯ серьезность
   → Описание: "Раздел 2.1 использует пассивный залог, рекомендуется активное формулирование"

ИТОГОВАЯ ШКАЛА:
- 85-100 баллов: Отличный ТЗ, полностью соответствует требованиям
- 70-84 баллов: Хороший ТЗ с незначительными замечаниями
- 50-69 баллов: Удовлетворительный ТЗ, требует доработки
- 30-49 баллов: Неудовлетворительный ТЗ, значительные недостатки
- 0-29 баллов: Критический ТЗ, не соответствует требованиям
"""


def build_analysis_prompt(document_text: str) -> str:
    """
    Build the analysis prompt for Gemini to evaluate TZ document.

    Args:
        document_text: The text content of the TZ document to analyze

    Returns:
        The complete prompt to send to Gemini
    """
    prompt = f"""
You are an expert evaluator of Kazakhstani scientific technical assignment documents (ТЗ - Technical Specification).

REFERENCE RULES AND SCORING CRITERIA:
{RULES_TEXT}

DOCUMENT TO ANALYZE:
{document_text}

EVALUATION INSTRUCTIONS:
1. First, detect the language of the document (Russian or Kazakh) and respond in the SAME language.
2. Evaluate this document against ALL the requirements and rules provided above.
3. Apply the exact scoring rubric provided in the rules.
4. For each deficiency found, identify:
   - Which section it affects
   - Severity level (high, medium, or low)
   - The specific problem
   - The exact problematic text from the document (max 200 characters)
   - A concrete suggestion for improvement

5. Calculate the total score by applying the rubric exactly:
   - Section completeness (all 6 sections present): 25 points max
   - Strategic documents with specific paragraph numbers (Section 3): 20 points max
   - Quantitative measurable results with specific numbers (Section 4.1): 20 points max
   - Budget breakdown by year (Section 5): 15 points max
   - Goal-task-result logical consistency: 10 points max
   - Language clarity and absence of vague formulations: 10 points max
   Total: 100 points

CRITICAL ISSUES TO CHECK:
- Section 3 must cite specific paragraph/point numbers, not just document names
- Section 4.1 must specify exact numbers for publications, their quartile/percentile, and patent offices
- Section 4.2 must address economic, ecological, and social effects separately
- Section 5 must show breakdown by year, not just total
- All sections must be present and substantive (not empty)
- Tasks in Section 2.2 must be measurable and specific (SMART criteria)

OUTPUT FORMAT (JSON ONLY, NO MARKDOWN, NO PREAMBLE):
Return ONLY valid JSON with this exact structure:
{{
  "language": "russian" or "kazakh",
  "original_score": <integer 0-100>,
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
      "section": "<section name>",
      "severity": "high" or "medium" or "low",
      "description": "<detailed description of what is wrong>",
      "original_text": "<exact quote from document, max 200 chars>",
      "suggested_fix": "<concrete replacement or addition>"
    }}
  ],
  "suggestions": [
    "<actionable suggestion 1>",
    "<actionable suggestion 2>"
  ],
  "corrected_sections": {{
    "<section_name>": "<full corrected text for that section>"
  }},
  "summary": "<2-3 sentence overall assessment>"
}}

IMPORTANT:
- Return ONLY JSON, no markdown code fences, no preamble, no explanation
- All text must be in the SAME language as the input document
- Score breakdown numbers must sum to original_score
- Be strict with scoring - deduct points for missing required elements
- Detect vague language and formulations without specific numbers
"""
    return prompt


def build_correction_prompt(document_text: str, issues: list, user_instruction: str) -> str:
    """
    Build prompt for Gemini to apply corrections to TZ document.

    Args:
        document_text: The original TZ document text
        issues: List of issues found in the analysis
        user_instruction: User's instruction for how to fix the issues

    Returns:
        The correction prompt to send to Gemini
    """
    issues_text = "\n".join([
        f"- Section: {issue['section']}, Severity: {issue['severity']}, Issue: {issue['description']}"
        for issue in issues
    ])

    prompt = f"""
You are an expert editor of Kazakhstani scientific technical assignment documents (ТЗ).

ORIGINAL DOCUMENT:
{document_text}

ISSUES FOUND:
{issues_text}

USER INSTRUCTION FOR CORRECTION:
{user_instruction}

TASK:
1. Apply the corrections requested by the user.
2. Address all the issues listed above.
3. Ensure the corrected document follows all official requirements for ТЗ.
4. After correction, re-evaluate the document using the same scoring criteria (0-100 scale).
5. List all changes made.

OUTPUT FORMAT (JSON ONLY, NO MARKDOWN):
Return ONLY valid JSON with this exact structure:
{{
  "corrected_text": "<full corrected document text>",
  "new_score": <integer 0-100>,
  "changes_made": [
    "<description of change 1>",
    "<description of change 2>"
  ]
}}

IMPORTANT: Return ONLY JSON, no markdown fences, no explanation text.
"""
    return prompt


async def analyze_document(document_text: str, api_key: str) -> dict:
    """
    Analyze TZ document using Gemini API.

    Args:
        document_text: The text content of the TZ document
        api_key: Google Generative AI API key

    Returns:
        Dictionary with analysis results including issues, score, and suggestions

    Raises:
        ValueError: If JSON parsing fails or API returns invalid response
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = build_analysis_prompt(document_text)

        generation_config = {
            "temperature": 0.1,
            "max_output_tokens": 65536,
            "top_p": 0.95,
            "top_k": 40,
            "response_mime_type": "application/json"
        }

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        response_text = response.text.strip()

        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse Gemini response as JSON. "
                f"Parse error: {str(e)}. "
                f"Raw response: {response_text[:500]}"
            )

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Error calling Gemini API: {str(e)}")


async def apply_correction(
    document_text: str,
    issues: list,
    user_instruction: str,
    api_key: str
) -> dict:
    """
    Apply corrections to TZ document using Gemini API.

    Args:
        document_text: The original TZ document text
        issues: List of issues found in analysis
        user_instruction: User's instruction for corrections
        api_key: Google Generative AI API key

    Returns:
        Dictionary with corrected_text, new_score, and changes_made

    Raises:
        ValueError: If JSON parsing fails or API returns invalid response
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = build_correction_prompt(document_text, issues, user_instruction)

        generation_config = {
            "temperature": 0.1,
            "max_output_tokens": 65536,
            "top_p": 0.95,
            "top_k": 40,
            "response_mime_type": "application/json"
        }

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        response_text = response.text.strip()

        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse Gemini response as JSON. "
                f"Parse error: {str(e)}. "
                f"Raw response: {response_text[:500]}"
            )

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Error calling Gemini API: {str(e)}")
