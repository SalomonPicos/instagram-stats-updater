# fetch_all.py
import subprocess
import sys

def run_script(script_name):
    print(f"\n🚀 Avvio {script_name}...")
    try:
        result = subprocess.run(["python", script_name], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore durante l'esecuzione di {script_name}:")
        print(e.stdout)
        print(e.stderr)

if __name__ == "__main__":
    run_script("fetch_instagram.py")
    run_script("fetch_tiktok.py")