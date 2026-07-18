"""
ОРКЕСТРАТОР: ПОЛНАЯ АВТОМАТИЗАЦИЯ в 1 клик
"""
from .competitor_analyst import CompetitorAnalystAgent
from .reels_creator import ReelsCreatorAgent
from .publisher import PublisherAgent

class ReelsOrchestrator:
    def __init__(self):
        self.analyst = CompetitorAnalystAgent()
        self.creator = ReelsCreatorAgent()
        self.publisher = PublisherAgent()

    async def run_one_click_pipeline(self, niche: str, competitors: list[str], style: str, progress_callback=None):
        """
        Полный пайплайн в 1 клик — 100% автомат, без ручных действий
        """
        async def notify(msg):
            if progress_callback:
                await progress_callback(msg)
            print(msg)

        await notify("🔍 АГЕНТ 1: Анализирую конкурентов и тренды через Gemini...")
        analysis = await self.analyst.analyze(niche=niche, competitors=competitors)
        await notify(f"✅ Анализ готов: {len(analysis.get('recommendations', []))} идеи. Тренды: {', '.join(analysis.get('trends', [])[:2])}")

        await notify("🎬 АГЕНТ 2: Генерирую вирусный сценарий + промпты...")
        # Теперь это ПОЛНЫЙ АВТОМАТ: если Veo нет — Imagen+MoviePy
        result = await self.creator.create_full_auto_reel(analysis, niche, style)
        
        concept = result["concept"]
        video = result["video"]
        
        await notify(f"✅ Концепт: {concept.get('title')}")
        if video["method"] == "veo":
            await notify("🎥 Видео сгенерировано через Veo 3!")
        else:
            await notify(f"🎥 Видео собрано АВТОМАТОМ через Imagen 3 + MoviePy: {video.get('path')}")

        await notify("📤 АГЕНТ 3: Готовлю к автопубликации...")
        
        return {
            "niche": niche,
            "analysis": analysis,
            "concept": concept,
            "video": video,
            "method": result.get("method", "auto")
        }

    async def publish_auto(self, video_path: str, caption: str) -> dict:
        """Автопубликация без участия человека"""
        return await self.publisher.publish_via_instagrapi(video_path, caption)
