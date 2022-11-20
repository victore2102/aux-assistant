'''Aux Assistant - Victor Ekpenyong & Jacob Gaudet'''
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

#'''.env initialization'''
load_dotenv(find_dotenv())

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')

# API URL'S
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_CATEGORIES_URL = 'https://api.spotify.com/v1/browse/categories'
SPOTIFY_RECOMMENDATIONS_URL = 'https://api.spotify.com/v1/recommendations'

## Authorization request & response & header assignment
auth_response = requests.post(SPOTIFY_AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
    'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
}, timeout=10)
auth_response_data = auth_response.json()
SPOTIFY_ACCESS_TOKEN = auth_response_data['access_token']
headers = {
    "Authorization": "Bearer " + SPOTIFY_ACCESS_TOKEN
}

selected_genres = list()

# Helper Function(s)
def categories_playlists_tracks(categorie):
    '''Function requests playlists based on categorie and returns a list of lists of random tracks within random playlist'''
    categorie_playlist_url = f'https://api.spotify.com/v1/browse/categories/{categorie}/playlists'
    categorie_playlists = requests.get(url=categorie_playlist_url, headers=headers, timeout=10).json()
    i = 0
    categorie_playlists_tracks_list = list()
    while i < 3:
        track_info_list = list()
        rand_playlist = random.randint(0,19)
        playlist_name = categorie_playlists['playlists']['items'][rand_playlist]['name']
        track_info_list.append(playlist_name)
        playlist_url = categorie_playlists['playlists']['items'][rand_playlist]['id']
        playlist_tracks_url = f'https://api.spotify.com/v1/playlists/{playlist_url}/tracks'
        playlist_tracks = requests.get(url=playlist_tracks_url, headers=headers, timeout=10).json()
        rand_song = random.randint(0,19)
        song_name = playlist_tracks['items'][rand_song]['track']['name']
        track_info_list.append(song_name)
        song_id = playlist_tracks['items'][rand_song]['track']['id']
        track_info_list.append(song_id)
        artist_name = playlist_tracks['items'][rand_song]['track']['artists'][0]['name']
        track_info_list.append(artist_name)
        artist_id = playlist_tracks['items'][rand_song]['track']['artists'][0]['id']
        track_info_list.append(artist_id)
        song_image_url = playlist_tracks['items'][rand_song]['track']['album']['images'][1]['url']
        track_info_list.append(song_image_url)
        categorie_playlists_tracks_list.append(track_info_list)
        i += 1
    return categorie_playlists_tracks_list
    # returns -> [ [playlist_name, song_name, song_id, artist_name, artist_id, song_image_url] ]
    # 3 inner lists are within outer list


@app.route('/')
def hello():
    '''Home Page Display'''
    return render_template('index.html')

@app.route('/genres', methods=['GET', 'POST'])
def genre_display():
    '''Genres Selection Page Display'''
    return render_template('genres.html')

@app.route('/seed_tracks', methods=['GET', 'POST'])
def seed_tracks_display():
    '''Genre Handler & Seed Tracks Display'''
    print("valid - ", request.form.get("valid"))
    if(request.form.get("valid") == "false"):
        flash('Select at least one genre to continue')
        return redirect(url_for('genre_display'))
    genre_list = request.form.getlist("genres")
    global selected_genres
    selected_genres = genre_list
    categorie_list = request.form.getlist("categories")
    print("Genres - ", genre_list)
    print("Categorie IDs - ", categorie_list)
    seed_track_and_artist_list = list()
    for categorie in categorie_list:
        seed_track_and_artist_list.append(categories_playlists_tracks(categorie))
    return render_template('seed_tracks.html', seedTracks=seed_track_and_artist_list)

@app.route('/selection', methods=['GET', 'POST'])
def final_selection():
    '''Seed Track & Seed Artist Handler and User Selection Dispaly'''
    seed_tracks = request.form.getlist('seed_tracks')
    seed_artists = request.form.getlist('seed_artists')
    print("Seed Tracks IDs - ", seed_tracks)
    print("Seed Artists IDs - ", seed_artists)
    return render_template('final_selection.html', genres=len(selected_genres), tracks=len(seed_tracks), artists=len(seed_artists))

@app.route('/generate', methods=['GET', 'POST'])
def generate_playlist():
    '''Playlist Creation Display (work in progress)'''
    genre_num = request.form.get('genre_num')
    track_num = request.form.get('track_num')
    artist_num = request.form.get('artist_num')
    print("Number of Genres to Include - ", genre_num)
    print("Number of Tracks to Include - ", track_num)
    print("Number of Artists to Include - ", artist_num)

    #recommended_songs = requests.get(
    #    url=SPOTIFY_RECOMMENDATIONS_URL,
     #   headers=headers,
      #  params={
       #     'seed_genres': f'{selected_genres[0]},{selected_genres[1]},{selected_genres[2]},{selected_genres[3]},{selected_genres[4]}',
        #    'seed_tracks': '',
         #   'seed_artists': ''
      #  },
       # timeout=10).json()
    #print(json.dumps(recommended_songs, indent=2))
    return redirect(url_for('hello'))
