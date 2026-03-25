import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from collections import Counter
from absa_engine import run_sentiment_analysis, ASPECT_MAP
from social_media_fetcher import search_and_fetch_reviews
from sales_forecaster import train_forecasting_model
from firebase_handler import register_restaurant, authenticate_user, upload_data_to_cloud, fetch_data_from_cloud

# --- CONFIG: NEW TITLE & ICON ---
st.set_page_config(page_title="Restaurant optimization System", layout="wide", page_icon="🏢")

# --- 🎨 CSS: LIGHT MODE & PROFESSIONAL UI ---
st.markdown("""
    <style>
        /* Light Mode Backgrounds */
        .stApp {
            background-color: #F8F9FA; /* Soft White */
            color: #212529; /* Dark Gray Text */
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #DEE2E6;
        }

        /* Headings */
        h1 {
            color: #0F172A; /* Navy Blue */
            font-family: 'Segoe UI', sans-serif;
            font-weight: 800;
        }
        h2, h3 {
            color: #334155; /* Slate Gray */
            font-weight: 600;
        }

        /* Metric Cards - White with Shadow */
        div[data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        div[data-testid="stMetricValue"] {
            font-size: 36px !important;
            font-weight: 700 !important;
            color: #1E293B !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #64748B !important;
            font-weight: 500 !important;
        }

        /* Custom Explanation Box */
        .explanation-box {
            background-color: #E0F2FE; /* Light Blue */
            border-left: 5px solid #0284C7;
            padding: 15px;
            border-radius: 5px;
            color: #0C4A6E;
            font-size: 16px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 🧠 HELPER: PAIN POINT ANALYZER ---
def get_pain_point_summary(df):
    """
    Analyzes negative reviews to find the most frequent complaint words.
    Returns a plain English explanation.
    """
    if df.empty: return "No data available."
    
    # Filter for negative sentiment in Food or Service
    negatives = df[(df['Food'] < 0) | (df['Service'] < 0)]
    
    if negatives.empty:
        return "✅ **No major pain points detected.** Customers are generally satisfied."
    
    # Simple word frequency on negative reviews
    text = " ".join(negatives['Review_Text'].astype(str).tolist()).lower()
    ignore = ['the', 'and', 'was', 'for', 'that', 'with', 'food', 'service', 'place', 'restaurant', 'very']
    words = [w for w in text.split() if w not in ignore and len(w) > 3]
    
    if not words: return "📉 Negative sentiment detected, but no specific keywords dominated."
    
    most_common = Counter(words).most_common(1)[0][0]
    
    # Plain English Translation
    explanation = f"⚠️ **Top Complaint:** The word **'{most_common}'** appears frequently in negative reviews."
    if most_common in ['salt', 'cold', 'taste', 'bland', 'raw']:
        explanation += " This suggests a **Kitchen Consistency** issue."
    elif most_common in ['slow', 'late', 'wait', 'time']:
        explanation += " This points to **Slow Service** or staffing shortages."
    elif most_common in ['rude', 'staff', 'manager']:
        explanation += " This indicates **Staff Behavior** problems."
    
    return explanation

# --- 🧠 STRATEGIC PRESCRIPTION LOGIC (KEPT SAME) ---
def generate_professional_strategy(is_downfall, culprit_aspect, laggard_item, volume_leader, savior_aspect):
    if is_downfall:
        actions = {
            'Food': f"Initiate immediate kitchen audit for '{laggard_item}' preparation standards. Review ingredient logs.",
            'Service': f"Deploy floor manager to monitor peak-hour bottlenecks. Conduct rapid retraining on service speed.",
            'Ambience': "Schedule facility maintenance and deep-cleaning. Review noise level feedback.",
            'Pricing': f"Conduct competitor price benchmarking for '{laggard_item}'. Consider temporary bundle offers."
        }
        aspect = "General Operations" if pd.isna(culprit_aspect) or culprit_aspect == "N/A" else culprit_aspect
        specific_action = actions.get(aspect, f"Investigate operational bottlenecks affecting '{laggard_item}'.")
        return f"💡 **Strategy**: Statistical correlation indicates a failure in **{aspect}**. This negatively impacted **{laggard_item}** volume. \n\n**Action**: {specific_action}"
    else:
        return f"💡 **Strategy**: Operations stable. **{savior_aspect}** is driving retention. Capitalize by upselling **{volume_leader}**."

# --- 🧠 ALGORITHMIC ENGINE (KEPT SAME) ---
def calculate_z_score(current_val, series):
    mean, std = series.mean(), series.std()
    return (current_val - mean) / std if std != 0 else 0

def get_algorithmic_insight(sales_row, sales_df, sent_df, trans_df, model):
    date, revenue, branch = sales_row['Date'], sales_row['Daily_Sales_INR'], sales_row['Branch']
    branch_sales = sales_df[sales_df['Branch'] == branch]['Daily_Sales_INR']
    is_downfall = calculate_z_score(revenue, branch_sales) < -1.0
    
    day_trans = trans_df[(trans_df['Date'] == date) & (trans_df['Branch'] == branch)]
    if day_trans.empty: 
        laggard_item, laggard_drop, volume_leader = "N/A", "0%", "N/A"
    else:
        all_trans = trans_df[trans_df['Branch'] == branch]
        item_avgs = all_trans.groupby('Item_Name')['Quantity'].mean()
        day_qtys = day_trans.groupby('Item_Name')['Quantity'].sum()
        deviations = (day_qtys - item_avgs) / item_avgs
        laggard_item = deviations.idxmin()
        laggard_drop = f"{deviations.min()*100:.1f}%"
        volume_leader = day_qtys.idxmax()

    start_w, end_w = date - pd.Timedelta(days=7), date + pd.Timedelta(days=2)
    mask = (sent_df['Branch'] == branch) & (sent_df['Date'] >= start_w) & (sent_df['Date'] <= end_w)
    window_sent = sent_df[mask]
    if window_sent.empty: window_sent = sent_df[sent_df['Branch'] == branch] # Fallback history
    if window_sent.empty: window_sent = sent_df[sent_df['Branch'] == "General"] # Fallback general

    aspect_means = window_sent[['Food', 'Service', 'Ambience', 'Pricing']].mean()
    if aspect_means.isnull().all():
        culprit_aspect, savior_aspect, culprit_score, savior_score = "N/A", "N/A", 0.0, 0.0
    else:
        culprit_aspect, savior_aspect = aspect_means.idxmin(), aspect_means.idxmax()
        culprit_score, savior_score = aspect_means.min(), aspect_means.max()

    def get_proof(aspect, reviews, positive=True):

        if aspect == "N/A" or pd.isna(aspect): return "Insufficient Data"

        try:

            sorted_revs = reviews.sort_values(aspect, ascending=not positive)

            target_col = 'Translated_Text' if 'Translated_Text' in reviews.columns else 'Review_Text'

            for _, r in sorted_revs.iterrows():

                if any(k in str(r[target_col]).lower() for k in ASPECT_MAP.get(aspect, [])):

                    if (positive and r[aspect] >= 0.1) or (not positive and r[aspect] <= -0.1):

                        return f'"{str(r[target_col])[:120]}..."'

        except: pass

        return "No specific comments found."



    action_msg = generate_professional_strategy(is_downfall, culprit_aspect, laggard_item, volume_leader, savior_aspect)

   

    forecast_val = 0

    if model:

        try:

            b_code = sales_df['Branch'].astype('category').cat.codes.iloc[0] if 'Branch' in sales_df.columns else 0

            dow = (date.dayofweek + 1) % 7

            input_df = pd.DataFrame([[b_code, dow, 1 if dow >= 5 else 0, 75]], columns=['Branch_Code', 'DayOfWeek', 'IsWeekend', 'Stock_Level_Percent'])

            forecast_val = model.predict(input_df)[0]

        except: pass



    return {

        "is_downfall": is_downfall,

        "status_color": "error" if is_downfall else "success",

        "header": f"📉 DOWNFALL DETECTED: ₹{revenue}" if is_downfall else f"✅ STABLE PERFORMANCE: ₹{revenue}",

        "savior": f"✅ **Resilient Aspect**: {savior_aspect} (Score: {savior_score:.2f})",

        "savior_proof": get_proof(savior_aspect, window_sent, True),

        "culprit": f"🚩 **Root Cause**: {culprit_aspect} (Score: {culprit_score:.2f})",

        "proof": get_proof(culprit_aspect, window_sent, False),

        "impact": f"This downfall is primarily affecting **{laggard_item}** (Volume {laggard_drop}).",

        "why": f"Algorithmic correlation detects a crash in **{culprit_aspect}** sentiment (Score: {culprit_score:.2f}).",

        "action": action_msg,

        "forecast": f"₹{forecast_val:.0f}"

    }



# --- 🔐 AUTHENTICATION FLOW ---
if 'user' not in st.session_state: st.session_state['user'] = None

if st.session_state['user'] is None:
    st.title("Branch Check-In")
    tab_log, tab_reg = st.tabs(["🔑 Login", "📝 Register"])
    with tab_log:
        with st.form("Login"):
            l_name = st.text_input("Restaurant Name")
            l_pass = st.text_input("Password", type="password")
            if st.form_submit_button("Launch"):
                valid, msg = authenticate_user(l_name, l_pass)
                if valid:
                    st.session_state['user'] = l_name
                    st.rerun()
                else: st.error(msg)
    with tab_reg:
        with st.form("Register"):
            r_name = st.text_input("New Restaurant Name")
            r_pass = st.text_input("Set Password", type="password")
            if st.form_submit_button("Register"):
                valid, msg = register_restaurant(r_name, r_pass)
                if valid: st.success(msg)
                else: st.error(msg)
else:
    user = st.session_state['user']
    sales_df, trans_df, cloud_branches = fetch_data_from_cloud(user)

    # --- SIDEBAR & SYNC ---
    st.sidebar.title(f"📍 {user} HQ")
    with st.sidebar.expander("📤 Upload New Data"):
        up_s = st.file_uploader("Sales CSV", type=['csv'])
        up_t = st.file_uploader("Transactions CSV", type=['csv'])
        if st.button("Sync Intelligence"):
            if up_s and up_t:
                new_s, new_t = pd.read_csv(up_s), pd.read_csv(up_t)
                upload_data_to_cloud(user, new_s, new_t)
                new_s.to_csv(f'sales_{user}.csv', index=False)
                new_t.to_csv(f'transactions_{user}.csv', index=False)
                search_and_fetch_reviews(user, new_s['Branch'].unique().tolist())
                run_sentiment_analysis(user).to_csv(f'sentiment_{user}.csv', index=False)
                st.rerun()

    if sales_df.empty:
        st.warning("Welcome! Please upload Sales and Transaction data to begin.")
        if st.sidebar.button("Logout"):
            st.session_state['user'] = None
            st.rerun()
        st.stop()

    branch = st.sidebar.selectbox("Active Branch", cloud_branches)
    if st.sidebar.button("🚪 Logout"):
        st.session_state['user'] = None
        st.rerun()

    # --- DATA LOADING ---
    sent_file = f'sentiment_{user}.csv'
    if not os.path.exists(sent_file):
        search_and_fetch_reviews(user, cloud_branches)
        run_sentiment_analysis(user).to_csv(sent_file, index=False)
    sent_df = pd.read_csv(sent_file)
    sent_df['Date'] = pd.to_datetime(sent_df['Date']).dt.normalize()
    sales_file = f'sales_{user}.csv'
    model, _ = train_forecasting_model(sales_file if os.path.exists(sales_file) else None)

    # --- FILTERING ---
    b_sales = sales_df[sales_df['Branch'] == branch].sort_values('Date')
    weeks = [(d, d + pd.Timedelta(days=6)) for d in pd.date_range(b_sales['Date'].min(), b_sales['Date'].max(), freq='7D')]
    week_labels = [f"Week {i+1}: {s.strftime('%b %d')} - {e.strftime('%b %d')}" for i, (s, e) in enumerate(weeks)]
    selected_label = st.sidebar.selectbox("Select Week", week_labels)
    s_date, e_date = weeks[week_labels.index(selected_label)]
    filtered_sales = b_sales[(b_sales['Date'] >= s_date) & (b_sales['Date'] <= e_date)]

    # --- MAIN DASHBOARD ---
    st.title(f" {branch} Performance")
    t1, t2, t3 = st.tabs(["📊 Branch Insights", "📈 Performance Analytics", "⚔️ Branch Comparison"])

    # --- TAB 1: INSIGHTS & PAIN POINTS ---
    with t1:
        b_sent = sent_df[(sent_df['Branch'] == branch) | (sent_df['Branch'] == "General")]
        c1, c2, c3 = st.columns(3)
        c1.metric("Weekly Revenue", f"₹{filtered_sales['Daily_Sales_INR'].sum():,.0f}")
        c2.metric("Review Volume", len(b_sent))
        c3.metric("Health Score", f"{b_sent[['Food','Service']].mean().mean()*100:.0f}")

        # --- NEW: Pain Points Section ---
        c_graph, c_info = st.columns([2, 1])
        
        with c_graph:
            st.plotly_chart(px.bar(b_sent[['Food','Service','Ambience','Pricing']].mean().reset_index().rename(columns={0:'Score', 'index':'Aspect'}),
                                   x='Aspect', y='Score', color='Score', color_continuous_scale='RdYlGn', title="Sentiment Analysis"), width='stretch')
        
        with c_info:
            st.subheader("💡 What does this mean?")
            st.markdown("""
            <div class="explanation-box">
                This chart visualizes how customers feel about key aspects of your business.
                <br>• <b>Green</b> = Customers are happy.
                <br>• <b>Red</b> = Critical complaints detected.
            </div>
            """, unsafe_allow_html=True)
            
            # Smart Pain Point Summary
            pain_summary = get_pain_point_summary(b_sent)
            st.markdown(f"### 🔍 Mentions\n{pain_summary}")

    with t2:

        for _, row in filtered_sales.iterrows():

            res = get_algorithmic_insight(row, sales_df, sent_df, trans_df, model)

            icon = "⚠️" if res['is_downfall'] else "✅"

            with st.expander(f"{icon} {row['Date'].strftime('%Y-%m-%d')} | {res['header']}"):

                if res['is_downfall']:

                    st.markdown(f"**Analysis**: {res['why']}\n\n**Impact**: {res['impact']}")

                    c1, c2 = st.columns(2)

                    with c1: st.markdown(res['culprit']); st.caption(f"Evidence: {res['proof']}")

                    with c2: st.markdown(res['savior']); st.caption("This aspect remains strong.")

                else:

                    st.markdown("**Operations Stable.**")

                    st.markdown(res['savior']); st.caption(f"Reason: {res['savior_proof']}")

                st.divider()

                if res['status_color'] == 'error': st.error(res['action'])

                else: st.success(res['action'])

                st.caption(f"Projected Recovery Forecast: {res['forecast']}")

    # --- TAB 3: COMPARISON & RECOMMENDATION ---
    with t3:
        st.subheader("Revenue Face-off")
        st.plotly_chart(px.bar(sales_df.groupby('Branch')['Daily_Sales_INR'].sum().reset_index(), x='Branch', y='Daily_Sales_INR', color='Branch'), width='stretch')
        
        st.subheader("Best Strategy & Recommendation Engine")
        
        # Calculate Best Aspect for Recommendation
        comp_data = []
        best_aspects = {} # Store best aspect for each branch
        
        for b in cloud_branches:
            b_data = sent_df[(sent_df['Branch'] == b) | (sent_df['Branch'] == "General")]
            if not b_data.empty:
                means = b_data[['Food','Service','Ambience','Pricing']].mean()
                best_aspect = means.idxmax()
                best_score = means.max()
                best_aspects[b] = (best_aspect, best_score)
                
                for asp, sc in means.items():
                    comp_data.append({'Branch': b, 'Aspect': asp, 'Score': sc})
        
        # Recommendation Logic
        if branch in best_aspects:
            my_best, my_score = best_aspects[branch]
            st.success(f"🏆 **Your Strength:** This branch excels in **{my_best}** (Score: {my_score:.2f}). This strategy should be maintained.")
            
            # Find a branch that is better at something else
            for other_b, (other_best, other_score) in best_aspects.items():
                if other_b != branch and other_score > my_score:
                    st.info(f"💡 **Recommendation:** The **{other_b}** branch has a superior **{other_best}** score ({other_score:.2f}). Consider adopting their protocols for {other_best}.")
        
        if comp_data:
            st.plotly_chart(px.bar(pd.DataFrame(comp_data), x='Aspect', y='Score', color='Branch', barmode='group'), width='stretch')