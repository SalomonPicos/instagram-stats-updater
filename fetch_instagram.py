# fetch_instagram.py
import requests
import json
import os
from datetime import datetime, timedelta

print("\n🔧 Codice versione 6.6 in esecuzione...")

ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN")
PAGE_ID = os.environ.get("FB_PAGE_ID")
USERNAME = "salomonpicos"
GRAPH_API = "https://graph.facebook.com/v19.0"

if not ACCESS_TOKEN or not PAGE_ID:
    raise EnvironmentError("Missing IG_ACCESS_TOKEN or FB_PAGE_ID environment variable")

def safe_get(url):
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        print(f"⚠️ Errore richiesta a {url}: {e}")
        return {}

def get_ig_user_id():
    print("🔗 Recupero ID account Instagram collegato...")
    url = f"{GRAPH_API}/{PAGE_ID}?fields=instagram_business_account&access_token={ACCESS_TOKEN}"
    res = safe_get(url)
    ig_account = res.get("instagram_business_account", {}).get("id", None)
    if not ig_account:
        print(f"❌ Errore: nessun account Instagram collegato. Risposta:\n{json.dumps(res, indent=2)}")
        return None
    return ig_account

def get_followers(ig_user_id):
    url = f"{GRAPH_API}/{ig_user_id}?fields=followers_count&access_token={ACCESS_TOKEN}"
    res = safe_get(url)
    return res.get("followers_count", 0)

def get_media(ig_user_id):
    print("📊 Recupero lista post...")
    media = []
    url = f"{GRAPH_API}/{ig_user_id}/media?fields=id,timestamp&limit=100&access_token={ACCESS_TOKEN}"

    while url:
        res = safe_get(url)
        data = res.get("data", [])
        media.extend(data)
        url = res.get("paging", {}).get("next")

    return media

def get_media_metrics(media_id):
    url = f"{GRAPH_API}/{media_id}?fields=like_count,comments_count,media_type,timestamp&access_token={ACCESS_TOKEN}"
    res = safe_get(url)
    like_count = res.get("like_count", 0)
    comment_count = res.get("comments_count", 0)
    timestamp = res.get("timestamp")

    reach = 0
    insights_url = f"{GRAPH_API}/{media_id}/insights?metric=reach&access_token={ACCESS_TOKEN}"
    insights = safe_get(insights_url)

    if "error" in insights:
        error = insights["error"]
        if error.get("error_subcode") == 2108006:
            print(f"⏭️ Media {media_id} ignorato (pre-business account).")
            return None
        else:
            print(f"⚠️ Nessun insight reach per media {media_id}: {json.dumps(error)}")
            return 0, 0, 0, timestamp

    if "data" in insights:
        for item in insights["data"]:
            if item.get("name") == "reach":
                reach = item.get("values", [{}])[0].get("value", 0)

    return like_count, comment_count, reach, timestamp

def get_account_daily_reach(ig_user_id):
    since = (datetime.now() - timedelta(days=28)).date().isoformat()
    until = datetime.now().date().isoformat()
    url = f"{GRAPH_API}/{ig_user_id}/insights?metric=reach&period=day&since={since}&until={until}&access_token={ACCESS_TOKEN}"
    res = safe_get(url)

    if "data" in res:
        reach_data = res["data"][0]["values"]
        total = sum(day.get("value", 0) for day in reach_data)
        return round(total / 28)
    else:
        print(f"⚠️ Errore nel recuperare reach globale: {json.dumps(res)}")
        return 0

def file_changed(path, new_data):
    if not os.path.exists(path): return True
    with open(path) as f:
        old_data = json.load(f)
    return old_data != new_data

print("📥 Inizio fetch...")
ig_user_id = get_ig_user_id()
if not ig_user_id:
    exit(1)

print("✨ Recupero follower count...")
followers = get_followers(ig_user_id)
media_items = get_media(ig_user_id)
print(f"📦 Totale media trovati: {len(media_items)}")

likes, comments, views, timestamps = [], [], [], []
valid_posts = 0
likes_30d = 0
comments_30d = 0
reach_30d = 0

print("🔢 Calcolo metriche da post...")
cutoff_date = datetime.now() - timedelta(days=30)

for media in media_items:
    media_id = media["id"]
    try:
        result = get_media_metrics(media_id)
        if result is not None:
            like, comment, reach, timestamp = result
            post_date = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if post_date >= cutoff_date:
                likes_30d += like
                comments_30d += comment
                reach_30d += reach
            likes.append(like)
            comments.append(comment)
            views.append(reach)
            timestamps.append(timestamp)
            valid_posts += 1
    except Exception as e:
        print(f"⚠️ Errore media {media_id}: {e}")

print(f"🪵 Views totali trovate: {sum(views)} su {valid_posts} post validi")

avg_likes = round(sum(likes) / len(likes), 1) if likes else 0
avg_comments = round(sum(comments) / len(comments), 1) if comments else 0

engagement_rate = 0
if reach_30d > 0:
    engagement_rate = round(((likes_30d + comments_30d) / reach_30d) * 100, 2)

last_30_views = views[-30:] if len(views) >= 30 else views
avg_reach = round(sum(last_30_views) / len(last_30_views), 1) if last_30_views else 0

average_daily_reach = get_account_daily_reach(ig_user_id)
total_impressions = sum(views)

data = {
    "username": USERNAME,
    "followers": followers,
    "posts": valid_posts,
    "avg_likes": avg_likes,
    "avg_comments": avg_comments,
    "engagement_rate": f"{engagement_rate}%",
    "avg_reach": avg_reach,
    "daily_reach": average_daily_reach,
    "total_impressions": total_impressions,
    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

if file_changed("stats.json", data):
    print("📝 Salvataggio delle statistiche in stats.json...")
    with open("stats.json", "w") as f:
        json.dump(data, f, indent=2)

    print("📤 Git push in corso...")
    os.system("git config --global user.email 'salomonpicosofficial@gmail.com'")
    os.system("git config --global user.name 'Lorenzo'")
    os.system("git add stats.json")
    os.system("git commit -m 'update all stats'")
    os.system("git push origin main")
    print("🚀 Done!")
else:
    print("✅ Nessuna modifica ai dati. Salvataggio e push non necessari.")