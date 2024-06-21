import streamlit as st
import pandas as pd
import openai
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_groq import ChatGroq
from credentiels import openai_api_key

class TwitterAnalyzer:
    def __init__(self, openai_api_key=openai_api_key):
        self.openai_api_key = openai_api_key
        openai.api_key = self.openai_api_key
        self.dataframe = None

    def analyze_sentiments(self, tweets):
        prompt_system = ("You are a helpful and skilled assistant designed to analyze sentiments "
                         "expressed in a list of tweets. Based on a provided list of tweets, you will "
                         "provide an analysis of a summary table in csv format (delimiter '|') of the "
                         "tweets with their detected sentiment. You will chose between 3 sentiments: "
                         "Positive, Negative, Neutral. The output will be the sentiment detected regarding "
                         "Donald Trump's situation in the elections.")
        messages = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": "\n".join(tweets)}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
        )
        return response['choices'][0]['message']['content']

def main():
    st.title("Twitter Sentiment Analysis")

    if 'df' in st.session_state:
        df = st.session_state.df
        st.dataframe(df, use_container_width=True)

        if st.button("Analyze Sentiments"):
            analyzer = TwitterAnalyzer(openai_api_key)
            with st.spinner("Analyzing sentiments..."):
                tweets = df['Tweet'].tolist()
                analysis = analyzer.analyze_sentiments(tweets)
                st.text_area("Sentiment Analysis Output", value=analysis, height=300)

        if st.button("Back to Home"):
            st.session_state.page = 'home'
            st.experimental_rerun()
    else:
        st.error("No data available. Please go back to the home page and scrape tweets first.")

if __name__ == "__main__":
    main()