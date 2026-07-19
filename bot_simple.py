"""
Telegram бот UJC Creator — ПОЛНАЯ СХЕМА:
1. Анализирует конкурентов (ksusha.prettycutie)
2. Генерит промпт для Veo Pro — ты делаешь видео сам в Gemini Pro
3. Ты кидаешь готовое видео в бота → бот спрашивает артикул WB
4. Автопостинг по расписанию 10:00,15:00,19:00 МСК с вжиганием артикула
"""
import os, time, json, asyncio, requests, threading
from datetime import datetime
import pytz
from dotenv import load_dotenv
load_dotenv()

from config import TELEGRAM_BOT_TOKEN, DEFAULT_NICHE, DEFAULT_STYLE
from agents.orchestrator import ReelsOrchestrator

DB_FILE = "users_db.json"
QUEUE_FILE = "queue.json"
API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Расписание автопостинга МСК
POST_TIMES = ["10:00", "15:00", "19:00"]  # МСК

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
        "competitors": ["@ksusha.prettycutie"],
        "auto_publish": True,
        "state": None,
        "pending_video": None
    })

def set_user_settings(user_id, settings):
    db = load_db()
    db[str(user_id)] = settings
    save_db(db)

def load_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_queue(q):
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(q, f, ensure_ascii=False, indent=2)

orchestrator = ReelsOrchestrator()

def send_message(chat_id, text, reply_markup=None):
    url = f"{API_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    try:
        r = requests.post(url, data=data, timeout=15)
        res = r.json()
        if not res.get("ok"):
            print(f"Telegram API error: {res}")
        return res
    except Exception as e:
        print(f"Send error: {e}")
        return None

def send_video(chat_id, video_path, caption=""):
    url = f"{API_URL}/sendVideo"
    try:
        with open(video_path, 'rb') as f:
            files = {"video": f}
            data = {"chat_id": chat_id, "caption": caption[:1024]}
            r = requests.post(url, files=files, data=data, timeout=90)
            print(f"Send video {r.status_code}")
            return r.json()
    except Exception as e:
        print(f"Video send error {e}")
        return None

def download_telegram_video(file_id, dest_path):
    try:
        # get file path
        r = requests.get(f"{API_URL}/getFile?file_id={file_id}", timeout=10).json()
        if not r.get("ok"):
            print(f"getFile error {r}")
            return None
        file_path = r["result"]["file_path"]
        url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with requests.get(url, stream=True, timeout=60) as resp:
            with open(dest_path, 'wb') as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
        print(f"Downloaded video {dest_path} {os.path.getsize(dest_path)}")
        return dest_path
    except Exception as e:
        print(f"Download video error {e}")
        return None

def handle_start(chat_id, user_id):
    settings = get_user_settings(user_id)
    keyboard = {
        "inline_keyboard": [
            [{"text": "🚀 Получить промпт для Veo Pro", "callback_data": "one_click"}],
            [{"text": "🔍 Анализ @ksusha.prettycutie", "callback_data": "analyze"}],
            [{"text": "📦 Очередь постов", "callback_data": "queue"}],
            [{"text": "⚙️ Ниша UJC Creator", "callback_data": "settings"}],
        ]
    }
    text = f"""
👋 UJC Creator бот - схема для WB продаж

Твоя ниша: {settings['niche']}

**Как работает (ты делаешь красивое видео сам):**
1️⃣ Жми 🚀 Получить промпт — я проанализирую @ksusha.prettycutie и дам промпт для твоего Gemini Veo Pro
2️⃣ Ты делаешь видео в своем приложении Veo Pro (качество профи)
3️⃣ Кидаешь готовое видео СЮДА в бот — я спрошу артикул WB
4️⃣ Я сам выжигаю на видео АРТИКУЛ 12345678 НА WB и постю по расписанию {', '.join(POST_TIMES)} МСК в Instagram

Просто скинь видео файлом — начнем!
"""
    send_message(chat_id, text, reply_markup=keyboard)

