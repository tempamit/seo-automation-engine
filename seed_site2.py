from database import SessionLocal
from models import Site, Cluster

def seed_site2():
    db = SessionLocal()
    try:
        # 1. Register Site 2
        print("🌱 Seeding Site 2: Problem Solving Hub...")
        site2 = Site(
            name="Problem Solving Hub",
            domain="PENDING_URL" # We will update this later if needed
        )
        db.add(site2)
        db.commit()
        db.refresh(site2)
        print(f"✅ Site 2 Created! Database ID: {site2.id}")

        # 2. Define the 10 Clusters for the Fix & How-To Niche
        site2_clusters = [
            "Windows 11 Troubleshooting",
            "MacBook Quick Fixes",
            "iPhone Battery & Screen Issues",
            "Android Performance Tweaks",
            "WiFi & Router Troubleshooting",
            "Chrome & Browser Fixes",
            "Printer Offline Solutions",
            "Software Crash Guides",
            "Smart Home Device Fixes",
            "Daily Tech Hacks"
        ]

        # 3. Inject Clusters into the Database
        print("🌱 Seeding Topic Clusters for Site 2...")
        added_count = 0
        for topic in site2_clusters:
            existing = db.query(Cluster).filter(
                Cluster.topic_name == topic, 
                Cluster.site_id == site2.id
            ).first()
            
            if not existing:
                new_cluster = Cluster(site_id=site2.id, topic_name=topic)
                db.add(new_cluster)
                added_count += 1
        
        db.commit()
        print(f"✅ {added_count} Topic Clusters successfully seeded for Site 2!")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_site2()