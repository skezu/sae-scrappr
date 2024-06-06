import os
import time
import logging
import streamlit as st
import praw
from openai import OpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_groq import ChatGroq
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)

class RedditScraper:
    def __init__(self, reddit_client_id, reddit_client_secret, reddit_username, reddit_password, openai_api_key=os.getenv('OPENAI_API_KEY')):
        self.reddit_client_id = reddit_client_id
        self.reddit_client_secret = reddit_client_secret
        self.reddit_username = reddit_username
        self.reddit_password = reddit_password
        self.openai_api_key = openai_api_key
        self.prompt_system = ("You are a helpful and skilled assistant designed to analyze sentiments "
                              "expressed in a list of Reddit posts. Based on a provided list of posts, you will "
                              "provide an analysis of a summary table in csv format (delimiter '|') of the "
                              "posts with their detected sentiment. You will chose between 3 sentiments: "
                              "Positive, Negative, Neutral. The output will be the sentiment detected regarding "
                              "Donald Trump's situation in the elections.")
        self.client = OpenAI(api_key=self.openai_api_key)
        self.dataframe = None

        self.reddit = praw.Reddit(
            client_id=self.reddit_client_id,
            client_secret=self.reddit_client_secret,
            username=self.reddit_username,
            password=self.reddit_password,
            user_agent="sentiment_analysis"
        )

    def search_posts(self, subreddit, query, limit=100):
        try:
            logging.info("Searching Reddit posts...")
            subreddit = self.reddit.subreddit(subreddit)
            posts = subreddit.search(query, limit=limit)
            return [post.title + " " + post.selftext for post in posts]
        except Exception as e:
            logging.error(f"Error while searching posts: {e}")
            raise

    def analyze_sentiments(self, posts):
        logging.info("Analyzing sentiments...")
        nb_choix = len(posts) // 20 + 1
        parts = [posts[i * (len(posts) // nb_choix):(i + 1) * (len(posts) // nb_choix)] for i in range(nb_choix)]
        responses = []
        for part in parts:
            conversation = [
                {"role": "system", "content": self.prompt_system},
                {"role": "user", "content": str(part)}
            ]
            response = self.client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=conversation
            )
            responses.append(response.choices[0].message.content)
        return responses

    def chat_with_dataframe(self, dataframe):
        st.subheader("Llama-3-70b")
        agent = create_pandas_dataframe_agent(
            ChatGroq(model_name="llama3-70b-8192", temperature=0),
            dataframe,
            verbose=True
        )
        prompt = st.text_input("Enter your prompt:")
        if st.button("Generate"):
            if prompt:
                with st.spinner("Generating response..."):
                    response = agent.invoke(prompt)
                    st.write(response["output"])

def main():
    st.title("Reddit Sentiment Analysis")

    st.sidebar.title("Configuration")
    reddit_client_id = st.sidebar.text_input("Reddit Client ID")
    reddit_client_secret = st.sidebar.text_input("Reddit Client Secret", type="password")
    reddit_username = st.sidebar.text_input("Reddit Username")
    reddit_password = st.sidebar.text_input("Reddit Password", type="password")
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

    subreddit = st.text_input("Subreddit", "politics")
    query = st.text_input("Search Query", "Donald Trump election")
    max_posts = st.slider("Number of Posts to Scrape", min_value=10, max_value=500, value=100)

    if "responses" not in st.session_state:
        st.session_state.responses = None

    if st.button("Scrape posts"):
        if not (reddit_client_id and reddit_client_secret and reddit_username and reddit_password and openai_api_key):
            st.error("Please fill in all the fields in the sidebar.")
        else:
            scraper = RedditScraper(reddit_client_id, reddit_client_secret, reddit_username, reddit_password, openai_api_key)
            with st.spinner("Scraping and formatting posts..."):
                responses = scraper.search_posts(subreddit, query, max_posts)
            if responses:
                st.session_state.responses = responses
                st.session_state.df = pd.DataFrame(responses, columns=["Post"])
                st.dataframe(st.session_state.df, use_container_width=True)
            else:
                st.error("An error occurred during the process. Please check the logs.")

    if st.session_state.responses:
        scraper = RedditScraper(reddit_client_id, reddit_client_secret, reddit_username, reddit_password, openai_api_key)
        scraper.chat_with_dataframe(st.session_state.df)

if __name__ == "__main__":
    main()
