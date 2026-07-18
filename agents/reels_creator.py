"""
АГЕНТ 2: Креатор Reels — ПРОФЕССИОНАЛЬНОЕ КРАСИВОЕ ВИДЕО 1080x1920
- Veo 3.1 (если есть биллинг)
- Mixkit проф сток-видео (БЕСПЛАТНО, без ключа, реально красивое видео 9.7MB)
- Flux фото (фолбек)

Работает на moviepy 1.0.3
"""
import time, os, uuid, textwrap, json, requests, urllib.parse, random
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL_TEXT, GEMINI_MODEL_VIDEO

os.makedirs("generated_videos", exist_ok=True)
os.makedirs("generated_images", exist_ok=True)

MIXKIT_FITNESS_VIDEOS = {
    "home": [5056, 3441],
    "gym": [27019, 21271, 100522],
    "squats": [232, 21271],
    "bike": [40249],
    "all": [5056, 27019, 21271, 232, 40249, 100522, 3441]
}

class ReelsCreatorAgent:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.text_model = GEMINI_MODEL_TEXT
        self.video_model = GEMINI_MODEL_VIDEO

    async def generate_concept(self, analysis: dict, niche: str, style: str) -> dict:
        prompt = f"""Ты — сценарист Reels фитнес 2026, ниша {niche}, стиль {style}, анализ {analysis}
Верни JSON: {{"title":"...", "hook":"УБЕРИ ЖИВОТ В КРОВАТИ", "script":"00:00-00:02 хук", "veo_prompt":"Vertical 9:16 video...", "imagen_prompts":["Beautiful fitness girl...", "Flat belly...", "Girl drinking smoothie..."], "stock_keywords":"home / gym / squats", "negative_prompt":"blurry", "caption":"Подпись с CTA", "voiceover_text":"Хочешь плоский живот? Делай это 2 мин. Сохрани!"}} Только JSON."""
        response = self.client.models.generate_content(model=self.text_model, contents=prompt)
        text = response.text.strip().replace("```json","").replace("```","").strip()
        try:
            data = json.loads(text)
        except:
            data = {
                "title": f"Reels про {niche}",
                "hook": "СТОП! ДЕЛАЕШЬ НЕ ТАК",
                "script": "00:00-00:03 Хук",
                "veo_prompt": f"Vertical 9:16 video, beautiful fitness girl, {style}, 8 seconds",
                "imagen_prompts": ["Beautiful fitness girl stretching at home morning aesthetic vertical 9:16 photorealistic 8k", "Flat belly healthy woman aesthetic soft light vertical", "Girl with green smoothie aesthetic kitchen morning vertical"],
                "stock_keywords": "home",
                "negative_prompt": "blurry",
                "caption": f"🔥 {niche} Сохрани!",
                "voiceover_text": f"Хочешь результат в {niche}? Делай так!",
            }
        return data

    async def try_veo_generation(self, veo_prompt: str, negative_prompt: str) -> dict:
        video_id = str(uuid.uuid4())[:8]
        output_path = f"generated_videos/reel_veo_{video_id}.mp4"
        try:
            operation = self.client.models.generate_videos(model=self.video_model, prompt=veo_prompt, config={"aspect_ratio":"9:16","negative_prompt":negative_prompt,"duration_seconds":8})
            while not operation.done:
                time.sleep(10)
                operation = self.client.operations.get(operation)
            generated_video = operation.response.generated_videos[0]
            self.client.files.download(file=generated_video.video)
            generated_video.video.save(output_path)
            return {"success": True, "path": output_path, "method": "veo", "video_id": video_id}
        except Exception as e:
            return {"success": False, "error": str(e), "method": "veo"}

    async def download_mixkit_video(self, keywords: str, video_id: str) -> str:
        niche_lower = (keywords or "").lower()
        if "дом" in niche_lower or "home" in niche_lower or "ленив" in niche_lower or "кроват" in niche_lower:
            candidates = MIXKIT_FITNESS_VIDEOS["home"]
        elif "зал" in niche_lower or "gym" in niche_lower:
            candidates = MIXKIT_FITNESS_VIDEOS["gym"]
        elif "присед" in niche_lower or "squat" in niche_lower:
            candidates = MIXKIT_FITNESS_VIDEOS["squats"]
        else:
            candidates = MIXKIT_FITNESS_VIDEOS["all"]
        chosen_id = random.choice(candidates)
        print(f"[Mixkit] Выбрал ID {chosen_id} для '{keywords}'")
        for res in ["1080","720"]:
            url = f"https://assets.mixkit.co/videos/{chosen_id}/{chosen_id}-{res}.mp4"
            local_path = f"generated_videos/mixkit_{chosen_id}_{res}.mp4"
            if os.path.exists(local_path) and os.path.getsize(local_path) > 100000:
                return local_path
            try:
                print(f"[Mixkit] Скачиваю {url}...")
                r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=45, stream=True)
                if r.status_code == 200:
                    with open(local_path,'wb') as f:
                        for chunk in r.iter_content(8192):
                            f.write(chunk)
                    print(f"[Mixkit] ✅ {local_path} {os.path.getsize(local_path)//1024}KB")
                    return local_path
            except Exception as e:
                print(f"[Mixkit] Ошибка {e}")
        return None

    async def generate_images_beautiful(self, imagen_prompts: list, video_id: str) -> list:
        image_paths = []
        print(f"[Flux] Генерю {len(imagen_prompts)} кадра...")
        for i, prompt in enumerate(imagen_prompts[:3]):
            beautiful_prompt = f"{prompt}, beautiful fitness influencer, aesthetic, soft natural light, photorealistic, ultra detailed, 8k, professional photography, vertical 9:16"
            final_prompt = f"{beautiful_prompt}, instagram aesthetic"
            img_path = f"generated_images/{video_id}_{i}_beautiful.jpg"
            try:
                encoded = urllib.parse.quote(final_prompt)
                url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&model=flux&enhance=true"
                r = requests.get(url, timeout=60)
                if r.status_code==200 and len(r.content)>10000:
                    with open(img_path,'wb') as f:
                        f.write(r.content)
                    print(f"[Flux] ✅ Кадр {i}")
                else:
                    raise Exception(f"Bad {r.status_code}")
            except Exception as e:
                print(f"[Flux] Ошибка {i}: {e}")
                from PIL import Image
                img = Image.new('RGB',(1080,1920),color=(255,183,197))
                img.save(img_path)
            if os.path.exists(img_path):
                image_paths.append(img_path)
        return image_paths

    async def generate_voiceover_auto(self, text: str, video_id: str) -> str:
        audio_path = f"generated_videos/{video_id}_voice.mp3"
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='ru', slow=False)
            tts.save(audio_path)
            return audio_path
        except Exception as e:
            print(f"[TTS] {e}")
            return None

    async def assemble_professional_reel(self, stock_video_path: str, voice_path: str, concept: dict, video_id: str) -> str:
        output_path = f"generated_videos/reel_PRO_{video_id}.mp4"
        print(f"[PRO] Собираю проф Reels из {stock_video_path}...")
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, ImageClip
            from PIL import Image, ImageDraw, ImageFont

            clip = VideoFileClip(stock_video_path)
            if clip.duration > 8:
                start = max(0, (clip.duration-8)/2)
                clip = clip.subclip(start, start+8)
            else:
                clip = clip.loop(duration=8)

            w,h = clip.size
            target_ratio = 9/16
            if w/h > target_ratio:
                new_w = int(h*target_ratio)
                x1 = (w-new_w)//2
                clip = clip.crop(x1=x1, y1=0, x2=x1+new_w, y2=h)
            clip = clip.resize((1080,1920))

            # Текст оверлей
            try:
                hook = concept.get("hook","СТОП!")[:35]
                txt_img = Image.new('RGBA',(1080,1920),(0,0,0,0))
                draw = ImageDraw.Draw(txt_img)
                draw.rectangle([0,0,1080,380], fill=(0,0,0,150))
                try:
                    font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",90)
                    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",45)
                except:
                    font_big = ImageFont.load_default()
                    font_small = ImageFont.load_default()
                lines = textwrap.wrap(hook.upper(), width=13)
                y=30
                for line in lines[:2]:
                    draw.text((40,y), line, fill=(255,255,255), font=font_big, stroke_width=3, stroke_fill=(0,0,0))
                    y+=125
                draw.rectangle([0,1650,1080,1920], fill=(0,0,0,110))
                draw.text((50,1680),"Сохрани • Сделай завтра • Подпишись", fill=(255,255,255), font=font_small)
                draw.text((50,1750), concept.get("title","")[:40], fill=(255,255,255), font=font_small)
                tmp_txt = f"/tmp/pro_text_{video_id}.png"
                txt_img.save(tmp_txt)
                txt_clip = ImageClip(tmp_txt).set_duration(clip.duration)
                final = CompositeVideoClip([clip, txt_clip])
            except Exception as e:
                print(f"Text overlay fail {e}")
                final = clip

            if voice_path and os.path.exists(voice_path):
                try:
                    audio = AudioFileClip(voice_path)
                    if audio.duration > final.duration:
                        audio = audio.subclip(0, final.duration)
                    final = final.set_audio(audio)
                except Exception as e:
                    print(f"Audio {e}")

            final.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', bitrate="5000k", threads=4, logger=None, preset='medium')
            print(f"[PRO] ✅ Готов {output_path} {os.path.getsize(output_path)//1024}KB")
            return output_path
        except Exception as e:
            print(f"[PRO] Ошибка {e}")
            import traceback; traceback.print_exc()
            return None

    async def assemble_reel_beautiful(self, image_paths: list, voice_path: str, concept: dict, video_id: str) -> str:
        output_path = f"generated_videos/reel_BEAUTIFUL_{video_id}.mp4"
        print(f"[Flux] Сборка из {len(image_paths)} фото...")
        try:
            from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
            clips=[]
            per_clip=8/len(image_paths)
            for idx,img_path in enumerate(image_paths):
                clip=ImageClip(img_path).set_duration(per_clip+0.5)
                clip=clip.resize(height=1920).crop(x_center=clip.w/2, width=1080, height=1920)
                clip=clip.resize(lambda t: 1+0.1*t/per_clip)
                if idx>0:
                    clip=clip.crossfadein(0.5)
                clips.append(clip)
            final=concatenate_videoclips(clips, method="compose", padding=-0.5)
            if final.duration>8:
                final=final.subclip(0,8)
            if voice_path and os.path.exists(voice_path):
                try:
                    audio=AudioFileClip(voice_path)
                    if audio.duration>final.duration:
                        audio=audio.subclip(0,final.duration)
                    final=final.set_audio(audio)
                except:
                    pass
            final.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac', threads=4, logger=None)
            return output_path
        except Exception as e:
            print(f"Flux assembler {e}")
            return None

    async def create_full_auto_reel(self, analysis: dict, niche: str, style: str) -> dict:
        video_id = str(uuid.uuid4())[:6]
        concept = await self.generate_concept(analysis, niche, style)
        veo_result = await self.try_veo_generation(concept["veo_prompt"], concept.get("negative_prompt",""))
        if veo_result["success"]:
            return {"concept":concept,"video":veo_result,"method":"veo"}
        print(f"[PRO MODE] Mixkit для '{concept.get('stock_keywords')}'")
        stock_path = await self.download_mixkit_video(concept.get("stock_keywords","fitness")+" "+niche, video_id)
        if stock_path:
            voice_path = await self.generate_voiceover_auto(concept.get("voiceover_text",""), video_id)
            pro_video = await self.assemble_professional_reel(stock_path, voice_path, concept, video_id)
            if pro_video and os.path.exists(pro_video):
                return {"concept":concept,"video":{"success":True,"path":pro_video,"method":"pro_mixkit_stock","video_id":video_id},"method":"pro_stock"}
        print("[BEAUTIFUL] Mixkit не сработал, Flux")
        image_paths = await self.generate_images_beautiful(concept.get("imagen_prompts",[]), video_id)
        voice_path = await self.generate_voiceover_auto(concept.get("voiceover_text",""), video_id)
        final_video_path = await self.assemble_reel_beautiful(image_paths, voice_path, concept, video_id)
        return {"concept":concept,"video":{"success":True if final_video_path and os.path.exists(final_video_path) else False,"path":final_video_path,"method":"beautiful_flux","video_id":video_id},"method":"beautiful"}

    async def generate_video(self, veo_prompt: str, negative_prompt: str = "", aspect_ratio: str = "9:16") -> dict:
        return await self.try_veo_generation(veo_prompt, negative_prompt)
    async def create_full_reel(self, analysis: dict, niche: str, style: str) -> dict:
        return await self.create_full_auto_reel(analysis, niche, style)
