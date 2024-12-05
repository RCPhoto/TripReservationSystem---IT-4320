import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session

# --- DB functions ---
def get_db_connection():
    conn = sqlite3.connect(db_file_path)
    conn.row_factory = sqlite3.Row  # Access data by column name
    return conn

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv


def apply_schema_to_db(db_file, schema_file):
    """Applies a schema from an SQL file to an existing SQLite database."""
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            with open(schema_file, 'r') as f:
                sql_script = f.read()
            cursor.executescript(sql_script)
            conn.commit()
            print("Schema applied successfully")
    except Exception as e:
        print(f"Error applying schema: {e}")

schema_file_path = "schema.sql"  
db_file_path = "reservations.db" 

# Apply the schema to the database
apply_schema_to_db(db_file_path, schema_file_path)
query_db("SELECT * FROM Admins") 
app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Remember to hash passwords!

        admin = query_db('SELECT * FROM Admins WHERE username = ?', (username,), one=True)
        if admin and admin['password'] == password:
            # Set a session to indicate that the user is logged in
            session['logged_in'] = True 
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        flash('You need to be logged in to access the admin dashboard', 'danger')
        return redirect(url_for('admin_login'))

    return render_template('admin_dashboard.html')

@app.route('/seat_reservation')
def seat_reservation():
    return render_template('seat_reservation.html')

@app.route('/test_query')  # Add a new route for testing
def test_query():
    # Example queries to test (replace with your actual queries)
    query_db("INSERT INTO Admins (username, password) VALUES ('tree', 'tree')")
    query_db("SELECT * FROM Admins")  

    return "Queries executed (check your terminal)" 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
