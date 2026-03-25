import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# --- CONFIGURATION ---
start_date = datetime(2025, 10, 1) # Starting from Oct 2025
days = 100
branches = ["Hyderabad", "Visakhapatnam"]
items = ["Zinger Burger", "Chicken Wings", "French Fries", "Pepsi", "Rice Bowl"]

# --- STORAGE ---
sales_data = []
trans_data = []
review_data = []

print("⏳ Generating 100 Days of Evolving Data...")

for i in range(days):
    current_date = start_date + timedelta(days=i)
    date_str = current_date.strftime('%Y-%m-%d')
    month = current_date.month
    
    # --- SCENARIO LOGIC ---
    # Oct (10): Bad Food Quality -> Low Sales
    # Nov (11): Bad Service -> Recovery Phase
    # Dec (12): Great Ambience/Holidays -> Peak Sales
    # Jan (01): Pricing Complaints -> Sales Dip
    
    for branch in branches:
        # 1. SALES GENERATION
        if month == 10: 
            base_rev = np.random.randint(6000, 7500) # LOW
            focus = "Food"
            sentiment = "Negative"
        elif month == 11:
            base_rev = np.random.randint(8000, 9500) # MED
            focus = "Service"
            sentiment = "Negative"
        elif month == 12:
            base_rev = np.random.randint(12000, 15000) # HIGH
            focus = "Ambience"
            sentiment = "Positive"
        else:
            base_rev = np.random.randint(7000, 8500) # DIP
            focus = "Pricing"
            sentiment = "Negative"

        # Add noise
        revenue = base_rev + np.random.randint(-500, 500)
        sales_data.append([date_str, branch, revenue, np.random.randint(50, 90)])

        # 2. TRANSACTION GENERATION
        for item in items:
            qty = np.random.randint(20, 50)
            
            # Correlate Item Crashes with Monthly Theme
            if month == 10 and item == "Chicken Wings": qty = np.random.randint(2, 8) # Wings bad in Oct
            if month == 11 and item == "Rice Bowl": qty = np.random.randint(5, 12) # Service hits bowls
            if month == 1 and item == "Zinger Burger": qty = np.random.randint(10, 15) # Pricing hits burgers
            
            price = {"Zinger Burger": 199, "Chicken Wings": 249, "French Fries": 99, "Pepsi": 60, "Rice Bowl": 219}[item]
            trans_data.append(["T_ID", date_str, branch, item, "Main", qty, price, 0, qty*price])

        # 3. REVIEW GENERATION (Simulating User Feedback)
        # We generate reviews for ~40% of days to simulate realistic volume
        if np.random.random() > 0.3:
            num_reviews = np.random.randint(1, 3)
            for _ in range(num_reviews):
                platform = np.random.choice(["Google", "Zomato", "Swiggy"])
                
                if focus == "Food" and sentiment == "Negative":
                    txt = np.random.choice([
                        "Chicken wings were very basi and stale.", 
                        "Burgers tasted weird today, not fresh.",
                        "Food quality is declining, very cold wings.",
                        "Found a hair in my food, terrible hygiene."
                    ])
                    # Mock Scores for immediate testing
                    scores = {'Food': -0.9, 'Service': -0.2, 'Ambience': 0.1, 'Pricing': 0.0}
                    
                elif focus == "Service" and sentiment == "Negative":
                    txt = np.random.choice([
                        "Staff is extremely rude and arrogant.", 
                        "Order took 45 minutes to arrive.",
                        "Delivery was late and the rider was confused.",
                        "Waiters ignore you completely here."
                    ])
                    scores = {'Food': 0.2, 'Service': -0.95, 'Ambience': 0.0, 'Pricing': -0.1}
                    
                elif focus == "Ambience" and sentiment == "Positive":
                    txt = np.random.choice([
                        "Loved the Christmas vibe! Very cozy.", 
                        "Best place to hangout, great music.",
                        "Very clean and hygienic, loved the decor.",
                        "Perfect atmosphere for a date."
                    ])
                    scores = {'Food': 0.7, 'Service': 0.6, 'Ambience': 0.95, 'Pricing': 0.5}
                    
                else: # Pricing
                    txt = np.random.choice([
                        "Too expensive for the portion size.", 
                        "Not worth the money, bill was huge.",
                        "Pricing is very high compared to other outlets.",
                        "Hidden charges in the bill, not happy."
                    ])
                    scores = {'Food': 0.4, 'Service': 0.3, 'Ambience': 0.5, 'Pricing': -0.9}

                # Appending Review + Pre-calculated Scores (Simulating ABSA Engine)
                review_data.append([date_str, branch, platform, txt, scores['Food'], scores['Service'], scores['Ambience'], scores['Pricing']])

# --- SAVE FILES ---
# 1. Sales
df_sales = pd.DataFrame(sales_data, columns=['Date', 'Branch', 'Daily_Sales_INR', 'Stock_Level_Percent'])
df_sales.to_csv('sales.csv', index=False)

# 2. Transactions
df_trans = pd.DataFrame(trans_data, columns=['Transaction_ID', 'Date', 'Branch', 'Item_Name', 'Category', 'Quantity', 'Price_INR', 'Discount_Percent', 'Total_Amount_INR'])
df_trans.to_csv('transactions.csv', index=False)

# 3. Sentiment Report (Pre-processed for instant testing)
df_sent = pd.DataFrame(review_data, columns=['Date', 'Branch', 'Platform', 'Review_Text', 'Food', 'Service', 'Ambience', 'Pricing'])
# Also save a column called "Translated_Text" as copy of Review_Text for the new app logic
df_sent['Translated_Text'] = df_sent['Review_Text'] 
df_sent.to_csv('sentiment_report.csv', index=False)

print(f"✅ DATASET READY!")
print(f"   - sales.csv: {len(df_sales)} rows")
print(f"   - transactions.csv: {len(df_trans)} rows")
print(f"   - sentiment_report.csv: {len(df_sent)} rows (Auto-scored)")
print("👉 Upload 'sales.csv' and 'transactions.csv' to your dashboard now.")