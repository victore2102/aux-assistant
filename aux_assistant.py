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
aux_assistant_playlist = list()

# Helper Function(s)
# 1. Function makes API call to get a playlist based on passed in categorie
# 2. Random categorie playlist is chosen from response and API call is made to get items of playlist
# 3. Random track is chosen from random playlist, and track information is stored in a list of lists
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

# Function makes API call for Spotify Recommended Tracks
def generate_playlist_api(final_genres, final_track_ids, final_artist_ids):
    '''Function makes API call for recommended songs and calls function to populate into list of lists'''
    seed_genres = ','.join(final_genres)
    seed_tracks = ','.join(final_track_ids)
    seed_artists = ','.join(final_artist_ids)
    recommended_songs = requests.get(
        url=SPOTIFY_RECOMMENDATIONS_URL,
        headers=headers,
        params={
            'seed_genres': seed_genres,
            'seed_tracks': seed_tracks,
            'seed_artists': seed_artists
        },
        timeout=10).json()
    #print(json.dumps(recommended_songs, indent=2))
    recommended_songs_info_list(recommended_songs)

# Function takes JSON data of recommended songs and populates it into a global list of lists which will be used through jinja and for database
# For saved playlists in database I think schema should include
# username, playlist name, song uri, song name, song id, artist name, artist id, and song image url
def recommended_songs_info_list(recommended_songs):
    '''Function parses recommended songs JSON into list of lists of important info'''
    global aux_assistant_playlist
    aux_assistant_playlist.clear()
    i = 0
    while i < 20:
        track_info_list = list()
        song_uri = recommended_songs['tracks'][i]['uri']
        track_info_list.append(song_uri)
        song_name = recommended_songs['tracks'][i]['name']
        track_info_list.append(song_name)
        song_id = recommended_songs['tracks'][i]['id']
        track_info_list.append(song_id)
        artist_name = recommended_songs['tracks'][i]['artists'][0]['name']
        track_info_list.append(artist_name)
        artist_id = recommended_songs['tracks'][i]['artists'][0]['id']
        track_info_list.append(artist_id)
        song_image_url = recommended_songs['tracks'][i]['album']['images'][1]['url']
        track_info_list.append(song_image_url)
        aux_assistant_playlist.append(track_info_list)
        i+=1
    # aux_assistant_playlist global list in form of
    # [ [song_uri, song_name, song_id, artist_name, artist_id, song_image_url] ]
    # 20 inner lists within outer list

@app.route('/')
def hello():
    '''Home Page Display'''
    return render_template('index.html')

# When made add login required decorator
@app.route('/genres')
def genre_display():
    '''Genres Selection Page Display'''
    return render_template('genres.html')

# When made add login required decorator
@app.route('/seed_tracks', methods=['GET', 'POST'])
def seed_tracks_display():
    '''Genre Handler & Seed Tracks Display'''
    if(request.form.get("valid") == "false"):
        flash('Select at least one genre to continue')
        return redirect(url_for('genre_display'))
    genre_list = request.form.getlist("genres")
    global selected_genres
    selected_genres = genre_list
    categorie_list = request.form.getlist("categories")
    seed_track_and_artist_list = list()
    for categorie in categorie_list:
        seed_track_and_artist_list.append(categories_playlists_tracks(categorie))
        # seed_track_and_artist_list will be in format [ [ [],[],[] ], [ [],[],[] ], [ [],[],[] ]...]
    return render_template('seed_tracks.html', seedTracks=seed_track_and_artist_list)

# When made add login required decorator
@app.route('/selection', methods=['GET', 'POST'])
def final_selection():
    '''Prompts the user to make their final selection of up to 5 entries'''
    seed_track_ids = []
    seed_artist_ids = []
    seed_track_names = []
    seed_artist_names = []
    if(request.form.getlist('seed_track_ids') != None):
        seed_track_ids = request.form.getlist('seed_track_ids')
        seed_artist_ids = request.form.getlist('seed_artist_ids')
        seed_track_names = request.form.getlist('seed_track_names')
        seed_artist_names = request.form.getlist('seed_artist_names')
    if(len(selected_genres) + len(seed_track_names) + len(seed_artist_names) > 5):
        return render_template('final_selection.html', genres=selected_genres, track_names=seed_track_names, artist_names=seed_artist_names,
        track_ids=seed_track_ids, artist_ids=seed_artist_ids, genres_size=len(selected_genres), 
        tracks_size=len(seed_track_names), artists_size=len(seed_artist_names))
    generate_playlist_api(selected_genres, seed_track_ids, seed_artist_ids)
    return redirect(url_for('view_songs'))

# When made add login required decorator
@app.route('/generate', methods=['GET', 'POST'])
def generate_playlist():
    '''Handles form data from final selections and calls function for recommended tracks'''
    final_genres = request.form.getlist('final_genres')
    final_track_ids = request.form.getlist('final_track_ids')
    final_artist_ids = request.form.getlist('final_artist_ids')
    generate_playlist_api(final_genres, final_track_ids, final_artist_ids)
    return redirect(url_for('view_songs'))

# When made add login required decorator
@app.route('/playlist_view', methods=['GET', 'POST'])
def view_songs():
    '''Displays recommended tracks'''
    return render_template('view_playlist.html', playlist=aux_assistant_playlist)

@app.route('/about')
def about_page():
    '''Genres Selection Page Display'''
    return render_template('about.html')
