import os
import random
import hashlib
import requests
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_login import UserMixin

app = Flask(__name__)

SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/api/token'

auth_response = requests.post(SPOTIFY_AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
    'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
})

auth_response_data = auth_response.json()

SPOTIFY_ACCESS_TOKEN = auth_response_data['access_token']

SPOTIFY_API_GENRES_URL = 'https://api.spotify.com/v1/recommendations/available-genre-seeds'

cat = 'https://api.spotify.com/v1/browse/categories'

cat_playlists = 'https://api.spotify.com/v1/browse/categories/0JQ5DAqbMKFQ00XGBls6ym/playlists'

headers = {
    "Authorization": "Bearer " + SPOTIFY_ACCESS_TOKEN
}


res = requests.get(url=SPOTIFY_API_GENRES_URL, headers=headers)

res2 = requests.get(url=cat, headers=headers)

cats = res2.json()
#print(json.dumps(res.json(), indent=2))

res3 = requests.get(url=cat_playlists, headers=headers)

#print(json.dumps(cats['categories']['items'], indent=2))
#print(json.dumps(res.json(), indent=2))

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/genres', methods=['GET', 'POST'])
def genre_display():
    return render_template('genres.html')

@app.route('/genre_handler', methods=['GET', 'POST'])
def genre_handler():
    genre_list = request.form.getlist("genres")
    categorie_list = request.form.getlist("categories")
    print("Genre List - ", genre_list)
    print("Categorie List - ", categorie_list)
    return redirect(url_for('hello'))