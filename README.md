# 🚀 Telegram Reels Bot — 3 AI-агента + Gemini Veo 3

Бот делает Reels в **1 клик** из Telegram:
1.  **Агент-Аналитик** (Gemini 1.5 Flash) — анализирует конкурентов в твоей нише
2.  **Агент-Креатор** (Gemini + Veo 3) — пишет вирусный сценарий и генерит видео 9:16
3.  **Агент-Паблишер** — отправляет тебе и публикует в Instagram

### Как работает в Telegram
```
/start -> 🚀 Сделать Reels в 1 КЛИК
```
Бот:
- 🔍 Анализирует
- 🎬 Генерит концепт + промпт
- 🎥 Генерит видео через Veo 3 (или отдает промпт для Flow)
- 📤 Отправляет готовый Reels с подписью и хештегами

### Установка

1.  Создай бота у @BotFather, получи токен
2.  Получи Gemini API Key: https://aistudio.google.com/app/apikey
3.  Для Veo 3 нужен доступ: https://labs.google/fx/tools/flow (пока в preview, нужен Google Cloud проект с включенным Vertex AI)

```bash
git clone ...
cd telegram-reels-bot
pip install -r requirements.txt

cp .env.example .env
# заполни .env

python bot.py
```

### .env обязательно:
```
TELEGRAM_BOT_TOKEN=...
GEMINI_API_KEY=...
```

### Доступ к Veo 3

Google Veo 3 сейчас доступен через:
- **google-genai SDK** -> `veo-3.0-generate-001` (нужен платный GCP проект)
- **Flow** (labs.google) — если SDK вернет ошибку, бот отдаст готовый промпт, ты вставляешь его в Flow и получаешь видео за 60 сек

В коде уже реализован fallback на это.

### Автопубликация в Instagram

2 варианта:
1.  **Graph API** (официальный) — нужен бизнес-аккаунт FB + IG_USER_ID + IG_ACCESS_TOKEN
2.  **instagrapi** — логин/пароль в .env, бот сам загрузит через `clip_upload()`

### Структура
```
bot.py - Telegram бот, кнопки
agents/
  competitor_analyst.py - Агент 1
  reels_creator.py - Агент 2 (Veo)
  publisher.py - Агент 3
  orchestrator.py - Связывает всех в 1 клик
config.py
```

### Кастомизация под нишу

В Telegram напиши:
```
крипта | @banksta, @cryptonews
```
или
```
фитнес для девушек
```

Бот запомнит и будет генерить под эту нишу.

### Что дальше можно добавить
- Очередь задач (Celery / RQ)
- Планировщик постинга
- Анализ Reels через Instagram Basic Display API
- Голосовая озвучка через ElevenLabs
- Субтитры auto через Whisper

Хочешь, добавлю деплой на сервер / Docker?
