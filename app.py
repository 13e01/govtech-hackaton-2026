import streamlit as st
import pandas as pd

# ==========================================
# МАТРИЦА ЛОКАЛИЗАЦИИ (3 ЯЗЫКА)
# ==========================================
LANGUAGES = {
    "🇷🇺 Русский": {
        "page_title": "AI-Радар Ситуационного Центра",
        "title": "🚨 AI-Радар: Мониторинг скрытых инфраструктурных кризисов",
        "subtitle": "Система анализа неофициальных текстовых источников (пабликов и чатов) города Петропавловск.",
        "metric_total": "Всего обработано сообщений",
        "metric_crit": "⚠️ Критических инцидентов найдено",
        "metric_crit_delta": "требуют внимания",
        "metric_sources": "Отслеживаемых источников",
        "filter_header": "⚙️ Фильтры мониторинга",
        "filter_cat": "Выберите категории:",
        "filter_crit_only": "Показать ТОЛЬКО критические 🚨",
        "subheader": "📋 Лента инцидентов и объяснения ИИ",
        "no_messages": "Нет сообщений, соответствующих выбранным фильтрам.",
        "status_crit": "🔴 КРИТИЧЕСКИЙ СТАТУС",
        "status_std": "🔵 СТАНДАРТНЫЙ СТАТУС",
        "label_cat": "Категория",
        "label_src": "Источник",
        "label_date": "Дата",
        "text_citizen": "💬 Текст жителя:",
        "ai_explain": "🧠 Обоснование ИИ (Explainability):",
        "error_file": "Ошибка: Файл analyzed_city_messages.csv не найден! Сначала запусти скрипт analyzer.py",
        "cats": {
            "ЖКХ": "ЖКХ", 
            "Дороги": "Дороги", 
            "Общественный транспорт": "Общественный транспорт", 
            "Экология": "Экология", 
            "Безопасность": "Безопасность", 
            "Мусор": "Мусор", 
            "Флуд": "Флуд"
        }
    },
    "🇰🇿 Қазақша": {
        "page_title": "Ситуациялық орталықтың ИИ-Радары",
        "title": "🚨 AI-Радар: Жасырын инфрақұрылымдық дағдарыстарды мониторингілеу",
        "subtitle": "Петропавл қаласының бейресми мәтіндік көздерін (пабликтер мен чаттарды) талдау жүйесі.",
        "metric_total": "Барлық өңделген хабарламалар",
        "metric_crit": "⚠️ Критикалық оқиғалар табылды",
        "metric_crit_delta": "назар аударуды талап етеді",
        "metric_sources": "Қадағаланатын дереккөздер",
        "filter_header": "⚙️ Мониторинг сүзгілері",
        "filter_cat": "Санаттарды таңдаңыз:",
        "filter_crit_only": "ТЕК критикалық жағдайларды көрсету 🚨",
        "subheader": "📋 Оқиғалар таспасы және ИИ түсіндірмесі",
        "no_messages": "Таңдалған сүзгілерге сәйкес келетін хабарламалар жоқ.",
        "status_crit": "🔴 КРИТИКАЛЫҚ МӘРТЕБЕ",
        "status_std": "🔵 СТАНДАРТТЫ МӘРТЕБЕ",
        "label_cat": "Санат",
        "label_src": "Дереккөз",
        "label_date": "Күн",
        "text_citizen": "💬 Тұрғынның мәтіні:",
        "ai_explain": "🧠 ИИ негіздемесі (Explainability):",
        "error_file": "Қате: analyzed_city_messages.csv файлы табылмады! Алдымен analyzer.py скриптисін іске қосыңыз",
        "cats": {
            "ЖКХ": "ТҮКШ (ЖКХ)", 
            "Дороги": "Жолдар", 
            "Общественный транспорт": "Қоғамдық көлік", 
            "Экология": "Экология", 
            "Безопасность": "Қауіпсіздік", 
            "Мусор": "Қоқыс", 
            "Флуд": "Флуд / Спам"
        }
    },
    "🇬🇧 English": {
        "page_title": "Situational Center AI-Radar",
        "title": "🚨 AI-Radar: Monitoring Hidden Infrastructure Crises",
        "subtitle": "Analysis system for unofficial text sources (public pages and chats) in Petropavl city.",
        "metric_total": "Total messages processed",
        "metric_crit": "⚠️ Critical incidents found",
        "metric_crit_delta": "require attention",
        "metric_sources": "Monitored sources",
        "filter_header": "⚙️ Monitoring Filters",
        "filter_cat": "Select categories:",
        "filter_crit_only": "Show ONLY critical 🚨",
        "subheader": "📋 Incident Feed & AI Explainability",
        "no_messages": "No messages match the selected filters.",
        "status_crit": "🔴 CRITICAL STATUS",
        "status_std": "🔵 STANDARD STATUS",
        "label_cat": "Category",
        "label_src": "Source",
        "label_date": "Date",
        "text_citizen": "💬 Citizen text:",
        "ai_explain": "🧠 AI Reason (Explainability):",
        "error_file": "Error: File analyzed_city_messages.csv not found! Run analyzer.py script first",
        "cats": {
            "ЖКХ": "Utilities (ЖКХ)", 
            "Дороги": "Roads", 
            "Общественный transport": "Public Transport", 
            "Экология": "Ecology", 
            "Безопасность": "Security", 
            "Мусор": "Garbage", 
            "Флуд": "Flood / Spam"
        }
    }
}

