import streamlit as st
import feedparser
from google import genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="South India Centrist News",
    page_icon="📰",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stCard {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #3d4466;
        margin-bottom: 20px;
    }
    .headline {
        color: #ff4b4b;
        font-weight: bold;
        font-size: 24px;
    }
    .source-label {
        font-size: 12px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .centrist-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00d2ff;
        margin-top: 10px;
    }
</style>
""", unsafe_content_html=True)

# Sidebar - Configuration
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("Google API Key", value=os.getenv("GOOGLE_API_KEY", ""), type="password")
if not api_key:
    st.sidebar.warning("Please enter your Google Gemini API Key.")

# RSS Feeds
FEEDS = {
    "Center-Left (The Hindu)": [
        "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss",
        "https://www.thehindu.com/news/national/karnataka/feeder/default.rss",
        "https://www.thehindu.com/news/national/kerala/feeder/default.rss",
        "https://www.thehindu.com/news/national/telangana/feeder/default.rss",
        "https://www.thehindu.com/news/national/andhra-pradesh/feeder/default.rss"
    ],
    "Right-Leaning (OpIndia)": [
        "https://www.opindia.com/feed/"
    ]
}

def fetch_rss_data(urls, limit=5):
    items = []
    for url in urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:limit]:
            items.append({
                "title": entry.title,
                "summary": entry.get("summary", ""),
                "link": entry.link
            })
    return items

def synthesize_centrist_news(left_data, right_data, client):
    prompt = f"""
    Act as a highly objective centrist news editor. Below is news data from two sources with different ideological perspectives:
    
    LEFT-LEANING DATA:
    {left_data}
    
    RIGHT-LEANING DATA:
    {right_data}
    
    TASK:
    1. Identify matching or similar stories reported across both sources.
    2. For unique stories, summarize them objectively.
    3. For shared stories, synthesize a "Centrist Synthesis" that:
       - Highlights agreed-upon facts.
       - Transparently points out where the narratives differ (e.g., "While Source A emphasizes X, Source B focuses on Y").
       - Avoids sensationalism and emotive language.
    
    FORMAT:
    Return the news in a structured bulleted format with:
    - **[HEADLINE]**
    - [CENTRIST SUMMARY: ~3-4 lines]
    - [PERSPECTIVE NOTE: If significant bias difference exists]
    
    Use professional, neutral journalism.
    """
    
    try:
        response = client.models.generate_content(
            model='gemma-3-27b-it',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error synthesizing news: {e}"

# Main UI
st.title("📰 South India Centrist News Hub")
st.markdown("### Synthesizing perspectives for a balanced view.")

if api_key:
    client = genai.Client(api_key=api_key)
    
    if st.button("🔄 Fetch & Synthesize Latest News"):
        with st.spinner("Analyzing cross-source narratives..."):
            left_news = fetch_rss_data(FEEDS["Center-Left (The Hindu)"], limit=3)
            right_news = fetch_rss_data(FEEDS["Right-Leaning (OpIndia)"], limit=5) # More from OpIndia to find overlaps
            
            left_blob = "\n".join([f"Title: {n['title']}\nSummary: {n['summary']}" for n in left_news])
            right_blob = "\n".join([f"Title: {n['title']}\nSummary: {n['summary']}" for n in right_news])
            
            synthesis = synthesize_centrist_news(left_blob, right_blob, client)
            
            st.markdown("---")
            st.markdown("### 🕊️ The Centrist Synthesis")
            st.markdown(synthesis)
            
            with st.expander("Show Raw Source Data"):
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Center-Left (The Hindu)")
                    for n in left_news:
                        st.write(f"- **{n['title']}**")
                with col2:
                    st.subheader("Right-Leaning (OpIndia)")
                    for n in right_news:
                        st.write(f"- **{n['title']}**")
else:
    st.info("👈 Please enter your Google API key in the sidebar to begin.")

st.markdown("---")
st.caption("Disclaimer: This tool uses AI to synthesize news from sources with different editorial biases. Always verify critical information from primary sources.")
