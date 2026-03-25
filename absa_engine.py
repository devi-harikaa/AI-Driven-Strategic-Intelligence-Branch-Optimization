import pandas as pd
import os
from transformers import pipeline
from deep_translator import GoogleTranslator

print("⏳ Loading BERT Sentiment Model...")
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

ASPECT_MAP = {
    'Food': ['taste','burger','chicken','fresh','stale','zinger','spicy','quality','salty','cold'],
    'Service': ['staff','slow','fast','delivery','order','waiter','delay','rude','behavior'],
    'Ambience': ['clean','decor','music','place','atmosphere','crowd','hygiene','dirty'],
    'Pricing': ['price','cost','expensive','discount','value','offer','bill']
}

def translate_to_english(text):
    """Auto-translates any regional text (Telugu/Hindi/Hinglish) to English."""
    try:
        # Only translate if text is not empty and has non-ascii or looks mixed
        if not text or len(str(text)) < 3: return ""
        return GoogleTranslator(source='auto', target='en').translate(str(text))
    except:
        return str(text) # Fallback to original if offline/error

def get_aspect_sentiment(text):
    scores = {k:0.0 for k in ASPECT_MAP}; counts = {k:0 for k in ASPECT_MAP}
    text = str(text).lower()

    for aspect, keywords in ASPECT_MAP.items():
        if any(word in text for word in keywords):
            # Limit to 512 tokens for BERT safety
            result = sentiment_pipeline(text[:512])[0]
            # Map labels to scores
            score = result['score'] if result['label']=="POSITIVE" else -result['score']
            scores[aspect]+=score
            counts[aspect]+=1

    return {k:(scores[k]/counts[k] if counts[k]>0 else 0.0) for k in ASPECT_MAP}

def run_sentiment_analysis(restaurant_name):
    file_path = f'reviews_{restaurant_name}.csv'
    if not os.path.exists(file_path): return pd.DataFrame()

    df = pd.read_csv(file_path)
    df.drop_duplicates(subset=['Review_Text'], inplace=True)

    print("🌍 Translating Reviews (this may take a moment)...")
    # Apply Translation Step
    df['Translated_Text'] = df['Review_Text'].apply(translate_to_english)

    # Run Analysis on TRANSLATED text
    results = df['Translated_Text'].apply(get_aspect_sentiment).apply(pd.Series)
    
    # Merge results but keep original text for display if needed
    df_processed = pd.concat([df, results], axis=1)
    df_processed['Date'] = pd.to_datetime(df_processed['Date']).dt.normalize()

    return df_processed