from flask import Flask, request, jsonify
import logging
import os
from dotenv import load_dotenv
import pandas as pd
from scrappr import TwitterScraper

app = Flask(__name__)

load_dotenv()  # Load environment variables from a .env file

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    return "Flask API is running!"

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.json
        logging.debug("Received data: %s", data)
        
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        api_key = data.get('api_key')
        query = data.get('query', "Donald Trump election")
        max_tweets = data.get('max_tweets', 10)

        # Log the received values
        logging.debug("email: %s", email)
        logging.debug("username: %s", username)
        logging.debug("password: %s", password)
        logging.debug("api_key: %s", api_key)
        logging.debug("query: %s", query)
        logging.debug("max_tweets: %s", max_tweets)
        
        if not email or not username or not password:
            return jsonify({"error": "Missing email, username, or password"}), 400

        # Call your scraping function from scrappr.py with the provided parameters
        logging.debug("Starting TwitterScraper with email: %s, username: %s", email, username)
        df = initialisation(email, username, password, api_key, query, max_tweets)

        logging.debug("DataFrame content: %s", df)

        if not df.empty:
            tweets_json = df.to_dict(orient='records')
            return jsonify({"message": "Scraping completed successfully", "tweets": tweets_json})
        else:
            return jsonify({"error": "No tweets found or an error occurred"}), 500
    except Exception as e:
        logging.exception("An error occurred during the scraping process.")
        return jsonify({"error": str(e)}), 500

def initialisation(email, username, password, keyapi, query, max_tweets=10):
    scraper = TwitterScraper(email, username, password, keyapi)
    tweets = scraper.run(query, max_tweets)
    
    logging.debug("Tweets fetched: %s", tweets)

    # Check if tweets is a list of dictionaries with the correct keys
    if tweets and isinstance(tweets, list) and all(isinstance(tweet, dict) for tweet in tweets):
        df = pd.DataFrame(tweets)
    else:
        if not tweets:
            logging.error("No tweets found or an error occurred.")
        elif not isinstance(tweets, list):
            logging.error("Expected a list of tweets, got: %s", type(tweets))
        elif not all(isinstance(tweet, dict) for tweet in tweets):
            logging.error("Some items in the tweets list are not dictionaries: %s", tweets)
        df = pd.DataFrame([], columns=['tweet', 'username', 'reply', 'like', 'retweet', 'views'])
    return df

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
