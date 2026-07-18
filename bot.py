"""
TELEGRAM БОТ: ПОЛНАЯ АВТОМАТИЗАЦИЯ 1 КЛИК
Теперь: /start -> 1 клик -> Анализ -> Генерация видео (Veo или Imagen+MoviePy) -> Автопубликация в IG
Без ручных шагов.
"""
import os
import asyncio
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from dotenv import load_dotenv

from config import TELEGRAM_BOT_TOKEN, DEFAULT_NICHE, DEFAULT_STYLE
from agents.orchestrator import ReelsOrchestrator

load_dotenv()

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
        "auto_publish": True  # По умолчанию сразу публикуем
    })

def set_user_settings(user_id, settings):
    db = load_db()
    db[str(user_id)] = settings
    save_db(db)

orchestrator = ReelsOrchestrator()

# === КОМАНДЫ ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = get_user_settings(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("🚀 СДЕЛАТЬ REELS - 1 КЛИК (АВТО)", callback_data="one_click_auto")],
        [InlineKeyboardButton("🎬 Только сгенерить (без публикации)", callback_data="one_click")],
        [InlineKeyboardButton("🔍 Анализ конкурентов", callback_data="analyze")],
        [InlineKeyboardButton("⚙️ Настройки ниши", callback_data="settings")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"""
👋 Готов к полной автоматизации!

**Как работает сейчас (100% автомат):**

1️⃣ Агент-Аналитик -> анализирует нишу через Gemini
2️⃣ Агент-Креатор -> `Veo 3` если есть доступ, если нет - автоматом `Imagen 3 + MoviePy + gTTS`
3️⃣ Агент-Паблишер -> сам публикует в Instagram через instagrapi

**Текущая ниша:** {settings['niche']}
**Автопубликация:** {'✅ Включена' if settings.get('auto_publish', True) else '❌ Выключена'}
**Конкуренты:** {', '.join(settings.get('competitors', [])) or 'авто-поиск топов'}

Жми **1 КЛИК АВТО** и я все сделаю сам за 2 минуты 👇
"""
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚙️ Напиши свою нишу и конкурентов так:\n\n"
        "`ниша | конкурент1, конкурент2`\n\n"
        "Пример:\n"
        "`фитнес для мам | @mama_fit, @fitness_mom`\n\n"
        "Или просто:\n"
        "`крипта для новичков`\n\n"
        "После этого бот запомнит.",
        parse_mode="Markdown"
    )

