import os
import requests
from dotenv import load_dotenv
from database import SessionLocal
from models import Article, ArticleStatus, Cluster, Site
from generate import generate_seo_article
import datetime
import urllib.parse
import random

load_dotenv()

def get_site_credentials(site_name):
    """Dynamically fetches the correct WP credentials based on the site name."""
    if site_name == "AI ToolKit Hub":
        return os.getenv("WP_URL_SITE1"), os.getenv("WP_USER_SITE1"), os.getenv("WP_APP_PASSWORD_SITE1")
    elif site_name == "Problem Solving Hub":
        return os.getenv("WP_URL_SITE2"), os.getenv("WP_USER_SITE2"), os.getenv("WP_APP_PASSWORD_SITE2")
    return None, None, None

def upload_featured_image(keyword, wp_url, wp_user, wp_app_password):
    print(f"🎨 Generating optimized featured image for '{keyword}'...")
    
    safe_keyword = urllib.parse.quote_plus(keyword)
    image_api_url = f"https://image.pollinations.ai/prompt/professional%20technology%20concept%20{safe_keyword}?width=1200&height=630&nologo=true"
    
    img_response = requests.get(image_api_url)
    if img_response.status_code != 200:
        print("❌ Failed to generate image.")
        return None

    media_url = f"{wp_url}/wp-json/wp/v2/media"
    headers = {
        "Content-Disposition": f"attachment; filename={keyword.replace(' ', '_')}_featured.jpg",
        "Content-Type": "image/jpeg"
    }
    
    print(f"📤 Uploading image to WordPress Media Library at {wp_url}...")
    media_upload = requests.post(
        media_url,
        headers=headers,
        data=img_response.content,
        auth=(wp_user, wp_app_password)
    )
    
    if media_upload.status_code == 201:
        media_id = media_upload.json()['id']
        print(f"✅ Image uploaded! Media ID: {media_id}")
        return media_id
    else:
        print(f"❌ Image upload failed: {media_upload.text}")
        return None

def run_pipeline():
    # ==========================================
    # PHASE 1: READ DATABASE & CLOSE CONNECTION
    # ==========================================
    db = SessionLocal()
    try:
        pending_articles = db.query(Article).filter(Article.status == ArticleStatus.PENDING).all()
        
        if not pending_articles:
            print("📭 Queue is empty. Run discover.py to fill it up!")
            return

        # Smart Alternation Logic
        last_published = db.query(Article).filter(Article.status == ArticleStatus.PUBLISHED).order_by(Article.published_at.desc()).first()
        article = None
        
        if last_published:
            last_cluster = db.query(Cluster).filter(Cluster.id == last_published.cluster_id).first()
            last_site_id = last_cluster.site_id
            
            different_site_articles = []
            for a in pending_articles:
                c = db.query(Cluster).filter(Cluster.id == a.cluster_id).first()
                if c.site_id != last_site_id:
                    different_site_articles.append(a)
            
            if different_site_articles:
                article = random.choice(different_site_articles)
                print("🔀 Smart-Routing: Forcing alternation to the other website...")
        
        if not article:
            article = random.choice(pending_articles)
            print("🎲 Standard-Routing: Picking random available article...")

        cluster = db.query(Cluster).filter(Cluster.id == article.cluster_id).first()
        site = db.query(Site).filter(Site.id == cluster.site_id).first()

        # Save data to local variables so we can safely close the database connection
        target_article_id = article.id
        target_keyword = article.target_keyword
        target_cluster_topic = cluster.topic_name
        target_site_name = site.name
        
    finally:
        db.close() # Close connection to prevent Hostinger timeout

    print(f"⚙️ PIPELINE INITIATED: Target '{target_keyword}' -> Routing to {target_site_name}...")

    # ==========================================
    # PHASE 2: EXTERNAL API CALLS (Heavy Lifting)
    # ==========================================
    wp_url, wp_user, wp_app_password = get_site_credentials(target_site_name)
    
    if not wp_url:
        print(f"❌ Could not find credentials for site: {target_site_name}")
        return

    wp_api_posts_url = f"{wp_url}/wp-json/wp/v2/posts"
    print(f"🔍 Checking {target_site_name} for duplicates...")
    check_req = requests.get(f"{wp_api_posts_url}?search={urllib.parse.quote_plus(target_keyword)}", auth=(wp_user, wp_app_password))
    
    is_duplicate = False
    generation_failed = False
    wp_data = None

    if check_req.status_code == 200 and len(check_req.json()) > 0:
        print("⚠️ Article already exists on this website! Skipping generation.")
        is_duplicate = True
    else:
        # We must pass the actual transcript (article.raw_content) as the 3rd argument
        raw_html = generate_seo_article(target_keyword, target_cluster_topic, article.raw_content)
        
        if not raw_html:
            print("❌ Pipeline stalled at generation phase.")
            generation_failed = True
        else:
            # Generate Image & Push to WP
            featured_media_id = upload_featured_image(target_keyword, wp_url, wp_user, wp_app_password)
            data = {"title": target_keyword, "content": raw_html, "status": "publish"}
            if featured_media_id:
                data["featured_media"] = featured_media_id

            print(f"🚀 Pushing final content & image to {target_site_name}...")
            response = requests.post(wp_api_posts_url, json=data, auth=(wp_user, wp_app_password))

            if response.status_code == 201:
                wp_data = response.json()
            else:
                print(f"❌ WordPress Publishing Failed: {response.text}")
                generation_failed = True

    # ==========================================
    # PHASE 3: RECONNECT TO DATABASE & UPDATE
    # ==========================================
    db_update = SessionLocal()
    try:
        article_to_update = db_update.query(Article).filter(Article.id == target_article_id).first()
        
        if is_duplicate:
            article_to_update.status = ArticleStatus.PUBLISHED
            db_update.commit()
            print("💾 Database updated: Marked duplicate as PUBLISHED.")
            return

        if generation_failed:
            article_to_update.status = ArticleStatus.FAILED
            db_update.commit()
            print("💾 Database updated: Marked as FAILED.")
            return

        if wp_data:
            print(f"✅ Success! Article pushed to {target_site_name} (Post ID: {wp_data['id']}).")
            article_to_update.status = ArticleStatus.PUBLISHED
            article_to_update.wp_post_id = wp_data['id']
            article_to_update.published_at = datetime.datetime.now(datetime.timezone.utc)
            db_update.commit()

    except Exception as e:
        print(f"❌ Database Update Error: {e}")
        db_update.rollback()
    finally:
        db_update.close()

if __name__ == "__main__":
    run_pipeline()