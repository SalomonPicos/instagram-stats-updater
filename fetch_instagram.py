import requests
import json
import os
import subprocess

ACCESS_TOKEN = os.getenv("IG_TOKEN")
IG_USER_ID = os.getenv("IG_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = "SalomonPicos"  # tuo username GitHub

# Headers per le richieste
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# Step 1: Recupera followers
print("✨ Recupero follower count...")
user_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}?fields=followers_count&access_token={ACCESS_TOKEN}"
user_data = requests.get(user_url).json()
followers = user_data.get("followers_count", 0)

# Step 2: Recupera media (fino a 100 post)
print("📊 Recupero lista post...")
media_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media?fields=id,caption&limit=100&access_token={ACCESS_TOKEN}"
media_data = requests.get(media_url).json()
media_ids = [m["id"] for m in media_data.get("data", [])]

like_total = 0
comment_total = 0
reach_total = 0
impressions_total = 0
post_count = 0

# Step 3: Per ogni media recupera dati
print("🔢 Calcolo metriche da post...")
for media_id in media_ids:
    fields_url = f"https://graph.facebook.com/v22.0/{media_id}?fields=like_count,comments_count,insights.metric(reach,impressions)&access_token={ACCESS_TOKEN}"
    response = requests.get(fields_url).json()

    try:
        like_total += response.get("like_count", 0)
        comment_total += response.get("comments_count", 0)

        insights = response.get("insights", {}).get("data", [])
        reach_val = next((i["values"][0]["value"] for i in insights if i["name"] == "reach"), 0)
        impressions_val = next((i["values"][0]["value"] for i in insights if i["name"] == "impressions"), 0)

        reach_total += reach_val
        impressions_total += impressions_val

        post_count += 1
    except Exception as e:
        print(f"⚠️ Errore media {media_id}: {e}")

# Step 4: Recupera daily reach ultimi 7 giorni
print("🕜 Recupero daily reach...")
daily_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/insights?metric=reach&period=day&access_token={ACCESS_TOKEN}"
daily_data = requests.get(daily_url).json()
daily_values = daily_data.get("data", [{}])[0].get("values", [])
avg_daily_reach = int(sum(d["value"] for d in daily_values) / len(daily_values)) if daily_values else 0

# Step 5: Calcolo finali
avg_likes = like_total / post_count if post_count else 0
avg_comments = comment_total / post_count if post_count else 0
avg_reach = reach_total / post_count if post_count else 0
engagement_rate = ((avg_likes + avg_comments) / followers * 100) if followers else 0

# Step 6: Salva su stats.json
stats = {
    "username": "salomonpicos",
    "followers": followers,
    "posts": post_count,
    "avg_likes": round(avg_likes, 1),
    "avg_comments": round(avg_comments, 1),
    "engagement_rate": f"{engagement_rate:.2f}%",
    "avg_reach_per_post": int(avg_reach),
    "avg_daily_reach": avg_daily_reach,
    "total_impressions": impressions_total
}

with open("stats.json", "w") as f:
    json.dump(stats, f, indent=2)

print("📂 stats.json aggiornato.")

# Step 7: Commit e push su GitHub
print("📤 Git push in corso...")
subprocess.run('git config --global user.name "RenderBot"', shell=True)
subprocess.run('git config --global user.email "render@bot.com"', shell=True)
subprocess.run('git add stats.json', shell=True)
subprocess.run('git commit -m "update all stats"', shell=True)
push_url = f'https://{GITHUB_TOKEN}@github.com/{USERNAME}/instagram-stats-updater.git'
subprocess.run(f'git push {push_url} HEAD:main --force', shell=True)
print("🚀 Done!")