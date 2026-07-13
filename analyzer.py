import os
import json
import time
import pandas as pd
import openai
from openai import OpenAI

API_KEY = "your_deepseek_api_key_here" 
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

def analyze_text(text):
    prompt = f"""
    Ты — ведущий аналитик Ситуационного центра города Петропавловск. Твой стиль — предельно строгий, сухой, официально-деловой.
    Классифицируй текстовое сообщение.

    ПРАВИЛА ДЛЯ КРИТИЧЕСКИХ СИТУАЦИЙ (is_critical = true):
    - Прямая угроза жизни, здоровью, безопасности (оголенные провода, открытые люки, запах газа).
    - Системные аварии ЖКХ без предупреждения (прорыв теплотрассы, отсутствие тепла зимой, полное отключение воды).

    ПРАВИЛА ДЛЯ СТАНДАРТНЫХ СИТУАЦИЙ И ФЛУДА (is_critical = false):
    - Локальные бытовые жалобы (мусор во дворе, не работает валидатор в автобусе, яма во дворе).
    - Объявления, реклама, спам, обсуждения общего характера (категория "Флуд").

    ЖЕСТКИЕ ТРЕБОВАНИЯ К СТИЛЮ ПОЛЯ "explanation" (КРИТИЧЕСКИ ВАЖНО):
    1. ИСКЛЮЧИ любой ИИ-мусор и вводные маркеры.
    2. Пиши сухо, коротко (1-2 предложения). Начинай СРАЗУ с факта нарушения.

    Верни ответ СТРОГО в формате JSON-объекта:
    {{
      "category": "ЖКХ" или "Дороги" или "Общественный транспорт" или "Экология" или "Безопасность" или "Мусор" или "Флуд",
      "is_critical": true или false,
      "explanation": "Сухой текст обоснования."
    }}

    Текст сообщения: "{text}"
    """
    
    response = client.chat.completions.create(
        model='deepseek-chat',
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    raw_text = response.choices[0].message.content.strip()
    
    if raw_text.startswith("```"):
        lines = raw_text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        raw_text = "\n".join(lines).strip()
        if raw_text.startswith("json"):
            raw_text = raw_text[4:].strip()

    return json.loads(raw_text)

def main():
    print("Запуск скрипта анализа сообщений через DeepSeek API...")
    
    input_file = "city_messages.csv"
    output_file = "analyzed_city_messages.csv"
    
    if os.path.exists(output_file):
        print(f"Найден файл прошлым запуском: {output_file}. Продолжение обработки...")
        df = pd.read_csv(output_file)
    else:
        if not os.path.exists(input_file):
            print(f"Ошибка: Файл {input_file} не найден.")
            return
        df = pd.read_csv(input_file)
        
    for col in ['category', 'explanation']:
        if col not in df.columns:
            df[col] = "Не обработано"
    if 'is_critical' not in df.columns:
        df['is_critical'] = False

    for index, row in df.iterrows():
        current_status = str(row.get('category')).strip()
        if current_status != "Не обработано" and current_status != "Ошибка" and pd.notna(row.get('category')):
            continue
            
        print(f"[{index + 1}/{len(df)}] Анализ...")
        
        try:
            analysis = analyze_text(row['text'])
            df.at[index, 'category'] = analysis.get("category", "Флуд")
            df.at[index, 'is_critical'] = analysis.get("is_critical", False)
            df.at[index, 'explanation'] = analysis.get("explanation", "")
            
            time.sleep(1.5) 
            
        except json.JSONDecodeError:
            print(f"Ошибка парсинга JSON (строка {index + 1}). Пропуск.")
            df.at[index, 'category'] = "Ошибка JSON"
            df.at[index, 'explanation'] = "Модель вернула некорректный формат."
            
        except openai.APIConnectionError:
            print("Ошибка сети: Нет соединения с сервером. Ожидание 15 секунд...")
            time.sleep(15)
            df.at[index, 'category'] = "Не обработано"
            
        except openai.AuthenticationError:
            print("Ошибка 401: Неверный API_KEY. Работа скрипта остановлена.")
            break
            
        except openai.APIStatusError as e:
            status_code = e.status_code
            
            if status_code == 402:
                print("Ошибка 402: Недостаточно средств на балансе (Insufficient Balance). Работа скрипта остановлена.")
                break
                
            elif status_code == 429:
                print("Ошибка 429: Превышен лимит запросов (Rate Limit). Ожидание 30 секунд...")
                time.sleep(30)
                df.at[index, 'category'] = "Не обработано"
                
            elif status_code >= 500:
                print(f"Ошибка сервера {status_code}. Ожидание 15 секунд...")
                time.sleep(15)
                df.at[index, 'category'] = "Не обработано"
                
            else:
                print(f"Ошибка API {status_code}: {e.message}")
                df.at[index, 'category'] = "Ошибка API"
                time.sleep(5)
                
        except Exception as e:
            print(f"Непредвиденная ошибка (строка {index + 1}): {e}")
            df.at[index, 'category'] = "Ошибка"
            time.sleep(5)
            
        df.to_csv(output_file, index=False)

    print(f"Обработка завершена. Результаты сохранены в {output_file}.")

if __name__ == "__main__":
    main()