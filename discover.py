import os
from groq import Groq
from dotenv import load_dotenv
from database import SessionLocal
from models import Site, Cluster, Article, ArticleStatus

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def discover_keywords(cluster_name: str, count: int = 10):
    db = SessionLocal()
    try:
        # 1. Find the Cluster in the database
        cluster = db.query(Cluster).filter(Cluster.topic_name == cluster_name).first()
        if not cluster:
            print(f"❌ Cluster '{cluster_name}' not found in database.")
            return

        print(f"🔍 Analyzing Cluster: '{cluster.topic_name}'...")
        print(f"🧠 Asking Groq to generate {count} high-intent SEO keywords...")

        # 2. Ask Groq to generate the keywords
        prompt = f"""
        You are an expert SEO strategist. 
        Generate exactly {count} long-tail, high-intent SEO article titles/keywords for the topic cluster: "{cluster.topic_name}".
        These should be targeted at small business owners, freelancers, and marketers.
        
        CRITICAL: Return ONLY a comma-separated list of keywords. No bullet points, no numbers, no introductory text.
        Example: Best free AI writing tools for small businesses, Top AI image generators without watermarks, Free AI SEO software for beginners
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500
        )

        # 3. Clean and parse the output
        raw_output = response.choices[0].message.content.strip()
        keywords = [kw.strip() for kw in raw_output.split(',') if kw.strip()]

        # 4. Inject them into the Database
        added_count = 0
        for kw in keywords:
            # Check if keyword already exists to avoid duplicates
            existing = db.query(Article).filter(Article.target_keyword == kw).first()
            if not existing:
                new_article = Article(
                    cluster_id=cluster.id,
                    target_keyword=kw,
                    title=kw, # We'll use the keyword as the working title
                    status=ArticleStatus.PENDING
                )
                db.add(new_article)
                added_count += 1
        
        db.commit()
        print(f"✅ Successfully queued {added_count} new PENDING articles for generation!")

    except Exception as e:
        print(f"❌ Error during discovery: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Test discovery for Site 2
    discover_keywords("Windows 11 Troubleshooting", count=3)