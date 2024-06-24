from flask import Flask, request, jsonify
import scrappr  # assuming this is the name of your script for scrapping
import os
from dotenv import load_dotenv
from scrappr import TwitterScraper

app = Flask(__name__)

load_dotenv()  # Load environment variables from a .env file
@app.route('/')
def home():
    return "Flask API is running!"
@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    api_key = None
    
    if not email or not username or not password:
        return jsonify({"error": "Missing email, username, or password"}), 400

    # Call your scraping function from scrappr.py with the provided parameters
    result = TwitterScraper(scrape.email, scrape.username, scrape.password, scrape.api_key).initialisation()

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)







































