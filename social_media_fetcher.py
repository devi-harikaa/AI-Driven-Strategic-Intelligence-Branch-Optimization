import pandas as pd
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import tweepy
import instaloader
from datetime import datetime
import os
import re

# --- API KEYS ---
YOUTUBE_API_KEY = "AIzaSyACdYW15HYQDNumJobsneVOe7U55v2wKcA"
TWITTER_TOKEN = "AAAAAAAAAAAAAAAAAAAAACrm3QEAAAAAtHWiKae5bedFS1%2BhR1xBodjuvnk%3DU8GthSBc72CBZe3RHTmA7tb8w5KctQGgBwXHveHQKMpvfyft58"

# --- SMART FILTERS ---
KEYWORDS = {
    'food': ['taste', 'food', 'chicken', 'burger', 'meal', 'spicy', 'salty', 'fresh', 'stale', 'yummy', 'delicious', 'bad', 'undercooked', 'crispy'],
    'service': ['service', 'staff', 'waiter', 'manager', 'slow', 'rude', 'fast', 'late', 'ignore', 'polite', 'serving', 'order'],
    'ambience': ['place', 'vibe', 'atmosphere', 'noise', 'clean', 'dirty', 'smell', 'ac', 'music', 'decor', 'crowd'],
    'pricing': ['price', 'cost', 'expensive', 'cheap', 'value', 'bill', 'money', 'worth']
}

def is_useful_review(text, branch):
    """
    Returns True if the review is worth saving.
    - If Branch is Known: Always save (it's specific).
    - If General: Only save if it mentions a specific Aspect (Food/Service/etc).
    """
    if branch != "General": return True # Specific branch reviews are always valuable
    
    text = text.lower()
    # Check if it mentions any valid aspect
    for category in KEYWORDS.values():
        if any(word in text for word in category):
            return True
            
    return False # Discard vague "General" reviews

def is_junk_comment(text):
    clean_text = re.sub(r'[^\w\s]', '', text)
    words = clean_text.split()
    if len(words) < 3: return True 
    junk_keywords = ['subscribe', 'channel', 'promo', 'salary', 'giveaway', 'boss', 'dede', 'money', 'link in bio', 'good video']
    if any(k in text.lower() for k in junk_keywords): return True
    return False

def get_video_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t['text'] for t in transcript_list]).replace("\n", " ")
    except: return None

def search_and_fetch_reviews(restaurant_name, branches):
    new_reviews = []
    
    # 1. LOAD HISTORY
    if os.path.exists(f'reviews_{restaurant_name}.csv'):
        try:
            existing_df = pd.read_csv(f'reviews_{restaurant_name}.csv')
            existing_df['Review_Text'] = existing_df['Review_Text'].astype(str)
            existing_df['Date'] = pd.to_datetime(existing_df['Date'])
            print(f"📂 Loaded {len(existing_df)} existing reviews.")
        except: existing_df = pd.DataFrame(columns=['Date', 'Branch', 'Platform', 'Review_Text'])
    else: existing_df = pd.DataFrame(columns=['Date', 'Branch', 'Platform', 'Review_Text'])

    print(f"🕵️‍♂️ FETCHING & FILTERING REAL DATA FOR: {branches}")

    def attribute_branch(text, branch_list):
        if not isinstance(text, str): return "General"
        for b in branch_list:
            if b.lower() in text.lower(): return b
        return "General" 

    # --- 🎥 YOUTUBE ---
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        for branch in branches:
            query = f"{restaurant_name} {branch} food review"
            search = youtube.search().list(q=query, part="id,snippet", maxResults=5, type="video").execute()
            
            for item in search.get('items', []):
                vid_id = item['id'].get('videoId')
                if vid_id:
                    # Transcript
                    transcript = get_video_transcript(vid_id)
                    if transcript:
                        b_name = attribute_branch(transcript, branches)
                        if is_useful_review(transcript, b_name):
                            new_reviews.append([datetime.now(), b_name, 'YouTube Transcript', transcript])
                    
                    # Comments
                    try:
                        comments = youtube.commentThreads().list(part="snippet", videoId=vid_id, maxResults=15, textFormat="plainText").execute()
                        for c in comments['items']:
                            txt = c['snippet']['topLevelComment']['snippet']['textDisplay']
                            if not is_junk_comment(txt):
                                b_name = attribute_branch(txt, branches)
                                if is_useful_review(txt, b_name):
                                    new_reviews.append([datetime.now(), b_name, 'YouTube Comment', txt])
                    except: continue
    except: pass

    # --- 📷 INSTAGRAM ---
    try:
        L = instaloader.Instaloader()
        tag_name = restaurant_name.replace(" ", "").lower()
        hashtag = instaloader.Hashtag.from_name(L.context, tag_name)
        count = 0
        for post in hashtag.get_posts():
            if count >= 10: break
            if post.caption and len(post.caption) > 20: 
                b_name = attribute_branch(post.caption, branches)
                if is_useful_review(post.caption, b_name):
                    new_reviews.append([post.date, b_name, 'Instagram', post.caption])
            count += 1
    except: pass 

    # --- 🐦 TWITTER ---
    try:
        if "YOUR_TWITTER" not in TWITTER_TOKEN:
            client = tweepy.Client(bearer_token=TWITTER_TOKEN)
            for branch in branches:
                tweets = client.search_recent_tweets(query=f"{restaurant_name} {branch} -is:retweet lang:en", max_results=10)
                if tweets.data:
                    for tweet in tweets.data:
                        b_name = attribute_branch(tweet.text, branches)
                        if is_useful_review(tweet.text, b_name):
                            new_reviews.append([datetime.now(), b_name, 'Twitter', tweet.text])
    except: pass 

    # 2. SAVE & MERGE
    if new_reviews:
        new_df = pd.DataFrame(new_reviews, columns=['Date', 'Branch', 'Platform', 'Review_Text'])
        new_df['Date'] = pd.to_datetime(new_df['Date'])
        
        combined_df = pd.concat([existing_df, new_df])
        combined_df.drop_duplicates(subset=['Review_Text'], keep='last', inplace=True)
        combined_df = combined_df[combined_df['Review_Text'].str.strip() != ""]
        
        combined_df.to_csv(f'reviews_{restaurant_name}.csv', index=False)
        print(f"✅ CLEANED & SAVED. Total Valid Reviews: {len(combined_df)}")
        return combined_df
    else:
        return existing_df