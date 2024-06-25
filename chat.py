import streamlit as st
import pandas as pd
from openai import OpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import os

class TwitterAnalyzer:
    def __init__(self, openai_api_key=os.getenv('OPENAI_API_KEY')):
        self.openai_api_key = openai_api_key
        self.dataframe = None
        self.client = OpenAI(api_key=self.openai_api_key)

    def analyze_sentiments(self, tweets):
        prompt_system = """
        You are a helpful and skilled assistant designed to analyze sentiments "
        "expressed in a list of tweets. Based on a provided list of tweets, you will "
        "provide an analysis of a summary table in csv format (delimiter '|') of the "
        "tweets with their detected sentiment. You will chose between 3 sentiments: "
        "Positive, Negative, Neutral. The output will be the sentiment detected regarding "
        "Donald Trump's situation in the elections.
        """
        nb_choix = len(tweets) // 20 + 1
        parts = [tweets[i * (len(tweets) // nb_choix):(i + 1) * (len(tweets) // nb_choix)] for i in range(nb_choix)]
        responses = []
        for part in parts:
            conversation = [
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": str(part)}
            ]
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=conversation
            )
            responses.append(response.choices[0].message.content)
        return responses
    
    def chat_with_dataframe(self, dataframe):
        st.subheader("Chat with the AI")
        agent = create_pandas_dataframe_agent(
            ChatOpenAI(model_name="gpt-4-turbo-2024-04-09", temperature=0),
            dataframe,
            verbose=True
        )
        prompt = st.text_input("Enter your prompt:")
        if st.button("Chat"):
            if prompt:
                with st.spinner("Generating response..."):
                    response = agent.invoke(prompt)
                    st.write(response["output"])
    

def main():
    st.title("Twitter Sentiment Analysis")

    if 'df' in st.session_state:
        analyzer = TwitterAnalyzer()
        df = st.session_state.df
        st.dataframe(df, use_container_width=True)
        analyzer.chat_with_dataframe(df)

        if st.button("Analyze Sentiments"):
            with st.spinner("Analyzing sentiments..."):
                tweets = df["tweet"].tolist()
                analysis = analyzer.analyze_sentiments(tweets)
                st.text_area("Sentiment Analysis Output", value=analysis, height=300)

        if st.button("Back to Home"):
            st.session_state.page = 'home'
            st.experimental_rerun()
    else:
        st.error("No data available. Please go back to the home page and scrape tweets first.")

if __name__ == "__main__":
    main()