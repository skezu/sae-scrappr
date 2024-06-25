import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import networkx as nx
from collections import Counter
import re
from textblob import TextBlob

def create_top_tweets_chart(df, column, title):
    if column in df.columns and 'username' in df.columns and 'tweet' in df.columns:
        # df[f'{column}_numeric'] = pd.to_numeric(df[column].str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        top_tweets = df.nlargest(5, f'{column}_numeric')
        fig = px.bar(top_tweets, x='username', y=f'{column}_numeric', text=f'{column}_numeric',
                     hover_data=['tweet'], title=title)
        fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"Required columns for {title} not found in the DataFrame")

def create_engagement_scatter(df):
    if all(col in df.columns for col in ['like', 'retweet', 'views', 'username', 'tweet']):
        df['views_numeric'] = pd.to_numeric(df['views'].str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        df['engagement_rate'] = (df['like_numeric'] + df['retweet_numeric']) / df['views_numeric']
        top_engaged = df.nlargest(10, 'engagement_rate')
        fig = px.scatter(top_engaged, x='views_numeric', y='engagement_rate', 
                         size='like_numeric', color='retweet_numeric',
                         hover_data=['tweet', 'username'], 
                         title="Top Tweets by Engagement Rate")
        fig.update_layout(xaxis_title="Views", yaxis_title="Engagement Rate")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Required columns for Engagement Rate chart not found in the DataFrame")

def create_tweet_length_engagement_chart(df):
    if all(col in df.columns for col in ['tweet', 'like', 'retweet']):
        df['tweet_length'] = df['tweet'].str.len()
        df['total_engagement'] = df['like_numeric'] + df['retweet_numeric']
        fig = px.scatter(df, x='tweet_length', y='total_engagement', 
                         hover_data=['tweet', 'username'],
                         title="Tweet Length vs. Total Engagement")
        fig.update_layout(xaxis_title="Tweet Length (characters)", yaxis_title="Total Engagement (Likes + Retweets)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Required columns for Tweet Length vs. Engagement chart not found in the DataFrame")

def create_interaction_distribution(df):
    if all(col in df.columns for col in ['like', 'retweet', 'reply']):
        interaction_data = {
            'Type': ['Likes', 'Retweets', 'Replies'],
            'Count': [
                df['like_numeric'].sum(),
                df['retweet_numeric'].sum(),
                pd.to_numeric(df['reply'].str.replace(r'[^\d.]', '', regex=True), errors='coerce').sum()
            ]
        }
        fig = px.pie(interaction_data, values='Count', names='Type', 
                     title="Distribution of Interaction Types")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Required columns for Interaction Distribution chart not found in the DataFrame")

def create_hashtag_network(df):
    if 'tweet' in df.columns:
        hashtags = df['tweet'].str.findall(r'#(\w+)').explode().value_counts().head(10)
        G = nx.Graph()
        for tweet in df['tweet']:
            tweet_hashtags = re.findall(r'#(\w+)', tweet.lower())
            for i in range(len(tweet_hashtags)):
                for j in range(i+1, len(tweet_hashtags)):
                    G.add_edge(tweet_hashtags[i], tweet_hashtags[j])
        pos = nx.spring_layout(G)
        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        node_trace = go.Scatter(x=node_x, y=node_y, mode='markers', hoverinfo='text',
                                marker=dict(showscale=True, colorscale='YlGnBu', size=10))
        node_adjacencies = []
        node_text = []
        for node, adjacencies in enumerate(G.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))
            node_text.append(f'#{adjacencies[0]}: {len(adjacencies[1])} connections')
        node_trace.marker.color = node_adjacencies
        node_trace.text = node_text
        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(title="Hashtag Co-occurrence Network", showlegend=False, hovermode='closest',
                                         margin=dict(b=20,l=5,r=5,t=40)))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Column 'tweet' not found in the DataFrame")

def create_sentiment_distribution(df):
    if 'tweet' in df.columns:
        df['sentiment'] = df['tweet'].apply(lambda x: TextBlob(x).sentiment.polarity)
        sentiment_counts = pd.cut(df['sentiment'], bins=[-1, -0.1, 0.1, 1], labels=['Negative', 'Neutral', 'Positive']).value_counts()
        fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, title="Sentiment Distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Column 'tweet' not found in the DataFrame")

