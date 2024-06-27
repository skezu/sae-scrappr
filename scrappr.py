import os
import time
import logging
import streamlit as st
import requests
import pandas as pd
import dotenv

# Load environment variables
dotenv.load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)

API_URL = "http://localhost:5001/scrape"  # URL of the Flask API

def call_scrape_api(email=os.getenv("TWITTER_EMAIL"), username=os.getenv("TWITTER_USERNAME"), password=os.getenv("TWITTER_PASSWORD"), api_key=os.getenv("TWITTER_API_KEY"), query="RN Vote", max_tweets=10):
    try:
        payload = {
            "email": email,
            "username": username,
            "password": password,
            "api_key": api_key,
            "query": query,
            "max_tweets": max_tweets
        }
        print(payload)
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling scrape API: {e}")
        return {"error": str(e)}

def main_scraping_page():
    st.title("Twitter Sentiment Analysis")
    st.sidebar.title("Configuration")
    twitter_email = st.sidebar.text_input("Twitter Email")
    twitter_username = st.sidebar.text_input("Twitter Username")
    twitter_password = st.sidebar.text_input("Twitter Password", type="password")
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    query = st.text_input("Search Query", "RN Vote")
    allow_replies = st.checkbox("Allow Replies")
    if not allow_replies:
        query += " -filter:replies"
    tweet_type = st.radio("Select Tweet Type", ("Recent", "New"))
    max_tweets = st.slider("Number of Tweets to Scrape", min_value=10, max_value=100, value=50)

    if "responses" not in st.session_state:
        st.session_state.responses = None

    if st.button("Scrap tweets"):
        with st.spinner("Scraping and formatting tweets..."):
            response = call_scrape_api(twitter_email, twitter_username, twitter_password, openai_api_key, query, max_tweets)
            if "error" in response:
                st.error(f"An error occurred: {response['error']}")
            else:
                tweets = response.get("tweets", [])
                if tweets:
                    st.session_state.responses = tweets
                    st.session_state.df = pd.DataFrame(tweets, columns=["tweet", "username", "reply", "retweet", "like", "views"])
                    st.session_state.openai_api_key = openai_api_key
                else:
                    st.error("No tweets found or an error occurred.")

    if st.session_state.responses:
        st.dataframe(st.session_state.df, use_container_width=True)

        csv = st.session_state.df.to_csv(index=False, sep=',', encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="Download Table as CSV",
            data=csv,
            file_name="scraped_tweets.csv",
            mime="text/csv",
            key='download-csv'
        )

        if st.button("Analysis page"):
            st.session_state.page = 'chatbot'
            st.experimental_rerun()

def main():
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if st.session_state.page == "home":
        main_scraping_page()
    elif st.session_state.page == "chatbot":
        import chat
        chat.main()

if __name__ == "__main__":
    main()
