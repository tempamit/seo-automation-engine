# Save this as autopilot.py in your backend folder
import subprocess
import time

def run_engine():
    print("🚀 STARTING AUTOPILOT...")
    
    # 1. Find new trends
    print("📡 Phase 1: Scouring YouTube for new transcripts...")
    subprocess.run(["python", "discover_trends.py"])
    
    # 2. Process one article from the queue
    print("✍️ Phase 2: Generating and publishing content...")
    subprocess.run(["python", "pipeline.py"])
    
    print("🏁 Cycle Complete.")

if __name__ == "__main__":
    run_engine()