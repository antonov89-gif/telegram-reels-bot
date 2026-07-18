"""
Telegram бот на чистом requests — работает на Python 3.13 без проблем
ПОЛНАЯ АВТОМАТИЗАЦИЯ
"""
import os
import time
import json
import asyncio
import requests
from dotenv import load_dotenv
load_dotenv()

from config import TELEGRAM_BOT_TOKEN, DEFAULT_NICHE, DEFAULT_STYLE
from agents.orchestrator import ReelsOrchestrator

DB_FILE = "users_db.json"
API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

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
        "auto_publish": True
    })

def set_user_settings(user_id, settings):
    db = load_db()
    db[str(user_id)] = settings
    save_db(db)

orchestrator = ReelsOrchestrator()

def send_message(chat_id, text, reply_markup=None, parse_mode=""):
    url = f"{API_URL}/sendMessage"
    # Убираем Markdown чтобы не было ошибок парсинга
    data = {
        "chat_id": chat_id,
        "text": text,
    }
    if parse_mode:
        data["parse_mode"] = parse_mode
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    try:
        r = requests.post(url, data=data, timeout=10)
        res = r.json()
        if not res.get("ok"):
            print(f"Telegram API error: {res}")
            # Пробуем без parse_mode и без разметки
            if "parse_mode" in data:
                del data["parse_mode"]
                r2 = requests.post(url, data=data, timeout=10)
                print(f"Retry without parse_mode: {r2.json()}")
                return r2.json()
        return res
    except Exception as e:
        print(f"Send message error: {e}")
        import traceback
        traceback.print_exc()
        return None

def send_video(chat_id, video_path, caption=""):
    url = f"{API_URL}/sendVideo"
    try:
        with open(video_path, 'rb') as f:
            files = {"video": f}
            data = {"chat_id": chat_id, "caption": caption[:1024]}
            r = requests.post(url, files=files, data=data, timeout=60)
            print(f"Send video result: {r.status_code}")
            return r.json()
    except Exception as e:
        print(f"Send video error: {e}")
        return None

def handle_start(chat_id, user_id):
    settings = get_user_settings(user_id)
    keyboard = {
        "inline_keyboard": [
            [{"text": "🚀 СДЕЛАТЬ REELS - 1 КЛИК (АВТО)", "callback_data": "one_click_auto"}],
            [{"text": "🎬 Только сгенерить (без публикации)", "callback_data": "one_click"}],
            [{"text": "🔍 Анализ конкурентов", "callback_data": "analyze"}],
            [{"text": "⚙️ Настройки ниши", "callback_data": "settings"}],
        ]
    }
    text = f"""
👋 Готов к полной автоматизации!

Твоя ниша: {settings['niche']}
Конкуренты: {', '.join(settings.get('competitors', [])) or 'авто-поиск топов'}

Жми 🚀 1 КЛИК АВТО и я сделаю все сам за 2 минуты!

Бот: @VideoKsu222_bot — работает на 100% автомате (Gemini 3.5 Flash + Imagen fallback + MoviePy)
"""
    send_message(chat_id, text, reply_markup=keyboard)

