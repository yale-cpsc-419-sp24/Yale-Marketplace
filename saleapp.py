from html import escape  # Escape HTML characters in the search fields to prevent XSS attacks
from flask import Flask, redirect, render_template, request, make_response, url_for, session, jsonify  # The Flask web framework
from flask import g  # Store the database connection
import sqlite3  # Connect to the SQLite database
import os
import json  # Parse JSON data from the API
#import backend  # Send SQL queries to the database
import requests  # Send HTTP requests to the image URL
from cas import CASClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['DATABASE'] = 'marketplace.db'
cas_client = CASClient(
    version=3,
    service_url='http://localhost:3000/login?next=%2Findex',
    server_url='https://secure.its.yale.edu/cas/'
)

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
    return redirect(url_for('login'))

# @app.route('/index/')
# def listings():
#     search_query = request.args.get('search', '')
#     category_filter = request.args.get('category', None)
#     db = get_db()

#     if search_query and category_filter:
#         items = db.execute('SELECT * FROM item WHERE name LIKE ? AND category_id = ?', (f'%{search_query}%', category_filter)).fetchall()
#     elif search_query:
#         items = db.execute('SELECT * FROM item WHERE name LIKE ?', (f'%{search_query}%',)).fetchall()
#     elif category_filter:
#         items = db.execute('SELECT * FROM item WHERE category_id = ?', (category_filter,)).fetchall()
#     else:
#         items = db.execute('SELECT * FROM item').fetchall()

#     categories = db.execute('SELECT DISTINCT category_id FROM item').fetchall()

#     return render_template('index.html', items=items, search_query=search_query, categories=categories, current_category=category_filter)

@app.route('/index/')
def listings():
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', None)
    condition_filter = request.args.get('condition', None)
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    db = get_db()

    query = 'SELECT * FROM item WHERE 1=1'
    params = []

    if search_query:
        query += ' AND name LIKE ?'
        params.append(f'%{search_query}%')
    if category_filter:
        query += ' AND category_id = ?'
        params.append(category_filter)
    if condition_filter:
        query += ' AND condition = ?'
        params.append(condition_filter)
    if min_price:
        query += ' AND asking_price >= ?'
        params.append(min_price)
    if max_price:
        query += ' AND asking_price <= ?'
        params.append(max_price)

    items = db.execute(query, params).fetchall()
    categories = db.execute('SELECT DISTINCT category_id FROM item').fetchall()

    return render_template('index.html', items=items, search_query=search_query, categories=categories,
                           current_category=category_filter, current_condition=condition_filter,
                           min_price=min_price, max_price=max_price)


@app.route('/my_account/')
def my_account():
    if 'user_id' not in session:
        return redirect(url_for('log_in'))

    user_id = session['user_id']
    db = get_db()
    transactions = db.execute('''
        SELECT tr.*, it.name AS item_name
        FROM transaction_request tr
        JOIN item it ON tr.item_id = it.item_id
        WHERE it.user_account_id = ?
        ''', (user_id,)).fetchall()
    items_posted = db.execute('''
        SELECT *
        FROM item 
        WHERE item.user_account_id = ?
        ''', (user_id,)).fetchall()
    bids_posted = db.execute('''
        select tr.price as offer_amount, tr.accepted_declined, item.*
        from transaction_request tr
        join item
        on item.item_id = tr.item_id
        where buyer_id == ?        
        ''',(user_id,)).fetchall()

    

    return render_template('my_account.html', username=session.get('user_id'), transactions=transactions, items_posted=items_posted, bids_posted = bids_posted)


