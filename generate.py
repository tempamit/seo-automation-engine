import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_seo_article(target_keyword, cluster_topic, raw_transcript):
    """
    Takes a raw YouTube transcript, trims it to fit Groq limits, 
    and rewrites it into an SEO blog post.
    """
    
    # --- SAFETY CHECK ---
    if not raw_transcript:
        print(f"⚠️ No transcript found for '{target_keyword}'. Skipping generation.")
        return None

    # --- CHUNK LOGIC ---
    words = raw_transcript.split()
    if len(words) > 7000:
        print(f"✂️ Transcript too long ({len(words)} words). Trimming to 7000 words...")
        raw_transcript = " ".join(words[:7000])
    # -------------------

    system_instruction = """
    You are an elite human tech editor. 
    Rewrite the provided transcript into a polished, humanized, SEO-optimized blog post.
    - If Hindi, translate to English.
    - Use 8th-grade level English.
    - Vary sentence lengths. No AI buzzwords.
    - Output strictly in raw HTML (h2, h3, p, ul).
    """

    user_prompt = f"""
    Target SEO Title: {target_keyword}
    Niche Cluster: {cluster_topic}
    Output Language: English
    
    SOURCE MATERIAL (YouTube Transcript):
    \"\"\"
    {raw_transcript}
    \"\"\"

    INSTRUCTIONS:
    1. Analyze the transcript above. It may be in English or Hindi.
    2. If it is in Hindi, accurately translate the technical advice into English.
    3. Transform the spoken words into a structured, helpful blog post.
    4. Ensure the content is original, human-sounding, and highly readable.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=4096
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        # Check if it's still a rate limit error even after trimming
        if "rate_limit_exceeded" in str(e).lower():
            print("❌ Rate Limit hit again. Try a shorter video or wait a minute.")
        print(f"❌ Groq Generation Error: {e}")
        return None

if __name__ == "__main__":
    # Quick test block to ensure variables are working
    test_keyword = "Windows 11 Troubleshooting Test"
    test_topic = "Tech Support"
    test_transcript = "Hello friends, today I will show you how to fix Windows 11 slow speed. Pehle aap settings mein jaiye..."
    
    print("🧪 Testing Groq Brain...")
    result = generate_seo_article(test_keyword, test_topic, test_transcript)
    if result:
        print("✅ Brain is functional! Sample output received.")
        print(result[:200] + "...") # Print first 200 chars
    else:
        print("❌ Brain test failed.")