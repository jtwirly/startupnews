import streamlit as st
import requests
import feedparser
from datetime import datetime
import json
from pathlib import Path
import urllib.parse

# Page configuration
st.set_page_config(page_title="Climate Scale-Up News Dashboard", layout="wide")

# Combined company information for both cohorts
COMPANIES = {
    # 2024 Cohort
    "Talus Renewables": {
        "cohort": "2024",
        "description": "World's first commercial modular green ammonia, hydrogen to fertilizer plant",
        "search_terms": '"Talus Renewables"'
    },
    "Amini.ai": {
        "cohort": "2024",
        "description": "Time's 100 most influential people in AI",
        "search_terms": '"Amini.ai"'
    },
    "Mombak": {
        "cohort": "2024",
        "description": "Backed by Microsoft, AXA, Rockefeller Foundation",
        "search_terms": '"Mombak"'
    },
    "Moxair": {
        "cohort": "2024",
        "description": "Scalable methane emissions reduction technologies",
        "search_terms": '"Moxair"'
    },
    "ClearFlame": {
        "cohort": "2024",
        "description": "Fast Company's Next big thing in Tech",
        "search_terms": '"ClearFlame"'
    },
    "Source.co": {
        "cohort": "2024",
        "description": "Winner of McNulty Prize, Backed by Bill Gates and Blackrock",
        "search_terms": '"Source.co"'
    },
    "Carbonwave": {
        "cohort": "2024",
        "description": "World Economic Forum's Top Innovator Award",
        "search_terms": '"Carbonwave"'
    },
    "Running Tide": {
        "cohort": "2024",
        "description": "Ocean-based carbon removal and ecosystem restoration",
        "search_terms": '"Running Tide"'
    },
    # 2025 Cohort
    "EarthGrid PBC": {
        "cohort": "2025",
        "description": "Revolutionizing infrastructure with plasma boring robot for underground tunnels",
        "search_terms": '"EarthGrid PBC" OR "EarthGrid"'
    },
    "TURN2X": {
        "cohort": "2025",
        "description": "Producing renewable, CO₂-neutral natural gas from green hydrogen",
        "search_terms": '"TURN2X"'
    },
    "Upwell Materials": {
        "cohort": "2025",
        "description": "Innovating algae-based, carbon-negative materials for cosmetics",
        "search_terms": '"Upwell Materials"'
    },
    "re.green": {
        "cohort": "2025",
        "description": "Leading Brazil's ecological restoration initiatives",
        "search_terms": '"re.green"'
    },
    "WeForest": {
        "cohort": "2025",
        "description": "Restoring over 71,000 hectares of forest and nearly 100 million trees planted",
        "search_terms": '"WeForest"'
    },
    "NatureX RMS": {
        "cohort": "2025",
        "description": "Climate resilience and nature risk management platform using AI agents",
        "search_terms": '"NatureX RMS" OR "NatureX"'
    },
    "S3 Markets": {
        "cohort": "2025",
        "description": "Tackling Scope 3 emissions through supply chain insetting",
        "search_terms": '"S3 Markets"'
    },
    "ArtifexAI": {
        "cohort": "2025",
        "description": "Using AI to transform urban environments for sustainable development",
        "search_terms": '"ArtifexAI"'
    },
    "Seafields Solutions": {
        "cohort": "2025",
        "description": "Pioneering open-ocean aquaculture using Sargassum for CO₂ sequestration",
        "search_terms": '"Seafields Solutions"'
    }
}

def get_google_news(company_name):
    """Get news from Google News RSS feed"""
    # Encode company name for URL
    query = urllib.parse.quote(COMPANIES[company_name]['search_terms'].replace('"', ''))
    
    # Create Google News RSS URL
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        # Parse RSS feed
        feed = feedparser.parse(rss_url)
        
        # Format articles
        articles = []
        for entry in feed.entries[:5]:  # Get top 5 articles
            article = {
                'title': entry.title,
                'description': entry.description,
                'url': entry.link,
                'publishedAt': entry.published,
                'source': {
                    'name': entry.source.title if hasattr(entry, 'source') else 'Google News'
                }
            }
            articles.append(article)
        
        return {'articles': articles} if articles else None
    
    except Exception as e:
        st.error(f"Error fetching news for {company_name}: {str(e)}")
        return None

def load_manual_updates():
    """Load manually added company updates"""
    filepath = Path("company_updates.json")
    if filepath.exists():
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

def save_manual_update(update_data):
    """Save a manual company update"""
    filepath = Path("company_updates.json")
    updates = load_manual_updates()
    
    company = update_data['company']
    if company not in updates:
        updates[company] = []
    
    updates[company].append(update_data)
    
    with open(filepath, "w") as f:
        json.dump(updates, f)

def format_date(date_str):
    """Format date string to readable format"""
    try:
        date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        return date.strftime('%B %d, %Y')
    except:
        return date_str

def display_news_card(title, description, date, source, url=None):
    """Unified display format for news and updates"""
    if url:
        link_text = f'<a href="{url}" target="_blank">Read more →</a>'
    else:
        link_text = ""
        
    st.markdown(f"""
    <div style="border:1px solid #f0f0f0; padding:20px; margin:10px 0; border-radius:5px">
        <h4>{title}</h4>
        <p>{description}</p>
        <p><small>{format_date(date)} | {source}</small></p>
        {link_text}
    </div>
    """, unsafe_allow_html=True)

def main():
    st.title("Climate Scale-Up News Dashboard")
    
    # Sidebar configuration
    st.sidebar.header("Settings")
    selected_cohort = st.sidebar.radio("Select Cohort", ["All", "2024", "2025"])
    
    # Filter companies by selected cohort
    if selected_cohort == "All":
        available_companies = list(COMPANIES.keys())
    else:
        available_companies = [company for company, details in COMPANIES.items() 
                             if details['cohort'] == selected_cohort]
    
    selected_companies = st.sidebar.multiselect(
        "Companies",
        options=available_companies,
        default=available_companies
    )
    
    # Main content area
    tab1, tab2 = st.tabs(["📰 News Feed", "✍️ Submit Update"])
    
    with tab1:
        for company in selected_companies:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 1px 15px; border-radius: 5px; margin: 10px 0;">
                <h3>{company}</h3>
                <p><em>{COMPANIES[company]['description']}</em></p>
                <p><small>Cohort: {COMPANIES[company]['cohort']}</small></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Get manual updates
            manual_updates = load_manual_updates().get(company, [])
            
            # Get RSS news updates
            news_data = get_google_news(company)
            
            # Combine and display all updates
            if news_data and news_data.get('articles') or manual_updates:
                # Display manual updates first
                for update in manual_updates:
                    display_news_card(
                        update['title'],
                        update['description'],
                        update['date'],
                        "Company Update",
                        None
                    )
                
                # Then display news articles
                if news_data and news_data.get('articles'):
                    for article in news_data['articles']:
                        display_news_card(
                            article['title'],
                            article['description'],
                            article['publishedAt'],
                            article['source']['name'],
                            article['url']
                        )
            else:
                st.info(f"No recent updates found for {company}")
            
            st.markdown("---")
    
    with tab2:
        st.header("Submit Company Update")
        company = st.selectbox("Company", options=available_companies)
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
                    "date": datetime.now().strftime("%B %d, %Y")
                }
                save_manual_update(update_data)
                st.success("Update submitted successfully!")
            else:
                st.warning("Please fill in all fields")

if __name__ == "__main__":
    main()