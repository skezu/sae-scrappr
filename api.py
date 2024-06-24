from flask import Flask, request, jsonify
import logging
import os
from dotenv import load_dotenv
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
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        api_key = data.get('api_key')

        if not email or not username or not password:
            return jsonify({"error": "Missing email, username, or password"}), 400

        # Call your scraping function from scrappr.py with the provided parameters
        logging.debug("Starting TwitterScraper with email: %s, username: %s", email, username)
        result = TwitterScraper(email, username, password, api_key).initialisation()

        return jsonify(result)
    except Exception as e:
        logging.exception("An error occurred during the scraping process.")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)