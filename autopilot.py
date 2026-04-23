import subprocess
import time
import sys

def run_engine():
    print("🚀 STARTING AUTOPILOT...")
    while True:
        try:
            print(f"📡 Phase 1: Scouring YouTube... [{time.ctime()}]")
            subprocess.run([sys.executable, "discover_trends.py"], check=True)
            
            print("✍️ Phase 2: Generating and publishing content...")
            subprocess.run([sys.executable, "pipeline.py"], check=True)
            
            print("🏁 Cycle Complete. Sleeping for 2 hours...")
            time.sleep(7200) # 2-hour delay
            
        except Exception as e:
            print(f"⚠️ Cycle encountered an error: {e}")
            print("😴 Error cooldown... waiting 10 minutes before retry.")
            time.sleep(600)

if __name__ == "__main__":
    run_engine()