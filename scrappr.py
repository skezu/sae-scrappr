import os
import time
import logging
import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import openai
from credentiels import twitter_email, twitter_username, twitter_password, openai_api_key

# Configure logging
logging.basicConfig(level=logging.INFO)

class TwitterScraper:
    def __init__(self, twitter_email, twitter_username, twitter_password, openai_api_key=os.getenv('OPENAI_API_KEY')):
        self.twitter_email = twitter_email
        self.twitter_username = twitter_username
        self.twitter_password = twitter_password
        self.openai_api_key = openai_api_key
        openai.api_key = self.openai_api_key
        self.driver = self.initialize_driver()
        #self.client = OpenAI(api_key=self.openai_api_key)
        #self.dataframe = None

    @staticmethod   
    def initialize_driver():
        # Initialize the web driver
        options = webdriver.ChromeOptions()
        #options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
        
    def login_to_twitter(self):
        try:
            self.driver.get('https://twitter.com/i/flow/login')
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input'))).send_keys(self.twitter_email)
            # WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input'))).send_keys(self.twitter_username)
            self.driver.find_element(By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]').click()
            
            # try:
            #     WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input'))).send_keys(self.twitter_username)
            #     self.driver.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/button').click()
            # except NoSuchElementException:
            #     logging.info("Username confirmation page not found, continuing...")
            
            password = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[2]/div/label/div/div[2]/div[1]/input')))
            password.send_keys(self.twitter_password)
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
    st.title("x Analysis")

    query = st.text_input("Search Query", "Donald Trump election")
    max_tweets = st.slider("Number of Tweets to Scrape", min_value=10, max_value=100, value=50)

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
        st.dataframe(st.session_state.df, use_container_width=True)
        
        if st.button("Download Dataframe as CSV"):
            csv = st.session_state.df.to_csv(index=False)
            st.download_button(label="Download CSV", data=csv, file_name="tweets.csv", mime="text/csv")
        
        if st.button("Go to Chat Page"):
            st.session_state.page = 'chat'
            st.experimental_rerun()

if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

    if st.session_state.page == 'home':
        main()
    elif st.session_state.page == 'chat':
        import chat
        chat.main() 