async def handle_one_click(chat_id, user_id, auto_publish=True):
    settings = get_user_settings(user_id)
    
    send_message(chat_id, f"🚀 ЗАПУСТИЛ ПОЛНУЮ АВТОМАТИЗАЦИЮ...\n\nНиша: {settings['niche']}\n\n1. Анализирую конкурентов...\n2. Генерю видео...\n3. {'Сам опубликую в IG' if auto_publish else 'Пришлю тебе'}\n\nНе закрывай чат, это 1.5-2 минуты.")

    try:
        async def progress(msg):
            send_message(chat_id, msg)

        result = await orchestrator.run_one_click_pipeline(
            niche=settings["niche"],
            competitors=settings.get("competitors", []),
            style=settings.get("style", DEFAULT_STYLE),
            progress_callback=progress
        )

        concept = result["concept"]
        video = result["video"]
        analysis = result["analysis"]

        full_report = f"""
🎬 ГОТОВО! МЕТОД: {video['method']}

Название: {concept['title']}
Хук: {concept['hook']}

Сценарий: {concept['script'][:300]}

Подпись: {concept['caption'][:500]}

Тренды: {', '.join(analysis.get('trends', [])[:3])}
Видео: {video.get('path')}
"""

        # Отправляем видео
        if video["success"] and video.get("path") and os.path.exists(video["path"]):
            send_message(chat_id, f"✅ Видео готово! Метод: {video['method']}\nСейчас отправлю файл...")
            send_video(chat_id, video["path"], caption=f"{concept['title']}\n{concept['hook']}")
            send_message(chat_id, full_report, parse_mode="")

            if auto_publish and os.getenv("IG_USERNAME"):
                send_message(chat_id, "📤 Автопубликация в Instagram...")
                pub = await orchestrator.publish_auto(video["path"], concept["caption"])
                if pub["success"]:
                    send_message(chat_id, f"✅ ОПУБЛИКОВАНО В INSTAGRAM!\nID: {pub.get('media_id')}")
                else:
                    send_message(chat_id, f"⚠️ Ошибка публикации: {pub['error']}")
        else:
            send_message(chat_id, f"❌ Видео не создалось: {video.get('error')}\n{full_report}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        send_message(chat_id, f"❌ Ошибка: {e}")

async def handle_analyze(chat_id, user_id):
    settings = get_user_settings(user_id)
    send_message(chat_id, f"🔍 Анализирую нишу '{settings['niche']}' через Gemini 3.5...")
    try:
        analysis = await orchestrator.analyst.analyze(settings['niche'], settings.get('competitors', []))
        text = f"📊 Анализ: {settings['niche']}\n\n🔥 Тренды: {', '.join(analysis.get('trends', []))}\n🪝 Хуки: {', '.join(analysis.get('top_hooks', [])[:5])}\n\n💡 Идеи:\n"
        for i, rec in enumerate(analysis.get('recommendations', [])[:3], 1):
            text += f"\n{i}. {rec.get('idea')} -> Хук: {rec.get('hook')}"
        text += f"\n\n#️⃣ { ' '.join(analysis.get('hashtags', [])[:10])}"
        send_message(chat_id, text[:4000], parse_mode="")
    except Exception as e:
        send_message(chat_id, f"Ошибка анализа: {e}")

def handle_settings_prompt(chat_id):
    send_message(chat_id, "⚙️ Напиши нишу и конкурентов так:\n\nниша | @конк1, @конк2\n\nПример:\nфитнес для мам | @mama_fit, @fit\n\nИли просто: крипта для новичков", parse_mode="")

def handle_text_settings(chat_id, user_id, text):
    if "|" in text:
        niche, comps = text.split("|", 1)
        competitors = [c.strip() for c in comps.split(",") if c.strip()]
    else:
        niche = text
        competitors = []
    settings = get_user_settings(user_id)
    settings["niche"] = niche.strip()
    settings["competitors"] = competitors
    set_user_settings(user_id, settings)
    send_message(chat_id, f"✅ Сохранил!\n\nНиша: {settings['niche']}\nКонкуренты: {', '.join(competitors) if competitors else 'авто'}\n\nЖми /start для 1 клика")

def polling():
    print("🚀 Запускаю SIMPLE бота (requests) — совместим с Python 3.13")
    print(f"Бот: @VideoKsu222_bot Token OK")
    offset = 0
    while True:
        try:
            url = f"{API_URL}/getUpdates"
            params = {"offset": offset, "timeout": 30}
            resp = requests.get(url, params=params, timeout=35)
            data = resp.json()
            if not data.get("ok"):
                print(f"getUpdates error: {data}")
                time.sleep(2)
                continue
            
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                
                # Message
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    user_id = msg["from"]["id"]
                    text = msg.get("text", "")

                    print(f"Message from {user_id}: {text[:50]}")

                    if text.startswith("/start"):
                        handle_start(chat_id, user_id)
                    elif text.startswith("/settings"):
                        handle_settings_prompt(chat_id)
                    elif text.startswith("/"):
                        handle_start(chat_id, user_id)
                    else:
                        # Считаем что это настройки ниши
                        if len(text) > 2:
                            handle_text_settings(chat_id, user_id, text)

                # Callback query (кнопки)
                if "callback_query" in update:
                    cb = update["callback_query"]
                    chat_id = cb["message"]["chat"]["id"]
                    user_id = cb["from"]["id"]
                    data_cb = cb.get("data", "")

                    print(f"Callback {user_id}: {data_cb}")

                    # Отвечаем на callback чтобы убрать часики
                    requests.post(f"{API_URL}/answerCallbackQuery", data={
                        "callback_query_id": cb["id"]
                    })

                    if data_cb in ["one_click_auto", "one_click"]:
                        asyncio.run(handle_one_click(chat_id, user_id, auto_publish=(data_cb=="one_click_auto")))
                    elif data_cb == "analyze":
                        asyncio.run(handle_analyze(chat_id, user_id))
                    elif data_cb == "settings":
                        handle_settings_prompt(chat_id)

        except Exception as e:
            print(f"Polling error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)

if __name__ == "__main__":
    polling()
