# fetch_all.py
import subprocess
import sys
import time

def run_script(script_name):
    print(f"\n🚀 Avvio {script_name}...")
    try:
        result = subprocess.run(["python", script_name], check=True, capture_output=True, text=True)
        print(f"✅ {script_name} completato con successo!")
        print("--- STDOUT ---")
        print(result.stdout)
        print("--------------")
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore durante l'esecuzione di {script_name}:")
        print("--- STDOUT ---")
        print(e.stdout)
        print("--- STDERR ---")
        print(e.stderr)
        print("--------------")

if __name__ == "__main__":
    start_time = time.time()
    print("\n========================")
    print("🎯 Inizio fetch_all.py")
    print("========================")

    run_script("fetch_instagram.py")
    run_script("fetch_tiktok.py")

    duration = round(time.time() - start_time, 2)
    print("========================")
    print(f"✅ Fine fetch_all.py in {duration} sec")
    print("========================")