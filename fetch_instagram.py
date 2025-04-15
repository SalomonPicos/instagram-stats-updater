import requests
import json
import os
from datetime import datetime

# Variabili di configurazione
ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN")  # Devi settarlo come secret su Render
BUSINESS_ACCOUNT_ID = os.environ.get("IG_BUSINESS_ID")  # Settato come secret su Render
GRAPH_API = "https://graph.facebook.com/v19.0"
USERNAME = "salomonpicos"

# Funzione per ottenere il numero di follower
def get_followers():
    url = f"{GRAPH_API}/{BUSINESS_ACCOUNT_ID}?fields=followers_count&access_token={ACCESS_TOKEN}"
    response = requests.get(url)
    data = response.json()
    return data.get("followers_count", 0)

# Funzione per ottenere gli ultimi 100 post
def get_media():
    url = f"{GRAPH_API}/{BUSINESS_ACCOUNT_ID}/media?fields=id,timestamp&limit=100&access_token={ACCESS_TOKEN}"
    response = requests.get(url)
    data = response.json()
    return data.get("data", [])

# Funzione per ottenere le metriche dei singoli post (like, commenti, reach)
def get_media_metrics(media_id):
    url = f"{GRAPH_API}/{media_id}?fields=like_count,comments_count&access_token={ACCESS_TOKEN}"
    response = requests.get(url)
    data = response.json()

    like_count = data.get("like_count", 0)
    comment_count = data.get("comments_count", 0)

    # Recupera insights per il reach del post
    insights_url = f"{GRAPH_API}/{media_id}/insights?metric=reach&access_token={ACCESS_TOKEN}"
    insights = requests.get(insights_url).json()
    reach = 0

    if "data" in insights:
        for item in insights["data"]:
            if item["name"] == "reach":
                reach = item["values"][0]["value"]

    return like_count, comment_count, reach

# Funzione principale che aggiorna stats.json
def update_stats():
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
            print(f"⚠️ Errore durante il recupero per media {media_id}: {e}")

    avg_likes = round(sum(likes) / len(likes), 1) if likes else 0
    avg_comments = round(sum(comments) / len(comments), 1) if comments else 0
    engagement_rate = round(((avg_likes + avg_comments) / followers) * 100, 2) if followers else 0
    avg_reach = round(sum(reaches) / len(reaches), 1) if reaches else 0

    print("🕜 Recupero daily reach...")
    daily_reach = "1.4m"  # Per ora lasciamo fisso, ma si potrebbe rendere dinamico

    # Salva i dati nel file stats.json
    data = {
        "username": USERNAME,
        "followers": followers,
        "posts": len(media_items),
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "engagement_rate": f"{engagement_rate}%",
        "avg_reach": f"{avg_reach:,}",
        "daily_reach": daily_reach,
        "total_impressions": "20.1m"  # Per ora questo valore è fisso
    }

    # Scrivi nel file stats.json
    with open("stats.json", "w") as f:
        json.dump(data, f, indent=2)

    print("📂 stats.json aggiornato.")
    return data

# Funzione per il commit su GitHub
def git_commit_push():
    os.system("git config --global user.email 'render@bot.com'")
    os.system("git config --global user.name 'Render Bot'")

    print("📤 Git push in corso...")
    os.system("git add stats.json")
    os.system("git commit -m 'update all stats'")
    os.system("git push -f origin main")
    print("🚀 Done!")

# Main
if __name__ == "__main__":
    update_stats()
    git_commit_push()
