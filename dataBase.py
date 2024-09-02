import sqlite3
import passwordAuthentication as auth

def init_db():
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT NOT NULL UNIQUE,
                   password TEXT NOT NULL,
                   balance REAL NOT NULL DEFAULT 0.0
                   )
                   ''')
    connection.commit()

def add_user(username, password):
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()
    hashed_pass = auth.hash_password(password)
    query = f'''INSERT INTO users (username, password) VALUES (?, ?)'''
    cursor.execute(query, (username, hashed_pass))
    connection.commit()

def get_user(username):
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()
    query = f'''SELECT * FROM users WHERE username = ? '''
    cursor.execute(query, (username, ))
    return cursor.fetchone()

def get_all_users():
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()
    query = 'SELECT * FROM users'
    cursor.execute(query)
    return cursor.fetchall()

def init_movie_table():
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        image_url TEXT,
        is_sold BOOLEAN DEFAULT 0,          
        FOREIGN KEY (user_id) REFERENCES users (id)          
        )         
    ''')
    connection.commit()

def add_movie(user_id, title, description, price, image_url = None):
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()
    query = '''INSERT INTO movies (user_id, title, description, price, image_url) VALUES (?, ?, ?, ?, ?)'''
    cursor.execute(query, (user_id, title, description, price, image_url))
    connection.commit()

def get_movie (movie_id):
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()
    query ='''SELECT * FROM movies WHERE id =?'''
    cursor.execute(query, (movie_id,))
    return cursor.fetchone()

def get_users_movies(user_id):
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()
    query = '''SELECT * FROM movies WHERE user_id = ?'''
    cursor.execute(query,(user_id,))
    return cursor.fetchall()

def get_all_movies():
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()
    query = '''SELECT * FROM movies'''
    cursor.execute(query)
    return cursor.fetchall()

def is_movie_sold( movie_id):
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()
    query = ''' SELECT is_sold FROM movies WHERE id = ? '''
    cursor.execute(query, (movie_id,))
    return cursor.fetchone()[0]

def mark_movie_as_sold(movie_id):
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()
    movie_query = '''SELECT price, user_id FROM movies WHERE id = ?'''
    cursor.execute(movie_query, (movie_id,))
    movie_data = cursor.fetchone()

    if movie_data:
        movie_price, user_id = movie_data
        update_query = '''UPDATE movies SET is_sold = 1 WHERE id = ?'''
        cursor.execute(update_query, (movie_id,))
        connection.commit()
        update_balance_query = '''UPDATE users SET balance = balance + ? WHERE id = ?'''
        cursor.execute(update_balance_query, (movie_price, user_id))
        connection.commit()



def init_comments_table():
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           movie_id INTEGER NOT NULL,
           user_id INTEGER NOT NULL,
           text TEXT NOT NULL,
           timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
           FOREIGN KEY (movie_id) REFERENCES movies (id),
           FOREIGN KEY (user_id) REFERENCES users (id)                                                        
        )
''')
    
    connection.commit()


def add_comment(movie_id, user_id, text):
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()
    query = '''INSERT INTO comments (movie_id, user_id, text) VALUES (?, ?, ?)'''
    cursor.execute(query, (movie_id, user_id, text))
    connection.commit()

def get_balance(username):
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()
    query = f'''SELECT balance FROM users WHERE username = ? '''
    cursor.execute(query, (username, ))
    return cursor.fetchone()

def update_balance(newBalance , username):
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()
    query = f'''UPDATE users SET balance = ? WHERE username = ?'''
    cursor.execute(query, (newBalance , username ,))
    connection.commit()

def get_comments_for_movie(movie_id):
    connection = sqlite3.connect("db_test.db")
    cursor = connection.cursor()
    query = '''
        SELECT users.username, comments.text, comments.timestamp
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.movie_id = ?
    '''
    cursor.execute(query, (movie_id,))
    return cursor.fetchall()

def seed_admin_user():
    admin_username = 'admin'
    admin_password = 'Admin@123'
    admin_user = get_user(admin_username)
    if not admin_user:
        add_user(admin_username, admin_password)
        print("Admin user seeded successfully.")