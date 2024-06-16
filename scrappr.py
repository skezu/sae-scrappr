import os
import time
import logging
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from openai import OpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_groq import ChatGroq
import pandas as pd
from credentials import twitter_email, twitter_username, twitter_password, openai_api_key

# Configure logging
logging.basicConfig(level=logging.INFO)

class TwitterScraper:
    def __init__(self, twitter_email, twitter_username, twitter_password, openai_api_key=os.getenv('OPENAI_API_KEY')):
        self.twitter_email = twitter_email
        self.twitter_username = twitter_username
        self.twitter_password = twitter_password
        self.openai_api_key = openai_api_key
        self.prompt_system = ("You are a helpful and skilled assistant designed to analyze sentiments "
                              "expressed in a list of tweets. Based on a provided list of tweets, you will "
                              "provide an analysis of a summary table in csv format (delimiter '|') of the "
                              "tweets with their detected sentiment. You will chose between 3 sentiments: "
                              "Positive, Negative, Neutral. The output will be the sentiment detected regarding "
                              "Donald Trump's situation in the elections.")
        self.driver = self.initialize_driver()
        self.client = OpenAI(api_key=self.openai_api_key)
        self.dataframe = None

    @staticmethod
    def initialize_driver():
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.page_load_strategy = 'none'
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def login_to_twitter(self):
        try:
            self.driver.get('https://twitter.com/i/flow/login')
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input'))).send_keys(self.twitter_email)
            self.driver.find_element(By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]').click()
            
            try:
                WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input'))).send_keys(self.twitter_username)
                self.driver.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/button').click()
            except NoSuchElementException:
                logging.info("Username confirmation page not found, continuing...")

            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input'))).send_keys(self.twitter_password)
            self.driver.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/button').click()
        except TimeoutException:
            logging.error("Timeout while trying to log in to Twitter.")
            raise
        except WebDriverException as e:
            logging.error(f"WebDriver exception occurred: {e}")
            raise

    def search_tweets(self, query):
        try:
            time.sleep(3)
            self.driver.get('https://x.com/explore')
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div[1]/div/div/div/div/div[1]/div[2]/div/div/div/form/div[1]/div/div/div/div/div[2]/div/input')))
            search_box = self.driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div[1]/div/div/div/div/div[1]/div[2]/div/div/div/form/div[1]/div/div/div/div/div[2]/div/input')
            search_box.send_keys(query)
            search_box.send_keys(Keys.ENTER)
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div[2]/nav/div/div[2]/div/div[2]/a'))).click()
        except TimeoutException:
            logging.error("Timeout while trying to search tweets.")
            raise
        except WebDriverException as e:
            logging.error(f"WebDriver exception occurred: {e}")
            raise

    def scrape_tweets(self, max_tweets=100):
        try:
            time.sleep(1)
            logging.info("Scraping tweets...")
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            postings = soup.find_all('div', {'class': 'css-146c3p1 r-8akbws r-krxsd3 r-dnmrzs r-1udh08x r-bcqeeo r-1ttztb7 r-qvutc0 r-1qd0xha r-a023e6 r-rjixqe r-16dba41 r-bnwqim', 'data-testid': 'tweetText'})
            
            tweets = []
            while True:
                for post in postings:
                    tweets.append(post.text)
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(1)
                soup = BeautifulSoup(self.driver.page_source, 'lxml')
                postings = soup.find_all('div', class_='css-146c3p1 r-8akbws r-krxsd3 r-dnmrzs r-1udh08x r-bcqeeo r-1ttztb7 r-qvutc0 r-1qd0xha r-a023e6 r-rjixqe r-16dba41 r-bnwqim')
                tweets2 = list(set(tweets))
                if len(tweets2) > max_tweets:
                    break
            return tweets2
        except Exception as e:
            logging.error(f"Error while scraping tweets: {e}")
            raise

    def analyze_sentiments(self, tweets):
        logging.info("Analyzing sentiments...")
        nb_choix = len(tweets) // 20 + 1
        parts = [tweets[i * (len(tweets) // nb_choix):(i + 1) * (len(tweets) // nb_choix)] for i in range(nb_choix)]
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

    def run(self, query, max_tweets=100):
        try:
            self.login_to_twitter()
            self.search_tweets(query)
            tweets = self.scrape_tweets(max_tweets)
            return tweets
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None
        finally:
            self.driver.quit()

def main():
    st.title("x Sentiment Analysis")


    query = st.text_input("Search Query", "Donald Trump election")
    max_tweets = st.slider("Number of Tweets to Scrape", min_value=10, max_value=500, value=100)

    if "responses" not in st.session_state:
        st.session_state.responses = None

    if st.button("Scrap tweets"):
        if not (twitter_email and twitter_username and twitter_password and openai_api_key):
            st.error("Please fill in all the fields in the sidebar.")
        else:
            scraper = TwitterScraper(twitter_email, twitter_username, twitter_password, openai_api_key)
            with st.spinner("Scraping and formatting tweets..."):
                responses = scraper.run(query, max_tweets)
            if responses:
                st.session_state.responses = responses
                st.session_state.df = pd.DataFrame(responses, columns=["Tweet"])
                st.dataframe(st.session_state.df, use_container_width=True)
            else:
                st.error("An error occurred during the process. Please check the logs.")

    if st.session_state.responses:
        #st.dataframe(st.session_state.df, use_container_width=True)
        scraper = TwitterScraper(twitter_email, twitter_username, twitter_password, openai_api_key)
        scraper.chat_with_dataframe(st.session_state.df)

if __name__ == "__main__":
    main()
