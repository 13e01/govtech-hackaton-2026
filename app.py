import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


AI_SYSTEM_PROMPT = (
    "Ты — GovTech AI Assistant проекта. Тебе дают текст обращения гражданина и инструкцию, как на него ответить. "
    "Отвечай коротко, чётко и аргументированно. "
    "Формат ответа: уровень риска, краткое объяснение, действия, ответственная служба. "
    "Каждая рекомендация должна содержать одно фактное обоснование в поддержку уровня риска и одного или двух предложенных действий. "
    "Не добавляй пояснений, не объясняй процесс и не упоминай язык запроса. "
    "Если текст обращения содержит приветствие, игнорируй его. "
    "Отвечай на языке самого обращения, если это возможно. "
    "Если обращение не относится к сервису — ответь: "
    "\"Я могу помочь только по вопросам данного сервиса\"."
)


def send_chat_response(messages: list[dict]) -> str:
    """Отправляет сообщения в DeepSeek и возвращает окончательный ответ ассистента."""
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("Не задан DEEPSEEK_API_KEY в файле .env.")

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model='deepseek-v4-flash',
        messages=messages,
        temperature=0.0,
    )

    choice = response.choices[0] if response.choices else None
    if not choice:
        raise RuntimeError(f"Сервис вернул пустой ответ. full_response={response}")

    message = getattr(choice, 'message', None)
    content = (getattr(message, 'content', None) or "").strip() if message else ""
    reasoning = (getattr(message, 'reasoning_content', None) or "").strip() if message else ""

    if content:
        return content

    if reasoning:
        followup_prompt = (
            "Используй предыдущие рассуждения, чтобы сформировать финальный ответ по обращению. "
            "Ответ должен быть в формате: уровень риска, краткое объяснение, действия, ответственная служба. "
            "Не добавляй пояснений и не повторяй служебные инструкции."
        )
        followup_messages = [
            {"role": "system", "content": AI_SYSTEM_PROMPT},
            {"role": "assistant", "content": reasoning},
            {"role": "user", "content": followup_prompt},
        ]
        response = client.chat.completions.create(
            model='deepseek-v4-flash',
            messages=followup_messages,
            temperature=0.0,
        )
        choice = response.choices[0] if response.choices else None
        message = getattr(choice, 'message', None)
        content = (getattr(message, 'content', None) or "").strip() if message else ""
        if content:
            return content

    raise RuntimeError(f"Сервис вернул пустой ответ. full_response={response}")