async def handle_one_click(chat_id, user_id):
    settings = get_user_settings(user_id)
    send_message(chat_id, f"🔍 Анализирую {settings['niche']} и @ksusha.prettycutie... Генерю промпт для Veo Pro...")
    try:
        analysis = await orchestrator.analyst.analyze(settings['niche'], settings.get('competitors', ["@ksusha.prettycutie"]))
        concept = await orchestrator.creator.generate_concept(analysis, settings['niche'], settings.get('style', DEFAULT_STYLE))

        text = f"""
🎬 **ГОТОВО! Промпт для твоего Veo Pro:**

**Название:** {concept['title']}
**Хук:** {concept['hook']}

**Тренды:** {', '.join(analysis.get('trends', [])[:3])}

**PROMPT для Gemini Veo Pro (копируй):**
```
{concept['veo_prompt']}
```

**Negative:**
```
{concept.get('negative_prompt','')}
```

**Сценарий:**
{concept['script'][:500]}

**Подпись для Insta (с артикулом):**
{concept['caption']}

Сделай видео в своем приложении Gemini Pro → кидай сюда файлом → я спрошу артикул и поставлю на автопостинг {', '.join(POST_TIMES)} МСК
"""
        send_message(chat_id, text[:4000])
    except Exception as e:
        send_message(chat_id, f"Ошибка генерации промпта: {e}")

def handle_video_upload(chat_id, user_id, file_id):
    # Скачиваем видео
    os.makedirs("generated_videos", exist_ok=True)
    video_id = str(int(time.time()))[-6:]
    dest = f"generated_videos/uploaded_{user_id}_{video_id}.mp4"
    path = download_telegram_video(file_id, dest)
    if not path:
        send_message(chat_id, "❌ Не смог скачать видео, попробуй еще раз файлом")
        return

    # Сохраняем как pending
    settings = get_user_settings(user_id)
    settings["pending_video"] = path
    settings["state"] = "awaiting_article"
    set_user_settings(user_id, settings)

    send_message(chat_id, f"✅ Видео получил! {os.path.getsize(path)//1024}KB\n\nТеперь пришли **АРТИКУЛ WB** для этого видео (например 12345678 или 12345678 - Сыворотка Сияние)\n\nЯ выжгу его на видео и поставлю на автопостинг по расписанию {', '.join(POST_TIMES)} МСК")

def handle_article_input(chat_id, user_id, text):
    # Проверяем что это артикул (цифры 5-10 символов)
    settings = get_user_settings(user_id)
    pending = settings.get("pending_video")

    if not pending or not os.path.exists(pending):
        # Не ждет артикул, считаем что это настройка ниши
        if len(text) < 30 and text.isdigit() == False:
            # Возможно это ниша
            settings["niche"] = text
            set_user_settings(user_id, settings)
            send_message(chat_id, f"✅ Ниша сохранена: {text}\n\nТеперь скинь видео для автопостинга")
        return False

    # Это артикул для видео
    article = text.strip()
    # Извлекаем цифры артикула
    import re
    m = re.search(r'(\d{5,10})', article)
    article_num = m.group(1) if m else article

    # Добавляем в очередь
    queue = load_queue()
    caption = f"ВЫКИДЫВАЕМ БЕСПОЛЕЗНЫЕ БАНОЧКИ 🗑️\n\nВ 30 лет ни одной морщинки 👵 — секрет UJC Creator!\n\nАРТИКУЛ НА WB: {article_num} ⬇️\nЗабирай в описании! #{article_num}\n\n#ujccreator #уходзакожей #wbнаходки #артикулвб #skincare"

    item = {
        "video_path": pending,
        "article": article_num,
        "full_text": article,
        "caption": caption,
        "chat_id": chat_id,
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "posted": False,
        "scheduled_times": POST_TIMES
    }
    queue.append(item)
    save_queue(queue)

    # Сброс состояния
    settings["pending_video"] = None
    settings["state"] = None
    set_user_settings(user_id, settings)

    # Отправляем подтверждение и делаем превью с выжиганием артикула
    send_message(chat_id, f"✅ Добавил в очередь автопостинга!\n\nВидео: {pending}\nАртикул: {article_num}\nБудет запощено в {', '.join(POST_TIMES)} МСК\n\nСейчас сделаю превью с выжиганием артикула на видео...")

    # Делаем превью с артикулом (быстро)
    try:
        preview_path = asyncio.run(create_preview_with_article(pending, article_num))
        if preview_path and os.path.exists(preview_path):
            send_video(chat_id, preview_path, caption=f"Превью с артикулом {article_num} — так будет в Instagram\n\n{caption}")
    except Exception as e:
        print(f"Preview error {e}")

    send_message(chat_id, f"📦 Очередь: {len(queue)} видео. Посмотреть: кнопка 📦 Очередь постов в /start")
    return True

