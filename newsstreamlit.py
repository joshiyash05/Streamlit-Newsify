import streamlit as st
import requests
import sqlite3              #For SQL
import pyshorteners         #For short Urls python lib

# Function to generate a short URL
def shorten_url(url):
    shortener = pyshorteners.Shortener()
    short_url = shortener.tinyurl.short(url)
    return short_url


# Establish connection to an SQLite database
conn = sqlite3.connect('news_data.db')
cursor = conn.cursor()

# For NEWS fetching
API_KEY = '70aad84b320846ad98c6d2974b4145ee'

def get_news_articles(query):
    url = f'https://newsapi.org/v2/everything?q={query}&apiKey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    articles = data['articles']
    return articles


NEWS_API_ENDPOINT = 'https://newsapi.org/v2/top-headlines'

def get_news_categorywise(category,country):
    country = country.lower()
    params = {
        'country': country,
        'apiKey': API_KEY
    }
    if category:
        params['category'] = category
    response = requests.get(NEWS_API_ENDPOINT, params=params)
    data = response.json()
    print(data)
    article = data['articles']
    return article


# For Historical data Insertion 
def save_to_database(query, articles):
    cursor.execute("CREATE TABLE IF NOT EXISTS news (query TEXT, title TEXT, author TEXT, source TEXT, description TEXT, url TEXT)")
    for article in articles:
        title = article['title']
        author = article['author']
        source = article['source']['name']
        description = article['description']
        url = article['url']
        cursor.execute("INSERT INTO news (query, title, author, source, description, url) VALUES (?, ?, ?, ?, ?, ?)",
                       (query, title, author, source, description, url))
    conn.commit()

# For historical data Selection 
def fetch_historical_data():
    cursor.execute("SELECT query FROM news")
    return cursor.fetchall()

def fetch_historical_query(query):
    cursor.execute("SELECT * FROM news WHERE query = ?",(query,))
    return cursor.fetchall()

# Streamlit app
st.title(' 📰 Newsify')

# Custom CSS
css = """
    <style>
        body {
            background-color: #F5F5F5;
            color: #333333;
        }
        h1 {
            color: #008080;
        }
        button {
            background-color: #008080;
            color: white;
        }
    </style>
"""
st.markdown(css, unsafe_allow_html=True)


countries = ['US', 'GB', 'IN', 'CA', 'AU', 'FR', 'DE', 'JP', 'CN', 'RU', 'BR', 'MX', 'IT', 'ES', 'KR']# add more countries as needed
selected_country = st.sidebar.selectbox('Select a country', countries)

# Choose the category
categories = ['all', 'None' ,'Business', 'Entertainment', 'General', 'Health', 'Science', 'Sports', 'Technology']
selected_category = st.sidebar.selectbox('Select a category (optional)', categories)

if selected_category == 'None':
    selected_category = 0

# User input
st.sidebar.write("OR")
query = st.sidebar.text_input('Enter your search query')

# Search button

if st.sidebar.button('🔍 Search'):
    if query:
        articles = get_news_articles(query)
        save_to_database(query, articles)
        for article in articles:
            st.write('---')
            st.write('Title:', article['title'])
            st.write('Author:', article['author'])
            st.write('Source:', article['source']['name'])
            st.write('Description:', article['description'])
            st.write('Read more:', shorten_url(article['url']))


if selected_category:
    articles = get_news_categorywise(selected_category,selected_country)
    
    for article in articles:
      st.write('---')
      st.write('Title:', article['title'])
      st.write('Author:', article['author'])
      st.write('Source:', article['source']['name'])
      st.write('Description:', article['description'])
      st.write('Read more:', shorten_url(article['url']))

# Historical data
st.sidebar.write('---')
st.sidebar.write('Previously searched queries:')
list_ofquery = list(set(fetch_historical_data()))

selected_query = st.sidebar.selectbox('Select a query', list_ofquery)


if st.sidebar.button('Fetch Historical Data'):
    if selected_query:
        data = fetch_historical_query(selected_query[0])
        if data:
            for row in data:
                st.write('---')
                st.write('Query:', row[0])
                st.write('Title:', row[1])
                st.write('Author:', row[2])
                st.write('Source:', row[3])
                st.write('Description:', row[4])
                st.write('URL:', row[5])