def get_operator_recommendation(text: str) -> str:
    """Сформировать краткую рекомендацию оператору по обращению."""
    prompt = (
        "Текст обращения: " + text.strip() + "\n"
        "Ты — помощник оператору ситуационного центра. Составь краткую, чёткую и аргументированную рекомендацию по дальнейшим действиям: "
        "уровень риска, краткое объяснение с обоснованием, конкретные шаги, ответственная служба. "
        "Отвечай только по сути, без объяснений процесса, без дополнительных рассуждений."
    )
    return send_chat_response(
        [
            {"role": "system", "content": AI_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
    )

# ==========================================
# GITHUB-STYLE CSS (Primer Design System)
# ==========================================
st.markdown("""
<style>
    /* Системные шрифты как на GitHub */
    body, .stApp, .stMarkdown, .stTextInput, .stSelectbox, .stButton, .stExpander {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif !important;
    }
    
    /* НЕ задаем жесткий фон и цвет текста для .stApp, чтобы работал переключатель темы Streamlit */
    
    /* Сайдбар: только граница, без жесткого фона */
    section[data-testid="stSidebar"] {
        border-right: 1px solid var(--secondary-background-color, #d0d7de) !important;
    }
    
    /* Статусные бейджи (вместо эмодзи) */
    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        margin-right: 8px;
    }
    .status-critical { background-color: #ffebe9; color: #cf222e; border: 1px solid #ffc1c0; }
    .status-high { background-color: #fff8c5; color: #9a6700; border: 1px solid #d4a72c; }
    .status-planned { background-color: #dafbe1; color: #1a7f37; border: 1px solid #2da44e; }
    .status-spam { background-color: #f6f8fa; color: #57606a; border: 1px solid #d0d7de; }
    
    /* Экспандеры как карточки инцидентов на GitHub */
    .streamlit-expanderHeader {
        background-color: var(--secondary-background-color, #f6f8fa) !important;
        border: 1px solid var(--secondary-background-color, #d0d7de) !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        color: var(--text-color, #24292f) !important;
        font-size: 14px !important;
    }
    .streamlit-expanderHeader:hover {
        background-color: var(--secondary-background-color, #eef1f4) !important;
    }
    .streamlit-expanderContent {
        border: 1px solid var(--secondary-background-color, #d0d7de) !important;
        border-top: none !important;
        border-radius: 0 0 6px 6px !important;
        background-color: var(--background-color, #ffffff) !important;
        padding: 16px !important;
    }
    
    /* Цитата сообщения */
    .message-quote {
        background-color: var(--secondary-background-color, #f6f8fa);
        border-left: 4px solid var(--secondary-background-color, #d0d7de);
        padding: 12px 16px;
        border-radius: 0 6px 6px 0;
        color: var(--text-color, #57606a);
        font-size: 14px;
        line-height: 1.5;
        margin: 8px 0 16px 0;
    }
    
    /* Кнопки в стиле GitHub (Primary Green) */
    .stButton>button {
        background-color: #2da44e !important;
        color: #ffffff !important;
        border: 1px solid rgba(27,31,36,0.15) !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        padding: 6px 16px !important;
        transition: background-color 0.2s !important;
    }
    .stButton>button:hover {
        background-color: #2c974b !important;
    }
    .stButton>button:disabled {
        background-color: #94d3a2 !important;
        cursor: not-allowed !important;
    }
    
    /* Метрики */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 600 !important;
        color: var(--text-color, #24292f) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px !important;
        color: var(--text-color, #57606a) !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Скрыть лишние элементы Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Табы */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        font-weight: 600;
        color: var(--text-color, #57606a);
    }
    .stTabs [aria-selected="true"] {
        color: var(--text-color, #24292f) !important;
        border-bottom: 2px solid #fd8c73 !important; /* GitHub orange accent */
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# МАТРИЦА ЛОКАЛИЗАЦИИ (Строгий стиль, без эмодзи)
# ==========================================
LANGUAGES = {
    "Русский": {
        "lang_code": "ru",
        "title": "Ситуационный центр г. Астана",
        "subtitle": "Мониторинг инцидентов и автоматический скоринг угроз",
        "metric_total": "Всего обращений",
        "metric_crit": "Критические",
        "metric_avg": "Средний уровень угрозы",
        "filter_header": "Фильтры",
        "filter_cat": "Категории инцидентов",
        "filter_score": "Минимальный уровень угрозы (%)",
        "tab_feed": "Лента инцидентов",
        "tab_analytics": "Аналитика",
        "tab_data": "Данные и эффект",
        "no_messages": "Нет данных для отображения по выбранным фильтрам.",
        "label_loc": "Локация",
        "label_src": "Источник",
        "label_date": "Дата",
        "ai_explain": "Обоснование оценки",
        "reason_base": "Фактор угрозы",
        "reason_scope": "Масштаб воздействия",
        "reason_triggers": "Ключевые триггеры",
        "top_factors": "Топ-3 фактора результата",
        "factor_threat": "Угроза",
        "factor_scope": "Масштаб",
        "factor_repetition": "Повторяемость",
        "no_repetition": "Повторных обращений по локации не выявлено.",
        "model_confidence": "Индекс достоверности",
        "confidence_note": "Индекс отражает оценку алгоритма по полноте и однозначности сообщения; не является гарантией точности.",
        "limitations": "Ограничения автоматического анализа",
        "limitations_text": "Система анализирует только текст обращения: возможны ошибки в адресе, категории и контексте. Оценка не заменяет выезд, проверку первичных источников и решение ответственной службы.",
        "human_decision": "Финальное решение принимает специалист.",
        "btn_approve": "Утвердить и передать в службу",
        "toast_approved": "Инцидент передан в работу",
        "ai_consultant": "AI-консультант",
        "ai_situation": "Опишите ситуацию",
        "ai_situation_placeholder": "Например: во дворе открыт люк рядом с детской площадкой.",
        "ai_get_recommendation": "Получить рекомендацию",
        "ai_empty_situation": "Опишите ситуацию, чтобы получить рекомендацию.",
        "ai_error": "Не удалось получить рекомендацию. Проверьте подключение к API и попробуйте ещё раз.",
        "error_file": "Файл analyzed_city_messages.csv не найден. Запустите скрипт обработки данных.",
        "cats": {
            "ЖКХ": "ЖКХ", "Дороги": "Дороги", "Общественный транспорт": "Транспорт",
            "Экология": "Экология", "Безопасность": "Безопасность", "Мусор": "Мусор", "Флуд": "Спам / Инфошум"
        },
        "status_critical": "Критический",
        "status_high": "Повышенный",
        "status_planned": "Плановый",
        "status_flood": "Спам",
        "rep_bonus_text": "Повторяемость",
        "rep_bonus_desc": "Начислен бонус (+{bonus}%) за массовые жалобы",
        "chart_categories": "Распределение по категориям",
        "chart_dynamics": "Динамика уровня угрозы",
        "chart_dynamics_hint": "Средний скор по дням",
        "btn_refresh": "Обновить данные",
        "data_docs": "Документация по данным",
        "data_source": "Источник: демонстрационный, моделируемый набор обращений жителей Астаны из неформальных каналов (соцсети и чаты); не является официальным реестром.",
        "data_size": "Размер: 120 текстовых сообщений в city_messages.csv.",
        "data_features": "Признаки: текст, источник, дата; после анализа — категория, локация, индекс угрозы, масштаб, триггеры и повторяемость.",
        "data_preprocessing": "Очистка и обработка: проверка обязательных полей, приведение даты и числовых значений, нормализация названий локаций, фильтрация спама и объединение повторных сигналов по локации.",
        "data_limitations": "Ограничения данных: небольшой демонстрационный набор, сообщения могут быть неполными или эмоциональными, а их достоверность и адрес требуют проверки специалистом.",
        "effect": "Измеримый эффект",
        "effect_time": "Потенциальная экономия времени",
        "effect_load": "Снижение ручной нагрузки",
        "effect_priority": "Приоритизация рисков",
        "effect_time_desc": "Сценарная оценка: при 2 минутах ручного первичного разбора на сообщение.",
        "effect_load_desc": "Все обращения получают автоматическую первичную категоризацию и скоринг; специалист верифицирует только решение.",
        "effect_priority_desc": "Обращения с индексом угрозы от 80% вынесены в начало ленты для оперативной проверки.",
    },
    "Қазақша": {
        "lang_code": "kz",
        "title": "Астана қ. Ситуациялық орталығы",
        "subtitle": "Оқиғаларды мониторингілеу және автоматты скоринг",
        "metric_total": "Барлық өтініштер",
        "metric_crit": "Критикалық",
        "metric_avg": "Орташа қауіп деңгейі",
        "filter_header": "Сүзгілер",
        "filter_cat": "Оқиғалар санаттары",
        "filter_score": "Минималды қауіп деңгейі (%)",
        "tab_feed": "Оқиғалар таспасы",
        "tab_analytics": "Аналитика",
        "tab_data": "Деректер және әсер",
        "no_messages": "Таңдалған сүзгілер бойынша деректер жоқ.",
        "label_loc": "Орналасқан жері",
        "label_src": "Дереккөз",
        "label_date": "Күн",
        "ai_explain": "Бағалау негіздемесі",
        "reason_base": "Қауіп факторы",
        "reason_scope": "Әсер ету ауқымы",
        "reason_triggers": "Негізгі триггерлер",
        "top_factors": "Нәтижеге әсер еткен 3 фактор",
        "factor_threat": "Қауіп",
        "factor_scope": "Ауқым",
        "factor_repetition": "Қайталану",
        "no_repetition": "Локация бойынша қайталанған өтініштер анықталмады.",
        "model_confidence": "Сенімділік индексі",
        "confidence_note": "Индекс хабарламаның толықтығы мен бірмәнділігіне берілген алгоритм бағасын көрсетеді; бұл дәлдік кепілі емес.",
        "limitations": "Автоматты талдау шектеулері",
        "limitations_text": "Жүйе тек өтініш мәтінін талдайды: мекенжайда, санатта және контексте қателер болуы мүмкін. Баға жауапты қызметтің тексеруін, шығуын және шешімін алмастырмайды.",
        "human_decision": "Соңғы шешімді маман қабылдайды.",
        "btn_approve": "Бекіту және қызметке беру",
        "toast_approved": "Оқиға жұмысқа жіберілді",
        "ai_consultant": "AI-кеңесші",
        "ai_situation": "Жағдайды сипаттаңыз",
        "ai_situation_placeholder": "Мысалы: балалар алаңының жанындағы аулада ашық құдық бар.",
        "ai_get_recommendation": "Ұсыныс алу",
        "ai_empty_situation": "Ұсыныс алу үшін жағдайды сипаттаңыз.",
        "ai_error": "Ұсынысты алу мүмкін болмады. API қосылымын тексеріп, қайталап көріңіз.",
        "error_file": "analyzed_city_messages.csv табылмады. Деректерді өңдеу скриптін іске қосыңыз.",
        "cats": {
            "ЖКХ": "ТҮКШ", "Дороги": "Жолдар", "Общественный транспорт": "Көлік",
            "Экология": "Экология", "Безопасность": "Қауіпсіздік", "Мусор": "Қоқыс", "Флуд": "Спам"
        },
        "status_critical": "Критикалық",
        "status_high": "Жоғары",
        "status_planned": "Жоспарлы",
        "status_flood": "Спам",
        "rep_bonus_text": "Қайталану",
        "rep_bonus_desc": "Жаппай шағымдар үшін бонус қосылды (+{bonus}%)",
        "chart_categories": "Санаттар бойынша бөлу",
        "chart_dynamics": "Қауіп деңгейінің динамикасы",
        "chart_dynamics_hint": "Күн бойынша агрегация",
        "btn_refresh": "Деректерді жаңарту",
        "data_docs": "Деректер құжаттамасы",
        "data_source": "Дереккөз: Астана тұрғындарының бейресми арналарынан алынған өтініштердің демонстрациялық жинағы; ресми тізілім емес.",
        "data_size": "Көлемі: city_messages.csv файлындағы 120 мәтіндік хабарлама.",
        "data_features": "Белгілер: мәтін, дереккөз, күн; талдаудан кейін — санат, локация, қауіп индексі, ауқым, триггерлер және қайталану.",
        "data_preprocessing": "Өңдеу: міндетті өрістерді тексеру, күн мен сандық мәндерді келтіру, локация атауларын қалыпқа келтіру, спамды сүзу.",
        "data_limitations": "Шектеулер: шағын демонстрациялық жинақ, хабарламалар толық емес не эмоциялы болуы мүмкін.",
        "effect": "Өлшенетін әсер",
        "effect_time": "Уақытты ықтимал үнемдеу",
        "effect_load": "Қолмен орындалатын жүктемені азайту",
        "effect_priority": "Тәуекелдерді басымдыққа қою",
        "effect_time_desc": "Сценарийлік бағалау: бір хабарламаны қолмен талдауға 2 минут кеткенде.",
        "effect_load_desc": "Барлық өтініш автоматты санаттау мен скорингтен өтеді; маман шешімді ғана тексереді.",
        "effect_priority_desc": "Қауіп индексі 80%-дан жоғары өтініштер жедел тексеру үшін лентаның басына шығарылады.",
    },
    "English": {
        "lang_code": "en",
        "title": "Astana Situational Center",
        "subtitle": "Incident monitoring and automated threat scoring",
        "metric_total": "Total Reports",
        "metric_crit": "Critical",
        "metric_avg": "Avg Threat Level",
        "filter_header": "Filters",
        "filter_cat": "Categories",
        "filter_score": "Min Threat Level (%)",
        "tab_feed": "Incident Feed",
        "tab_analytics": "Analytics",
        "tab_data": "Data and impact",
        "no_messages": "No data available for selected filters.",
        "label_loc": "Location",
        "label_src": "Source",
        "label_date": "Date",
        "ai_explain": "Assessment Details",
        "reason_base": "Threat Factor",
        "reason_scope": "Impact Scope",
        "reason_triggers": "Key Triggers",
        "top_factors": "Top 3 result factors",
        "factor_threat": "Threat",
        "factor_scope": "Scope",
        "factor_repetition": "Repetition",
        "no_repetition": "No repeated reports for this location were found.",
        "model_confidence": "Confidence Score",
        "confidence_note": "Score reflects the algorithm's assessment of report completeness and clarity; it is not a guarantee of accuracy.",
        "limitations": "Automated analysis limitations",
        "limitations_text": "The system only analyzes report text, so location, category, and context can be wrong. The score does not replace field verification or the responsible service's decision.",
        "human_decision": "The final decision is made by a specialist.",
        "btn_approve": "Approve and Dispatch",
        "toast_approved": "Incident dispatched",
        "ai_consultant": "AI consultant",
        "ai_situation": "Describe the situation",
        "ai_situation_placeholder": "For example: an open manhole is next to a playground.",
        "ai_get_recommendation": "Get recommendation",
        "ai_empty_situation": "Describe the situation to get a recommendation.",
        "ai_error": "Could not get a recommendation. Check the API connection and try again.",
        "error_file": "analyzed_city_messages.csv not found. Run the data processing script.",
        "cats": {
            "ЖКХ": "Utilities", "Дороги": "Roads", "Общественный транспорт": "Transport",
            "Экология": "Ecology", "Безопасность": "Security", "Мусор": "Garbage", "Флуд": "Spam"
        },
        "status_critical": "Critical",
        "status_high": "Elevated",
        "status_planned": "Planned",
        "status_flood": "Spam",
        "rep_bonus_text": "Repetition",
        "rep_bonus_desc": "Bonus (+{bonus}%) applied for mass complaints",
        "chart_categories": "Distribution by category",
        "chart_dynamics": "Threat level dynamics",
        "chart_dynamics_hint": "Daily aggregation",
        "btn_refresh": "Refresh data",
        "data_docs": "Data documentation",
        "data_source": "Source: a demonstrative, simulated dataset of Astana residents' reports from informal channels; not an official registry.",
        "data_size": "Size: 120 text messages in city_messages.csv.",
        "data_features": "Features: text, source, date; after analysis — category, location, threat score, scope, triggers, and repetition.",
        "data_preprocessing": "Processing: required-field checks, date and numeric normalization, location-name normalization, spam filtering.",
        "data_limitations": "Data limitations: a small demonstrative dataset; messages may be incomplete or emotional.",
        "effect": "Measurable impact",
        "effect_time": "Potential time savings",
        "effect_load": "Reduced manual workload",
        "effect_priority": "Risk prioritization",
        "effect_time_desc": "Scenario estimate based on two minutes of manual initial review per report.",
        "effect_load_desc": "Every report receives automated initial categorization and scoring; the specialist verifies the decision.",
        "effect_priority_desc": "Reports with a threat score of 80% or higher are placed first for prompt review.",
    }
}

# ==========================================
# ИНИЦИАЛИЗАЦИЯ СТРАНИЦЫ
# ==========================================
st.set_page_config(page_title="Ситуационный Центр", page_icon="📊", layout="wide")

st.sidebar.markdown("Язык / Тіл / Language")
selected_lang = st.sidebar.selectbox("Lang", list(LANGUAGES.keys()), index=0, label_visibility="collapsed")
t = LANGUAGES[selected_lang]
lang_code = t["lang_code"]

st.title(t["title"])
st.markdown(f"<div style='color: #57606a; font-size: 16px; margin-top: -10px; margin-bottom: 24px;'>{t['subtitle']}</div>", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv("analyzed_city_messages.csv")
        if df.empty:
            st.warning("Файл данных пуст. Запустите скрипт обработки данных.")
            return pd.DataFrame()

        required_cols = [
            'criticality_score', 'rep_bonus', 'category', 'extracted_location',
            'base_threat_reason_ru', 'scope_reason_ru',
            'base_threat_reason_kz', 'scope_reason_kz',
            'base_threat_reason_en', 'scope_reason_en',
            'trigger_words', 'text'
        ]

        if 'date' not in df.columns:
            df['date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        if 'source' not in df.columns:
            df['source'] = 'unknown'

        df['date'] = pd.to_datetime(df['date'], errors='coerce')

        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Ошибка структуры данных. Отсутствуют колонки: {missing}.")
            st.info("Решение: Удалите старый `analyzed_city_messages.csv` и запустите скрипт обработки заново.")
            return pd.DataFrame()

        return df
    except FileNotFoundError:
        st.error("Файл `analyzed_city_messages.csv` не найден.")
        st.info("Как это исправить:\n1. Убедитесь, что вы запустили скрипт обработки данных.\n2. Или положите готовый демо-файл в корень проекта.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Непредвиденная ошибка при загрузке данных: {e}")
        return pd.DataFrame()
    
def get_status_config(score):
    if score >= 80: return "status-critical", t["status_critical"]
    if score >= 50: return "status-high", t["status_high"]
    if score > 0: return "status-planned", t["status_planned"]
    return "status-spam", t["status_flood"]

def get_model_confidence(row):
    confidence = row.get('model_confidence')
    if pd.notna(confidence):
        return max(0, min(100, int(confidence)))
    fields = ['base_threat_reason_ru', 'scope_reason_ru', 'trigger_words', 'extracted_location']
    completed = sum(
        pd.notna(row.get(field)) and str(row.get(field)).strip().lower() not in ['', 'nan', 'не обработано']
        for field in fields
    )
    return 55 + completed * 10

# ==========================================
# ОСНОВНОЙ БЛОК
# ==========================================
try:
    if st.sidebar.button(t["btn_refresh"]):
        st.cache_data.clear()
        st.rerun()

    df = load_data()
    if df.empty:
        st.stop()

    crit_count = len(df[df['criticality_score'] >= 80])
    avg_score = int(df['criticality_score'].mean())

    col1, col2, col3 = st.columns(3)
    col1.metric(t["metric_total"], len(df))
    col2.metric(t["metric_crit"], crit_count)
    col3.metric(t["metric_avg"], f"{avg_score}%")
    st.markdown("<hr style='border: 0; border-top: 1px solid #d0d7de; margin: 24px 0;'>", unsafe_allow_html=True)

    st.sidebar.markdown(f"### {t['filter_header']}")
    raw_cats = df['category'].dropna().unique().tolist()
    trans_cats_map = {cat: t["cats"].get(cat, cat) for cat in raw_cats}

    sel_trans_cats = st.sidebar.multiselect(
        t["filter_cat"], options=list(trans_cats_map.values()), default=list(trans_cats_map.values())
    )
    sel_raw_cats = [raw for raw, trans in trans_cats_map.items() if trans in sel_trans_cats]
    min_score = st.sidebar.slider(t["filter_score"], 0, 100, 0, 5)

    filtered_df = df[(df['category'].isin(sel_raw_cats)) & (df['criticality_score'] >= min_score)]
    filtered_df = filtered_df.sort_values(by='criticality_score', ascending=False)

    tab_feed, tab_analytics, tab_data = st.tabs([t["tab_feed"], t["tab_analytics"], t["tab_data"]])

    with tab_feed:
        if filtered_df.empty:
            st.info(t["no_messages"])
        else:
            for idx, row in filtered_df.iterrows():
                score = row['criticality_score']
                css_class, status_text = get_status_config(score)
                cat_trans = t["cats"].get(row['category'], row['category'])
                loc = row.get('extracted_location', '—')
                if pd.isna(loc) or str(loc).lower() in ['nan', 'none', 'null', '']:
                    loc = '—'

                # 1. Текстовый заголовок для самого экспандера (Streamlit не рендерит HTML в label)
                expander_title = f"{status_text}  |  [{score}%]  |  {cat_trans}  |  {loc}"
                
                with st.expander(expander_title, expanded=(score >= 80)):
                    
                    # 2. Красивый HTML-блок с бейджами рендерим ВНУТРИ экспандера
                    header_html = f"""
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                        <span class="status-badge {css_class}">{status_text}</span>
                        <span style="font-weight: 600; color: #24292f; font-size: 16px;">[{score}%]</span>
                        <span style="color: #57606a; font-weight: 500;">{cat_trans}</span>
                        <span style="color: #8c959f;">|</span>
                        <span style="color: #57606a; font-weight: 500;">{loc}</span>
                    </div>
                    """
                    st.markdown(header_html, unsafe_allow_html=True)
                    
                    # Цитата сообщения
                    st.markdown(f'<div class="message-quote">{row["text"]}</div>', unsafe_allow_html=True)
                    
                    date_str = row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else '—'
                    st.markdown(
                        f"<div style='font-size: 13px; color: #57606a; margin-bottom: 16px;'>"
                        f"<strong>{t['label_date']}:</strong> {date_str} &nbsp;|&nbsp; "
                        f"<strong>{t['label_src']}:</strong> {row['source']}"
                        f"</div>", unsafe_allow_html=True
                    )
                    
                    st.markdown(f"**{t['ai_explain']}**")
                    base_reason = row.get(f'base_threat_reason_{lang_code}', row.get('base_threat_reason_ru', '—'))
                    scope_reason = row.get(f'scope_reason_{lang_code}', row.get('scope_reason_ru', '—'))

                    st.markdown(f"**{t['top_factors']}:**")
                    st.markdown(f"1. **{t['factor_threat']}:** {base_reason}")
                    st.markdown(f"2. **{t['factor_scope']}:** {scope_reason}")
                    repetition = (
                        t['rep_bonus_desc'].format(bonus=row['rep_bonus'])
                        if row.get('rep_bonus', 0) > 0 else t['no_repetition']
                    )
                    st.markdown(f"3. **{t['factor_repetition']}:** {repetition}")

                    triggers = row.get('trigger_words', '—')
                    st.markdown(f"- **{t['reason_triggers']}:** `{triggers}`")
                    
                    st.metric(t['model_confidence'], f"{get_model_confidence(row)}%")
                    st.caption(t['confidence_note'])
                    
                    with st.expander(t['limitations']):
                        st.info(t['limitations_text'])
                        
                    st.warning(f"{t['human_decision']}")

                    btn_key = f"approved_{idx}"
                    if btn_key not in st.session_state:
                        st.session_state[btn_key] = False

                    if st.session_state[btn_key]:
                        st.success(t['toast_approved'])
                    else:
                        if st.button(t['btn_approve'], key=f"btn_{idx}"):
                            st.session_state[btn_key] = True
                            st.rerun()

                    st.markdown("<hr style='border: 0; border-top: 1px solid #d0d7de; margin: 24px 0 16px;'>", unsafe_allow_html=True)
                    st.markdown(f"**{t['ai_consultant']}**")

                    advice_key = f"ai_advice_{idx}"
                    if st.button(t['ai_get_recommendation'], key=f'ai_button_{idx}'):
                        try:
                            with st.spinner("Генерирую рекомендацию для оператора..."):
                                st.session_state[advice_key] = get_operator_recommendation(str(row['text']))
                        except Exception as e:
                            st.error(f"{t['ai_error']} ({e})")

                    if st.session_state.get(advice_key):
                        st.info(st.session_state[advice_key])

    with tab_analytics:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**{t['chart_categories']}**")
            cat_counts = filtered_df['category'].value_counts()
            cat_counts.index = cat_counts.index.map(lambda x: t["cats"].get(x, x))
            st.bar_chart(cat_counts)
        with col_b:
            st.markdown(f"**{t['chart_dynamics']}**")
            st.caption(t["chart_dynamics_hint"])

            if not filtered_df.empty:
                plot_df = filtered_df.copy()
                plot_df['date'] = pd.to_datetime(plot_df['date'], errors='coerce')
                daily_scores = plot_df.groupby(plot_df['date'].dt.date)['criticality_score'].mean()
                daily_scores = daily_scores.reset_index()
                daily_scores.columns = ['date', 'avg_score']
                daily_scores = daily_scores.set_index('date')
                st.line_chart(daily_scores)
            else:
                st.info(t["no_messages"])

    with tab_data:
        st.subheader(t['data_docs'])
        st.write(t['data_source'])
        st.write(t['data_size'])
        st.write(t['data_features'])
        st.write(t['data_preprocessing'])
        st.write(t['data_limitations'])

        st.markdown("<hr style='border: 0; border-top: 1px solid #d0d7de; margin: 24px 0;'>", unsafe_allow_html=True)
        st.subheader(t['effect'])
        time_col, load_col, priority_col = st.columns(3)
        with time_col:
            st.metric(t['effect_time'], f"~{len(df) * 2} мин")
            st.caption(t['effect_time_desc'])
        with load_col:
            st.metric(t['effect_load'], f"{len(df)} / {len(df)}")
            st.caption(t['effect_load_desc'])
        with priority_col:
            st.metric(t['effect_priority'], f"{crit_count}")
            st.caption(t['effect_priority_desc'])

except Exception as e:
    st.error(f"Критическая ошибка приложения: {e}")
