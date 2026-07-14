import os
import pandas as pd
import streamlit as st

# ==========================================
# МАТРИЦА ЛОКАЛИЗАЦИИ
# ==========================================
LANGUAGES = {
    "🇷🇺 Русский": {
        "lang_code": "ru",
        "title": "📊 Ситуационный Центр г. Петропавловск",
        "subtitle": "Мониторинг инцидентов и AI-скоринг угроз.",
        "metric_total": "Всего обращений",
        "metric_crit": "Критические (>80%)",
        "metric_avg": "Средний уровень угрозы",
        "filter_header": "Фильтры",
        "filter_cat": "Категории инцидентов:",
        "filter_score": "Минимальный уровень угрозы (%):",
        "tab_feed": "Лента инцидентов",
        "tab_analytics": "Аналитика",
        "no_messages": "Нет данных для отображения.",
        "label_loc": "Локация",
        "label_src": "Источник",
        "label_date": "Дата",
        "ai_explain": "Обоснование ИИ (Explainability)",
        "reason_base": "Угроза",
        "reason_scope": "Масштаб",
        "reason_triggers": "Триггеры",
        "btn_approve": "Утвердить и передать в службу",
        "toast_approved": "Инцидент передан в работу!",
        "error_file": "Файл analyzed_city_messages.csv не найден. Запустите analyzer.py.",
        "cats": {
            "ЖКХ": "ЖКХ", "Дороги": "Дороги", "Общественный транспорт": "Транспорт",
            "Экология": "Экология", "Безопасность": "Безопасность", "Мусор": "Мусор", "Флуд": "Флуд"
        },
        "status_critical": "КРИТИЧЕСКИЙ",
        "status_high": "ПОВЫШЕННЫЙ",
        "status_planned": "ПЛАНОВЫЙ",
        "status_flood": "ФЛУД",
        "rep_bonus_text": "Повторяемость",
        "rep_bonus_desc": "Начислен бонус (+{bonus}%) за массовые жалобы.",
        "chart_categories": "Распределение по категориям",
        "chart_dynamics": "Динамика уровня угрозы",
        "chart_dynamics_hint": "Средний скор по дням",
        "btn_refresh": "🔄 Обновить данные",
    },
    "🇰🇿 Қазақша": {
        "lang_code": "kz",
        "title": "📊 Петропавл қ. Ситуациялық орталығы",
        "subtitle": "Оқиғаларды мониторингілеу және AI-скоринг.",
        "metric_total": "Барлық өтініштер",
        "metric_crit": "Критикалық (>80%)",
        "metric_avg": "Орташа қауіп деңгейі",
        "filter_header": "Сүзгілер",
        "filter_cat": "Оқиғалар санаттары:",
        "filter_score": "Минималды қауіп деңгейі (%):",
        "tab_feed": "Оқиғалар таспасы",
        "tab_analytics": "Аналитика",
        "no_messages": "Көрсетілетін деректер жоқ.",
        "label_loc": "Орналасқан жері",
        "label_src": "Дереккөз",
        "label_date": "Күн",
        "ai_explain": "Жасанды интеллект негіздемесі",
        "reason_base": "Қауіп",
        "reason_scope": "Ауқымы",
        "reason_triggers": "Триггерлер",
        "btn_approve": "Бекіту және қызметке беру",
        "toast_approved": "Оқиға жұмысқа жіберілді!",
        "error_file": "analyzed_city_messages.csv табылмады. analyzer.py іске қосыңыз.",
        "cats": {
            "ЖКХ": "ТҮКШ", "Дороги": "Жолдар", "Общественный транспорт": "Көлік",
            "Экология": "Экология", "Безопасность": "Қауіпсіздік", "Мусор": "Қоқыс", "Флуд": "Флуд"
        },
        "status_critical": "КРИТИКАЛЫҚ",
        "status_high": "ЖОҒАРЫ",
        "status_planned": "ЖОСПАРЛЫ",
        "status_flood": "ФЛУД",
        "rep_bonus_text": "Қайталану",
        "rep_bonus_desc": "Жаппай шағымдар үшін бонус қосылды (+{bonus}%).",
        "chart_categories": "Санаттар бойынша бөлу",
        "chart_dynamics": "Қауіп деңгейінің динамикасы",
        "chart_dynamics_hint": "Күн бойынша агрегация",
        "btn_refresh": "🔄 Деректерді жаңарту",
    },
    "🇬🇧 English": {
        "lang_code": "en",
        "title": "📊 Petropavl Situational Center",
        "subtitle": "Incident monitoring and AI threat scoring.",
        "metric_total": "Total Reports",
        "metric_crit": "Critical (>80%)",
        "metric_avg": "Avg Threat Level",
        "filter_header": "Filters",
        "filter_cat": "Categories:",
        "filter_score": "Min Threat Level (%):",
        "tab_feed": "Incident Feed",
        "tab_analytics": "Analytics",
        "no_messages": "No data available.",
        "label_loc": "Location",
        "label_src": "Source",
        "label_date": "Date",
        "ai_explain": "AI Explainability",
        "reason_base": "Threat",
        "reason_scope": "Scope",
        "reason_triggers": "Triggers",
        "btn_approve": "Approve & Dispatch",
        "toast_approved": "Incident dispatched!",
        "error_file": "analyzed_city_messages.csv not found. Run analyzer.py.",
        "cats": {
            "ЖКХ": "Utilities", "Дороги": "Roads", "Общественный транспорт": "Transport",
            "Экология": "Ecology", "Безопасность": "Security", "Мусор": "Garbage", "Флуд": "Flood"
        },
        "status_critical": "CRITICAL",
        "status_high": "ELEVATED",
        "status_planned": "PLANNED",
        "status_flood": "FLOOD",
        "rep_bonus_text": "Repetition",
        "rep_bonus_desc": "Bonus (+{bonus}%) applied for mass complaints.",
        "chart_categories": "Distribution by category",
        "chart_dynamics": "Threat level dynamics",
        "chart_dynamics_hint": "Daily aggregation",
        "btn_refresh": "🔄 Refresh data",
    }
}

