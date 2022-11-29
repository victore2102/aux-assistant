'''Aux Assistant - Victor Ekpenyong & Jacob Gaudet'''
import os
import random
import hashlib
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_login import UserMixin

#'''.env initialization'''
load_dotenv(find_dotenv())

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')
# Used for security regarding passwords
app.config['SECRET_KEY'] = app.secret_key
# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)  # initializing database using flask "app"

# DATABASE MODELS

# Defining the user table for storing User profile info in database
class User(UserMixin, db.Model):
    '''User Model'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)
    def __repr__(self)->str:
        return f"Username: {self.username}"
# Used to return all names of playlists associated with user
class PlaylistNames(db.Model):
    '''PlaylistNames Model'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=False, nullable=False)
    playlist_name = db.Column(db.String(100), unique=True, nullable=False)
    playlist_date = db.Column(db.String(100), unique=False, nullable=False)
    def __repr__(self) -> str:
        return f"{self.playlist_name}-&-{self.playlist_date}--END--"

# build the table
with app.app_context():
    db.create_all()

# Login manager setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    '''Load user from User model in db'''
    return User.query.get(int(user_id))

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

# Global variables used in multiple different functions
SELECTED_GENRES = list()
SELECTED_CATEGORIES = list()
AUX_ASSISTANT_PLAYLIST = list()


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
    recommended_songs_info_list(recommended_songs)

# Function takes JSON data of recommended songs and populates it into a global list of lists which will be used through jinja and for database
# For saved playlists in database I think schema should include
# username, playlist name, song uri, song name, song id, artist name, artist id, and song image url
def recommended_songs_info_list(recommended_songs):
    '''Function parses recommended songs JSON into list of lists of important info'''
    # Global list variable is cleared to allow new playlist data to be stored in it
    global AUX_ASSISTANT_PLAYLIST
    AUX_ASSISTANT_PLAYLIST.clear()
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
        AUX_ASSISTANT_PLAYLIST.append(track_info_list)
        i+=1
    # AUX_ASSISTANT_PLAYLIST global list in form of
    # [ [song_uri, song_name, song_id, artist_name, artist_id, song_image_url] ]
    # 20 inner lists within outer list

# 1. Function queries the PlaylistNames model by username into a string
# 2. It takes that returned string and filters it and splits it into multiple lists
# 3. Each list is split into a sub list then returned as a list of lists
# 4. saved_playlists returns [ [playlist_name, date], [playlist_name, date], ... ]
def saved_playlists_list():
    '''Function which assists in returning the names of saved playlists a user has'''
    saved_playlists = []
    saved_playlists_names = str(PlaylistNames.query.filter_by(username=str(current_user.username)).all())
    filtered_names = saved_playlists_names.lstrip("[")
    filtered_names = filtered_names.rstrip("--END--]")
    saved_playlists_names_split = list(filtered_names.split("--END--, "))
    for p in saved_playlists_names_split:
        p_split = list(p.split("-&-"))
        saved_playlists.append(p_split)
    return saved_playlists

# Similar process as function above
# 4. specific_playlists returns [ [song_name, artist_name, song_image_url], [song_name, artist_name, song_image_url], ... ]
def specific_playlist_list(name):
    '''Function which assists in returning the list data of a specific playlist'''
    specific_playlist = []
    all_songs = str(SavedPlaylists.query.filter_by(username=str(current_user.username), playlist_name=name).all())
    filtered_songs = all_songs.lstrip("[")
    filtered_songs = filtered_songs.rstrip("--END--]")
    all_songs_split = list(filtered_songs.split("--END--, "))
    for s in all_songs_split:
        s_split = list(s.split("-&-"))
        specific_playlist.append(s_split)
    return specific_playlist



@app.route('/')
def hello():
    '''Home Page Display'''
    if current_user.is_authenticated:
        user = str(current_user.username)
    else:
        user = None
    return render_template('index.html', user=user)

@app.route('/about')
def about_page():
    '''About Page Display'''
    return render_template('about.html')

# Login, Signup, Logout Routes & Validation Functions
@app.route('/login')
def login_page():
    '''Renders login page'''
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    '''Renders signup page'''
    return render_template('signup.html')

@app.route('/validateSignup', methods=['GET', 'POST'])
def validate_signup():
    '''Validates signup'''
    username = str(request.form.get("UserName"))
    password = str(request.form.get("PassWord")) + os.getenv("SALT")
    hashed_password = hashlib.md5(password.encode())
    user = User.query.filter_by(username=username).first()
    if user:
        flash('Username already in use, try again or click below to Login')
        return redirect(url_for('signup_page'))
    new_user = User(username=username, password=str(hashed_password.hexdigest()))
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login_page'))

@app.route('/validateLogin', methods=['GET', 'POST'])
def validate_login():
    '''Validates login'''
    username = str(request.form.get("UserName"))
    password = str(request.form.get("PassWord")) + os.getenv("SALT")
    hashed_password = hashlib.md5(password.encode())
    user = User.query.filter_by(username=username, password=str(hashed_password.hexdigest())).first()
    if user:
        login_user(user)
        return redirect(url_for('hello'))
    flash('Username and/or Password invalid, try again or click below to Sign Up')
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    '''User logout'''
    logout_user()
    return redirect(url_for('hello'))

