# fetch_tiktok.py
import os
import json
import asyncio
from datetime import datetime, timedelta
from TikTokApi import TikTokApi
from dotenv import load_dotenv

load_dotenv()

print("\n🔧 fetch_tiktok.py avviato...")

USERNAME = "salomonpicos"
ms_token = os.environ.get("TIKTOK_TOKEN")

if not ms_token:
    raise EnvironmentError("❌ Variabile ambiente TIKTOK_TOKEN mancante")

async def main():
    try:
        async with TikTokApi() as api:
            await api.create_sessions(
                ms_tokens=[ms_token],
                num_sessions=1,
                sleep_after=3,
                headless=False,
                browser="webkit"

         )

            user = api.user(username=USERNAME)
            videos = [video async for video in user.videos(count=100)]

            print(f"📦 Trovati {len(videos)} video pubblici per {USERNAME}")

            user_info = await user.info()
            followers = user_info.user_info.stats.follower_count

            total_views = total_likes = total_comments = 0
            views_last_28d = 0
            now = datetime.now()

            for video in videos:
                stats = video.as_dict.get("stats", {})
                create_time = datetime.fromtimestamp(video.as_dict.get("createTime", 0))

                total_views += stats.get("playCount", 0)
                total_likes += stats.get("diggCount", 0)
                total_comments += stats.get("commentCount", 0)

                if now - create_time <= timedelta(days=28):
                    views_last_28d += stats.get("playCount", 0)

            total_posts = len(videos)
            avg_views = round(total_views / total_posts, 1) if total_posts else 0
            avg_likes = round(total_likes / total_posts, 1) if total_posts else 0
            avg_comments = round(total_comments / total_posts, 1) if total_posts else 0

            engagement_rate = round(((total_likes + total_comments) / total_views) * 100, 2) if total_views else 0
            avg_daily_views = round(views_last_28d / 28) if views_last_28d else 0

            stats = {
                "username": USERNAME,
                "followers": followers,
                "posts": total_posts,
                "avg_views": avg_views,
                "avg_likes": avg_likes,
                "avg_comments": avg_comments,
                "engagement_rate": f"{engagement_rate}%",
                "daily_views": avg_daily_views,
                "total_views": total_views,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            with open("tiktok_stats.json", "w") as f:
                json.dump(stats, f, indent=2)

            print("✅ Statistiche salvate in tiktok_stats.json")

    except Exception as e:
        print(f"❌ Errore TikTok API: {e}")

if __name__ == "__main__":
    asyncio.run(main())