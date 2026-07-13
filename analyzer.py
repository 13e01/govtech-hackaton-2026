import pandas as pd
from google import genai
from google.genai import types
import json
import time

API_KEY = "AQ.Ab8RN6KAb67KNF4-PftpLO7Fsn9a1FdovLO7blcPJlGFZcujTw"
client = genai.Client(api_key=API_KEY)

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
    
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return json.loads(response.text.strip())

def main():
    print("⏳ Запуск скрипта")
    df = pd.read_csv("city_messages.csv")
    
    # Сразу создаем колонки
    if 'category' not in df.columns:
        df['category'] = "Не обработано"
        df['is_critical'] = False
        df['explanation'] = ""
    
    output_file = "analyzed_city_messages.csv"

    for index, row in df.iterrows():
        # Если строка уже обработана при прошлом запуске — пропускаем
        if row.get('category') != "Не обработано" and pd.notna(row.get('category')):
            continue
            
        print(f"[{index + 1}/{len(df)}] Анализ...")
        
        try:
            analysis = analyze_text(row['text'])
            df.at[index, 'category'] = analysis.get("category", "Флуд")
            df.at[index, 'is_critical'] = analysis.get("is_critical", False)
            df.at[index, 'explanation'] = analysis.get("explanation", "")
            
            # Ждем 3 секунды, чтобы не словить бан по лимитам API
            time.sleep(3) 
            
        except Exception as e:
            print(f"⚠️ Ошибка на строке {index + 1}: {e}.")
            print("Ждем 60 секунд для сброса квоты...")
            df.at[index, 'category'] = "Ошибка"
            time.sleep(60)
            
        # СОХРАНЕНИЕ ПОСЛЕ КАЖДОЙ СТРОКИ. 
        # Если ты прервешь скрипт (Ctrl+C), данные уже будут в файле.
        df.to_csv(output_file, index=False)

    print(f"\n✅ Готово! Файл {output_file} можно отдавать на фронт.")

if __name__ == "__main__":
    main()