# Login Required for all routes below

@app.route('/genres')
@login_required
def genre_display():
    '''Genres Selection Page Display'''
    return render_template('genres.html')

@app.route('/seed_tracks', methods=['GET', 'POST'])
@login_required
def seed_tracks_display():
    '''Genre Handler & Seed Tracks Display'''
    if(request.form.get("valid") == "false"):
        flash('Select at least one genre to continue')
        return redirect(url_for('genre_display'))
    genre_list = request.form.getlist("genres")
    global SELECTED_GENRES
    SELECTED_GENRES = genre_list
    categorie_list = request.form.getlist("categories")
    global SELECTED_CATEGORIES
    SELECTED_CATEGORIES = categorie_list
    seed_track_and_artist_list = list()
    for categorie in SELECTED_CATEGORIES:
        seed_track_and_artist_list.append(categories_playlists_tracks(categorie))
        # seed_track_and_artist_list will be in format [ [ [],[],[] ], [ [],[],[] ], [ [],[],[] ]...]
    return render_template('seed_tracks.html', seedTracks=seed_track_and_artist_list)

@app.route('/re_shuffle', methods=['GET', 'POST'])
@login_required
def re_shuffle_tracks():
    '''Handles the re-shuffling of tracks on seed track page'''
    global SELECTED_CATEGORIES
    seed_track_and_artist_list = list()
    for categorie in SELECTED_CATEGORIES:
        seed_track_and_artist_list.append(categories_playlists_tracks(categorie))
    return render_template('seed_tracks.html', seedTracks=seed_track_and_artist_list)

@app.route('/selection', methods=['GET', 'POST'])
@login_required
def final_selection():
    '''Prompts the user to make their final selection of up to 5 entries'''
    seed_track_ids = []
    seed_artist_ids = []
    seed_track_names = []
    seed_artist_names = []
    if(request.form.getlist('seed_track_ids') is not None):
        seed_track_ids = request.form.getlist('seed_track_ids')
        seed_artist_ids = request.form.getlist('seed_artist_ids')
        seed_track_names = request.form.getlist('seed_track_names')
        seed_artist_names = request.form.getlist('seed_artist_names')
    if(len(SELECTED_GENRES) + len(seed_track_names) + len(seed_artist_names) > 5):
        return render_template('final_selection.html', genres=SELECTED_GENRES, track_names=seed_track_names, artist_names=seed_artist_names,
        track_ids=seed_track_ids, artist_ids=seed_artist_ids, genres_size=len(SELECTED_GENRES),
        tracks_size=len(seed_track_names), artists_size=len(seed_artist_names))
    generate_playlist_api(SELECTED_GENRES, seed_track_ids, seed_artist_ids)
    return redirect(url_for('view_songs'))

@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate_playlist():
    '''Handles form data from final selections and calls function for recommended tracks'''
    final_genres = request.form.getlist('final_genres')
    final_track_ids = request.form.getlist('final_track_ids')
    final_artist_ids = request.form.getlist('final_artist_ids')
    generate_playlist_api(final_genres, final_track_ids, final_artist_ids)
    return redirect(url_for('view_songs'))

@app.route('/playlist_view', methods=['GET', 'POST'])
@login_required
def view_songs():
    '''Displays recommended tracks'''
    return render_template('view_playlist.html', playlist=AUX_ASSISTANT_PLAYLIST)

@app.route('/save')
@login_required
def save_playlist():
    '''View Save Playlist Page'''
    return render_template('save_playlist.html')

@app.route('/save_handler', methods=['GET', 'POST'])
@login_required
def save_playlist_handler():
    '''Handler for saving playlist'''
    playlist_name = request.form.get('playlist_name')
    date = request.form.get('date')
    playlist = PlaylistNames.query.filter_by(username=str(current_user.username), playlist_name=playlist_name).first()
    if playlist:
        flash('Playlist Name already exists')
        return redirect(url_for('save_playlist'))
    new_playlist_name = PlaylistNames(username=str(current_user.username), playlist_name=playlist_name, playlist_date=date)
    db.session.add(new_playlist_name)
    db.session.commit()
    for p in AUX_ASSISTANT_PLAYLIST:
        new_playlist = SavedPlaylist(username=str(current_user.username), playlist_name=playlist_name, date=date, song_uri=p[0],
        song_name=p[1], song_id=p[2], artist_name=p[3], artist_id=p[4], song_image_url=p[5])
        db.session.add(new_playlist)
        db.session.commit()
    return redirect(url_for('hello'))

@app.route('/view_saved')
@login_required
def view_saved_playlists():
    '''Renders page display of saved playlists'''
    saved = saved_playlists_list()
    return render_template('view_saved_playlists.html', saved_playlists=saved, size=len(saved))

@app.route('/view_specific', methods=['GET', 'POST'])
@login_required
def view_specific_saved_playlists():
    '''Renders page which displays specific saved playlist'''
    playlist_name = request.form.get('p')
    specific = specific_playlist_list(playlist_name)
    return render_template('view_specific.html', playlist=specific, name=playlist_name)
