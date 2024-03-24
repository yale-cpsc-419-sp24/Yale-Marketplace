from html import escape  # Escape HTML characters in the search fields to prevent XSS attacks
from flask import Flask, render_template, request, make_response  # The Flask web framework
import json  # Parse JSON data from the API
#import backend  # Send SQL queries to the database
import requests  # Send HTTP requests to the image URL

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