# ==========================================
# ИНИЦИАЛИЗАЦИЯ СТРАНИЦЫ
# ==========================================
st.set_page_config(page_title="Ситуационный Центр", page_icon="📊", layout="wide")

st.sidebar.markdown("### 🌐 Тіл / Язык / Language")
selected_lang = st.sidebar.selectbox("Lang", list(LANGUAGES.keys()), index=0, label_visibility="collapsed")
t = LANGUAGES[selected_lang]
lang_code = t["lang_code"]

st.title(t["title"])
st.markdown(t["subtitle"])

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv("analyzed_city_messages.csv")

    # Обязательные колонки (включая мультиязычные)
    required_cols = [
        'criticality_score', 'rep_bonus', 'category', 'extracted_location',
        'base_threat_reason_ru', 'scope_reason_ru',
        'base_threat_reason_kz', 'scope_reason_kz',
        'base_threat_reason_en', 'scope_reason_en',
        'trigger_words', 'text'
    ]

    # Graceful handling для date/source
    if 'date' not in df.columns:
        df['date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
    if 'source' not in df.columns:
        df['source'] = 'unknown'

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Отсутствуют колонки: {missing}. Запустите analyzer.py с актуальной версией.")

    df['criticality_score'] = pd.to_numeric(df['criticality_score'], errors='coerce').fillna(0).astype(int)
    df['rep_bonus'] = pd.to_numeric(df.get('rep_bonus', 0), errors='coerce').fillna(0).astype(int)

    # Преобразуем date в datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce').fillna(pd.Timestamp.now())

    return df

def get_status_config(score, t):
    if score >= 80: return "🔴", t["status_critical"]
    if score >= 50: return "🟠", t["status_high"]
    if score > 0: return "🟢", t["status_planned"]
    return "⚪", t["status_flood"]

# ==========================================
# ОСНОВНОЙ БЛОК
# ==========================================
try:
    # Кнопка обновления данных
    if st.sidebar.button(t["btn_refresh"]):
        st.cache_data.clear()
        st.rerun()

    df = load_data()
    crit_count = len(df[df['criticality_score'] >= 80])
    avg_score = int(df['criticality_score'].mean())

    col1, col2, col3 = st.columns(3)
    col1.metric(t["metric_total"], len(df))
    col2.metric(t["metric_crit"], crit_count)
    col3.metric(t["metric_avg"], f"{avg_score}%")
    st.markdown("---")

    st.sidebar.header(t["filter_header"])
    raw_cats = df['category'].dropna().unique().tolist()
    trans_cats_map = {cat: t["cats"].get(cat, cat) for cat in raw_cats}

    sel_trans_cats = st.sidebar.multiselect(
        t["filter_cat"], options=list(trans_cats_map.values()), default=list(trans_cats_map.values())
    )
    sel_raw_cats = [raw for raw, trans in trans_cats_map.items() if trans in sel_trans_cats]
    min_score = st.sidebar.slider(t["filter_score"], 0, 100, 0, 5)

    filtered_df = df[(df['category'].isin(sel_raw_cats)) & (df['criticality_score'] >= min_score)]
    filtered_df = filtered_df.sort_values(by='criticality_score', ascending=False)

    tab_feed, tab_analytics = st.tabs([t["tab_feed"], t["tab_analytics"]])

    with tab_feed:
        if filtered_df.empty:
            st.info(t["no_messages"])
        else:
            for idx, row in filtered_df.iterrows():
                score = row['criticality_score']
                color, status_text = get_status_config(score, t)
                cat_trans = t["cats"].get(row['category'], row['category'])
                loc = row.get('extracted_location', '—')
                if pd.isna(loc) or str(loc).lower() in ['nan', 'none', 'null', '']:
                    loc = '—'

                header = f"{color} [{score}%] {status_text} | {cat_trans} | 📍 {loc}"
                with st.expander(header, expanded=(score >= 80)):
                    st.write(f"💬 *«{row['text']}»*")
                    st.caption(
                        f"📅 {t['label_date']}: {row['date'].strftime('%Y-%m-%d')} | "
                        f"🌐 {t['label_src']}: {row['source']}"
                    )
                    st.markdown(f"**🤖 {t['ai_explain']}:**")

                    # Динамическое отображение reason на выбранном языке
                    base_reason = row.get(f'base_threat_reason_{lang_code}', row.get('base_threat_reason_ru', '—'))
                    scope_reason = row.get(f'scope_reason_{lang_code}', row.get('scope_reason_ru', '—'))

                    st.markdown(f"- **{t['reason_base']}:** {base_reason}")
                    st.markdown(f"- **{t['reason_scope']}:** {scope_reason}")

                    if row.get('rep_bonus', 0) > 0:
                        st.markdown(
                            f"- **{t['rep_bonus_text']}:** {t['rep_bonus_desc'].format(bonus=row['rep_bonus'])}"
                        )

                    triggers = row.get('trigger_words', '—')
                    st.markdown(f"- **{t['reason_triggers']}:** `{triggers}`")

                    # Кнопка утверждения с сохранением состояния в сессии
                    btn_key = f"approved_{idx}"
                    if btn_key not in st.session_state:
                        st.session_state[btn_key] = False

                    if st.session_state[btn_key]:
                        st.success(f"✅ {t['toast_approved']}")
                    else:
                        if st.button(f"✅ {t['btn_approve']}", key=f"btn_{idx}"):
                            st.session_state[btn_key] = True
                            st.rerun()

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

            # Реальная динамика: агрегация по дням
            if not filtered_df.empty:
                daily_scores = filtered_df.groupby(filtered_df['date'].dt.date)['criticality_score'].mean()
                daily_scores = daily_scores.reset_index()
                daily_scores.columns = ['date', 'avg_score']
                daily_scores = daily_scores.set_index('date')
                st.line_chart(daily_scores)
            else:
                st.info(t["no_messages"])

except FileNotFoundError:
    st.error(t["error_file"])
except ValueError as e:
    st.error(str(e))