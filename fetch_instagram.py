import requests
import json
import os
from datetime import datetime

print("\n🔧 Codice versione 4.0 in esecuzione...")

ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN")
USER_ID = os.environ.get("IG_USER_ID")
USERNAME = "salomonpicos"
GRAPH_API = "https://graph.facebook.com/v19.0"

def get_ig_account_id():
    url = f"{GRAPH_API}/{USER_ID}?fields=instagram_business_account&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    ig_account = res.get("instagram_business_account")
    return ig_account.get("id") if ig_account else None

def get_followers(ig_account_id):
    url = f"{GRAPH_API}/{ig_account_id}?fields=followers_count&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    return res.get("followers_count", 0)

def get_media(ig_account_id):
    url = f"{GRAPH_API}/{ig_account_id}/media?fields=id,timestamp&limit=100&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    return res.get("data", [])

def get_media_metrics(media_id):
    url = f"{GRAPH_API}/{media_id}?fields=like_count,comments_count,media_type&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    like_count = res.get("like_count", 0)
    comment_count = res.get("comments_count", 0)

    reach = 0
    impressions = 0
    insights_url = f"{GRAPH_API}/{media_id}/insights?metric=reach,impressions&access_token={ACCESS_TOKEN}"
    insights = requests.get(insights_url).json()
    if "data" in insights and isinstance(insights["data"], list):
        for item in insights["data"]:
            if item.get("name") == "reach":
                reach = item.get("values", [{}])[0].get("value", 0)
            if item.get("name") == "impressions":
                impressions = item.get("values", [{}])[0].get("value", 0)
    return like_count, comment_count, reach, impressions

print("📥 Inizio fetch...")
print("🔗 Recupero ID account Instagram collegato...")
ig_account_id = get_ig_account_id()

print("✨ Recupero follower count...")
followers = get_followers(ig_account_id)

print("📊 Recupero lista post...")
media_items = get_media(ig_account_id)
print(f"📦 Totale media trovati: {len(media_items)}")

likes, comments, reaches, impressions = [], [], [], []

print("🔢 Calcolo metriche da post...")
for media in media_items:
    media_id = media["id"]
    try:
        like, comment, reach, impression = get_media_metrics(media_id)
        likes.append(like)
        comments.append(comment)
        reaches.append(reach)
        impressions.append(impression)
    except Exception as e:
        print(f"⚠️ Errore media {media_id}: {e}")

avg_likes = round(sum(likes) / len(likes), 1) if likes else 0
avg_comments = round(sum(comments) / len(comments), 1) if comments else 0
engagement_rate = round(((avg_likes + avg_comments) / followers) * 100, 2) if followers else 0
avg_reach = round(sum(reaches) / len(reaches), 1) if reaches else 0

print("🕜 Recupero daily reach...")
daily_reach = "1.4m"  # placeholder per ora

print("📝 Salvataggio delle statistiche in stats.json...")
data = {
    "username": USERNAME,
    "followers": followers,
    "posts": len(media_items),
    "avg_likes": avg_likes,
    "avg_comments": avg_comments,
    "engagement_rate": f"{engagement_rate}%",
    "avg_reach": f"{avg_reach:.1f}",
    "daily_reach": daily_reach,
    "total_impressions": f"{int(sum(impressions)):,}".replace(",", "")  # numerico puro
}

with open("stats.json", "w") as f:
    json.dump(data, f, indent=2)

print("✅ Dati salvati in stats.json")

print("📤 Git push in corso...")
os.system("git config --global user.email 'render@bot.com'")
os.system("git config --global user.name 'Render Bot'")
os.system("git add stats.json")
os.system(f"git commit -m 'update all stats'")
os.system("git push -f origin HEAD:main")
print("🚀 Done!")
