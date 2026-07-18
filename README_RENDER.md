# Deploy to Render — 24/7 Bot in 1 click

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/antonov89-gif/telegram-reels-bot)

## Что нужно вставить при деплое:
- TELEGRAM_BOT_TOKEN: твой токен от @BotFather
- GEMINI_API_KEY: ключ с aistudio.google.com
- WEBHOOK_URL: будет https://твое-имя.onrender.com/webhook/ТОКЕН

После деплоя бот сам вызовет setWebhook и будет 24/7.

## Проверка
curl https://твое-приложение.onrender.com/
Должно вернуть: "✅ Reels Bot is running 24/7"

Потом в Telegram: /start -> бот отвечает всегда.
