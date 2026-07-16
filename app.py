import os
import pandas as pd
import streamlit as st

# ==========================================
# МАТРИЦА ЛОКАЛИЗАЦИИ
# ==========================================
LANGUAGES = {
    "🇷🇺 Русский": {
        "lang_code": "ru",
        "title": "📊 Ситуационный центр г. Астана",
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
        "top_factors": "Топ-3 фактора результата",
        "factor_threat": "Угроза",
        "factor_scope": "Масштаб",
        "factor_repetition": "Повторяемость",
        "no_repetition": "Повторных обращений по локации не выявлено.",
        "model_confidence": "Уверенность модели",
        "confidence_note": "Уверенность отражает оценку модели по полноте и однозначности сообщения; это не гарантия точности.",
        "limitations": "Ограничения модели",
        "limitations_text": "Модель анализирует только текст обращения: возможны ошибки в адресе, категории и контексте. Оценка не заменяет выезд, проверку первичных источников и решение ответственной службы.",
        "human_decision": "Финальное решение принимает специалист.",
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
        "tab_data": "Данные и эффект",
        "data_docs": "Документация по данным",
        "data_source": "Источник: демонстрационный, моделируемый набор обращений жителей Астаны из неформальных каналов (соцсети и чаты); не является официальным реестром.",
        "data_size": "Размер: 120 текстовых сообщений в city_messages.csv.",
        "data_features": "Признаки: текст, источник, дата; после анализа — категория, локация, индекс угрозы, масштаб, триггеры и повторяемость.",
        "data_preprocessing": "Очистка и обработка: проверка обязательных полей, приведение даты и числовых значений, нормализация названий локаций, фильтрация флуда и объединение повторных сигналов по локации.",
        "data_limitations": "Ограничения данных: небольшой демонстрационный набор, сообщения могут быть неполными или эмоциональными, а их достоверность и адрес требуют проверки специалистом.",
        "effect": "Измеримый эффект",
        "effect_time": "Потенциальная экономия времени",
        "effect_load": "Снижение ручной нагрузки",
        "effect_priority": "Приоритизация рисков",
        "effect_time_desc": "Сценарная оценка: при 2 минутах ручного первичного разбора на сообщение.",
        "effect_load_desc": "Все обращения получают автоматическую первичную категоризацию и скоринг; специалист верифицирует только решение.",
        "effect_priority_desc": "Обращения с индексом угрозы от 80% вынесены в начало ленты для оперативной проверки.",
    },
    "🇰🇿 Қазақша": {
        "lang_code": "kz",
        "title": "📊 Астана қ. Ситуациялық орталығы",
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
        "top_factors": "Нәтижеге әсер еткен 3 фактор",
        "factor_threat": "Қауіп",
        "factor_scope": "Ауқым",
        "factor_repetition": "Қайталану",
        "no_repetition": "Локация бойынша қайталанған өтініштер анықталмады.",
        "model_confidence": "Модель сенімділігі",
        "confidence_note": "Сенімділік хабарламаның толықтығы мен бірмәнділігіне берілген модель бағасын көрсетеді; бұл дәлдік кепілі емес.",
        "limitations": "Модель шектеулері",
        "limitations_text": "Модель тек өтініш мәтінін талдайды: мекенжайда, санатта және контексте қателер болуы мүмкін. Баға жауапты қызметтің тексеруін, шығуын және шешімін алмастырмайды.",
        "human_decision": "Соңғы шешімді маман қабылдайды.",
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
        "tab_data": "Деректер және әсер",
        "data_docs": "Деректер құжаттамасы",
        "data_source": "Дереккөз: Астана тұрғындарының бейресми арналарынан (әлеуметтік желілер мен чаттар) алынған өтініштердің демонстрациялық, модельденген жинағы; ресми тізілім емес.",
        "data_size": "Көлемі: city_messages.csv файлындағы 120 мәтіндік хабарлама.",
        "data_features": "Белгілер: мәтін, дереккөз, күн; талдаудан кейін — санат, локация, қауіп индексі, ауқым, триггерлер және қайталану.",
        "data_preprocessing": "Өңдеу: міндетті өрістерді тексеру, күн мен сандық мәндерді келтіру, локация атауларын қалыпқа келтіру, флудты сүзу және локация бойынша қайталанатын сигналдарды біріктіру.",
        "data_limitations": "Шектеулер: шағын демонстрациялық жинақ, хабарламалар толық емес не эмоциялы болуы мүмкін; олардың дұрыстығы мен мекенжайын маман тексеруі керек.",
        "effect": "Өлшенетін әсер",
        "effect_time": "Уақытты ықтимал үнемдеу",
        "effect_load": "Қолмен орындалатын жүктемені азайту",
        "effect_priority": "Тәуекелдерді басымдыққа қою",
        "effect_time_desc": "Сценарийлік бағалау: бір хабарламаны қолмен бастапқы талдауға 2 минут кеткенде.",
        "effect_load_desc": "Барлық өтініш автоматты бастапқы санаттау мен скорингтен өтеді; маман шешімді ғана тексереді.",
        "effect_priority_desc": "Қауіп индексі 80%-дан жоғары өтініштер жедел тексеру үшін лентаның басына шығарылады.",
    },
    "🇬🇧 English": {
        "lang_code": "en",
        "title": "📊 Astana Situational Center",
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
        "top_factors": "Top 3 result factors",
        "factor_threat": "Threat",
        "factor_scope": "Scope",
        "factor_repetition": "Repetition",
        "no_repetition": "No repeated reports for this location were found.",
        "model_confidence": "Model confidence",
        "confidence_note": "Confidence reflects the model's assessment of report completeness and clarity; it is not a guarantee of accuracy.",
        "limitations": "Model limitations",
        "limitations_text": "The model only analyzes report text, so location, category, and context can be wrong. The score does not replace field verification, source checks, or the responsible service's decision.",
        "human_decision": "The final decision is made by a specialist.",
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
        "tab_data": "Data and impact",
        "data_docs": "Data documentation",
        "data_source": "Source: a demonstrative, simulated dataset of Astana residents' reports from informal channels (social media and chats); it is not an official registry.",
        "data_size": "Size: 120 text messages in city_messages.csv.",
        "data_features": "Features: text, source, date; after analysis—category, location, threat score, scope, triggers, and repetition.",
        "data_preprocessing": "Processing: required-field checks, date and numeric normalization, location-name normalization, flood filtering, and grouping repeated signals by location.",
        "data_limitations": "Data limitations: a small demonstrative dataset; messages may be incomplete or emotional, and their accuracy and location require specialist verification.",
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
    if 'model_confidence' in df.columns:
        df['model_confidence'] = pd.to_numeric(df['model_confidence'], errors='coerce')

    # Преобразуем date в datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce').fillna(pd.Timestamp.now())

    return df

def get_status_config(score, t):
    if score >= 80: return "🔴", t["status_critical"]
    if score >= 50: return "🟠", t["status_high"]
    if score > 0: return "🟢", t["status_planned"]
    return "⚪", t["status_flood"]

def get_model_confidence(row):
    """Возвращает оценку уверенности из модели либо консервативный fallback для старых результатов."""
    confidence = row.get('model_confidence')
    if pd.notna(confidence):
        return max(0, min(100, int(confidence)))

    # Старые выгрузки не содержат поля model_confidence. Оценка основана на полноте
    # структурированных факторов, а не выдаётся за результат повторного запуска модели.
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

    tab_feed, tab_analytics, tab_data = st.tabs([t["tab_feed"], t["tab_analytics"], t["tab_data"]])

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
                    st.warning(f"⚖️ {t['human_decision']}")

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

    with tab_data:
        st.subheader(t['data_docs'])
        st.write(t['data_source'])
        st.write(t['data_size'])
        st.write(t['data_features'])
        st.write(t['data_preprocessing'])
        st.write(t['data_limitations'])

        st.subheader(t['effect'])
        time_col, load_col, priority_col = st.columns(3)
        with time_col:
            st.metric(t['effect_time'], f"~{len(df) * 2} мин")
            st.caption(t['effect_time_desc'])
        with load_col:
            st.metric(t['effect_load'], f"{len(df)} / {len(df)}")
            st.caption(t['effect_load_desc'])
        with priority_col:
            st.metric(t['effect_priority'], f"{crit_count} {t['metric_crit'].lower()}")
            st.caption(t['effect_priority_desc'])

except FileNotFoundError:
    st.error(t["error_file"])
except ValueError as e:
    st.error(str(e))