@app.route('/item/<int:item_id>/')
def item_details(item_id):
    user_id = session['user_id']
    db = get_db()
    item = db.execute('SELECT * FROM item WHERE item_id = ?', (item_id,)).fetchone()
    username = db.execute('SELECT name FROM user WHERE  user_account_id = ?', (session.get('username'),)).fetchone()
    bids_on_item = db.execute('''
    select tr.*, us.phone_number, us.email_address
    from transaction_request tr
    join user us
    on us.user_account_id = tr.buyer_id
    where tr.item_id = ?''', (item_id,)).fetchall()
    print('bids', bids_on_item)
    if item:
        return render_template('details.html', item=item, item_id=item_id, user_id=user_id, bids_on_item = bids_on_item)
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
        condition = request.form.get('condition', '0')  # Default to '0' if not provided
        category = request.form['category']
        user_id = session['user_id']
        
        from datetime import datetime

        time = datetime.now()
        filename = f"{user_id}_{str(time)}.{image.filename.split('.')[-1]}"
        image.save(os.path.join(app.root_path, 'static', 'uploads', filename))
        db = get_db()
        db.execute('INSERT INTO item (user_account_id, name, description, asking_price, condition, category_id, image_path) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (user_id, name, description, asking_price, condition, category, filename))
        db.commit()

        return redirect(url_for('listings'))
    else:
        return render_template('add_item.html')


@app.route('/edit_item/<int:item_id>', methods=['POST'])
def edit_item(item_id):
    if 'user_id' not in session:
        return redirect(url_for('log_in'))

    description = request.form['description']
    asking_price = request.form['asking_price']

    db = get_db()
    db.execute('UPDATE item SET description = ?, asking_price = ? WHERE item_id = ?',
               (description, asking_price, item_id))
    db.commit()
    
    return jsonify({"message": "Item updated successfully"})

@app.route('/submit_item_bid/<int:item_id>/', methods=['GET', 'POST'])
def submit_item_bid(item_id):
    if 'user_id' not in session:
        return redirect(url_for('log_in'))

    db = get_db()
    if request.method == 'POST':
        # Process the bid submission
        offer_price = request.form['offer_price']
        comments = request.form['comments']
        buyer_id = session['user_id']  # The ID of the logged-in user

        # Establish a database connection and insert the new transaction
        db.execute('''
            INSERT INTO transaction_request (item_id, buyer_id, price, messages, date_time_requested)
            VALUES (?, ?, ?, ?, datetime('now'))
            ''', (item_id, buyer_id, offer_price, comments))
        #get highest bid so far, check if none. if non eupdate, else update only if new bid larger
        highest_bid = db.execute('''
        select highest_bid
        from item
        where item_id == ?        
        ''',(item_id,)).fetchone()[0]
        print(highest_bid, highest_bid == None, highest_bid == '')
        if highest_bid == None or float(offer_price) > float(highest_bid):
            highest_bid = offer_price
            db.execute('''
            UPDATE item
            SET highest_bid = ?
            WHERE item_id = ?;
            ''', (offer_price, item_id))
   


        db.commit()

        return redirect(url_for('listings'))
    else:
        item = db.execute('SELECT * FROM item WHERE item_id = ?', (item_id,)).fetchone()

        return render_template('request_transaction.html', item_id=item_id, item=item)


@app.route('/accept_bid/<int:bid_id>', methods=['POST'])
def accept_bid(bid_id):
    
    db = get_db()
    db.execute('UPDATE transaction_request SET accepted_declined = "accepted" WHERE transaction_id = ?', (bid_id,))
    db.commit()
    bid = db.execute('SELECT * FROM transaction_request WHERE transaction_id = ?', (bid_id,)).fetchall()
    #for i in bid:
    #    for j in i:
    #        print(j)

    bids_on_item = db.execute('SELECT * FROM transaction_request WHERE item_id = ?', (str(bid[0]['item_id']),)).fetchall()
    #for i in bids_on_item:
    #    for j in i:
    #        print(j)

    return jsonify(success=True)

@app.route('/decline_bid/<int:bid_id>', methods=['POST'])
def decline_bid(bid_id):
    db = get_db()
    db.execute('UPDATE transaction_request SET accepted_declined = "declined" WHERE transaction_id = ?', (bid_id,))
    db.commit()
    return jsonify(success=True)

@app.route('/llogin/', methods=['GET', 'POST'])
def log_in():
    if request.method == 'POST':
        username = request.form['username']

        db = get_db()
        cursor = db.execute('SELECT user_account_id, name FROM user WHERE name = ?', (username,))
        user = cursor.fetchone()

        if user:
            # User found, proceed with login
            session['user_id'] = username  # Store the user's ID in the session
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
            cursor = db.execute('INSERT INTO user (user_account_id, name, email_address) VALUES (?, ?, ?)', (username, username,  username + "@example.com"))
            db.commit()
            
            # Fetch the user_account_id of the newly created user
            user_account_id = username
            
            # Store both username and user_account_id in the session
            session['username'] = username
            session['user_id'] = username  # Store the user's ID in the session
            
            #print("Account created for username: ", username, "with user ID: ", user_account_id)
            return redirect(url_for('listings'))
        except sqlite3.IntegrityError as e:
            print("Error occurred: ", e)
            # This error occurs if the username is not unique
            return render_template('sign_up.html', error="An account with this username already exists. Please choose another username.")
    else:
        return render_template('sign_up.html')


#@app.route('/logout/')
#def logout():
#    print("logged_out")
#    session.pop('username', None)
#    return redirect(url_for('log_in'))



@app.route('/login/')
def login():
    if 'user_id' in session:
        # Already logged in
        return redirect(url_for('listings'))

    next = request.args.get('next')
    ticket = request.args.get('ticket')
    if not ticket:
        # No ticket, the request come from end user, send to CAS login
        cas_login_url = cas_client.get_login_url()
        app.logger.debug('CAS login URL: %s', cas_login_url)
        return redirect(cas_login_url)

    # There is a ticket, the request come from CAS as callback.
    # need call `verify_ticket()` to validate ticket and get user profile.
    app.logger.debug('ticket: %s', ticket)
    app.logger.debug('next: %s', next)

    user, attributes, pgtiou = cas_client.verify_ticket(ticket)

    app.logger.debug(
        'CAS verify ticket response: user: %s, attributes: %s, pgtiou: %s', user, attributes, pgtiou)

    if not user:
        return 'Failed to verify ticket. <a href="/login">Login</a>'
    else:  # Login successfully, redirect according `next` query parameter.
        session['user_id'] = user
        session['username'] = user
        db = get_db()
        user_in_db = db.execute('SELECT * FROM user WHERE user_account_id = ?', (user,)).fetchall()
        if(len(user_in_db) == 0):
            return render_template('add_user_details.html')
        return redirect(next)

@app.route('/submit_user_info/', methods=['GET', 'POST'])
def submit_user_info():
    username = session['user_id']
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    
    print(f"Name: {name}, Email: {email}, Phone: {phone}")
    db = get_db()
    cursor = db.execute('INSERT INTO user (user_account_id, name, email_address, phone_number) VALUES (?, ?, ?, ?)', (username, name,  email, phone,))
    db.commit()

    return redirect(url_for('listings'))

@app.route('/logout/')
def logout():
    print("----------")
    redirect_url = url_for('logout_callback', _external=True)
    cas_logout_url = cas_client.get_logout_url(redirect_url)
    app.logger.debug('CAS logout URL: %s', cas_logout_url)

    return redirect(cas_logout_url)

@app.route('/logout_callback')
def logout_callback():
    # redirect from CAS logout request after CAS logout successfully
    session.pop('user_id', None)
    session.pop('username', None)
    return 'Logged out from CAS. <a href="/login">Login</a>'

