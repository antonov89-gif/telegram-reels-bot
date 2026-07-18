"""
АГЕНТ 3: Паблишер
Публикует Reels в Instagram и Telegram
"""
import os
import requests

class PublisherAgent:
    def __init__(self):
        from config import IG_USER_ID, IG_ACCESS_TOKEN, IG_USERNAME, IG_PASSWORD
        self.ig_user_id = IG_USER_ID
        self.ig_access_token = IG_ACCESS_TOKEN
        self.ig_username = IG_USERNAME
        self.ig_password = IG_PASSWORD

    def get_publish_instruction(self, video_path: str, caption: str) -> str:
        return f"""
✅ Видео готово: {video_path}

Для автопубликации в Instagram нужно:

ВАРИАНТ 1 (Graph API - для бизнес аккаунтов):
1. Залить видео на публичный URL (S3 / Cloudinary)
2. POST https://graph.facebook.com/v19.0/{self.ig_user_id}/media
   - media_type=REELS
   - video_url=...
   - caption={caption}
3. Затем POST /media_publish

ВАРИАНТ 2 (instagrapi - проще):
Логин и пароль в .env и вызов client.clip_upload()

Сейчас файл готов к отправке в Telegram и скачиванию.
"""

    async def publish_to_instagram_graph_api(self, public_video_url: str, caption: str) -> dict:
        """Публикация через официальный Graph API"""
        if not self.ig_user_id or not self.ig_access_token:
            return {"success": False, "error": "IG_USER_ID / IG_ACCESS_TOKEN не заданы в .env"}

        try:
            # Шаг 1: Создать контейнер
            url = f"https://graph.facebook.com/v19.0/{self.ig_user_id}/media"
            data = {
                "media_type": "REELS",
                "video_url": public_video_url,
                "caption": caption,
                "access_token": self.ig_access_token
            }
            r1 = requests.post(url, data=data).json()
            if "id" not in r1:
                return {"success": False, "error": r1}

            creation_id = r1["id"]

            # Шаг 2: Опубликовать
            url2 = f"https://graph.facebook.com/v19.0/{self.ig_user_id}/media_publish"
            data2 = {
                "creation_id": creation_id,
                "access_token": self.ig_access_token
            }
            r2 = requests.post(url2, data=data2).json()
            return {"success": True, "result": r2}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def publish_via_instagrapi(self, video_path: str, caption: str) -> dict:
        """Публикация через instagrapi (неофициально, но работает)"""
        if not self.ig_username or not self.ig_password:
            return {"success": False, "error": "IG_USERNAME / IG_PASSWORD не заданы"}

        try:
            from instagrapi import Client
            cl = Client()
            cl.login(self.ig_username, self.ig_password)
            media = cl.clip_upload(video_path, caption=caption)
            return {"success": True, "media_id": str(media.id)}
        except Exception as e:
            return {"success": False, "error": str(e)}
