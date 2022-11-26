### aux-assistant
# Spotify Aux Assistant
### Created By : Victor Ekpenyong, Jacob Gaudet
## Deployed Site - https://aux-assistant.fly.dev/
## [Group Propasal Doc](https://docs.google.com/document/d/1hJv1MvUgkZs_L3tX0NVIcCq2RzdMOK0tk118iaEE9-Q/edit#heading=h.2e49ugtutnjr)
## Overview
* This application is designed to assist people in playlist creation using Spotify's API. Logged in users will be able to create a playlist and save it for future referance. We are hoping to assist in any hassle when it comes to finding new music one might be interested in, or knowing what to play when passed the aux!
* This project utilizes python flask framework on the backend for the server side of the technology stack. Libraries utilized within this project include:
    * os, dotenv.load_dotenv, and dotenv.find_dotenv used for retrieval of secret variables within .env file. 
    * Python's random library is used in order to assist in seed tracks display. 
    * The requests library is used in coordination with requesting data through API calls.
    * Flask.Flask, flask.render_template, flask.request, flask.redirect, flask.url_for, flask.flash are used for multiple app functionalities including rendering pages, redirecting and error handling.
    * Fly postgresql database used for user sign up and playlist saving
    * Finally, flask login used for user sessions
## API Calls
1. Authorization 
    * Post request which sends spotify client id and client secret code in order to gain authorization to make subsequent API calls.
2. Categorie Playlists
    * Get request which returns a list of playlists pertaining to a passed in categorie (i.e pop, r&b, dance)
3. Playlist Items
    * Based on the selected categorie playlist, this Get request is made to return the tracks within the categorie playlist
4. Recommended Tracks
    * Get request which takes in multiple parameters including genres, seed tracks, seed artists, and more which then returns a list of 20 recommended tracks using Spotify's algorithm
## Initial Set Up
1. Make Sure that you have a functioning Spotify Client ID & Client Secret
    * [Click Here for more information](https://developer.spotify.com/documentation/general/guides/authorization/app-settings/)
    * Store both within .env file as SPOTIFY_CLIENT_ID & SPOTIFY_CLIENT_SECRET
2. Create an app_secret_key
    * Make your own app_secret_key and store it within your .env file set to the variable name 'APP_SECRET_KEY'
3. For local development, have a postgresql database established and add url to .env file saved as DATABASE_URL
## How To Run
1. Ensure you have python or python3 installed
2. Ensure you have flask installed, if not [Install Flask Here](https://flask.palletsprojects.com/en/1.1.x/installation/#virtual-environments)
3. There are multiple ways to run within the terminal, choose one you're most comfortable with
    * FLASK_APP=aux_assistant flask run
    * python3 aux_assistant.py or python aux_assistant.py
## Technical Requirements
* Flask server
* REST API Integration
* User login
* Postgres database
* Beautification
## Reviewed Pull Requests
### Victor Ekpenyong
1. [Title page & Genre Selection Page](https://github.com/victore2102/aux-assistant/pull/1)
2. [Seed tracks Display & Code Cleanup](https://github.com/victore2102/aux-assistant/pull/2)
3. [Recommended Playlist Generation & Misc Functionalites](https://github.com/victore2102/aux-assistant/pull/3)
### Jacob Gaudet
1.
2.
## Follow Up Questions
### Victor Ekpenyong
#### "What is an example of something you enjoyed about or learned from this project?"
* I enjoyed the freedom we had for this project because it allowed me to show creativity and try to make the best product not only to meet requirements, but also to flex my muscles as a software engineer.
#### "What is an example of something you didn’t enjoy or wanted to learn from this project?"
* I wish that we had more time. I wouldn't say I felt rushed, but I wish that more time was present for me to implement the grander scope of the project which I envisioned.
### Jacob Gaudet
#### "What is an example of something you enjoyed about or learned from this project?"
*
#### "What is an example of something you didn’t enjoy or wanted to learn from this project?"
*

### Thank You for reading, happy coding!
