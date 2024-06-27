import unittest
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from chat import (
    update_numeric_columns
)
import plotly.io as pio

class TestTwitterAnalysis(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            'username': ['user1', 'user2', 'user3', 'user4', 'user5'],
            'tweet': [
                'This is tweet one #fun #python',
                'This is tweet two #fun',
                'This is tweet three #python',
                'This is tweet four #fun #coding',
                'This is tweet five #coding'
            ],
            'like': ['100', '200', '150', '300', '50'],
            'retweet': ['10', '20', '15', '30', '5'],
            'reply': ['5', '10', '7', '12', '3'],
            'views': ['1 k', '2 k', '1.5 k', '3 k', '500']
        })
        self.df = update_numeric_columns(self.df)

    def test_valid_values(self):
        df = pd.DataFrame({
            'like': ['1 k', '2 k', '1.5 k'],
            'retweet': ['10', '20', '15'],
            'reply': ['5', '10', '7'],
            'views': ['1 k', '2 k', '1.5 k']
        })
        updated_df = update_numeric_columns(df)
        self.assertTrue('like_numeric' in updated_df.columns)
        self.assertTrue('retweet_numeric' in updated_df.columns)
        self.assertTrue('reply_numeric' in updated_df.columns)
        self.assertTrue('views_numeric' in updated_df.columns)

    def test_empty_values(self):
        df = pd.DataFrame({
            'like': [''],
            'retweet': [''],
            'reply': [''],
            'views': ['']
        })
        updated_df = update_numeric_columns(df)
        self.assertTrue('like_numeric' in updated_df.columns)
        self.assertTrue('retweet_numeric' in updated_df.columns)
        self.assertTrue('reply_numeric' in updated_df.columns)
        self.assertTrue('views_numeric' in updated_df.columns)
        self.assertEqual(updated_df['like_numeric'].iloc[0], 0)
        self.assertEqual(updated_df['retweet_numeric'].iloc[0], 0)
        self.assertEqual(updated_df['reply_numeric'].iloc[0], 0)
        self.assertEqual(updated_df['views_numeric'].iloc[0], 0)
if __name__ == '__main__':
    unittest.main()
