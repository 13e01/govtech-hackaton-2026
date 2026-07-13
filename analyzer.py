import os
import json
import time
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# 1. Определение схемы ответа для гарантии валидного JSON
class CityMessageAnalysis(BaseModel):
    category: str = Field(description="Категория сообщения: ЖКХ, Дороги, Общественный транспорт, Экология, Безопасность, Мусор, Флуд")
    is_critical: bool = Field(description="Критичность ситуации (true или false)")
    explanation: str = Field(description="Сухой текст обоснования нарушения в 1-2 предложениях")

# Инициализация клиента
API_KEY = "AQ.Ab8RN6KAb67KNF4-PftpLO7Fsn9a1FdovLO7blcPJlGFZcujTw"
client = genai.Client(api_key=API_KEY)

def analyze_text(text: str) -> CityMessageAnalysis:
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

    Текст сообщения: "{text}"
    """
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CityMessageAnalysis, 
        ),
    )
    # SDK автоматически парсит JSON в Pydantic-объект
    return response.parsed

def main():
    print("⏳ Запуск скрипта анализа сообщений (Петропавловск)")
    
    input_file = "city_messages.csv"
    output_file = "analyzed_city_messages.csv"
    
    # Загружаем существующий прогресс, если скрипт упал ранее
    if os.path.exists(output_file):
        df = pd.read_csv(output_file)
        print(f"📦 Найден файл прошлым запуском. Загружено строк: {len(df)}")
    else:
        df = pd.read_csv(input_file)
        
    # Надежная инициализация колонок
    for col in ['category', 'is_critical', 'explanation']:
        if col not in df.columns:
            df[col] = False if col == 'is_critical' else "Не обработано"

    total_rows = len(df)

    for index, row in df.iterrows():
        # Пропускаем то, что уже успешно обработано
        if row['category'] not in ["Не обработано", "Ошибка"] and pd.notna(row['category']):
            continue
            
        print(f"[{index + 1}/{total_rows}] Анализ текста...")
        
        attempts = 3
        while attempts > 0:
            try:
                # Отправляем текст на анализ
                analysis = analyze_text(str(row['text']))
                
                # Запись результатов из типизированного объекта
                df.at[index, 'category'] = analysis.category
                df.at[index, 'is_critical'] = analysis.is_critical
                df.at[index, 'explanation'] = analysis.explanation
                
                time.sleep(2)  # Базовый интервал между запросами
                break  # Успешно обработано, выходим из цикла попыток
                
            except Exception as e:
                attempts -= 1
                print(f"⚠️ Ошибка на строке {index + 1}: {e}")
                
                if attempts > 0:
                    print("⏱ Поймали лимит или сбой. Ждем 60 секунд перед повтором этой же строки...")
                    time.sleep(60)
                else:
                    print("❌ 3 попытки исчерпаны. Маркируем строку как Ошибка.")
                    df.at[index, 'category'] = "Ошибка"
            
        # Инкрементальное сохранение прогресса в файл
        df.to_csv(output_file, index=False)

    print(f"\n✅ Обработка завершена! Результаты сохранены в: {output_file}")

if __name__ == "__main__":
    main()