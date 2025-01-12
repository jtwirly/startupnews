import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import json
from pathlib import Path

# Set page configuration to match Climate Scale-Up branding
st.set_page_config(
    page_title="Climate Scale-Up News Dashboard",
    page_icon="🌍",
    layout="wide"
)

# Custom CSS to match Climate Scale-Up styling
st.markdown("""
    <style>
    .main {
        font-family: 'Helvetica Neue', sans-serif;
    }
    h1 {
        font-family: 'Times New Roman', serif;
        font-weight: 300;
        letter-spacing: 0.05em;
    }
    .stButton>button {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #000000;
        border-radius: 0;
        padding: 10px 20px;
    }
    .company-card {
        border: 1px solid #f0f0f0;
        padding: 20px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Company information
COMPANIES = {
    "Talus Renewables": {
        "ceo": "Hiro Iwanaga",
        "description": "World's first commercial modular green ammonia, hydrogen to fertilizer plant"
    },
    "Amini.ai": {
        "ceo": "Kate Kallot",
        "description": "AI and space technologies for environmental data in Africa"
    },
    "Mombak": {
        "ceo": "Peter Fernandez",
        "description": "Backed by Microsoft, AXA, Rockefeller Foundation"
    },
    "Moxair": {
        "ceo": "Adi Gottumukkala",
        "description": "Scalable methane emissions reduction technologies"
    }
}

def save_company_update(update_data):
    """Save company update to a JSON file"""
    filepath = Path("company_updates.json")
    if filepath.exists():
        with open(filepath, "r") as f:
            updates = json.load(f)
    else:
        updates = []
    
    updates.append(update_data)
    with open(filepath, "w") as f:
        json.dump(updates, f)

def get_company_updates():
    """Read company updates from JSON file"""
    filepath = Path("company_updates.json")
    if filepath.exists():
        with open(filepath, "r") as f:
            return json.load(f)
    return []

def main():
    # Header
    st.title("Climate Scale-Up News Dashboard")
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["📰 News Feed", "✍️ Submit Update", "📊 Company Insights"])
    
    with tab1:
        # Company selection in sidebar
        st.sidebar.header("Companies")
        selected_companies = st.sidebar.multiselect(
            "Select Companies",
            options=list(COMPANIES.keys()),
            default=list(COMPANIES.keys())
        )
        
        api_key = st.sidebar.text_input("News API Key", value="53b865be204a4e02b8a32e01fa2713e1", type="password")
        days_ago = st.sidebar.slider("Days of History", 1, 30, 7)
        
        if selected_companies and api_key:
            for company in selected_companies:
                st.markdown(f"### {company}")
                st.markdown(f"*{COMPANIES[company]['description']}*")
                
                # Fetch news using NewsAPI
                url = f"https://newsapi.org/v2/everything?q={company}&apiKey={api_key}&from={datetime.now()-timedelta(days=days_ago)}&sortBy=publishedAt"
                try:
                    response = requests.get(url)
                    news = response.json()
                    
                    if news.get('articles'):
                        for article in news['articles'][:5]:  # Show latest 5 articles
                            with st.container():
                                st.markdown(f"""
                                <div class="company-card">
                                    <h4>{article['title']}</h4>
                                    <p>{article['description']}</p>
                                    <p><small>{article['publishedAt'][:10]} | {article['source']['name']}</small></p>
                                    <a href="{article['url']}" target="_blank">Read more →</a>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info(f"No recent news found for {company}")
                except Exception as e:
                    st.error(f"Error fetching news for {company}: {str(e)}")
    
    with tab2:
        st.header("Submit Company Update")
        
        # Company update form
        company = st.selectbox("Company", options=list(COMPANIES.keys()))
        update_type = st.selectbox("Update Type", [
            "Partnership Announcement",
            "Product Launch",
            "Funding News",
            "Technology Milestone",
            "Other"
        ])
        title = st.text_input("Title")
        description = st.text_area("Description")
        
        if st.button("Submit Update"):
            if title and description:
                update_data = {
                    "company": company,
                    "type": update_type,
                    "title": title,
                    "description": description,
                    "date": datetime.now().isoformat()
                }
                save_company_update(update_data)
                st.success("Update submitted successfully!")
            else:
                st.warning("Please fill in all fields")
    
    with tab3:
        st.header("Company Insights")
        
        # Display company updates
        updates = get_company_updates()
        if updates:
            for update in updates:
                st.markdown(f"""
                <div class="company-card">
                    <h4>{update['company']} - {update['type']}</h4>
                    <h5>{update['title']}</h5>
                    <p>{update['description']}</p>
                    <p><small>{update['date'][:10]}</small></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No company updates submitted yet")

if __name__ == "__main__":
    main()
