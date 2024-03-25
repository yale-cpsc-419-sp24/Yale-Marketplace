from html import escape  # Escape HTML characters in the search fields to prevent XSS attacks
from flask import Flask, redirect, render_template, request, make_response, url_for, session  # The Flask web framework
import json  # Parse JSON data from the API
#import backend  # Send SQL queries to the database
import requests  # Send HTTP requests to the image URL
app = Flask(__name__)
app.secret_key = 'your_secret_key'
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
    print(session.get('username'))
    return render_template('index.html', items=dummy_items)


@app.route('/logout/')
def logout():
    print("logged_out")
    session.pop('username', None)
    return redirect(url_for('log_in'))

@app.route('/my_account/')
def my_account():
    return render_template('my_account.html', username=session.get('username'))

@app.route('/item/<item_id>/')
def item_details(item_id):
    return render_template('details.html', item=dummy_items[int(item_id)-1], item_id=item_id)

@app.route('/post/')
def add_item():
    return render_template('add_item.html')

@app.route('/submit_item/', methods=['GET', 'POST'])
def submit_item():
    name = request.form['name']
    description = request.form['description']
    asking_price = request.form['asking_price']
    image = request.files['image']
    negotiable = request.form['negotiable']
    category = request.form.getlist('category')
    nit={
        'name': name,
        'id': len(dummy_items),
        'description': description,
        'image_url': image,
        'contact_method': asking_price
    }
    return render_template('details.html', item=nit, item_id=len(dummy_items))
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
        password = request.form['password']
        #here we can store an id for a user. later we will replace this with cas login but still use usernames in the database
        print("in log in")
        session['username'] = username
        return redirect(url_for('listings', username=username))
    else:
        return render_template('log_in.html')

@app.route('/sign_up/', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #here we can store an id for a user. later we will replace this with cas login but still use usernames in the database
        session['username'] = username
        print("creating account with username: ", username)
        return redirect(url_for('listings', username=username))
    else:
        return render_template('sign_up.html')































