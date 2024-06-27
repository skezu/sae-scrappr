import os
import time
import logging
import streamlit as st
import requests
import pandas as pd
import dotenv

# Chargement des variables d'environnement
dotenv.load_dotenv()

# Configuration du logging
logging.basicConfig(level=logging.INFO)

# URL de l'API Flask
API_URL = "http://localhost:5001/scrape"


def appelle_api_scrape(email, username, password, api_key, query, max_tweets=10):
    """
    Appelle l'API de scrapping Twitter avec les informations fournies.

    Args:
        email (str): Email de connexion à Twitter.
        username (str): Nom d'utilisateur de connexion à Twitter.
        password (str): Mot de passe de connexion à Twitter.
        api_key (str): Clé d'API OpenAI.
        query (str): Requête de recherche.
        max_tweets (int, optional): Nombre maximum de tweets à scraper. Defaults to 10.

    Returns:
        dict: Réponse de l'API contenant les tweets scrappés.
    """
    try:
        email = email or os.getenv("TWITTER_EMAIL")
        username = username or os.getenv("TWITTER_USERNAME")
        password = password or os.getenv("TWITTER_PASSWORD")
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        payload = {
            "email": email,
            "username": username,
            "password": password,
            "api_key": api_key,
            "query": query,
            "max_tweets": max_tweets
        }
        print(payload)
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur lors de l'appel de l'API de scrapping: {e}")
        return {"error": str(e)}


def page_scraping():
    """
    Page Streamlit pour le scrapping des tweets.
    """
    st.title("Analyse des sentiments Twitter")
    st.sidebar.title("Configuration")
    twitter_email = st.sidebar.text_input("Email Twitter")
    twitter_username = st.sidebar.text_input("Nom d'utilisateur Twitter")
    twitter_password = st.sidebar.text_input("Mot de passe Twitter", type="password")
    openai_api_key = st.sidebar.text_input("Clé d'API OpenAI", type="password")
    query = st.text_input("Recherche", "RN Vote")
    allow_replies = st.checkbox("Autoriser les réponses")
    if not allow_replies:
        query += " -filter:replies"
    tweet_type = st.radio("Sélectionner le type de tweet", ("Récent", "Nouveau"))
    max_tweets = st.slider("Nombre de tweets à scraper", min_value=10, max_value=100, value=50)

    if "responses" not in st.session_state:
        st.session_state.responses = None

    if st.button("Scraper les tweets"):
        with st.spinner("Scraper et formatage des tweets..."):
            response = appelle_api_scrape(twitter_email, twitter_username, twitter_password, openai_api_key, query, max_tweets)
            if "error" in response:
                st.error(f"Une erreur est survenue: {response['error']}")
            else:
                tweets = response.get("tweets", [])
                if tweets:
                    st.session_state.responses = tweets
                    st.session_state.df = pd.DataFrame(tweets, columns=["tweet", "username", "reply", "retweet", "like", "views"])
                    st.session_state.openai_api_key = openai_api_key
                else:
                    st.error("Aucun tweet trouvé ou une erreur est survenue.")

    if st.session_state.responses:
        st.dataframe(st.session_state.df, use_container_width=True)

        csv = st.session_state.df.to_csv(index=False, sep=',', encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="Télécharger les tweets en CSV",
            data=csv,
            file_name="tweets_scrappes.csv",
            mime="text/csv",
            key='download-csv'
        )

        if st.button("Page d'analyse"):
            st.session_state.page = 'chatbot'
            st.experimental_rerun()

def main():
    """
    Point d'entrée de l'application.
    """
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if st.session_state.page == "home":
        page_scraping()
    elif st.session_state.page == "chatbot":
        import chat
        chat.main()

if __name__ == "__main__":
    main()

