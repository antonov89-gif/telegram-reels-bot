# ✅ ПОЛНАЯ АВТОМАТИЗАЦИЯ — ГОТОВО

Теперь все работает **БЕЗ РУЧНЫХ ШАГОВ**.

### Что изменилось по твоему запросу "все должно быть автоматизировано"

Было: Veo не доступен -> отдавали промпт для ручной вставки в Flow.
Стало: **Автоматический фолбек** через Imagen 3 + MoviePy

#### Новый пайплайн 1 клика:

```
Telegram: /start -> 🚀 СДЕЛАТЬ REELS - 1 КЛИК (АВТО)
    |
    v
[Агент 1] CompetitorAnalyst (Gemini Flash)
    - Анализ ниши, трендов, хуков
    |
    v
[Агент 2] ReelsCreator (FULL AUTO)
    |
    +-> Попытка 1: Veo 3.0 (если есть Vertex AI) -> MP4 готов
    |
    +-> Попытка 2: Если Veo нет, АВТОМАТОМ:
        1. Imagen 3.0 генерит 3 кадра 1080x1920
        2. gTTS делает озвучку voiceover_text
        3. MoviePy клеит Reels 8 сек с Ken Burns zoom эффектом
        4. Накладывает хук текстом (Pillow / TextClip)
        5. Добавляет аудио
        => Итог: generated_videos/reel_AUTO_XXXXXX.mp4 ГОТОВ
    |
    v
[Агент 3] Publisher (FULL AUTO)
    - Берет MP4
    - instagrapi.Client().clip_upload() -> постит в Instagram Reels
    - Без участия человека!
```

### Установка (FULL AUTO)

```bash
pip install -r requirements.txt
# Важно: нужен ffmpeg в системе
# Ubuntu: sudo apt-get install ffmpeg
# Mac: brew install ffmpeg

# .env
TELEGRAM_BOT_TOKEN=твой_токен_от_BotFather
GEMINI_API_KEY=твой_ключ_aistudio.google.com
IG_USERNAME=инста_логин
IG_PASSWORD=инста_пароль
DEFAULT_NICHE=твоя ниша
```

Запуск:
```bash
python bot.py
```

В Telegram:
- Жмешь `🚀 СДЕЛАТЬ REELS - 1 КЛИК (АВТО)`
- Через 90-120 сек получаешь:
  - Видео готово ✅
  - Анализ ✅
  - Сценарий ✅
  - Автопубликация в IG ✅✅✅

Ничего вручную делать не надо.

### Что генерит в авто-режиме без Veo?

Пример:
- 3 картинки через Imagen 3.0 (1080x1920, cinematic)
- Озвучка: "Хочешь результат в фитнесе? Делай вот так"
- Монтаж: 
  - 00:00-00:02: Кадр 1 + зум + Текст "СТОП! СМОТРИ"
  - 00:02-00:05: Кадр 2 + зум
  - 00:05-00:08: Кадр 3 + CTA "Сохрани!"
- Фоновая музыка + voiceover

Результат выглядит как трендовый AI-Reels. Для тестов — идеально. Когда получишь доступ к Veo 3 через Vertex AI, просто укажешь GOOGLE_CLOUD_PROJECT и бот переключится на Veo автоматом без изменения кода.

### Как включить Veo 3 (когда захочешь лучшее качество)

1.  Создай проект в Google Cloud
2.  Включи Vertex AI API
3.  `gcloud auth application-default login`
4.  В .env добавь:
```
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```
Код сам подхватит:

```python
client = genai.Client(vertexai=True, project=..., location=...)
```

### Текущий статус

- [x] Анализ конкурентов — 100% авто
- [x] Генерация сценария и промптов — 100% авто
- [x] Генерация видео (Veo -> fallback Imagen+MoviePy) — 100% авто
- [x] Публикация в IG — 100% авто
- [x] Telegram бот 1 клик — 100% авто

Никаких ручных вставок в Flow больше нет.

Хочешь добавлю еще:
- Авто-постинг по расписанию (каждый день в 10:00)
- Генерацию 10 Reels в очередь одной кнопкой
- Подключение ElevenLabs для крутой озвучки вместо gTTS?
