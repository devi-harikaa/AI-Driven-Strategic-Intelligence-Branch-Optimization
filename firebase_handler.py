import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import pandas as pd
import bcrypt

# --- INITIALIZE ---
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json") 
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- AUTHENTICATION ---
def register_restaurant(name, password):
    """Creates a new restaurant account if it doesn't exist."""
    doc_ref = db.collection('restaurants').document(name)
    if doc_ref.get().exists:
        return False, "⚠️ Restaurant name already registered. Please Login."
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    doc_ref.set({
        'created_at': firestore.SERVER_TIMESTAMP,
        'password_hash': hashed.decode('utf-8')
    })
    return True, "✅ Registration Successful! Please Login."

def authenticate_user(name, password):
    """Verifies Name + Password."""
    doc_ref = db.collection('restaurants').document(name)
    doc = doc_ref.get()
    
    if not doc.exists:
        return False, "❌ Restaurant not found. Please Register."
    
    data = doc.to_dict()
    stored_hash = data.get('password_hash', '').encode('utf-8')
    
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        return True, "✅ Login Success"
    return False, "❌ Invalid Password."

# --- SEGREGATED DATA SYNC ---
def upload_data_to_cloud(name, sales_df, trans_df):
    """Uploads data SPECIFICALLY to this restaurant's sub-collection."""
    sales_df['Date'] = sales_df['Date'].astype(str)
    trans_df['Date'] = trans_df['Date'].astype(str)
    
    def batch_upload(df, sub_collection):
        # Path: restaurants/{name}/{sub_collection}
        # Example: restaurants/KFC/sales
        collection_ref = db.collection('restaurants').document(name).collection(sub_collection)
        
        # 1. Delete old data for this restaurant only
        docs = collection_ref.stream()
        for doc in docs: doc.reference.delete()
            
        # 2. Add new data
        records = df.to_dict(orient='records')
        batch = db.batch()
        count = 0
        for record in records:
            doc_ref = collection_ref.document()
            batch.set(doc_ref, record)
            count += 1
            if count == 400:
                batch.commit()
                batch = db.batch()
                count = 0
        batch.commit()

    batch_upload(sales_df, 'sales')
    batch_upload(trans_df, 'transactions')

def fetch_data_from_cloud(name):
    """Fetches data ONLY for the logged-in restaurant."""
    def load_coll(sub_coll):
        docs = db.collection('restaurants').document(name).collection(sub_coll).stream()
        data = [doc.to_dict() for doc in docs]
        return pd.DataFrame(data) if data else pd.DataFrame()

    sales_df = load_coll('sales')
    trans_df = load_coll('transactions')
    
    branches = []
    if not sales_df.empty:
        sales_df['Date'] = pd.to_datetime(sales_df['Date'])
        branches = sorted(sales_df['Branch'].unique().tolist())
    if not trans_df.empty:
        trans_df['Date'] = pd.to_datetime(trans_df['Date'])
        
    return sales_df, trans_df, branches