def create_top_words(df):
    if 'tweet' in df.columns:
        common_words = set([
            # English
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 
            'from', 'up', 'about', 'into', 'over', 'after', 'is', 'am', 'are', 'was', 'were', 'be', 
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall', 
            'should', 'can', 'could', 'may', 'might', 'must', 'ought', 'i', 'you', 'he', 'she', 'it', 
            'we', 'they', 'them', 'their', 'this', 'that', 'these', 'those', 'who', 'whom', 'whose',
            'which', 'where', 'when', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 'just', 'even', 'also',
            # French
            'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'ou', 'mais', 'donc', 'car',
            'ni', 'que', 'qui', 'quoi', 'dont', 'où', 'quand', 'comment', 'pourquoi', 'quel',
            'quelle', 'quels', 'quelles', 'ce', 'cet', 'cette', 'ces', 'mon', 'ma', 'mes', 'ton',
            'ta', 'tes', 'son', 'sa', 'ses', 'notre', 'nos', 'votre', 'vos', 'leur', 'leurs',
            'je', 'tu', 'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles', 'me', 'te', 'se',
            'lui', 'y', 'en', 'au', 'aux', 'avec', 'sans', 'pour', 'par', 'dans', 'sur', 'sous',
            'être', 'avoir', 'faire', 'dire', 'aller', 'voir', 'savoir', 'pouvoir', 'vouloir',
            'falloir', 'devoir', 'pas', 'est', 'ne', 'si', 'ça'
        ])

        word_counts = Counter()
        word_tweet_counts = Counter()
        total_tweets = len(df)

        for tweet in df['tweet']:
            tweet_words = set(re.findall(r'\b\w+\b', tweet.lower()))
            tweet_words = [word for word in tweet_words if word not in common_words and len(word) > 1]
            word_counts.update(tweet_words)
            word_tweet_counts.update(tweet_words)

        word_scores = {word: (count / total_tweets) * word_counts[word] 
                       for word, count in word_tweet_counts.items()}

        top_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        fig = px.bar(x=[word for word, score in top_words], 
                     y=[score for word, score in top_words], 
                     title="Top 5 Correlated Words Across Tweets")
        fig.update_layout(xaxis_title="Word", yaxis_title="Correlation Score")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("Column 'tweet' not found in the DataFrame")

def create_top_hashtags(df):
    if 'tweet' in df.columns:
        hashtags = re.findall(r'#(\w+)', ' '.join(df['tweet']))
        hashtag_counts = Counter(hashtags)
        top_hashtags = hashtag_counts.most_common(5)
        
        fig = px.bar(x=[tag for tag, count in top_hashtags], 
                     y=[count for tag, count in top_hashtags],
                     title="Top 5 Hashtags")
        fig.update_layout(xaxis_title="Hashtag", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Column 'tweet' not found in the DataFrame")
        
def convert_to_numeric(value):
    if isinstance(value, str):
        value = value.lower().replace(' ', '')  # Remove any spaces
        if 'k' in value:
            value = value.replace('k', '000')
        elif 'm' in value:
            value = value.replace('m', '000000')
        # Remove any non-numeric characters except for '.'
        value = re.sub(r'[^\d.]', '', value)
        try:
            return float(value)
        except ValueError:
            return 0.0  # Default to 0 if conversion fails
    return value

def update_numeric_columns(df):
    for column in ['reply', 'like', 'retweet', 'views']:
        if column in df.columns:
            df[f'{column}_numeric'] = df[column].apply(convert_to_numeric).fillna(0)
    return df

def main():
    st.title("Advanced Twitter Analysis Dashboard")

    if 'df' in st.session_state:
        df = st.session_state.df
        df = update_numeric_columns(df)
        
        # Display DataFrame without numeric columns
        display_df = df.drop(columns=['like', 'retweet', 'views'], errors='ignore')
        st.dataframe(display_df, use_container_width=True)
        
        # 4. Sentiment Distribution
        create_sentiment_distribution(df)

        # 1. Top 5 Most Liked Tweets
        create_top_tweets_chart(df, 'like', "Most Liked Tweets")

        # 2. Top 5 Most Retweeted Tweets
        create_top_tweets_chart(df, 'retweet', "Most Retweeted Tweets")

        # 3. Top 5 Most Viewed Tweets
        create_top_tweets_chart(df, 'views', "Most Viewed Tweets")


        # 5. Top 5 Hashtags
        create_top_hashtags(df)

        # 6. Top 5 Correlated Words Across Tweets
        create_top_words(df)

        # 7. Hashtag Co-occurrence Network
        create_hashtag_network(df)

        # 8. Engagement Rate (Likes + Retweets) / Views
        create_engagement_scatter(df)

        # 9. Distribution of Interaction Types
        create_interaction_distribution(df)

        # 10. Tweet Length vs. Total Engagement
        create_tweet_length_engagement_chart(df)

        if st.button("Back to Home"):
            st.session_state.page = 'home'
            st.rerun()
    else:
        st.error("No data available. Please go back to the home page and scrape tweets first.")


if __name__ == "__main__":
    main()