async def create_preview_with_article(video_path, article):
    """Выжигает артикул на видео для превью"""
    try:
        from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
        from PIL import Image, ImageDraw, ImageFont
        import textwrap
        output = video_path.replace(".mp4", f"_preview_{article}.mp4")
        clip = VideoFileClip(video_path)
        if clip.duration > 8:
            clip = clip.subclip(0, 8)
        w,h = clip.size
        if w/h > 9/16:
            new_w = int(h*9/16)
            x1=(w-new_w)//2
            clip = clip.crop(x1=x1, y1=0, x2=x1+new_w, y2=h)
        clip = clip.resize((1080,1920))

        # Текст артикула
        txt_img = Image.new('RGBA',(1080,1920),(0,0,0,0))
        draw = ImageDraw.Draw(txt_img)
        try:
            font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
            font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
        except:
            font_big = ImageFont.load_default()
            font_med = font_big

        draw.rectangle([0,1650,1080,1920], fill=(0,0,0,160))
        draw.text((40,1660), f"АРТИКУЛ {article} НА WB", fill=(255,255,255), font=font_big, stroke_width=3, stroke_fill=(0,0,0))
        draw.text((40,1750), "ЗАБИРАЙ В ОПИСАНИИ ⬇️", fill=(255,255,255), font=font_med, stroke_width=3, stroke_fill=(0,0,0))

        tmp = f"/tmp/art_{article}.png"
        txt_img.save(tmp)
        txt_clip = ImageClip(tmp).set_duration(clip.duration)
        final = CompositeVideoClip([clip, txt_clip])
        final.write_videofile(output, fps=24, codec='libx264', audio_codec='aac', threads=2, logger=None)
        return output
    except Exception as e:
        print(f"Preview create error {e}")
        return None

def handle_queue_show(chat_id):
    queue = load_queue()
    if not queue:
        send_message(chat_id, "📦 Очередь пустая. Скинь видео — я добавлю на автопостинг")
        return
    text = f"📦 Очередь {len(queue)} видео:\n\n"
    for i, item in enumerate(queue[-5:], 1):
        status = "✅ Опубликовано" if item.get("posted") else "⏳ В очереди"
        text += f"{i}. Артикул {item['article']} — {status} — {item['video_path']}\n"
    text += f"\nРасписание: {', '.join(POST_TIMES)} МСК\nБот сам постит в это время в Instagram"
    send_message(chat_id, text)

