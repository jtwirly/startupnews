import streamlit as st
import requests
import feedparser
from datetime import datetime
import json
from pathlib import Path
import urllib.parse
import os

# Page configuration
#st.set_page_config(page_title="Climate Scale-Up News Dashboard", layout="wide")

# Complete company information with CEOs
COMPANIES = {
    # 2024 Cohort
    "Talus Renewables": {
        "cohort": "2024",
        "ceo": "Hiro Iwanaga",
        "description": "World's first commercial modular green ammonia, hydrogen to fertilizer plant",
        "search_terms": '"Talus Renewables" AND "Hiro Iwanaga"'
    },
    "Amini.ai": {
        "cohort": "2024",
        "ceo": "Kate Kallot",
        "description": "Time's 100 most influential people in AI",
        "search_terms": '"Amini.ai" AND "Kate Kallot"'
    },
    "Mombak": {
        "cohort": "2024",
        "ceo": "Peter Fernandez",
        "description": "Backed by Microsoft, AXA, Rockefeller Foundation",
        "search_terms": '"Mombak" AND "Peter Fernandez"'
    },
    "Moxair": {
        "cohort": "2024",
        "ceo": "Adi Gottumukkala",
        "description": "Scalable methane emissions reduction technologies",
        "search_terms": '"Moxair" AND "Aditya Gottumukkala"'
    },
    "ClearFlame": {
        "cohort": "2024",
        "ceo": "BJ Johnson",
        "description": "Fast Company's Next big thing in Tech",
        "search_terms": '"ClearFlame" AND "BJ Johnson"'
    },
    "Source.co": {
        "cohort": "2024",
        "ceo": "Cody Friesen",
        "description": "Winner of McNulty Prize, Backed by Bill Gates and Blackrock",
        "search_terms": '"Source.co" AND "Cody Friesen"'
    },
    "Carbonwave": {
        "cohort": "2024",
        "ceo": "Geoff Chapin",
        "description": "World Economic Forum's Top Innovator Award",
        "search_terms": '"Carbonwave" AND "Geoff Chapin"'
    },
    "Running Tide": {
        "cohort": "2024",
        "ceo": "Marty Odlin",
        "description": "Ocean-based carbon removal and ecosystem restoration",
        "search_terms": '"Running Tide" AND "Marty Odlin"'
    },
    # 2025 Cohort
    "EarthGrid PBC": {
        "cohort": "2025",
        "ceo": "Troy Helming",
        "description": "Revolutionizing infrastructure with plasma boring robot for underground tunnels",
        "search_terms": '"EarthGrid PBC" AND "Troy Helming"'
    },
    "TURN2X": {
        "cohort": "2025",
        "ceo": "Philip Kessler",
        "description": "Producing renewable, CO₂-neutral natural gas from green hydrogen",
        "search_terms": '"TURN2X" AND "Philip Kessler"'
    },
    "Upwell Materials": {
        "cohort": "2025",
        "ceo": "Daniella Zakon",
        "description": "Innovating algae-based, carbon-negative materials for cosmetics",
        "search_terms": '"Upwell" AND "Daniella Zakon"'
    },
    "re.green": {
        "cohort": "2025",
        "ceo": "Thiago Picolo",
        "description": "Leading Brazil's ecological restoration initiatives",
        "search_terms": '"re.green" AND "Thiago Picolo"'
    },
    "WeForest": {
        "cohort": "2025",
        "ceo": "Marie-Noëlle Keijzer",
        "description": "Restoring over 71,000 hectares of forest and nearly 100 million trees planted",
        "search_terms": '"WeForest" AND "Marie-Noëlle Keijzer"'
    },
    "NatureX RMS": {
        "cohort": "2025",
        "ceo": "Raviv Turner",
        "description": "Climate resilience and nature risk management platform using AI agents",
        "search_terms": '"NatureX" AND "Raviv Turner"'
    },
    "S3 Markets": {
        "cohort": "2025",
        "ceo": "Saman Baghestani",
        "description": "Tackling Scope 3 emissions through supply chain insetting",
        "search_terms": '"S3" AND "Saman Baghestani"'
    },
    "ArtifexAI": {
        "cohort": "2025",
        "ceo": "Russ Wilcox",
        "description": "Using AI to transform urban environments for sustainable development",
        "search_terms": '"ArtifexAI" AND "Russ Wilcox"'
    },
    "Seafields Solutions": {
        "cohort": "2025",
        "ceo": "John Wedge Auckland",
        "description": "Pioneering open-ocean aquaculture using Sargassum for CO₂ sequestration",
        "search_terms": '"Seafields" AND "John Auckland"'
    }
}

def get_google_news(company_name):
    """Get news from Google News RSS feed requiring both company and CEO name"""
    company_info = COMPANIES[company_name]
    
    # Create search query with company name OR CEO name
    query = company_info['search_terms']
    encoded_query = urllib.parse.quote(query)
    
    # Create Google News RSS URL
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
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
    <div style="background-color: #2D2D2D; border:1px solid #333; padding:20px; margin:10px 0; border-radius:5px; color: #FFFFFF;">
        <h4 style="color: #FFFFFF;">{title}</h4>
        <p style="color: #CCCCCC;">{description}</p>
        <p style="color: #999999;"><small>{format_date(date)} | {source}</small></p>
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
            <div style="background-color: #2D2D2D; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3 style="color: #FFFFFF; font-size: 38px; font-weight: 700; margin-bottom: 12px;">{company}</h3>
                <p style="color: #CCCCCC; font-size: 16px;"><em>{COMPANIES[company]['description']}</em></p>
                <p style="color: #999999; font-size: 14px;"><small>Cohort: {COMPANIES[company]['cohort']} | CEO: {COMPANIES[company]['ceo']}</small></p>
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
        st.header("Submit Company Update - In Beta")
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