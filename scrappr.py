import argparse
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)

class TwitterScraper:
    def __init__(self, twitter_email, twitter_username, twitter_password):
        self.twitter_email = twitter_email
        self.twitter_username = twitter_username
        self.twitter_password = twitter_password
        self.prompt_system = ("You are a helpful and skilled assistant designed to analyze sentiments "
                              "expressed in a list of tweets. Based on a provided list of tweets, you will "
                              "provide an analysis of a summary table in csv format (delimiter '|') of the "
                              "tweets with their detected sentiment. You will chose between 3 sentiments: "
                              "Positive, Negative, Neutral. The output will be the sentiment detected regarding "
                              "Donald Trump's situation in the elections.")
        self.driver = self.initialize_driver()
        self.dataframe = None

    @staticmethod
    def initialize_driver():
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
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

    def initialisation(email, username, password, query, max_tweets=10, output="output.csv"):
        scraper = TwitterScraper(email, username, password)
        tweets = scraper.run(query, max_tweets)
        if tweets:
            df = pd.DataFrame(tweets, columns=["Tweet"])
            df.to_csv(output, index=False)
            print(f"CSV generated: {output}")
        else:
            print("No tweets found or an error occurred.")
        return df


def main():
    parser = argparse.ArgumentParser(description='Scrappr script')
    parser.add_argument('--email', type=str, required=True, help='Twitter Email')
    parser.add_argument('--username', type=str, required=True, help='Twitter Username')
    parser.add_argument('--password', type=str, required=True, help='Twitter Password')
    parser.add_argument('--query', type=str, default="Donald Trump election", help='Search Query')
    parser.add_argument('--max_tweets', type=int, default=100, help='Number of Tweets to Scrape')
    parser.add_argument('--output', type=str, default='output.csv', help='Output CSV file')
    args = parser.parse_args()

    scraper = TwitterScraper(args.email, args.username, args.password)
    tweets = scraper.run(args.query, args.max_tweets)
    if tweets:
        df = pd.DataFrame(tweets, columns=["Tweet"])
        df.to_csv(args.output, index=False)
        print(f"CSV generated: {args.output}")
    else:
        print("No tweets found or an error occurred.")

if __name__ == "__main__":
    main()