# ==========================================
# ИНИЦИАЛИЗАЦИЯ ИНТЕРФЕЙСА В СЛОВАХ ЛОКАЛИЗАЦИИ
# ==========================================

# Выбор языка выносим в самый верх боковой панели
st.sidebar.markdown("### 🌐 Language / Тіл / Язык")
selected_lang = st.sidebar.selectbox(
    "Select dashboard language:", 
    list(LANGUAGES.keys()), 
    index=0,
    label_visibility="collapsed"
)

# Вытаскиваем нужный словарь перевода (t)
t = LANGUAGES[selected_lang]

# Настройка вкладки браузера
st.set_page_config(page_title=t["page_title"], page_icon="🤖", layout="wide")

# Заголовки на выбранном языке
st.title(t["title"])
st.markdown(t["subtitle"])

# Функция загрузки сохраненных ИИ-данных
@st.cache_data
def load_data():
    return pd.read_csv("analyzed_city_messages.csv")

try:
    df = load_data()

    # Верхняя панель с метриками
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=t["metric_total"], value=len(df))
    with col2:
        critical_count = len(df[df['is_critical'] == True])
        st.metric(label=t["metric_crit"], value=critical_count, delta=f"{critical_count} {t['metric_crit_delta']}")
    with col3:
        st.metric(label=t["metric_sources"], value=df['source'].nunique())

    st.markdown("---")

    # Настройка фильтров в Сайдбаре
    st.sidebar.header(t["filter_header"])
    
    # Подгружаем категории и переводим их названия для отображения в списке фильтра
    raw_categories = df['category'].unique().tolist()
    translated_cats_map = {cat: t["cats"].get(cat, cat) for cat in raw_categories}
    
    # Селектбокс отображает переведенные названия
    selected_translated_cats = st.sidebar.multiselect(
        t["filter_cat"], 
        options=list(translated_cats_map.values()), 
        default=list(translated_cats_map.values())
    )
    
    # Переводим обратно в исходные ключи для фильтрации датафрейма
    selected_raw_categories = [raw for raw, trans in translated_cats_map.items() if trans in selected_translated_cats]
    
    # Переключатель критических инцидентов
    only_critical = st.sidebar.checkbox(t["filter_crit_only"], value=False)

    # Применение фильтров к базе
    filtered_df = df[df['category'].isin(selected_raw_categories)]
    if only_critical:
        filtered_df = filtered_df[filtered_df['is_critical'] == True]

    # Вывод результатов ленты инцидентов
    st.subheader(t["subheader"])
    
    if filtered_df.empty:
        st.info(t["no_messages"])
    else:
        for idx, row in filtered_df.iterrows():
            # Подставляем перевод категории динамически
            current_cat_translated = t["cats"].get(row['category'], row['category'])
            
            if row['is_critical'] == True:
                st.error(f"{t['status_crit']} | {t['label_cat']}: {current_cat_translated} | {t['label_src']}: {row['source']} | {t['label_date']}: {row['date']}")
            else:
                st.info(f"{t['status_std']} | {t['label_cat']}: {current_cat_translated} | {t['label_src']}: {row['source']} | {t['label_date']}: {row['date']}")
            
            # Текст жителя и объяснение ИИ
            st.write(f"{t['text_citizen']} *\"{row['text']}\"*")
            st.warning(f"{t['ai_explain']} {row['explanation']}")
            st.markdown("---")

except FileNotFoundError:
    st.error(t["error_file"])