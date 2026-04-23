from database import SessionLocal
from models import Site, Cluster

def seed_database():
    db = SessionLocal()
    try:
        # 1. Register the Website
        existing_site = db.query(Site).filter(Site.name == "AI ToolKit Hub").first()
        if existing_site:
            print("⚠️ Site already exists in the database. Using existing record.")
            site = existing_site
        else:
            print("🌱 Seeding Site: AI ToolKit Hub...")
            site = Site(
                name="AI ToolKit Hub",
                domain="https://lemonchiffon-curlew-185730.hostingersite.com"
            )
            db.add(site)
            db.commit()
            db.refresh(site)
            print(f"✅ Site Created! Database ID: {site.id}")

        # 2. Define your 10 Strategic Clusters
        core_clusters = [
            "AI Tools for Marketing",
            "AI Tools for Students",
            "AI Tools for Developers",
            "AI Tools for Designers",
            "AI Tools for Small Business",
            "Best Free AI Tools",
            "AI Tool Comparisons",
            "AI Productivity Calculators",
            "AI Automation Tutorials",
            "AI Software Reviews"
        ]

        # 3. Inject Clusters into the Database
        print("🌱 Seeding Topic Clusters...")
        added_count = 0
        for topic in core_clusters:
            existing_cluster = db.query(Cluster).filter(
                Cluster.topic_name == topic, 
                Cluster.site_id == site.id
            ).first()
            
            if not existing_cluster:
                new_cluster = Cluster(site_id=site.id, topic_name=topic)
                db.add(new_cluster)
                added_count += 1
        
        db.commit()
        if added_count > 0:
            print(f"✅ {added_count} Topic Clusters successfully seeded!")
        else:
            print("⚠️ Clusters already exist. No new data added.")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()