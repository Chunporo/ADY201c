import json
import plotly
import pandas as pd
import pickle
import os
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag
from sklearn.base import BaseEstimator, TransformerMixin
from flask import Flask, render_template, request, jsonify
from plotly.graph_objs import Bar
from sqlalchemy import create_engine
import sqlite3

app = Flask(__name__)
    
class StartingVerbExtractor(BaseEstimator, TransformerMixin):
    def starting_verb(self, text):
        sentence_list = nltk.sent_tokenize(text)
        for sentence in sentence_list:
            pos_tags = nltk.pos_tag(word_tokenize(sentence))
            first_word, first_tag = pos_tags[0]
            if first_tag in ['VB', 'VBP'] or first_word == 'RT':
                return True
        return False

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_tagged = pd.Series(X).apply(self.starting_verb)
        return pd.DataFrame(X_tagged)

def tokenize(text):
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    clean_tokens = [lemmatizer.lemmatize(tok).lower().strip() for tok in tokens]
    return clean_tokens

# Load data
dbfile = 'data/disaster_response_db.db'
conn = sqlite3.connect(dbfile)
df = pd.read_sql_query("SELECT * FROM disaster_response_db_table", conn)

# Load model
model = pickle.load(open(os.getcwd() + '/models/classifier.pkl', 'rb'))

@app.route('/')
@app.route('/index')
def index():
    genre_counts = df.groupby('genre').count()['message']
    genre_names = list(genre_counts.index)
    
    category_names = df.iloc[:, 4:].columns
    category_boolean = (df.iloc[:, 4:] != 0).sum().values
    
    genre_colors = ['#ff9999','#66b3ff','#99ff99']  # Add more colors if there are more genres
    category_colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#ffb3e6',
                       '#c2f0c2','#f0e68c','#d2b48c','#87ceeb','#ff6347','#4682b4',
                       '#dda0dd','#8b0000','#2e8b57','#ff7f50','#f5deb3','#ff4500',
                       '#daa520','#b8860b','#8b4513','#7fffd4','#d2691e','#9acd32',
                       '#ff1493','#1e90ff','#ff00ff','#8b008b','#00fa9a','#4b0082',
                       '#ffdab9','#696969','#00ced1','#afeeee']  # Extend this list to cover all categories

    graphs = [
        {
            'data': [Bar(
                x=genre_names, 
                y=genre_counts,
                marker=dict(color=genre_colors)
            )],
            'layout': {
                'title': 'Distribution of Message Genres',
                'yaxis': {'title': "Count"},
                'xaxis': {'title': "Genre"},
                'plot_bgcolor': 'rgba(245, 246, 249, 1)',
                'paper_bgcolor': 'rgba(245, 246, 249, 1)',
                'font': {'family': 'Arial, sans-serif', 'size': 14}
            }
        },
        {
            'data': [Bar(
                x=category_names, 
                y=category_boolean,
                marker=dict(color=category_colors[:len(category_names)])  # Use as many colors as there are categories
            )],
            'layout': {
                'title': 'Distribution of Message Categories',
                'yaxis': {'title': "Count"},
                'xaxis': {'title': "Category", 'tickangle': -45},
                'plot_bgcolor': 'rgba(245, 246, 249, 1)',
                'paper_bgcolor': 'rgba(245, 246, 249, 1)',
                'font': {'family': 'Arial, sans-serif', 'size': 14}
            }
        }
    ]
    
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('master.html', ids=ids, graphJSON=graphJSON)

@app.route('/go')
def go():
    query = request.args.get('query', '') 
    classification_labels = model.predict([query])[0]
    classification_results = dict(zip(df.columns[4:], classification_labels))
    
    return render_template('go.html', query=query, classification_result=classification_results)

def main():
    app.run(host='0.0.0.0', port=3001, debug=True)

if __name__ == '__main__':
    main()
                     