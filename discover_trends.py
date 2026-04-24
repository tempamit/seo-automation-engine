from youtubesearchpython import VideosSearch
from youtube_transcript_api import YouTubeTranscriptApi
from database import SessionLocal
from models import Article, ArticleStatus, Cluster
import time
import requests

def get_free_proxies():
    """Fetches a list of free HTTP proxies."""
    try:
        response = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")
        if response.status_code == 200:
            return response.text.splitlines()
    except Exception as e:
        print(f"⚠️ Failed to fetch free proxies: {e}")
    return []

def get_video_transcript(video_id):
    # 1. Try without proxy first
    try:
        fetched_transcript = YouTubeTranscriptApi().fetch(video_id, languages=['en', 'hi'])
        transcript_data = fetched_transcript.to_raw_data()
        return " ".join([t['text'] for t in transcript_data])
    except Exception as e:
        print(f"🔄 VPS IP blocked for {video_id}. Attempting free proxies...")

    # 2. Try with a rotation of free proxies
    proxies_list = get_free_proxies()
    # Try the top 10 proxies from the list
    for proxy in proxies_list[:10]:
        proxy_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        try:
            # Note: youtube_transcript_api requires proxies passed as a dict
            fetched_transcript = YouTubeTranscriptApi().fetch(
                video_id, 
                languages=['en', 'hi'], 
                proxies=proxy_dict
            )
            transcript_data = fetched_transcript.to_raw_data()
            print(f"✅ Success using proxy: {proxy}")
            return " ".join([t['text'] for t in transcript_data])
        except:
            continue # Try next proxy if this one fails
            
    print(f"❌ All 10 free proxies failed for {video_id}.")
    return None

def discover_trending_content(cluster_name):
    db = SessionLocal()
    try:
        # Find the specific cluster in the database
        cluster = db.query(Cluster).filter(Cluster.topic_name == cluster_name).first()
        if not cluster:
            print(f"❌ Cluster '{cluster_name}' not found.")
            return

        print(f"🔍 Searching YouTube for trending content related to: '{cluster.topic_name}'...")
        
        # Search YouTube for the top 5 videos in this cluster
        videos_search = VideosSearch(cluster.topic_name, limit=5)
        results = videos_search.result()['result']

        queued_count = 0
        for video in results:
            video_id = video['id']
            video_title = video['title']
            video_link = video['link']

            # 1. Check if we have already scraped this video (Duplicate Source Check)
            existing_source = db.query(Article).filter(Article.source_url == video_link).first()
            if existing_source:
                print(f"⏭️ Skipping: We already processed '{video_title}'")
                continue

            # 2. Extract Transcript
            print(f"🎙️ Extracting transcript for: '{video_title}'...")
            transcript = get_video_transcript(video_id)
            
            # If there's no transcript or it's just a 30-second short, skip it
            if not transcript or len(transcript) < 500:
                print("⚠️ Transcript too short or unavailable. Skipping.")
                continue

            # 3. Queue for Rewriting
            new_article = Article(
                cluster_id=cluster.id,
                target_keyword=video_title, # We use the video title as the working title
                title=video_title,
                source_url=video_link,
                raw_content=transcript,     # Save the actual spoken words for Groq to rewrite
                status=ArticleStatus.PENDING
            )
            db.add(new_article)
            db.commit()
            queued_count += 1
            print(f"✅ Queued for rewrite: {video_title}")
            
            time.sleep(2) # Be polite to YouTube servers

        print(f"🎉 Successfully queued {queued_count} new trending videos for rewriting!")

    except Exception as e:
        print(f"❌ Error during discovery: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Feel free to change this to any of your clusters!
    discover_trending_content("Windows 11 Troubleshooting")