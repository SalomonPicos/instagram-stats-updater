# Script Python per ottenere dati Instagram via Graph API e salvarli in un JSON

import requests
import json

# === CONFIGURA QUI I TUOI DATI ===
import os
ACCESS_TOKEN = os.getenv('IG_TOKEN')
IG_USER_ID = os.getenv('IG_ID')


# === URL DI BASE ===
BASE_URL = f'https://graph.facebook.com/v17.0/{IG_USER_ID}'

# === RICHIESTA POST RECENTI CON METRICHE ===
media_url = f'{BASE_URL}/media?fields=id,caption,like_count,comments_count,timestamp&limit=100&access_token={ACCESS_TOKEN}'
media_data = requests.get(media_url).json()

# === RACCOLTA DEI DATI ===
posts = media_data.get('data', [])

# Calcola media like/commenti
total_likes = sum(post.get('like_count', 0) for post in posts)
total_comments = sum(post.get('comments_count', 0) for post in posts)

avg_likes = round(total_likes / len(posts), 1) if posts else 0
avg_comments = round(total_comments / len(posts), 1) if posts else 0

# === RICHIESTA DATI PROFILO ===
profile_url = f'{BASE_URL}?fields=followers_count,media_count,username&access_token={ACCESS_TOKEN}'
profile_data = requests.get(profile_url).json()

# Calcola engagement rate
followers = profile_data.get('followers_count', 1)
engagement_rate = round(((avg_likes + avg_comments) / followers) * 100, 2)

# === CREAZIONE FILE JSON ===
data = {
    'username': profile_data.get('username'),
    'followers': followers,
    'posts': profile_data.get('media_count'),
    'avg_likes': avg_likes,
    'avg_comments': avg_comments,
    'engagement_rate': f'{engagement_rate}%'
}

with open('stats.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Dati salvati in stats.json")



import subprocess

subprocess.run('git config --global user.name "render-bot"', shell=True)
subprocess.run('git config --global user.email "render@auto.com"', shell=True)
subprocess.run('git pull origin main', shell=True)  # Per sicurezza
subprocess.run('git add stats.json', shell=True)
subprocess.run('git commit -m "update stats.json"', shell=True)
subprocess.run('git push https://$GITHUB_TOKEN@github.com/tuo-username/instagram-stats-updater.git', shell=True)
