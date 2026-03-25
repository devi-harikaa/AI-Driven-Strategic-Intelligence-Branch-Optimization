# 🏢 Restaurant Branch Optimization system: AI-Driven Strategic Intelligence

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Random%20Forest-orange.svg)
![NLP](https://img.shields.io/badge/NLP-ABSA-green.svg)
![Firebase](https://img.shields.io/badge/Auth-Firebase-FFCA28.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

---

## 📌 Overview

**Branch_Optimization** is an enterprise-grade, multi-tenant SaaS platform built for large-scale restaurant chains. It acts as an autonomous strategic intelligence engine — merging financial transactional data with real-time customer sentiment to identify operational bottlenecks, forecast recovery timelines, and prescribe actionable management strategies.

> Instead of just showing *what* happened to sales, this AI engine explains *why* it happened — by correlating statistical financial anomalies with Aspect-Based Sentiment Analysis (ABSA) from live social media.

---

## ✨ Core Features

| Feature | Description |
|---|---|
| 🔐 **Multi-Tenant Architecture** | Secure, isolated data silos per brand (e.g., Domino's vs. KFC). Firebase auth dynamically routes each session to the correct database. |
| 📉 **Z-Score Anomaly Detection** | Statistically analyzes daily revenue against historical baselines to flag uncharacteristic sales crashes. |
| 🛒 **Transactional Laggard Identification** | Deep-dives into daily item volumes to pinpoint the exact menu item causing a revenue drop (e.g., French Fries, Zinger Burger). |
| 🧠 **Aspect-Based Sentiment Analysis** | Scrapes real-time reviews from YouTube, Twitter, and Instagram. Scores four operational pillars: **Food, Service, Ambience, and Pricing**. |
| 🤖 **AI Correlation & Strategy Engine** | Links the date of a sales crash to the lowest-scoring sentiment aspect and generates a prescriptive management action plan. |
| 📈 **ML Sales Forecaster** | Uses a `RandomForestRegressor` to predict future sales based on historical trends, day-of-week seasonality, and branch performance. |

---

## 🏗️ System Architecture & Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  1. DATA INGESTION                                              │
│     Firebase Auth → Upload sales.csv + transactions.csv         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  2. SOCIAL MEDIA FETCHER                                        │
│     YouTube API · Twitter (Tweepy) · Instaloader                │
└──────────────────────────────┬──────────────────────────────────┘
                               │
          ┌────────────────────┴────────────────────┐
          │                                         │
┌─────────▼──────────┐                   ┌──────────▼──────────┐
│  3a. FINANCIAL     │                   │  3b. TEXTUAL        │
│      PIPELINE      │                   │      PIPELINE       │
│  Z-Score Analysis  │                   │  Text Cleaning      │
│  Volumetric Drop   │                   │  ABSA Neural Scoring│
└─────────┬──────────┘                   └──────────┬──────────┘
          │                                         │
          └────────────────────┬────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  4. CORRELATION ENGINE                                          │
│     Root Cause Analysis · Strategy Card Generation             │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               |
                               │                                         
                     ┌─────────▼──────────┐                  
                     │  Streamlit UI      │                  
                     │  Strategy Cards    │                 
                     └────────────────────┘            
```

---

## 💻 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend / Web Framework** | Streamlit, `streamlit.components.v1` |
| **Data Processing** | Pandas, NumPy |
| **Machine Learning** | Scikit-Learn (`RandomForestRegressor`) |
| **NLP / Sentiment** | Transformers / BERT (Custom ABSA mapping) |
| **Social Scraping** | YouTube Data API v3, Tweepy (Twitter), Instaloader |
| **Cloud Auth & DB** | Google Firebase (Firestore, Admin SDK) |
| **Visualization** | Plotly Express |

---

## 📂 File Structure

```
Restaurant branch optimization system/
│
├── app.py                          # Main Streamlit app & UI routing
├── absa_engine.py                  # NLP logic for aspect-based sentiment scoring
├── social_media_fetcher.py         # YouTube, Twitter & Instagram API integration
├── sales_forecaster.py             # Random Forest predictive modelling
├── firebase_handler.py             # Cloud authentication & Firestore data sync
├── dashboard.py                    # Power BI embedded dashboard logic
├── requirements.txt                # Python package dependencies
├── requirement_packages.txt        # Supplementary package list
├── firebase_key.json               # 🔒 Firebase credentials (DO NOT COMMIT)
├── .gitignore
│
├── sample1/                        # Sample tenant data for testing
│
└── data/                           # Per-brand data silos
    ├── sales.csv
    ├── sales_KFC.csv
    ├── transactions.csv
    ├── transactions_KFC.csv
    ├── transactions_Domino's pizza.csv
    ├── reviews_KFC.csv
    ├── reviews_Domino's pizza.csv
    ├── sentiment_KFC.csv
    ├── sentiment_Domino's pizza.csv
    ├── sentiment_daily_avg.csv
    ├── sentiment_report.csv
    └── final_optimization_report.csv
```

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Driven-Strategic-Intelligence-Branch-Optimization.git
cd Restaurant Optimization
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory. 

```env
YOUTUBE_API_KEY=your_youtube_api_key_here
TWITTER_TOKEN=your_twitter_bearer_token_here
```

Also place your `firebase_key.json` credentials file in the root directory. This is required for Firestore database connection and user authentication.

### 5. Run the Application

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

---

## 🔐 Multi-Tenant Data Isolation

Each restaurant brand operates in a completely isolated data environment. On login, Firebase authenticates the session and dynamically routes the user to their brand-specific data silo. No data from one tenant (e.g., KFC) is ever accessible to another (e.g., Domino's), ensuring enterprise-grade data privacy.

---

## 🧠 How the AI Engine Works

1. A **Z-Score anomaly** flags a date where revenue deviated significantly from the historical baseline.
2. The **Transactional Laggard** module identifies which specific menu item saw the sharpest volume drop on that date.
3. The **ABSA engine** independently scores the four operational pillars (Food, Service, Ambience, Pricing) from scraped customer reviews on the same date.
4. The **Correlation Engine** links the financial crash to the lowest-scoring sentiment aspect and generates a prescriptive action plan in the form of a **Strategy Card**.

---

## 📈 Sales Forecasting

The `sales_forecaster.py` module trains a `RandomForestRegressor` on historical sales data, incorporating:

- Rolling revenue averages
- Day-of-week seasonality encoding
- Branch-level performance baselines

Forecasts are visualized interactively via Plotly Express within the Streamlit dashboard.

---
Outputs
<img width="1918" height="958" alt="Screenshot 2026-03-25 182758" src="https://github.com/user-attachments/assets/ead08788-f526-4527-a0fd-63a648103c3f" />
<img width="1920" height="1128" alt="Screenshot 2026-03-25 165039" src="https://github.com/user-attachments/assets/35cd4df7-94fa-413d-9f6f-4713a841f971" />
<img width="1916" height="966" alt="Screenshot 2026-03-25 175709" src="https://github.com/user-attachments/assets/1b604e18-17a6-45c8-822f-56f2eebb87f1" />
<img width="1908" height="887" alt="Screenshot 2026-03-25 175654" src="https://github.com/user-attachments/assets/5b15db31-046d-40aa-9173-ce4ea7ebbfb1" />
<img width="1915" height="1165" alt="Screenshot 2026-03-25 175646" src="https://github.com/user-attachments/assets/7e55b68d-424b-40e1-8bc1-7f0549465ccc" />
<img width="1919" height="913" alt="Screenshot 2026-03-25 175623" src="https://github.com/user-attachments/assets/8bfd1c28-d159-4a63-b20d-2f49708e7301" />
<img width="1910" height="962" alt="Screenshot 2026-03-25 175538" src="https://github.com/user-attachments/assets/6aa1e309-5942-46e3-8f79-ad69455a1911" />
<img width="1576" height="837" alt="Screenshot 2026-03-25 175441" src="https://github.com/user-attachments/assets/51552fd8-4d9e-481b-a2e7-5634adc309ed" />
<img width="1909" height="962" alt="Screenshot 2026-03-25 175429" src="https://github.com/user-attachments/assets/d79c9ae8-5798-4dba-b4be-c01c3a7bfef1" />
<img width="1918" height="929" alt="Screenshot 2026-03-25 175416" src="https://github.com/user-attachments/assets/97123934-84f2-459e-b493-7d862e1ab7bb" />
<img width="1915" height="1013" alt="Screenshot 2026-03-25 175400" src="https://github.com/user-attachments/assets/ebbc8cc4-93b2-4031-be28-d0a6eb16d7c6" />
<img width="1916" height="1171" alt="Screenshot 2026-03-25 175344" src="https://github.com/user-attachments/assets/15b7bcdc-4bd1-44a2-adcb-2ebc5fb2f13a" />
<img width="1919" height="850" alt="Screenshot 2026-03-25 175332" src="https://github.com/user-attachments/assets/079d67d6-56b2-423b-932c-be0a25cfd581" />
<img width="1919" height="936" alt="Screenshot 2026-03-25 175308" src="https://github.com/user-attachments/assets/7fb314e8-5cf2-4345-ad5f-654bc0e7a25b" />
<img width="1872" height="1042" alt="Screenshot 2026-03-25 171218" src="https://github.com/user-attachments/assets/5b8d00fe-a742-43a5-be58-ba42a85c08ca" />
## 🔮 Future Scope

| Upgrade | Description |
|---|---|
| **Cloud Data Warehouse** | Migrate local CSV silos to Google BigQuery or Snowflake for scalable storage. |
| **Real-time Streaming** | Replace batch CSV uploads with a live Kafka or Pub/Sub pipeline for continuous ingestion. |
| **LLM Strategy Generation** | Replace rule-based strategy cards with GPT-4 / Claude-powered natural language action plans. |

---

## ⚠️ Important Notes

- `firebase_key.json` is listed in `.gitignore` and must **never** be pushed to a public repository.
- Social media scraping must comply with the Terms of Service of each respective platform.
- YouTube Data API has a daily quota limit — monitor usage in the Google Cloud Console.

---

## 📄 License

This project is licensed under the MIT License.
