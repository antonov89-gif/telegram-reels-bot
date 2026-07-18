# СТАРТ — Создаем бота по шагам (5 минут)

## Шаг 1: Telegram Bot (1 минута)
1. Открой Telegram -> @BotFather
2. Напиши `/newbot`
3. Имя: `Reels Factory Bot`
4. Юзернейм: `tvoi_reels_bot` (любой свободный)
5. Скопируй токен вида `123456:AAH...` — это `TELEGRAM_BOT_TOKEN`

## Шаг 2: Gemini API Key (1 минута)
1. Иди на https://aistudio.google.com/app/apikey
2. Create API Key -> Скопируй `AIzaSy...`
3. Это `GEMINI_API_KEY` — с ним уже работает ПОЛНЫЙ АВТОМАТ (Imagen 3 + MoviePy)

Для Veo 3 (опционально, позже):
- Нужен Google Cloud проект + Vertex AI API enabled
- Бот и без него работает на 100% автомате через Imagen fallback

## Шаг 3: Instagram (1 минута)
Для автопостинга:
- Логин и пароль от Instagram (аккаунт должен быть не под 2FA или добавь в исключения)
- Это `IG_USERNAME` + `IG_PASSWORD`

Альтернатива для бизнес-аккаунтов — Graph API, но начнем с instagrapi.

## Шаг 4: Установка у меня (уже готово)

Проект уже собран. Тебе нужно только заполнить `.env`:

```
TELEGRAM_BOT_TOKEN=123456:AAH...
GEMINI_API_KEY=AIzaSy...
IG_USERNAME=...
IG_PASSWORD=...
DEFAULT_NICHE=твоя ниша, например: фитнес для мам
DEFAULT_STYLE=динамичный, вирусный, 9:16
```

## Шаг 5: Запуск

```bash
pip install -r requirements.txt
python bot.py
```

Или:
```bash
./run.sh
```

Зашел в своего бота в Telegram -> /start -> 🚀 1 КЛИК АВТО -> через 2 минуты получаешь видео + оно улетает в Instagram.

---

## Что дальше делаю я для тебя:

1.  Запущу тест пайплайна без Telegram (quick_start.py) — проверим что Gemini и генерация видео работает
2.  Настрою .env из твоих токенов
3.  Запущу бота

Скинь мне:
- TELEGRAM_BOT_TOKEN
- GEMINI_API_KEY
- IG_USERNAME / IG_PASSWORD (если хочешь автопостинг сейчас, или пропустим)