async def handle_settings_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "|" in text:
        niche, comps = text.split("|", 1)
        competitors = [c.strip() for c in comps.split(",") if c.strip()]
    else:
        niche = text
        competitors = []

    settings = get_user_settings(update.effective_user.id)
    settings["niche"] = niche.strip()
    settings["competitors"] = competitors
    set_user_settings(update.effective_user.id, settings)

    await update.message.reply_text(
        f"✅ Сохранил! Теперь все на автомате.\n\nНиша: {settings['niche']}\nКонкуренты: {', '.join(competitors) if competitors else 'авто'}\n\nЖми /start -> 🚀 1 КЛИК АВТО"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    settings = get_user_settings(user_id)

    if query.data in ["one_click_auto", "one_click"]:
        is_full_auto = query.data == "one_click_auto"
        
        if is_full_auto:
            await query.edit_message_text("🚀 ЗАПУСТИЛ ПОЛНУЮ АВТОМАТИЗАЦИЮ...\n\n1. Анализирую конкурентов...\n2. Генерю видео...\n3. Сам опубликую в IG\n\nНе закрывай чат, это 1.5-2 минуты.")
        else:
            await query.edit_message_text("🎬 Генерирую Reels без публикации...")

        async def progress(msg):
            try:
                await context.bot.send_message(chat_id=user_id, text=msg)
            except:
                pass

        try:
            result = await orchestrator.run_one_click_pipeline(
                niche=settings["niche"],
                competitors=settings.get("competitors", []),
                style=settings.get("style", DEFAULT_STYLE),
                progress_callback=progress
            )

            concept = result["concept"]
            analysis = result["analysis"]
            video = result["video"]

            caption = f"{concept['caption']}"

            full_report = f"""
🎬 **ГОТОВО! МЕТОД: {video['method']}**

**Название:** {concept['title']}
**Хук:** {concept['hook']}
**Сценарий:** {concept['script'][:300]}

**Подпись:** {caption}
**Тренды:** {', '.join(analysis.get('trends', [])[:3])}
**Путь:** {video.get('path')}
"""

            # Отправляем видео
            if video["success"] and video.get("path") and os.path.exists(video["path"]):
                # Проверяем это видео или картинка-заглушка
                if video["path"].lower().endswith(('.mp4', '.mov')):
                    await context.bot.send_video(
                        chat_id=user_id,
                        video=open(video["path"], 'rb'),
                        caption=f"✅ Готово! Метод: {video['method']}\n\n{concept['title']}\n{concept['hook']}",
                    )
                else:
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=open(video["path"], 'rb'),
                        caption=f"✅ Кадры готовы, собираю видео... Метод: {video['method']}"
                    )
                
                await context.bot.send_message(chat_id=user_id, text=full_report, parse_mode="Markdown")

                # === ПОЛНЫЙ АВТОМАТ: СРАЗУ ПУБЛИКУЕМ В IG ===
                if is_full_auto:
                    await context.bot.send_message(chat_id=user_id, text="📤 АВТОПУБЛИКАЦИЯ: Заливаю в Instagram...")
                    pub_result = await orchestrator.publish_auto(video["path"], caption)
                    if pub_result["success"]:
                        await context.bot.send_message(
                            chat_id=user_id, 
                            text=f"✅✅✅ ОПУБЛИКОВАНО В INSTAGRAM АВТОМАТОМ!\nID: {pub_result.get('media_id')}\n\nВесь пайплайн в 1 клик завершен!"
                        )
                    else:
                        await context.bot.send_message(
                            chat_id=user_id, 
                            text=f"⚠️ Автопубликация не удалась: {pub_result['error']}\n\nПроверь IG_USERNAME / IG_PASSWORD в .env\n\nИнструкция: {orchestrator.publisher.get_publish_instruction(video['path'], caption)}"
                        )
                else:
                    # Кнопка для ручной публикации если выбрал режим без авто
                    keyboard = [[InlineKeyboardButton("📤 Опубликовать в IG сейчас", callback_data="publish_last")]]
                    await context.bot.send_message(chat_id=user_id, text="Хочешь запостить?", reply_markup=InlineKeyboardMarkup(keyboard))

            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=full_report + f"\n\n❌ Видео не создалось: {video.get('error')}",
                    parse_mode="Markdown"
                )

            context.user_data['last_result'] = result

        except Exception as e:
            import traceback
            traceback.print_exc()
            await context.bot.send_message(chat_id=user_id, text=f"❌ Ошибка пайплайна: {e}\nПопробуй еще раз /start")

    elif query.data == "analyze":
        await query.edit_message_text(f"🔍 Анализирую '{settings['niche']}'...")
        try:
            analysis = await orchestrator.analyst.analyze(settings['niche'], settings.get('competitors', []))
            text = f"📊 **Анализ: {settings['niche']}**\n\n🔥 Тренды: {', '.join(analysis.get('trends', []))}\n🪝 Хуки: {', '.join(analysis.get('top_hooks', [])[:5])}\n\n💡 Идеи:\n"
            for i, rec in enumerate(analysis.get('recommendations', [])[:3], 1):
                text += f"\n{i}. {rec.get('idea')} -> {rec.get('hook')}"
            await context.bot.send_message(chat_id=user_id, text=text[:4000], parse_mode="Markdown")
        except Exception as e:
            await context.bot.send_message(chat_id=user_id, text=f"Ошибка: {e}")

    elif query.data == "settings":
        await context.bot.send_message(chat_id=user_id, text="⚙️ Напиши: `ниша | @конк1, @конк2`", parse_mode="Markdown")

    elif query.data == "publish_last":
        result = context.user_data.get('last_result')
        if not result:
            await context.bot.send_message(chat_id=user_id, text="Нет последнего видео. Сделай /start")
            return
        video = result["video"]
        concept = result["concept"]
        await context.bot.send_message(chat_id=user_id, text="📤 Публикую в IG...")
        pub_result = await orchestrator.publish_auto(video["path"], concept["caption"])
        if pub_result["success"]:
            await context.bot.send_message(chat_id=user_id, text=f"✅ Опубликовано! {pub_result.get('media_id')}")
        else:
            await context.bot.send_message(chat_id=user_id, text=f"❌ {pub_result['error']}")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await context.bot.get_file(update.message.video.file_id)
    path = f"generated_videos/uploaded_{update.effective_user.id}.mp4"
    os.makedirs("generated_videos", exist_ok=True)
    await file.download_to_drive(path)
    await update.message.reply_text(f"✅ Видео сохранено {path}. Публикую автоматом в IG...")
    pub_result = await orchestrator.publish_auto(path, "🔥 Reels via bot #auto")
    if pub_result["success"]:
        await update.message.reply_text(f"✅ Опубликовано в IG: {pub_result.get('media_id')}")
    else:
        await update.message.reply_text(f"⚠️ Ошибка публикации: {pub_result['error']}")

def main():
    print("🚀 Запускаю БОТА ПОЛНОЙ АВТОМАТИЗАЦИИ...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_settings_input))
    print("Бот запущен в режиме FULL AUTO. Жду /start в Telegram...")
    app.run_polling()

if __name__ == "__main__":
    main()
