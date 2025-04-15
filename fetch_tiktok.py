# fetch_tiktok.py
import os
import asyncio
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
                browser_type="webkit"
            )

            user = api.user(username=USERNAME)
            print(f"✅ Connessione riuscita con l'utente: {USERNAME}")

    except Exception as e:
        print(f"❌ Errore TikTok API: {e}")

if __name__ == "__main__":
    asyncio.run(main())
