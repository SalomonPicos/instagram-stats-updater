# fetch_tiktok.py
import os
import json
from datetime import datetime, timedelta
from TikTokApi import TikTokApi
from dotenv import load_dotenv

load_dotenv()

print("\n🔧 fetch_tiktok.py avviato...")

ms_token = os.environ.get("TIKTOK_TOKEN")
USERNAME = "salomonpicos"

if not ms_token:
    raise EnvironmentError("TIKTOK_TOKEN non definito nelle variabili ambiente")

try:
    api = TikTokApi(ms_token=ms_token)

    user = api.user(username=USERNAME)
    videos = user.videos(count=100)

    print(f"📦 Trovati {len(videos)} video pubblici per {USERNAME}")

    followers = user.info_full()["userInfo"]["stats"]["followerCount"]
    print(f"👥 Followers: {followers}")

    total_views, total_likes, total_comments = 0, 0, 0
    daily_views = []
    views_last_28d = 0
    now = datetime.now()

    for video in videos:
        stats = video.as_dict["stats"]
        create_time = datetime.fromtimestamp(video.as_dict["createTime"])

        views = stats["playCount"]
        likes = stats["diggCount"]
        comments = stats["commentCount"]

        total_views += views
        total_likes += likes
        total_comments += comments

        if now - create_time <= timedelta(days=28):
            views_last_28d += views
            daily_views.append((create_time.date(), views))

    total_posts = len(videos)
    avg_views = round(total_views / total_posts, 1) if total_posts else 0
    avg_likes = round(total_likes / total_posts, 1) if total_posts else 0
    avg_comments = round(total_comments / total_posts, 1) if total_posts else 0

    engagement_rate = 0
    if total_views > 0:
        engagement_rate = round(((total_likes + total_comments) / total_views) * 100, 2)

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