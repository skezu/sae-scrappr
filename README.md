```markdown
# Twitter Sentiment Analysis

A Python application for scraping tweets related to a specific topic and analyzing their sentiments using OpenAI's GPT-4. The project leverages Streamlit for the web interface, Selenium for web scraping, BeautifulSoup for HTML parsing, and LangChain for enhanced language model interactions.

## Features

- **Twitter Login**: Automates login to Twitter using provided credentials.
- **Tweet Scraping**: Searches and scrapes tweets based on a specified query.
- **Sentiment Analysis**: Analyzes the sentiments of scraped tweets using OpenAI's GPT-4 model.
- **Data Display**: Displays the results in a Streamlit web application.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/twitter-sentiment-analysis.git
    cd twitter-sentiment-analysis
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. Create a `.env` file in the root directory and add your OpenAI API key:
    ```plaintext
    OPENAI_API_KEY=your_openai_api_key
    ```

2. Update the `TwitterScraper` class with your Twitter credentials (email, username, and password) in the Streamlit sidebar.

## Usage

1. Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```

2. Open the application in your web browser. Fill in the Twitter credentials and OpenAI API key in the sidebar.

3. Enter a search query (e.g., "Donald Trump election") and select the number of tweets to scrape.

4. Click the "Scrap tweets" button to start the scraping and sentiment analysis process.

5. The scraped tweets and their sentiments will be displayed in a table. You can interact with the data using the Llama-3-70b model for further analysis.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License.

## Contact

For any inquiries or issues, please open an issue in the GitHub repository.

---

**Note**: Ensure that your Twitter credentials and OpenAI API key are kept secure and not exposed in any public repositories or environments.
```