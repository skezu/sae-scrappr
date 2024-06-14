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

# Configure logging
logging.basicConfig(level=logging.INFO)

class RedditScraper:
    def __init__(self, reddit_email, reddit_username, reddit_password, openai_api_key=os.getenv('OPENAI_API_KEY')):
        self.reddit_email = reddit_email
        self.reddit_username = reddit_username
        self.reddit_password = reddit_password
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

    def login_to_reddit(self):
        try:
            self.driver.get('https://www.reddit.com/login/')
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/shreddit-app/shreddit-overlay-display/span[4]/input'))).send_keys(self.reddit_email)
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/shreddit-app/shreddit-overlay-display/span[5]/input'))).send_keys(self.reddit_password)
            time.sleep(5)
            # self.driver.find_element(By.XPATH, '/html/body/shreddit-app/shreddit-overlay-display//shreddit-signup-drawer//shreddit-drawer/div/shreddit-async-loader/div/shreddit-slotter//span/shreddit-async-loader/auth-flow-login/faceplate-tabpanel/faceplate-form[1]/auth-flow-modal/div[2]/faceplate-tracker/button').click()
            self.driver.find_element(By.XPATH, '//*[@id="login"]/auth-flow-modal/div[2]/faceplate-tracker/button').send_keys(Keys.ENTER)
        except TimeoutException:
            logging.error("Timeout while trying to log in to Reddit.")
            raise
        except WebDriverException as e:
            logging.error(f"WebDriver exception occurred: {e}")
            raise

    def search_reddits(self, query):
        try:
            time.sleep(3)
            self.driver.get('https://www.reddit.com/')
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/shreddit-app/reddit-header-large/reddit-header-action-items/header/nav/div[2]/div/div/search-dynamic-id-cache-controller/reddit-search-large//div/div[1]/form/faceplate-search-input//label/div/span[2]/input')))
            search_box = self.driver.find_element(By.XPATH, '/html/body/shreddit-app/reddit-header-large/reddit-header-action-items/header/nav/div[2]/div/div/search-dynamic-id-cache-controller/reddit-search-large//div/div[1]/form/faceplate-search-input//label/div/span[2]/input')
            search_box.send_keys(query)
            search_box.send_keys(Keys.ENTER)
            #WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div[2]/nav/div/div[2]/div/div[2]/a'))).click()
        except TimeoutException:
            logging.error("Timeout while trying to search reddits.")
            raise
        except WebDriverException as e:
            logging.error(f"WebDriver exception occurred: {e}")
            raise

    def scrape_reddits(self, max_reddits=100):
        try:
            time.sleep(1)
            logging.info("Scraping reddits...")
            self.driver.find_element(By.XPATH, '/html/body/shreddit-app/search-dynamic-id-cache-controller/div/div/div[1]/div[2]/main/div/reddit-feed/faceplate-tracker[1]/post-consume-tracker/div/faceplate-tracker[1]/h2/a').click()
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            postings = soup.find_all('section', {'class': 'flex flex-col px-md xs:px-0 gap-md relative', 'aria-label': 'Commentaires'})
            
            reddits = []
            while True:
                for post in postings:
                    reddits.append(post.text)
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(1)
                soup = BeautifulSoup(self.driver.page_source, 'lxml')
                postings = soup.find_all('section', class_='flex flex-col px-md xs:px-0 gap-md relative')
                reddits2 = list(set(reddits))
                if len(reddits2) > max_reddits:
                    break
            return reddits2
        except Exception as e:
            logging.error(f"Error while scraping reddits: {e}")
            raise

    def analyze_sentiments(self, reddits):
        logging.info("Analyzing sentiments...")
        nb_choix = len(reddits) // 20 + 1
        parts = [reddits[i * (len(reddits) // nb_choix):(i + 1) * (len(reddits) // nb_choix)] for i in range(nb_choix)]
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

    def run(self, query, max_reddits=100):
        try:
            self.login_to_reddit()
            self.search_reddits(query)
            reddits = self.scrape_reddits(max_reddits)
            return reddits
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None
        finally:
            self.driver.quit()

def main():
    st.title("Reddit Sentiment Analysis")

    st.sidebar.title("Configuration")
    reddit_email = st.sidebar.text_input("Reddit Email", type="password")
    reddit_username = st.sidebar.text_input("Reddit Username")
    reddit_password = st.sidebar.text_input("Reddit Password", type="password")
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

    query = st.text_input("Search Query", "Donald Trump election")
    max_reddits = st.slider("Number of Reddits to Scrape", min_value=10, max_value=500, value=100)

    if "responses" not in st.session_state:
        st.session_state.responses = None

    if st.button("Scrap reddits"):
        if not (reddit_email and reddit_username and reddit_password and openai_api_key):
            st.error("Please fill in all the fields in the sidebar.")
        else:
            scraper = RedditScraper(reddit_email, reddit_username, reddit_password, openai_api_key)
            with st.spinner("Scraping and formatting reddits..."):
                responses = scraper.run(query, max_reddits)
            if responses:
                st.session_state.responses = responses
                st.session_state.df = pd.DataFrame(responses, columns=["Reddits"])
                st.dataframe(st.session_state.df, use_container_width=True)
            else:
                st.error("An error occurred during the process. Please check the logs.")

    if st.session_state.responses:
        #st.dataframe(st.session_state.df, use_container_width=True)
        scraper = RedditScraper(reddit_email, reddit_username, reddit_password, openai_api_key)
        scraper.chat_with_dataframe(st.session_state.df)

if __name__ == "__main__":
    main()
