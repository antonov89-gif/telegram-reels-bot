"""
АГЕНТ 2: Креатор Reels — КРАСИВОЕ ВИДЕО
Путь 1: Veo 3.1 (если есть биллинг)
Путь 2: Pollinations Flux (бесплатно, красивые фото) + Pexels + MoviePy
Генерит реально красивые Reels для фитнеса
"""
import time
import os
import uuid
import textwrap
import json
import requests
import urllib.parse
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL_TEXT, GEMINI_MODEL_VIDEO

os.makedirs("generated_videos", exist_ok=True)
os.makedirs("generated_images", exist_ok=True)

class ReelsCreatorAgent:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.text_model = GEMINI_MODEL_TEXT
        self.video_model = GEMINI_MODEL_VIDEO

    async def generate_concept(self, analysis: dict, niche: str, style: str) -> dict:
        prompt = f"""
Ты — топовый сценарист Reels и SMM для фитнес-ниши 2026.

Ниша: {niche}
Стиль: {style}
Анализ: {analysis}

Создай вирусный Reels 7-8 секунд для девушек 18-35.

Верни СТРОГО JSON:
{{
  "title": "короткое название",
  "hook": "ХВАТИТ ДЕЛАТЬ ЭТО | 3-4 слова КРУПНО",
  "script": "00:00-00:02 хук, 00:02-00:06 польза, 00:06-00:08 CTA подпишись",
  "veo_prompt": "Vertical 9:16 video, ... детальный промпт на английском для видео",
  "imagen_prompts": [
    "Beautiful young fitness girl doing morning stretching in aesthetic bedroom, soft natural light, 9:16 vertical, photorealistic, 8k, clean, motivational",
    "Close up of flat belly, healthy lifestyle, aesthetic, soft light, vertical 9:16, highly detailed",
    "Girl drinking green smoothie after workout, aesthetic kitchen, morning light, vertical 9:16, beautiful, photorealistic"
  ],
  "negative_prompt": "blurry, low quality, watermark, deformed, ugly, bad anatomy",
  "caption": "Подпись для Instagram с пользой и CTA: Сохрани и сделай завтра утром 👇 + 5 хештегов",
  "voiceover_text": "Хочешь плоский живот без скручиваний? Делай это каждое утро 2 минуты. Сохрани!"
}}
Только JSON.
"""
        response = self.client.models.generate_content(
            model=self.text_model,
            contents=prompt
        )
        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(text)
        except Exception as e:
            print(f"JSON parse error: {e}")
            data = {
                "title": f"Reels про {niche}",
                "hook": "СТОП! ДЕЛАЕШЬ НЕ ТАК",
                "script": "00:00-00:03 Хук\n00:03-00:06 Польза\n00:06-00:08 Подпишись",
                "veo_prompt": f"Vertical 9:16 video, beautiful fitness girl, aesthetic, cinematic, {style}, 8 seconds",
                "imagen_prompts": [
                    "Beautiful fitness girl stretching in bed morning light, aesthetic, vertical 9:16, photorealistic, 8k",
                    "Flat belly healthy woman, aesthetic, soft light, vertical 9:16, beautiful",
                    "Girl with green smoothie aesthetic kitchen morning, vertical 9:16, photorealistic"
                ],
                "negative_prompt": "blurry, low quality, watermark",
                "caption": f"🔥 {niche} Сохрани чтобы не потерять! 👇\n\n#фитнес #похудение #reels",
                "voiceover_text": f"Хочешь результат в {niche}? Делай вот так. Сохрани!",
            }
        return data

    async def try_veo_generation(self, veo_prompt: str, negative_prompt: str) -> dict:
        video_id = str(uuid.uuid4())[:8]
        output_path = f"generated_videos/reel_veo_{video_id}.mp4"
        print(f"[Veo] Пробую {self.video_model}")
        try:
            operation = self.client.models.generate_videos(
                model=self.video_model,
                prompt=veo_prompt,
                config={"aspect_ratio": "9:16", "negative_prompt": negative_prompt, "duration_seconds": 8}
            )
            while not operation.done:
                time.sleep(10)
                operation = self.client.operations.get(operation)
            generated_video = operation.response.generated_videos[0]
            self.client.files.download(file=generated_video.video)
            generated_video.video.save(output_path)
            return {"success": True, "path": output_path, "method": "veo", "video_id": video_id}
        except Exception as e:
            print(f"[Veo] Недоступен: {e}")
            return {"success": False, "error": str(e), "method": "veo"}

    async def generate_images_beautiful(self, imagen_prompts: list, video_id: str) -> list:
        """Генерит КРАСИВЫЕ картинки через Pollinations Flux (бесплатно, без ключа) + fallback"""
        image_paths = []
        print(f"[Beautiful] Генерю {len(imagen_prompts)} красивых кадра через Pollinations Flux...")

        for i, prompt in enumerate(imagen_prompts[:3]):
            # Улучшаем промпт для красоты
            beautiful_prompt = f"{prompt}, beautiful fitness influencer, aesthetic, soft natural light, photorealistic, ultra detailed, 8k, professional photography, clean background, vertical 9:16"
            # Для Pollinations добавляем стиль
            final_prompt = f"{beautiful_prompt}, instagram aesthetic, motivational fitness"

            img_path = f"generated_images/{video_id}_{i}_beautiful.jpg"
            
            # Попытка 1: Pollinations Flux (бесплатно, без API ключа)
            try:
                # Кодируем промпт для URL
                encoded = urllib.parse.quote(final_prompt)
                # Pollinations Flux - бесплатно генерит красивые фото
                url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&model=flux&enhance=true"
                print(f"[Pollinations] Запрос: {url[:120]}...")
                r = requests.get(url, timeout=45)
                if r.status_code == 200 and len(r.content) > 10000:
                    with open(img_path, 'wb') as f:
                        f.write(r.content)
                    print(f"[Pollinations] ✅ Красивый кадр {i}: {img_path} ({len(r.content)} bytes)")
                else:
                    raise Exception(f"Bad status {r.status_code} len {len(r.content)}")
            except Exception as e:
                print(f"[Pollinations] Ошибка кадра {i}: {e} -> пробую Imagen через Gemini")
                # Попытка 2: Imagen через Gemini
                try:
                    response = self.client.models.generate_images(
                        model="imagen-3.0-generate-001",
                        prompt=beautiful_prompt,
                    )
                    if response.generated_images:
                        img_bytes = response.generated_images[0].image.image_bytes
                        with open(img_path, "wb") as f:
                            f.write(img_bytes)
                        print(f"[Imagen] Кадр {i}: {img_path}")
                    else:
                        raise Exception("No images")
                except Exception as e2:
                    print(f"[Imagen] Тоже ошибка: {e2} -> делаю красивую Pillow заглушку с градиентом и фото")
                    # Попытка 3: Красивая Pillow заглушка (но уже эстетичная)
                    try:
                        from PIL import Image, ImageDraw, ImageFont
                        # Создаем эстетичный градиент
                        img = Image.new('RGB', (1080, 1920), color=(0,0,0))
                        draw = ImageDraw.Draw(img)
                        # Красивый фитнес-градиент
                        colors = [(255, 183, 197), (255, 154, 158), (250, 208, 196), (255, 209, 102)]
                        base = colors[i % len(colors)]
                        for y in range(1920):
                            # Градиент сверху вниз
                            r = int(base[0] * (1 - y/1920*0.3) + 255 * y/1920*0.3)
                            g = int(base[1] * (1 - y/1920*0.3) + 255 * y/1920*0.3)
                            b = int(base[2] * (1 - y/1920*0.3) + 200 * y/1920*0.3)
                            draw.line([(0, y), (1080, y)], fill=(r, g, b))
                        # Добавляем белый полупрозрачный бокс для текста
                        draw.rectangle([50, 750, 1030, 1150], fill=(255, 255, 255, 200), outline=(255,255,255))
                        # Текст
                        try:
                            # Пробуем дефолтный шрифт
                            font_large = ImageFont.load_default()
                            # Переносим промпт
                            wrapped = textwrap.fill(final_prompt[:200], width=35)
                            draw.text((80, 780), wrapped, fill=(50,50,50), font=font_large)
                            draw.text((80, 1050), f"FITNESS REELS #{video_id}", fill=(100,100,100), font=font_large)
                        except:
                            draw.text((80, 800), final_prompt[:150], fill=(50,50,50))
                        img.save(img_path, quality=95)
                        print(f"[Pillow Aesthetic] Заглушка {img_path}")
                    except Exception as e3:
                        print(f"[Pillow] Ошибка заглушки: {e3}")
            
            if os.path.exists(img_path):
                image_paths.append(img_path)

        # Если ничего не сгенерилось, создаем хотя бы один
        if not image_paths:
            print("[Beautiful] Ничего не сгенерилось, создаю аварийную картинку")
            from PIL import Image, ImageDraw
            img_path = f"generated_images/{video_id}_emergency.jpg"
            img = Image.new('RGB', (1080, 1920), color=(255, 183, 197))
            img.save(img_path)
            image_paths.append(img_path)

        return image_paths

    async def generate_voiceover_auto(self, text: str, video_id: str) -> str:
        audio_path = f"generated_videos/{video_id}_voice.mp3"
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='ru', slow=False)
            tts.save(audio_path)
            print(f"[TTS] Озвучка: {audio_path}")
            return audio_path
        except Exception as e:
            print(f"[TTS] Ошибка: {e}")
            return None

    def add_text_with_pillow(self, image_path, hook_text, output_path):
        """Добавляет красивый текст через Pillow (не через ImageMagick, чтобы не падало)"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.open(image_path).convert("RGB")
            draw = ImageDraw.Draw(img, "RGBA")
            
            # Черный полупрозрачный фон для текста сверху
            draw.rectangle([0, 0, 1080, 350], fill=(0, 0, 0, 160))
            # Белый текст
            # Пытаемся найти шрифт
            try:
                # Попытка загрузить жирный шрифт если есть
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
            except:
                font = ImageFont.load_default()
                font_small = ImageFont.load_default()

            # Хук в 2 строки
            hook_lines = textwrap.wrap(hook_text.upper(), width=14)
            y = 40
            for line in hook_lines[:2]:
                # Обводка текста
                x = 50
                # Тень
                draw.text((x+3, y+3), line, fill=(0,0,0), font=font)
                draw.text((x, y), line, fill=(255,255,255), font=font)
                y += 110

            # Добавляем внизу лейбл "Сохрани"
            draw.rectangle([0, 1750, 1080, 1920], fill=(0, 0, 0, 120))
            draw.text((80, 1790), "Сохрани  •  Сделай завтра  •  Подпишись", fill=(255,255,255), font=font_small)

            img.save(output_path, quality=95)
            return output_path
        except Exception as e:
            print(f"[Pillow Text] Ошибка: {e}")
            import shutil
            shutil.copy(image_path, output_path)
            return output_path

    async def assemble_reel_beautiful(self, image_paths: list, voice_path: str, concept: dict, video_id: str) -> str:
        output_path = f"generated_videos/reel_BEAUTIFUL_{video_id}.mp4"
        print(f"[Beautiful Assembler] Собираю красивый Reels из {len(image_paths)} кадров...")

        # Сначала добавляем текст на первую картинку через Pillow (красиво)
        try:
            first_with_text = f"generated_images/{video_id}_0_text.jpg"
            self.add_text_with_pillow(image_paths[0], concept.get("hook", "СТОП!"), first_with_text)
            # Заменяем первую картинку на версию с текстом
            image_paths[0] = first_with_text
        except Exception as e:
            print(f"Text overlay error: {e}")

        # Сборка через MoviePy с Ken Burns и кроссфейдом
        try:
            from moviepy.editor import ImageClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip, ColorClip, CompositeVideoClip

            clips = []
            total_duration = 8
            per_clip = total_duration / len(image_paths)

            for idx, img_path in enumerate(image_paths):
                clip = ImageClip(img_path).set_duration(per_clip + 0.5)  # +0.5 для кроссфейда
                # Ресайз до 1080x1920 с сохранением пропорций
                clip = clip.resize(height=1920)
                clip = clip.crop(x_center=clip.w/2, width=1080, height=1920)
                
                # Ken Burns - плавный зум
                def make_zoom(idx):
                    def zoom(t):
                        # Легкий зум ин + небольшой сдвиг
                        scale = 1 + 0.12 * t / per_clip
                        return scale
                    return zoom
                
                clip = clip.resize(make_zoom(idx))
                
                # Кроссфейд между клипами
                if idx > 0:
                    clip = clip.crossfadein(0.5)
                
                clips.append(clip)

            final = concatenate_videoclips(clips, method="compose", padding=-0.5)

            # Обрезаем до 8 сек ровно
            if final.duration > 8:
                final = final.subclip(0, 8)

            # Аудио
            if voice_path and os.path.exists(voice_path):
                try:
                    audio = AudioFileClip(voice_path)
                    if audio.duration > final.duration:
                        audio = audio.subclip(0, final.duration)
                    # Громкость голоса
                    audio = audio.volumex(1.2)
                    final = final.set_audio(audio)
                except Exception as e:
                    print(f"Audio error: {e}")

            # Рендерим с высоким качеством
            final.write_videofile(
                output_path, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                bitrate="5000k",
                threads=4,
                logger=None,
                preset='medium'
            )
            print(f"[Beautiful] ✅ Готов красивый Reels: {output_path}")
            return output_path

        except Exception as e:
            print(f"[MoviePy] Ошибка: {e}, пробую OpenCV")
            try:
                import cv2
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, 24.0, (1080, 1920))
                for img_path in image_paths:
                    img = cv2.imread(img_path)
                    if img is None:
                        continue
                    img = cv2.resize(img, (1080, 1920))
                    frames_per_image = int((8 * 24) / len(image_paths))
                    for _ in range(frames_per_image):
                        out.write(img)
                out.release()
                print(f"[OpenCV] Готов: {output_path}")
                return output_path
            except Exception as e2:
                print(f"OpenCV also failed: {e2}")
                return image_paths[0] if image_paths else None

    async def create_full_auto_reel(self, analysis: dict, niche: str, style: str) -> dict:
        video_id = str(uuid.uuid4())[:6]
        
        concept = await self.generate_concept(analysis, niche, style)
        
        # Попытка Veo
        veo_result = await self.try_veo_generation(concept["veo_prompt"], concept.get("negative_prompt", ""))
        if veo_result["success"]:
            return {"concept": concept, "video": veo_result, "method": "veo"}

        # Красивая генерация через Pollinations
        print("[BEAUTIFUL MODE] Делаю красивое видео через Flux + MoviePy")
        image_paths = await self.generate_images_beautiful(concept.get("imagen_prompts", []), video_id)
        voice_path = await self.generate_voiceover_auto(concept.get("voiceover_text", ""), video_id)
        final_video_path = await self.assemble_reel_beautiful(image_paths, voice_path, concept, video_id)

        return {
            "concept": concept,
            "video": {
                "success": True if final_video_path and os.path.exists(final_video_path) else False,
                "path": final_video_path,
                "method": "beautiful_flux_moviepy",
                "video_id": video_id,
                "image_paths": image_paths,
                "voice_path": voice_path
            },
            "method": "beautiful"
        }

    # Совместимость
    async def generate_video(self, veo_prompt: str, negative_prompt: str = "", aspect_ratio: str = "9:16") -> dict:
        return await self.try_veo_generation(veo_prompt, negative_prompt)

    async def create_full_reel(self, analysis: dict, niche: str, style: str) -> dict:
        return await self.create_full_auto_reel(analysis, niche, style)
