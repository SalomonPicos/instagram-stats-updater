import requests
import json
import os
from datetime import datetime

ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN")  # imposta su Render come Secret
BUSINESS_ACCOUNT_ID = os.environ.get("IG_BUSINESS_ID")  # imposta su Render come Secret
USERNAME = "salomonpicos"
GRAPH_API = "https://graph.facebook.com/v19.0"

# Recupera il numero di follower
def get_followers():
    url = f"{GRAPH_API}/{BUSINESS_ACCOUNT_ID}?fields=followers_count&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    return res.get("followers_count", 0)

# Recupera gli ultimi media (max 100)
def get_media():
    url = f"{GRAPH_API}/{BUSINESS_ACCOUNT_ID}/media?fields=id,timestamp&limit=100&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    return res.get("data", [])

# Recupera like, commenti e reach per un singolo media
def get_media_metrics(media_id):
    url = f"{GRAPH_API}/{media_id}?fields=like_count,comments_count,media_type&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    like_count = res.get("like_count", 0)
    comment_count = res.get("comments_count", 0)
    media_type = res.get("media_type", "UNKNOWN")

    reach = 0
    insights_url = f"{GRAPH_API}/{media_id}/insights?metric=reach&access_token={ACCESS_TOKEN}"
    insights = requests.get(insights_url).json()

    # ✅ Evita crash se il campo "data" manca
    if "data" in insights and isinstance(insights["data"], list):
        for item in insights["data"]:
            if item.get("name") == "reach":
                reach = item.get("values", [{}])[0].get("value", 0)
    else:
        print(f"⚠️ Nessun insight per media {media_id} (type: {media_type}) → Response: {insights}")

    return like_count, comment_count, reach

print("✨ Recupero follower count...")
followers = get_followers()

print("📊 Recupero lista post...")
media_items = get_media()

likes = []
comments = []
reaches = []

print("🔢 Calcolo metriche da post...")
for media in media_items:
    media_id = media["id"]
    try:
        like, comment, reach = get_media_metrics(media_id)
        likes.append(like)
        comments.append(comment)
        reaches.append(reach)
    except Exception as e:
        print(f"⚠️ Nessun insight per media {media_id}: {e}")

avg_likes = round(sum(likes) / len(likes), 1) if likes else 0
avg_comments = round(sum(comments) / len(comments), 1) if comments else 0
engagement_rate = round(((avg_likes + avg_comments) / followers) * 100, 2) if followers else 0
avg_reach = round(sum(reaches) / len(reaches), 1) if reaches else 0

print("🕜 Recupero daily reach...")
daily_reach = "1.4m"  # per ora lasciamo fisso, si aggiornerà poi da insights totali se necessario

# Dati da salvare in stats.json
data = {
    "username": USERNAME,
    "followers": followers,
    "posts": len(media_items),
    "avg_likes": avg_likes,
    "avg_comments": avg_comments,
    "engagement_rate": f"{engagement_rate}%",
    "avg_reach": f"{avg_reach:,}",
    "daily_reach": daily_reach,
    "total_impressions": "20.1m"  # per ora statica
}

# Salvataggio delle statistiche nel file stats.json
print("📝 Salvataggio delle statistiche in stats.json...")
with open("stats.json", "w") as f:
    json.dump(data, f, indent=2)
print("✅ Dati salvati in stats.json")

# GIT PUSH AUTOMATICO (solo su Render con repo collegato)
print("📤 Git push in corso...")
os.system("git config --global user.email 'render@bot.com'")
os.system("git config --global user.name 'Render Bot'")
os.system("git add stats.json")
os.system(f"git commit -m 'update all stats'")
os.system("git push -f origin HEAD:main")
print("🚀 Done!")
