from html import escape  # Escape HTML characters in the search fields to prevent XSS attacks
from flask import Flask, redirect, render_template, request, make_response, url_for, session  # The Flask web framework
from flask import g  # Store the database connection
import sqlite3  # Connect to the SQLite database
import os
import json  # Parse JSON data from the API
#import backend  # Send SQL queries to the database
import requests  # Send HTTP requests to the image URL


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['DATABASE'] = 'marketplace.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row 
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


dummy_items = [
    {
        'name': 'Item 1',
        'id': '1',
        'description': 'This is the description of item 1. Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
        'image_url': 'https://example.com/item1.jpg',
        'contact_method': 'Email: example@example.com'
    },
    {
        'name': 'Item 2',
        'id': '2',
        'description': 'Description of item 2. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
        'image_url': 'https://example.com/item2.jpg',
        'contact_method': 'Phone: 123-456-7890'
    },
    {
        'name': 'Item 3',
        'id': '3',
        'description': 'Description of item 2. Sed do eiusmod tempor incididunt ut labore et doloreDescription of item 2. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Description of item 2. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Description of item 2. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Description of item 2. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Description of item 2. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Description of item 2. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Description of item 2. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Description of item 2. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Description of item 2. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Description of item 2. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. magna aliqua.',
        'image_url': 'https://example.com/item2.jpg',
        'contact_method': 'Phone: 123-456-7890'
    },

    # Add more items as needed
]

@app.route('/')
def root():
    return redirect(url_for('log_in'))

@app.route('/index/')
def listings():
    db = get_db()
    items = db.execute('SELECT * FROM item').fetchall()
    #print(session.get('username'))
    return render_template('index.html', items=items)


@app.route('/logout/')
def logout():
    print("logged_out")
    session.pop('username', None)
    return redirect(url_for('log_in'))

@app.route('/my_account/')
def my_account():
    return render_template('my_account.html', username=session.get('username'))

@app.route('/item/<int:item_id>/')
def item_details(item_id):
    db = get_db()
    item = db.execute('SELECT * FROM item WHERE item_id = ?', (item_id,)).fetchone()

    if item:
        for row in item:
            print(row)
        return render_template('details.html', item=item, item_id=item_id)
    else:
        return "Item not found", 404

@app.route('/post/')
def add_item():
    return render_template('add_item.html')


@app.route('/submit_item/', methods=['GET', 'POST'])
def submit_item():
    if request.method == 'POST':
        # Ensure a user is logged in
        if 'user_id' not in session:
            return redirect(url_for('log_in'))

        # Retrieve form data
        name = request.form['name']
        description = request.form['description']
        image = request.files['image']
        asking_price = request.form['asking_price']
        negotiable = request.form.get('negotiable', '0')  # Default to '0' if not provided
        category = request.form['category']
        user_id = session['user_id']
        
        from datetime import datetime

        time = datetime.now()
        filename = f"{user_id}_{str(time)}.{image.filename.split('.')[-1]}"
        image.save(os.path.join(app.root_path, 'static', 'uploads', filename))
        db = get_db()
        db.execute('INSERT INTO item (user_account_id, name, description, asking_price, negotiable, category_id, image_path) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (user_id, name, description, asking_price, negotiable, category, filename))
        db.commit()

        return redirect(url_for('listings'))
    else:
        return render_template('add_item.html')

@app.route('/submit_item_bid/', methods=['GET', 'POST'])
def submit_item_bid():
    if(request.method=='POST'):
        offer_price = request.form['offer_price']
        comments = request.form['comments']
        nit={
            'offer_price': offer_price,
            'comments': comments
        }
        print(offer_price, comments)
        return redirect(url_for('listings'))
    return render_template('request_transaction.html')


@app.route('/log_in/', methods=['GET', 'POST'])
def log_in():
    if request.method == 'POST':
        username = request.form['username']

        db = get_db()
        cursor = db.execute('SELECT user_account_id, name FROM user WHERE name = ?', (username,))
        user = cursor.fetchone()

        if user:
            # User found, proceed with login
            session['username'] = username
            session['user_id'] = user['user_account_id']  # Store the user's ID in the session
            return redirect(url_for('listings'))
        else:
            # No user found with the given username
            return render_template('log_in.html', error="Account not found. Please sign up.")
    else:
        return render_template('log_in.html')

    
@app.route('/sign_up/', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        
        db = get_db()
        try:
            # Inserting the new user into the database
            cursor = db.execute('INSERT INTO user (name, email_address) VALUES (?, ?)', (username, username + "@example.com"))
            db.commit()
            
            # Fetch the user_account_id of the newly created user
            user_account_id = cursor.lastrowid
            
            # Store both username and user_account_id in the session
            session['username'] = username
            session['user_id'] = user_account_id  # Store the user's ID in the session
            
            print("Account created for username: ", username, "with user ID: ", user_account_id)
            return redirect(url_for('listings'))
        except sqlite3.IntegrityError as e:
            print("Error occurred: ", e)
            # This error occurs if the username is not unique
            return render_template('sign_up.html', error="An account with this username already exists. Please choose another username.")
    else:
        return render_template('sign_up.html')
