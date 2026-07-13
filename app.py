import os
import json
import time
import pandas as pd
import streamlit as st

# ==========================================
# МАТРИЦА ЛОКАЛИЗАЦИИ
# ==========================================
LANGUAGES = {
    "🇷🇺 Русский": {
        "page_title": "Ситуационный Центр — Петропавловск",
        "title": "📊 Мониторинг инцидентов Ситуационного Центра г. Петропавловск",
        "subtitle": "Автоматизированный анализ обращений граждан из открытых источников.",
        "metric_total": "Всего сообщений",
        "metric_crit": "Критические инциденты",
        "metric_crit_delta": "требуют внимания",
        "metric_sources": "Источники данных",
        "filter_header": "Фильтры",
        "filter_cat": "Категории инцидентов:",
        "filter_crit_only": "Только критические",
        "subheader": "Лента инцидентов",
        "no_messages": "Нет данных для отображения.",
        "status_crit": "КРИТИЧЕСКИЙ СТАТУС",
        "status_std": "СТАНДАРТНЫЙ СТАТУС",
        "label_cat": "Категория",
        "label_src": "Источник",
        "label_date": "Дата",
        "text_citizen": "Текст сообщения:",
        "ai_explain": "Обоснование:",
        "error_file": "Ошибка: Файл analyzed_city_messages.csv не найден. Запустите скрипт analyzer.py.",
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
        "page_title": "Ситуациялық орталық — Петропавл",
        "title": "📊 Петропавл қ. Ситуациялық орталығының оқиғаларды мониторингілеуі",
        "subtitle": "Ашық дереккөздерден түскен тұрғындардың өтініштерін автоматты түрде талдау.",
        "metric_total": "Хабарламалар саны",
        "metric_crit": "Критикалық оқиғалар",
        "metric_crit_delta": "назар аударуды қажет етеді",
        "metric_sources": "Дереккөздер",
        "filter_header": "Сүзгілер",
        "filter_cat": "Оқиғалар санаттары:",
        "filter_crit_only": "Тек критикалық",
        "subheader": "Оқиғалар таспасы",
        "no_messages": "Көрсетілетін деректер жоқ.",
        "status_crit": "КРИТИКАЛЫҚ МӘРТЕБЕ",
        "status_std": "СТАНДАРТТЫ МӘРТЕБЕ",
        "label_cat": "Санат",
        "label_src": "Дереккөз",
        "label_date": "Күн",
        "text_citizen": "Хабарлама мәтіні:",
        "ai_explain": "Негіздеме:",
        "error_file": "Қате: analyzed_city_messages.csv файлы табылмады. Алдымен analyzer.py скриптін іске қосыңыз.",
        "cats": {
            "ЖКХ": "ТҮКШ (ЖКХ)", 
            "Дороги": "Жолдар", 
            "Общественный транспорт": "Қоғамдық көлік", 
            "Экология": "Экология", 
            "Безопасность": "Қауіпсіздік", 
            "Мусор": "Қоқыс", 
            "Флуд": "Флуд"
        }
    },
    "🇬🇧 English": {
        "page_title": "Situational Center — Petropavl",
        "title": "📊 Incident Monitoring Dashboard — Petropavl City",
        "subtitle": "Automated analysis of citizen reports from open sources.",
        "metric_total": "Total Messages",
        "metric_crit": "Critical Incidents",
        "metric_crit_delta": "require attention",
        "metric_sources": "Data Sources",
        "filter_header": "Filters",
        "filter_cat": "Incident Categories:",
        "filter_crit_only": "Critical only",
        "subheader": "Incident Feed",
        "no_messages": "No data available.",
        "status_crit": "CRITICAL STATUS",
        "status_std": "STANDARD STATUS",
        "label_cat": "Category",
        "label_src": "Source",
        "label_date": "Date",
        "text_citizen": "Message text:",
        "ai_explain": "Justification:",
        "error_file": "Error: File analyzed_city_messages.csv not found. Run analyzer.py first.",
        "cats": {
            "ЖКХ": "Utilities", 
            "Дороги": "Roads", 
            "Общественный транспорт": "Public Transport", 
            "Экология": "Ecology", 
            "Безопасность": "Security", 
            "Мусор": "Garbage", 
            "Флуд": "Flood"
        }
    }
}

# Смена конфигурации страницы (должна идти строго первой из команд Streamlit)
st.set_page_config(page_title="Ситуационный Центр", page_icon="📊", layout="wide")

# Выбор языка в сайдбаре
st.sidebar.markdown("### 🌐 Language / Тіл / Язык")
selected_lang = st.sidebar.selectbox(
    "Language selector", 
    list(LANGUAGES.keys()), 
    index=0,
    label_visibility="collapsed"
)

t = LANGUAGES[selected_lang]

st.title(t["title"])
st.markdown(t["subtitle"])

@st.cache_data
def load_data():
    return pd.read_csv("analyzed_city_messages.csv")

try:
    df = load_data()

    # Метрики
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=t["metric_total"], value=len(df))
    with col2:
        critical_count = len(df[df['is_critical'] == True])
        st.metric(label=t["metric_crit"], value=critical_count, delta=f"{critical_count} {t['metric_crit_delta']}", delta_color="inverse")
    with col3:
        st.metric(label=t["metric_sources"], value=df['source'].nunique())

    st.markdown("---")

    # Настройка фильтров
    st.sidebar.header(t["filter_header"])
    
    raw_categories = df['category'].unique().tolist()
    translated_cats_map = {cat: t["cats"].get(cat, cat) for cat in raw_categories}
    
    selected_translated_cats = st.sidebar.multiselect(
        t["filter_cat"], 
        options=list(translated_cats_map.values()), 
        default=list(translated_cats_map.values())
    )
    
    selected_raw_categories = [raw for raw, trans in translated_cats_map.items() if trans in selected_translated_cats]
    only_critical = st.sidebar.checkbox(t["filter_crit_only"], value=False)

    # Фильтрация
    filtered_df = df[df['category'].isin(selected_raw_categories)]
    if only_critical:
        filtered_df = filtered_df[filtered_df['is_critical'] == True]

    # Вывод ленты
    st.subheader(t["subheader"])
    
    if filtered_df.empty:
        st.info(t["no_messages"])
    else:
        for idx, row in filtered_df.iterrows():
            current_cat_translated = t["cats"].get(row['category'], row['category'])
            
            # Рендеринг карточки инцидента
            if row['is_critical'] == True:
                st.error(f"🔴 {t['status_crit']} | {t['label_cat']}: {current_cat_translated} | {t['label_src']}: {row['source']} | {t['label_date']}: {row['date']}")
            else:
                st.info(f"🔵 {t['status_std']} | {t['label_cat']}: {current_cat_translated} | {t['label_src']}: {row['source']} | {t['label_date']}: {row['date']}")
            
            st.write(f"**{t['text_citizen']}** *\"{row['text']}\"*")
            st.warning(f"**{t['ai_explain']}** {row['explanation']}")
            st.markdown("---")

except FileNotFoundError:
    st.error(t["error_file"])