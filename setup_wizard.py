"""
Мастер настройки — создает .env пошагово
"""
import os

print("🧙‍♂️ МАСТЕР НАСТРОЙКИ Reels Bot — ПОЛНАЯ АВТОМАТИЗАЦИЯ")
print("="*60)
print("Я создам тебе .env файл. Просто вставляй токены.")
print("Можешь пропустить IG — потом добавишь.")
print()

def ask(prompt, default=""):
    val = input(f"{prompt} [{default}]: ").strip()
    return val or default

if os.path.exists(".env"):
    print("⚠️ .env уже существует. Перезаписать? (y/N)")
    if input().lower() != 'y':
        print("Отмена")
        exit()

telegram = ask("1. TELEGRAM_BOT_TOKEN от @BotFather (123456:AAH...)")
gemini = ask("2. GEMINI_API_KEY с aistudio.google.com (AIzaSy...)")
ig_user = ask("3. IG_USERNAME (логин инсты, можно пропустить)", "")
ig_pass = ask("4. IG_PASSWORD (пароль инсты, можно пропустить)", "")
niche = ask("5. DEFAULT_NICHE (твоя ниша)", "бизнес, мотивация, саморазвитие")
style = ask("6. DEFAULT_STYLE", "динамичный, вирусный, вертикальный 9:16, субтитры")

env_content = f"""TELEGRAM_BOT_TOKEN={telegram}
GEMINI_API_KEY={gemini}
GEMINI_MODEL_TEXT=gemini-1.5-flash
GEMINI_MODEL_VIDEO=veo-3.0-generate-001

IG_USERNAME={ig_user}
IG_PASSWORD={ig_pass}

DEFAULT_NICHE={niche}
DEFAULT_STYLE={style}

BOT_ADMIN_ID=
"""

with open(".env", "w", encoding="utf-8") as f:
    f.write(env_content)

print("\n✅ .env создан!")
print("Проверка...")
from dotenv import load_dotenv
load_dotenv()
import config
print(f"✅ Telegram token: {'есть' if config.TELEGRAM_BOT_TOKEN else 'НЕТ'}")
print(f"✅ Gemini key: {'есть' if config.GEMINI_API_KEY else 'НЕТ'}")
print(f"✅ IG: {config.IG_USERNAME or 'не задан (ок, добавим позже)'}")
print()
print("Следующий шаг: python quick_start.py — тест генерации")
print("Или: python bot.py — запуск Telegram бота")
