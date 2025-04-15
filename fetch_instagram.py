import requests
import json
import os
from datetime import datetime, timedelta  # <-- IMPORT NUOVO

print("\n🔧 Codice versione 6.3 in esecuzione...")

ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN")
PAGE_ID = os.environ.get("FB_PAGE_ID")
USERNAME = "salomonpicos"
GRAPH_API = "https://graph.facebook.com/v19.0"

def get_ig_user_id():
    print("🔗 Recupero ID account Instagram collegato...")
    url = f"{GRAPH_API}/{PAGE_ID}?fields=instagram_business_account&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    ig_account = res.get("instagram_business_account", {}).get("id", None)
    if not ig_account:
        print(f"❌ Errore: nessun account Instagram collegato alla pagina. Risposta:\n{json.dumps(res, indent=2)}")
        return None
    return ig_account

def get_followers(ig_user_id):
    url = f"{GRAPH_API}/{ig_user_id}?fields=followers_count&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    return res.get("followers_count", 0)

def get_media(ig_user_id):
    print("📊 Recupero lista post...")
    media = []
    url = f"{GRAPH_API}/{ig_user_id}/media?fields=id,timestamp&limit=100&access_token={ACCESS_TOKEN}"

    while url:
        res = requests.get(url).json()
        data = res.get("data", [])
        media.extend(data)
        url = res.get("paging", {}).get("next")

    return media

def get_media_metrics(media_id):
    url = f"{GRAPH_API}/{media_id}?fields=like_count,comments_count,media_type&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    like_count = res.get("like_count", 0)
    comment_count = res.get("comments_count", 0)

    reach = 0
    insights_url = f"{GRAPH_API}/{media_id}/insights?metric=reach&access_token={ACCESS_TOKEN}"
    insights = requests.get(insights_url).json()

    if "error" in insights:
        error = insights["error"]
        if error.get("error_subcode") == 2108006:
            print(f"⏭️ Media {media_id} ignorato (pubblicato prima della conversione a business account).")
            return None
        else:
            print(f"⚠️ Nessun insight reach per media {media_id}: {json.dumps(error)}")
            return 0, 0, 0

    if "data" in insights:
        for item in insights["data"]:
            if item.get("name") == "reach":
                reach = item.get("values", [{}])[0].get("value", 0)

    return like_count, comment_count, reach

print("📥 Inizio fetch...")

ig_user_id = get_ig_user_id()
if not ig_user_id:
    exit(1)

print("✨ Recupero follower count...")
followers = get_followers(ig_user_id)

media_items = get_media(ig_user_id)
print(f"📦 Totale media trovati: {len(media_items)}")

likes = []
comments = []
views = []
valid_posts = 0
timestamps = []

print("🔢 Calcolo metriche da post...")
for media in media_items:
    media_id = media["id"]
    try:
        result = get_media_metrics(media_id)
        if result is not None:
            like, comment, reach = result
            likes.append(like)
            comments.append(comment)
            views.append(reach)
            timestamps.append(media["timestamp"])
            valid_posts += 1
    except Exception as e:
        print(f"⚠️ Errore media {media_id}: {e}")

print(f"🪵 Views totali trovate: {sum(views)} su {valid_posts} post validi")
print(f"🔍 Prime 10 views: {views[:10]}")

avg_likes = round(sum(likes) / len(likes), 1) if likes else 0
avg_comments = round(sum(comments) / len(comments), 1) if comments else 0

# 📉 Engagement rate per post / reach
engagement_rates = []
for like, comment, reach in zip(likes, comments, views):
    if reach > 0:
        post_engagement = ((like + comment) / reach) * 100
        engagement_rates.append(post_engagement)
engagement_rate = round(sum(engagement_rates) / len(engagement_rates), 2) if engagement_rates else 0

# 📊 Media reach degli ultimi 30 post
last_30_views = views[-30:] if len(views) >= 30 else views
avg_reach = round(sum(last_30_views) / len(last_30_views), 1) if last_30_views else 0

# 🗓️ Daily reach ultimi 28 giorni
cutoff_date = datetime.now().astimezone() - timedelta(days=28)
recent_reach = [
    reach for ts, reach in zip(timestamps, views)
    if datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z") > cutoff_date
]
average_daily_reach = round(sum(recent_reach) / 28) if recent_reach else 0

total_impressions = sum(views)

print("📝 Salvataggio delle statistiche in stats.json...")
data = {
    "username": USERNAME,
    "followers": followers,
    "posts": valid_posts,
    "avg_likes": avg_likes,
    "avg_comments": avg_comments,
    "engagement_rate": f"{engagement_rate}%",
    "avg_reach": avg_reach,
    "daily_reach": average_daily_reach,  # ✅ ora calcolato
    "total_impressions": total_impressions
}

with open("stats.json", "w") as f:
    json.dump(data, f, indent=2)

print("✅ Dati salvati in stats.json")
print("📤 Git push in corso...")
os.system("git config --global user.email 'salomonpicosofficial@gmail.com'")
os.system("git config --global user.name 'Lorenzo'")
os.system("git add stats.json")
os.system("git commit -m 'update all stats'")
os.system("git push origin main")
print("🚀 Done!")
