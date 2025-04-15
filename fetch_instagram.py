import requests
import json
import os

print("\\n🔧 Codice versione 6.1 in esecuzione...")

ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN")  # su Render
PAGE_ID = os.environ.get("FB_PAGE_ID")            # su Render
USERNAME = "salomonpicos"
GRAPH_API = "https://graph.facebook.com/v19.0"

def get_ig_user_id():
    print("🔗 Recupero ID account Instagram collegato...")
    url = f"{GRAPH_API}/{PAGE_ID}?fields=instagram_business_account&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    ig_account = res.get("instagram_business_account", {}).get("id", None)
    if not ig_account:
        print(f"❌ Errore: nessun account Instagram collegato alla pagina. Risposta:\\n{json.dumps(res, indent=2)}")
        return None
    return ig_account

def get_followers(ig_user_id):
    url = f"{GRAPH_API}/{ig_user_id}?fields=followers_count&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    return res.get("followers_count", 0)

def get_media(ig_user_id):
    url = f"{GRAPH_API}/{ig_user_id}/media?fields=id,media_type,media_product_type,timestamp&limit=100&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    return res.get("data", [])

def get_media_metrics(media_id):
    url = f"{GRAPH_API}/{media_id}?fields=like_count,comments_count,media_type&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()

    like_count = res.get("like_count", 0)
    comment_count = res.get("comments_count", 0)

    insights_url = f"{GRAPH_API}/{media_id}/insights?metric=ig_reels_aggregated_all_plays_count&access_token={ACCESS_TOKEN}"
    insights = requests.get(insights_url).json()

    views = 0
    if "data" in insights:
        for item in insights["data"]:
            if item.get("name") == "ig_reels_aggregated_all_plays_count":
                views = item.get("values", [{}])[0].get("value", 0)
    else:
        print(f"⚠️ Nessun insight per media {media_id}: {insights}")

    return like_count, comment_count, views


print("📥 Inizio fetch...")

ig_user_id = get_ig_user_id()
if not ig_user_id:
    exit(1)

print("✨ Recupero follower count...")
followers = get_followers(ig_user_id)

print("📊 Recupero lista post...")
media_items = get_media(ig_user_id)
print(f"📦 Totale media trovati: {len(media_items)}")

likes = []
comments = []
views = []

print("🔢 Calcolo metriche da post...")
for media in media_items:
    media_id = media["id"]
    media_type = media.get("media_type", "")
    try:
        like, comment, view = get_media_metrics(media_id, media_type)
        likes.append(like)
        comments.append(comment)
        views.append(view)
    except Exception as e:
        print(f"⚠️ Errore media {media_id}: {e}")

print(f"🪵 Views totali trovate: {sum(views)} su {len(views)} post")
print(f"🔍 Prime 10 views: {views[:10]}")

avg_likes = round(sum(likes) / len(likes), 1) if likes else 0
avg_comments = round(sum(comments) / len(comments), 1) if comments else 0
engagement_rate = round(((avg_likes + avg_comments) / followers) * 100, 2) if followers else 0

last_30_views = views[-30:] if len(views) >= 30 else views
avg_reach = round(sum(last_30_views) / len(last_30_views), 1) if last_30_views else 0
total_impressions = sum(views)
daily_reach = "1.4m"  # Statico

print("📝 Salvataggio delle statistiche in stats.json...")
data = {
    "username": USERNAME,
    "followers": followers,
    "posts": len(media_items),
    "avg_likes": avg_likes,
    "avg_comments": avg_comments,
    "engagement_rate": f"{engagement_rate}%",
    "avg_reach": avg_reach,
    "daily_reach": daily_reach,
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