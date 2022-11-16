import os
import random
import hashlib
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_login import UserMixin

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')