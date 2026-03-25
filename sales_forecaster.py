import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import os

def train_forecasting_model(file_path=None):
    # ⚠️ THE FIX: We added "if file_path is None" to prevent the Python TypeError!
    if file_path is None or not os.path.exists(file_path): 
        return None, pd.DataFrame()
        
    try:
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date', 'Daily_Sales_INR']) 
        
        # Feature Engineering
        df['DayOfWeek'] = df['Date'].dt.dayofweek
        df['IsWeekend'] = df['DayOfWeek'].apply(lambda x: 1 if x >= 5 else 0)
        
        if 'Branch' in df.columns:
            df['Branch_Code'] = df['Branch'].astype('category').cat.codes
        else: df['Branch_Code'] = 0
            
        if 'Stock_Level_Percent' not in df.columns: df['Stock_Level_Percent'] = 50 
            
        # The 4 Features expected by app.py
        X = df[['Branch_Code', 'DayOfWeek', 'IsWeekend', 'Stock_Level_Percent']]
        y = df['Daily_Sales_INR']
        
        if len(df) < 5: return None, df

        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X, y)
        return model, df
    except Exception as e:
        print(f"Error: {e}") 
        return None, pd.DataFrame()