def scheduler_loop():
    """Фоновая проверка очереди каждые 60 сек и постинг в scheduled times"""
    print(f"⏰ Scheduler запущен, времена {POST_TIMES} МСК")
    while True:
        try:
            # МСК время
            tz = pytz.timezone('Europe/Moscow')
            now = datetime.now(tz)
            current_time = now.strftime("%H:%M")
            # print(f"[Scheduler] Check {current_time} MSK")

            if current_time in POST_TIMES:
                queue = load_queue()
                # Находим первое не опубликованное за сегодня
                for item in queue:
                    if not item.get("posted"):
                        # Проверяем не постили ли уже в это время сегодня
                        last_post = item.get(f"posted_at_{current_time}")
                        if last_post:
                            continue
                        print(f"[Scheduler] Время {current_time} — постю артикул {item['article']}")
                        # Постим
                        try:
                            # Добавляем артикул на видео если еще нет
                            preview = asyncio.run(create_preview_with_article(item['video_path'], item['article']))
                            video_to_post = preview if preview and os.path.exists(preview) else item['video_path']

                            result = asyncio.run(orchestrator.publish_auto(video_to_post, item['caption']))
                            if result.get("success"):
                                item["posted"] = True  # Для простоты - один пост, можно сделать по расписанию каждый день
                                item[f"posted_at_{current_time}"] = now.isoformat()
                                save_queue(queue)
                                send_message(item['chat_id'], f"✅ Автопостинг в {current_time} МСК выполнен! Артикул {item['article']} опубликован в Instagram")
                                print(f"[Scheduler] Posted {item['article']} at {current_time}")
                            else:
                                print(f"[Scheduler] Publish failed {result}")
                                send_message(item['chat_id'], f"⚠️ Не смог запостить артикул {item['article']} в {current_time}: {result.get('error')}")
                        except Exception as e:
                            print(f"[Scheduler] Error {e}")
                            import traceback; traceback.print_exc()
                        break  # Постим только одно видео за один time slot

                # Чтобы не постить 60 раз в одну минуту — спим 61 сек после поста
                if current_time in POST_TIMES:
                    time.sleep(70)

            time.sleep(60)
        except Exception as e:
            print(f"[Scheduler] Loop error {e}")
            time.sleep(60)

def polling():
    print("🚀 Запускаю UJC Creator бота — схема Veo Pro + автопостинг по расписанию")
    print(f"Расписание {POST_TIMES} МСК")
    # Запускаем scheduler в отдельном потоке
    t = threading.Thread(target=scheduler_loop, daemon=True)
    t.start()

    offset = 0
    while True:
        try:
            url = f"{API_URL}/getUpdates"
            params = {"offset": offset, "timeout": 30}
            resp = requests.get(url, params=params, timeout=35)
            data = resp.json()
            if not data.get("ok"):
                print(f"getUpdates error {data}")
                time.sleep(2)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    user_id = msg["from"]["id"]

                    # Видео
                    if "video" in msg:
                        file_id = msg["video"]["file_id"]
                        print(f"Video from {user_id} file_id {file_id}")
                        handle_video_upload(chat_id, user_id, file_id)
                        continue
                    if "document" in msg and msg["document"].get("mime_type","").startswith("video"):
                        file_id = msg["document"]["file_id"]
                        handle_video_upload(chat_id, user_id, file_id)
                        continue

                    text = msg.get("text","")
                    if not text:
                        continue
                    print(f"Text from {user_id}: {text[:80]}")

                    if text.startswith("/start"):
                        handle_start(chat_id, user_id)
                    elif text.startswith("/queue") or text == "очередь":
                        handle_queue_show(chat_id)
                    else:
                        # Сначала пробуем как артикул
                        handled = handle_article_input(chat_id, user_id, text)
                        if not handled:
                            # Иначе как ниша
                            if len(text) > 2 and not text.startswith("/"):
                                settings = get_user_settings(user_id)
                                # Если ждет артикул - уже обработали выше, иначе это ниша
                                if settings.get("state") != "awaiting_article":
                                    settings["niche"] = text
                                    set_user_settings(user_id, settings)
                                    send_message(chat_id, f"✅ Ниша {text} сохранена. Теперь скинь видео с Veo Pro")

                if "callback_query" in update:
                    cb = update["callback_query"]
                    chat_id = cb["message"]["chat"]["id"]
                    user_id = cb["from"]["id"]
                    data_cb = cb.get("data","")
                    requests.post(f"{API_URL}/answerCallbackQuery", data={"callback_query_id": cb["id"]})

                    if data_cb == "one_click":
                        asyncio.run(handle_one_click(chat_id, user_id))
                    elif data_cb == "queue":
                        handle_queue_show(chat_id)
                    elif data_cb == "settings":
                        send_message(chat_id, "Напиши нишу: UJC Creator косметика | @ksusha.prettycutie")

        except Exception as e:
            print(f"Polling error {e}")
            import traceback; traceback.print_exc()
            time.sleep(5)

if __name__ == "__main__":
    polling()
