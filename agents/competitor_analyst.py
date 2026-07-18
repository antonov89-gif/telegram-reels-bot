"""
АГЕНТ 1: Аналитик конкурентов
Задача: взять нишу + список конкурентов и выдать что сейчас залетает
"""
import json
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL_TEXT

class CompetitorAnalystAgent:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL_TEXT

    async def analyze(self, niche: str, competitors: list[str] = None, extra_context: str = "") -> dict:
        competitors_str = ", ".join(competitors) if competitors else "топовые аккаунты в этой нише"
        
        prompt = f"""
Ты — агент-аналитик Reels, эксперт по вирусному контенту Instagram 2025-2026.

НИША: {niche}
КОНКУРЕНТЫ: {competitors_str}
ДОП. КОНТЕКСТ: {extra_context}

Твоя задача:
1. Проанализируй что сейчас залетает в этой нише (хуки, форматы, длина, тренды)
2. Какие темы у конкурентов набирают больше всего просмотров
3. Какие ошибки они делают
4. Дай 3 готовых направления для Reels которые порвут

Верни ответ СТРОГО в JSON формате:
{{
  "trends": ["тренд1", "тренд2", "тренд3"],
  "top_hooks": ["хук1", "хук2", "хук3", "хук4", "хук5"],
  "content_pillars": ["столп1", "столп2", "столп3"],
  "competitor_weakness": "что они делают плохо",
  "recommendations": [
    {{"idea": "идея Reels 1", "why_viral": "почему залетит", "hook": "первая фраза"}},
    {{"idea": "идея Reels 2", "why_viral": "...", "hook": "..."}},
    {{"idea": "идея Reels 3", "why_viral": "...", "hook": "..."}}
  ],
  "hashtags": ["#хештег1", "#хештег2"],
  "visual_style": "описание визуального стиля который сейчас в тренде"
}}
Только JSON, без markdown.
"""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        
        try:
            data = json.loads(text)
        except:
            # Fallback если модель вернула не чистый JSON
            data = {
                "trends": ["динамичный монтаж", "говорящая голова + b-roll", "AI визуал"],
                "top_hooks": text[:500].split("\n")[:5],
                "content_pillars": ["обучение", "развлечение", "мотивация"],
                "competitor_weakness": "Скучный монтаж",
                "recommendations": [{"idea": text[:200], "why_viral": "Актуально", "hook": "Стоп! Ты делаешь это не так"}],
                "hashtags": ["#reels", "#viral"],
                "visual_style": "вертикаль 9:16, быстрые склейки, субтитры",
                "raw": text
            }
        return data
