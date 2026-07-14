import os
import json
import time
import pandas as pd
import openai
from openai import OpenAI
from dotenv import load_dotenv
from collections import Counter

# ==========================================
# КОНФИГУРАЦИЯ И НАСТРОЙКИ
# ==========================================
INPUT_FILE = "city_messages.csv"
OUTPUT_FILE = "analyzed_city_messages.csv"
FORCE_REFRESH = True  # True = всегда считать с нуля; False = резюмировать по OUTPUT_FILE
MAX_RETRIES = 3
RETRY_DELAY = 5

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================
def init_client() -> OpenAI:
    """Инициализация клиента OpenAI (DeepSeek)."""
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("Критическая ошибка: DEEPSEEK_API_KEY не найден в файле .env")
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def calculate_repetition_bonus(location: str, location_counter: Counter) -> int:
    """Оценка фактора массовости жалоб (повторений по локации)."""
    if not location or str(location).lower() in ["null", "none", "", "nan"]:
        return 0

    loc = str(location).strip().lower()
    count = 0

    # Ищем совпадения: loc входит в существующую локацию или наоборот
    for existing_loc, existing_count in location_counter.items():
        if existing_loc and (loc in existing_loc or existing_loc in loc):
            count += existing_count

    if count >= 2:
        return 20
    elif count == 1:
        return 10
    return 0

def extract_json_from_response(raw_text: str) -> dict:
    """Очистка ответа от markdown-тегов и парсинг JSON."""
    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        lines = raw_text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw_text = "\n".join(lines).strip()
        if raw_text.startswith("json"):
            raw_text = raw_text[4:].strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Пытаемся найти JSON по фигурным скобкам (модель иногда добавляет пояснения)
        start = raw_text.find('{')
        end = raw_text.rfind('}')
        if start != -1 and end != -1 and end > start:
            return json.loads(raw_text[start:end + 1])
        raise

# ==========================================
# ОСНОВНАЯ ЛОГИКА АНАЛИЗА
# ==========================================
def analyze_text(client: OpenAI, text: str) -> dict:
    """Отправка запроса в DeepSeek API и получение структурированного ответа."""
    prompt = f"""
    Твоя задача — классифицировать обращение гражданина. Обращение может быть на русском или казахском языке.
    ВЕРНИ СТРОГО JSON-ОБЪЕКТ. БЕЗ ПРИВЕТСТВИЙ, БЕЗ МАРКДАУНА, БЕЗ ПОЯСНЕНИЙ.

    Критерии:
    1. base_threat_score (0-50): 
       - 50: угроза жизни (газ, открытый люк, ДТП, оголенный провод).
       - 35: угроза безопасности детей или уязвимых групп (непогашенное освещение у школы/площадки,
             агрессивные животные рядом с детской площадкой, отсутствие ограждений у опасных объектов).
       - 30: аварии ЖКХ (нет воды, прорыв трубы, нет света в доме).
       - 15: нарушение стандартов без прямой угрозы здоровью (мусор, задержка автобусов, шум).
       - 0: флуд, реклама.
    2. scope_score (0-20):
       - 5: 1-2 человека.
       - 10: дом/двор.
       - 20: микрорайон/улица.

    ТРЕБОВАНИЯ К ЯЗЫКУ И УНИФИКАЦИИ:
    - Поле "extracted_location" пиши СТРОГО на русском языке в именительном падеже.
      Например: "Әуезов көшесі" -> "улица Ауэзова", "Берекеде" -> "Береке".
    - Обоснования (reason) должны быть на 3 языках: русском, казахском и английском.

    Формат JSON (строго соблюдай):
    {{
      "category": "ЖКХ" | "Дороги" | "Транспорт" | "Экология" | "Безопасность" | "Мусор" | "Флуд",
      "base_threat_score": 0,
      "scope_score": 0,
      "extracted_location": "Название улицы/района строго на русском или null",
      "explanations": {{
        "ru": {{
          "base_threat_reason": "Сухое обоснование угрозы на русском (1 предложение).",
          "scope_reason": "Сухое обоснование масштаба на русском (1 предложение)."
        }},
        "kz": {{
          "base_threat_reason": "Қауіпті негіздеу қазақ тілінде (1 сөйлем).",
          "scope_reason": "Масштабты негіздеу қазақ тілінде (1 сөйлем)."
        }},
        "en": {{
          "base_threat_reason": "Dry threat justification in English (1 sentence).",
          "scope_reason": "Dry scope justification in English (1 sentence)."
        }}
      }},
      "trigger_words": ["слово1", "слово2"]
    }}

    Текст обращения: "{text}"
    """

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model='deepseek-chat',
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return extract_json_from_response(response.choices[0].message.content)
        except (openai.APIConnectionError, openai.APIStatusError) as e:
            if attempt < MAX_RETRIES - 1:
                print(f"Попытка {attempt + 1} не удалась, повтор через {RETRY_DELAY} сек...")
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                raise
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"Ошибка парсинга (попытка {attempt + 1}), повтор...")
                time.sleep(RETRY_DELAY)
            else:
                raise

