"""
Быстрый тест ПОЛНОЙ АВТОМАТИЗАЦИИ без Telegram
Запускает всех 3 агентов и генерит Reels
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from agents.orchestrator import ReelsOrchestrator

async def main():
    print("🚀 QUICK START — Тест полной автоматизации")
    print("="*60)
    
    # Проверяем ключи
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Нет GEMINI_API_KEY в .env")
        print("Создай .env из .env.example")
        return
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("⚠️ Нет TELEGRAM_BOT_TOKEN, но тест видео все равно запустим")

    orchestrator = ReelsOrchestrator()
    
    niche = os.getenv("DEFAULT_NICHE", "мотивация, бизнес")
    style = os.getenv("DEFAULT_STYLE", "динамичный, вирусный, 9:16")
    competitors = []  # можно добавить ["@garyvee", "@hormozi"]

    print(f"Ниша: {niche}")
    print(f"Стиль: {style}")
    print()

    async def progress(msg):
        print(f">>> {msg}")

    result = await orchestrator.run_one_click_pipeline(
        niche=niche,
        competitors=competitors,
        style=style,
        progress_callback=progress
    )

    print("\n" + "="*60)
    print("✅ РЕЗУЛЬТАТ:")
    print(f"Концепт: {result['concept']['title']}")
    print(f"Хук: {result['concept']['hook']}")
    print(f"Видео: {result['video'].get('path')}")
    print(f"Метод: {result['video'].get('method')}")
    print(f"Подпись: {result['concept']['caption'][:200]}")
    print()
    
    video_path = result['video'].get('path')
    if video_path and os.path.exists(video_path):
        print(f"📁 Файл готов: {os.path.abspath(video_path)}")
        
        # Тест автопубликации
        if os.getenv("IG_USERNAME"):
            print("\n📤 Тестирую автопубликацию в Instagram...")
            pub = await orchestrator.publish_auto(video_path, result['concept']['caption'])
            print(f"Результат публикации: {pub}")
        else:
            print("\n⚠️ IG_USERNAME не задан — пропускаю автопубликацию")
            print("Добавь IG_USERNAME/IG_PASSWORD в .env чтобы тестить постинг")
    else:
        print("❌ Видео не создалось")

    print("\n✅ Тест завершен! Если видео создалось — система 100% автоматизирована и готова.")

if __name__ == "__main__":
    asyncio.run(main())
