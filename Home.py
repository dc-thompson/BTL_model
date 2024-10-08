import streamlit as st
from streamlit_lottie import st_lottie
import requests
import json

def load_lottie(source):
    if source.startswith('http'):
        # If the source is a URL
        r = requests.get(source)
        if r.status_code != 200:
            return None
        return r.json()
    else:
        # If the source is a local file path
        with open(source, 'r') as f:
            return json.load(f)

# Load a relevant Lottie animation
lottie_house = load_lottie("1725915498155.json")

# Set page config
st.set_page_config(page_title="Buy-to-Let Property Model", page_icon="🏠", layout="wide")

st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stAlert {
        background-color: #e8f4f8;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3498db;
    }
    .stTabs {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* CSS for sidebar */
    [data-testid="stSidebar"] {
        min-height: 100vh;
    }
    [data-testid="stSidebar"] > div:first-child {
        height: 100vh;
        overflow-y: auto;
    }

    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .stApp {
            max-width: 100%;
            padding: 10px;
        }
        h1 {
            font-size: 1.8rem;
        }
        h2 {
            font-size: 1.5rem;
        }
        h3 {
            font-size: 1.2rem;
        }
        .stAlert {
            padding: 15px;
        }
        .stTabs {
            padding: 15px;
        }
        [data-testid="stSidebar"] {
            min-height: auto;
        }
        [data-testid="stSidebar"] > div:first-child {
            height: auto;
        }
        /* Improve input readability on mobile */
        .stTextInput > div > div > input {
            font-size: 16px;
        }
        .stSelectbox > div > div > select {
            font-size: 16px;
        }
        .stNumberInput > div > div > input {
            font-size: 16px;
        }
    }

    /* Ensure text is visible on all backgrounds */
    .stMarkdown, .stText {
        color: #2c3e50 !important;
    }
</style>
""", unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🏠 Buy-to-Let Property Financial Modelling")
    st.markdown("""
    Welcome to our Buy-to-Let property financial modelling app! 
    
    This tool is designed to assist you in making informed decisions about property investments, 
    whether you're considering purchasing as an individual or through a limited company.
    """)

    st.info("""
    **Please Note**: While this app provides valuable insights, it is not a substitute for 
    professional tax or accountancy advice. The results presented here do not constitute 
    financial advice. Always consult with qualified professionals before making significant 
    financial decisions.
    """)

with col2:
    if lottie_house is not None:
        st_lottie(lottie_house, speed=1, height=200, key="house_animation")
    else:
        st.warning("Failed to load house animation.")

# Add more sections for your app here