def prepare_dataframe() -> pd.DataFrame:
    """Подготовка и инициализация DataFrame для работы."""
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Исходный файл {INPUT_FILE} не найден.")

    if not FORCE_REFRESH and os.path.exists(OUTPUT_FILE):
        print(f"Обнаружен {OUTPUT_FILE}. Возобновление работы...")
        df = pd.read_csv(OUTPUT_FILE)
        # Если старый OUTPUT_FILE от другой схемы (нет колонки text) — берём исходник заново
        if 'text' not in df.columns:
            print("Старый файл несовместим по схеме, беру исходный INPUT_FILE.")
            df = pd.read_csv(INPUT_FILE)
    else:
        print(f"Загрузка {INPUT_FILE} (полный пересчёт)...")
        df = pd.read_csv(INPUT_FILE)

    # Убедимся, что есть колонки date и source (app.py ожидает их)
    if 'date' not in df.columns:
        df['date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
    if 'source' not in df.columns:
        df['source'] = 'unknown'

    # Колонки строковые (включая мультиязычные reason)
    columns_str = [
        'category', 'extracted_location',
        'base_threat_reason_ru', 'scope_reason_ru',
        'base_threat_reason_kz', 'scope_reason_kz',
        'base_threat_reason_en', 'scope_reason_en',
        'trigger_words'
    ]
    # Колонки числовые
    columns_int = ['criticality_score', 'rep_bonus']

    for col in columns_str:
        if col not in df.columns:
            df[col] = "Не обработано"
        elif FORCE_REFRESH:
            df[col] = "Не обработано"

    for col in columns_int:
        if col not in df.columns:
            df[col] = 0
        elif FORCE_REFRESH:
            df[col] = 0

    return df

# ==========================================
# ЗАПУСК ПРОЦЕССА
# ==========================================
def main():
    try:
        client = init_client()
        df = prepare_dataframe()
    except Exception as e:
        print(f"Ошибка инициализации: {e}")
        return

    print("Запуск обработки инцидентов...")

    # Предварительный подсчёт локаций для оптимизации дедупликации
    location_counter = Counter()

    for index, row in df.iterrows():
        status = str(row.get('category', 'Не обработано')).strip()
        if status not in ["Не обработано", "Ошибка", "Ошибка API", "Ошибка JSON"]:
            # Уже обработано — добавляем локацию в счётчик для следующих строк
            loc = str(row.get('extracted_location', '')).strip().lower()
            if loc and loc not in ["nan", "none", "null", ""]:
                location_counter[loc] += 1
            continue

        print(f"[{index + 1}/{len(df)}] Анализ строки...")

        try:
            analysis = analyze_text(client, row['text'])

            # Извлечение базовых метрик
            loc = analysis.get("extracted_location")
            base_score = int(analysis.get("base_threat_score", 0))
            scope_score = int(analysis.get("scope_score", 0))

            # Расчет бонуса за массовость
            rep_bonus = calculate_repetition_bonus(loc, location_counter)
            total_score = min(base_score + scope_score + rep_bonus, 100)

            # Запись результатов
            df.at[index, 'category'] = str(analysis.get("category", "Флуд"))
            df.at[index, 'extracted_location'] = str(loc) if loc else ""
            df.at[index, 'criticality_score'] = total_score
            df.at[index, 'rep_bonus'] = rep_bonus

            # Мультиязычные объяснения
            explanations = analysis.get("explanations", {})
            for lang in ['ru', 'kz', 'en']:
                exp = explanations.get(lang, {})
                df.at[index, f'base_threat_reason_{lang}'] = str(exp.get("base_threat_reason", ""))
                df.at[index, f'scope_reason_{lang}'] = str(exp.get("scope_reason", ""))

            words = analysis.get("trigger_words", [])
            df.at[index, 'trigger_words'] = ", ".join(words) if isinstance(words, list) else ""

            # Обновляем счётчик локаций
            if loc:
                loc_clean = str(loc).strip().lower()
                if loc_clean not in ["nan", "none", "null", ""]:
                    location_counter[loc_clean] += 1

            # Задержка для соблюдения Rate Limits API
            time.sleep(1.5)

        except json.JSONDecodeError:
            print(f"Ошибка JSON (строка {index + 1}).")
            df.at[index, 'category'] = "Ошибка JSON"
        except openai.APIConnectionError:
            print("Нет соединения. Ожидание 15 секунд...")
            time.sleep(15)
        except openai.AuthenticationError:
            print("Ошибка 401: Неверный ключ. Остановка.")
            break
        except openai.APIStatusError as e:
            if e.status_code == 402:
                print("Ошибка 402: Баланс исчерпан. Остановка.")
                break
            elif e.status_code == 429:
                print("Ошибка 429: Лимит запросов. Ожидание 30 сек...")
                time.sleep(30)
            elif e.status_code >= 500:
                print(f"Ошибка сервера {e.status_code}. Ожидание 15 сек...")
                time.sleep(15)
            else:
                print(f"Ошибка API {e.status_code}.")
                df.at[index, 'category'] = "Ошибка API"
                time.sleep(5)
        except Exception as e:
            print(f"Непредвиденная ошибка (строка {index + 1}): {e}")
            df.at[index, 'category'] = "Ошибка"
            time.sleep(5)

        # Атомарное сохранение
        df.to_csv(OUTPUT_FILE, index=False)

    print(f"Готово. Файл: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()