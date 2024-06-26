import pandas as pd
import plotly.express as px
import streamlit as st
import unittest
from unittest.mock import patch
from chat import create_top_tweets_chart

class TestCreateTopTweetsChart(unittest.TestCase):

    @patch('streamlit.error')
    def test_missing_column(self, mock_error):
        df = pd.DataFrame({'username': ['user1', 'user2'], 'tweet': ['tweet1', 'tweet2']})
        create_top_tweets_chart(df, 'likes', 'Top Tweets')
        mock_error.assert_called_with("Required columns for Top Tweets not found in the DataFrame")

    @patch('streamlit.error')
    def test_missing_username_column(self, mock_error):
        df = pd.DataFrame({'column': [1, 2], 'tweet': ['tweet1', 'tweet2']})
        create_top_tweets_chart(df, 'column', 'Top Tweets')
        mock_error.assert_called_with("Required columns for Top Tweets not found in the DataFrame")

    @patch('streamlit.error')
    def test_missing_tweet_column(self, mock_error):
        df = pd.DataFrame({'column': [1, 2], 'username': ['user1', 'user2']})
        create_top_tweets_chart(df, 'column', 'Top Tweets')
        mock_error.assert_called_with("Required columns for Top Tweets not found in the DataFrame")

    @patch('streamlit.plotly_chart')
    def test_all_columns_present(self, mock_plotly_chart):
        df = pd.DataFrame({'username': ['user1', 'user2'], 'tweet': ['tweet1', 'tweet2'], 'column_numeric': [10, 20]})
        create_top_tweets_chart(df, 'column', 'Top Tweets')
        mock_plotly_chart.assert_called()

if __name__ == '__main__':
    unittest.main()