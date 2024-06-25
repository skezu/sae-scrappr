from flask import Flask, request, jsonify
import logging
import os
from dotenv import load_dotenv
from scrappr import TwitterScraper, initialisation

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
        output = data.get('output', "output.csv")

        # Log the received values
        logging.debug("email: %s", email)
        logging.debug("username: %s", username)
        logging.debug("password: %s", password)
        logging.debug("api_key: %s", api_key)
        logging.debug("query: %s", query)
        logging.debug("max_tweets: %s", max_tweets)
        logging.debug("output: %s", output)
        
        if not email or not username or not password:
            return jsonify({"error": "Missing email, username, or password"}), 400

        # Call your scraping function from scrappr.py with the provided parameters
        logging.debug("Starting TwitterScraper with email: %s, username: %s", email, username)
        df = initialisation(email, username, password, api_key, query, max_tweets, output)

        if df is not None:
            return jsonify({"message": "Scraping completed successfully", "output_file": output})
        else:
            return jsonify({"error": "Scraping failed"}), 500
    except Exception as e:
        logging.exception("An error occurred during the scraping process.")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
