import sqlite3

def create_tables(db_name='marketplace.db'):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # Create 'user' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        user_account_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email_address TEXT NOT NULL UNIQUE,
        phone_number TEXT,
        profile_photo TEXT
    );
    ''')

    # Create 'item' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS item (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_account_id TEXT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        asking_price DOUBLE,
        highest_bid INTEGER,
        image TEXT,
        condition INTEGER,
        sold INTEGER DEFAULT 0,
        image_path TEXT,
        category_id INTEGER,
        FOREIGN KEY (user_account_id) REFERENCES user (user_account_id),
        FOREIGN KEY (category_id) REFERENCES category (category_id)
    );
    ''')

    # Create 'category' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS category (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        deliverability INTEGER
    );
    ''')

    # Create 'transaction_request' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transaction_request (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        buyer_id INTEGER,
        price TEXT,
        messages TEXT,
        accepted_declined INTEGER,
        date_time_requested TEXT,
        date_time_confirmed TEXT,
        FOREIGN KEY (item_id) REFERENCES item (item_id),
        FOREIGN KEY (buyer_id) REFERENCES user (user_account_id)
    );
    ''')

    # Create 'message' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS message (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        contents TEXT,
        sender INTEGER,
        recipient INTEGER,
        time_sent TEXT,
        FOREIGN KEY (sender) REFERENCES user (user_account_id),
        FOREIGN KEY (recipient) REFERENCES user (user_account_id)
    );
    ''')    

    # Commit changes and close the connection
    connection.commit()
    connection.close()

    print("Database setup complete.")

if __name__ == "__main__":
    create_tables()
