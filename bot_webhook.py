"""
Webhook версия бота для 24/7 хостинга на Render / Railway / Fly.io
Работает постоянно, без ограничений песочницы
"""
import os
import asyncio
from flask import Flask, request
from dotenv import load_dotenv
load_dotenv()

from config import TELEGRAM_BOT_TOKEN, DEFAULT_NICHE, DEFAULT_STYLE
from agents.orchestrator import ReelsOrchestrator
import json, requests

app = Flask(__name__)
orchestrator = ReelsOrchestrator()

API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
DB_FILE = "users_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_settings(user_id):
    db = load_db()
    return db.get(str(user_id), {
        "niche": DEFAULT_NICHE,
        "style": DEFAULT_STYLE,
        "competitors": [],
    })

def set_user_settings(user_id, settings):
    db = load_db()
    db[str(user_id)] = settings
    save_db(db)

def send_message(chat_id, text, reply_markup=None):
    url = f"{API_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    try:
        r = requests.post(url, data=data, timeout=10)
        return r.json()
    except Exception as e:
        print(f"Send error: {e}")
        return None

def send_video(chat_id, video_path, caption=""):
    url = f"{API_URL}/sendVideo"
    try:
        with open(video_path, 'rb') as f:
            files = {"video": f}
            data = {"chat_id": chat_id, "caption": caption[:1024]}
            r = requests.post(url, files=files, data=data, timeout=60)
            print(f"Send video {r.status_code}")
            return r.json()
    except Exception as e:
        print(f"Video error: {e}")
        return None

@app.route('/')
def index():
    return "✅ Reels Bot is running 24/7 — @VideoKsu222_bot — Beautiful Flux mode"

@app.route(f'/webhook/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    update = request.get_json()
    print(f"Webhook update: {update}")

    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        user_id = msg["from"]["id"]
        text = msg.get("text", "")

        if text.startswith("/start"):
            settings = get_user_settings(user_id)
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🚀 СДЕЛАТЬ REELS - 1 КЛИК (КРАСИВО)", "callback_data": "one_click_auto"}],
                    [{"text": "🎬 Только сгенерить", "callback_data": "one_click"}],
                    [{"text": "🔍 Анализ конкурентов", "callback_data": "analyze"}],
                ]
            }
            send_message(chat_id, f"👋 Привет! Я на 24/7 хостинге!\nНиша: {settings['niche']}\nЖми 1 КЛИК и я сделаю КРАСИВЫЙ Reels через Flux + MoviePy за 2 мин", reply_markup=keyboard)
        elif text.startswith("/settings"):
            send_message(chat_id, "Напиши нишу так: фитнес | @конк1, @конк2")
        elif not text.startswith("/"):
            # Сохраняем нишу
            if "|" in text:
                niche, comps = text.split("|", 1)
                competitors = [c.strip() for c in comps.split(",")]
            else:
                niche = text
                competitors = []
            settings = get_user_settings(user_id)
            settings["niche"] = niche.strip()
            settings["competitors"] = competitors
            set_user_settings(user_id, settings)
            send_message(chat_id, f"✅ Сохранил нишу: {settings['niche']}")

    if "callback_query" in update:
        cb = update["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        user_id = cb["from"]["id"]
        data = cb.get("data", "")

        # Убираем часики
        requests.post(f"{API_URL}/answerCallbackQuery", data={"callback_query_id": cb["id"]})

        if data in ["one_click_auto", "one_click"]:
            auto = data == "one_click_auto"
            settings = get_user_settings(user_id)
            send_message(chat_id, f"🚀 Запустил генерацию красивого Reels для ниши {settings['niche']}... 90-120 сек")

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def run():
                result = await orchestrator.run_one_click_pipeline(
                    niche=settings["niche"],
                    competitors=settings.get("competitors", []),
                    style=settings.get("style", DEFAULT_STYLE),
                    progress_callback=None
                )
                concept = result["concept"]
                video = result["video"]
                if video["success"] and os.path.exists(video["path"]):
                    send_message(chat_id, f"✅ Готово! {concept['title']}\nХук: {concept['hook']}\nСейчас отправлю видео...")
                    send_video(chat_id, video["path"], caption=f"{concept['title']}\n{concept['hook']}\n\n{concept['caption'][:500]}")
                else:
                    send_message(chat_id, f"❌ Ошибка: {video.get('error')}")

            loop.run_until_complete(run())

        elif data == "analyze":
            settings = get_user_settings(user_id)
            send_message(chat_id, f"🔍 Анализирую {settings['niche']}...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            async def ana():
                analysis = await orchestrator.analyst.analyze(settings['niche'], settings.get('competitors', []))
                txt = f"Тренды: {', '.join(analysis.get('trends', []))}\nХуки: {', '.join(analysis.get('top_hooks', [])[:5])}"
                send_message(chat_id, txt[:4000])
            loop.run_until_complete(ana())

    return "ok"

if __name__ == "__main__":
    # Для Render: порт из переменной PORT
    port = int(os.getenv("PORT", 10000))
    print(f"🚀 Webhook bot listening on port {port} — 24/7 mode")
    # Устанавливаем webhook автоматически если есть URL
    webhook_url = os.getenv("WEBHOOK_URL")  # например https://your-app.onrender.com/webhook/TOKEN
    if webhook_url:
        print(f"Setting webhook to {webhook_url}")
        requests.get(f"{API_URL}/setWebhook?url={webhook_url}")
    app.run(host="0.0.0.0", port=port)
