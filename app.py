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

@app.route('/test_query')  # Add a new route for testing
def test_query():
    # Example queries to test (replace with your actual queries)
    query_db("INSERT INTO Admins (username, password) VALUES ('tree', 'tree')")
    query_db("SELECT * FROM Admins")  

    return "Queries executed (check your terminal)" 

# seat function route
@app.route('/seat_reservation', methods=['GET', 'POST'])
def seat_reservation():
    # Initialize
    seating_chart = [["O", "O", "O", "O"] for _ in range(12)]
    reservations = query_db("SELECT seatRow, seatColumn FROM reservations")

    # charting update
    for r in reservations:
        seating_chart[r['seatRow'] - 1][r['seatColumn'] - 1] = "X"

    if request.method == 'POST':
        # get data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        seat_row = request.form['seat_row']
        seat_column = request.form['seat_column']

        # validation
        if not first_name or not last_name or not seat_row or not seat_column:
            flash("")
            return render_template('seat_reservation.html', seating_chart=seating_chart)

        # conversion of input to int
        seat_row = int(seat_row)
        seat_column = int(seat_column)

        # Generate reservation code
        seat_row_str = str(seat_row)
        seat_column_str = str(seat_column)
        random_part = os.urandom(4).hex()
        reservation_code = "R" + seat_row_str + "C" + seat_column_str + "-" + random_part

        # availability check
        if seating_chart[seat_row - 1][seat_column - 1] == "X":
            flash(f"Row {seat_row}, Seat {seat_column} is already assigned. Please choose again.")
            return render_template('seat_reservation.html', seating_chart=seating_chart)

        # passenger name
        full_name = first_name + " " + last_name

        # insert reservation into the database
        query = """
            INSERT INTO reservations (passengerName, seatRow, seatColumn, eTicketNumber)
            VALUES (?, ?, ?, ?)
        """
        query_args = (full_name, seat_row, seat_column, reservation_code)
        query_db(query, query_args)

        # Flash a success message
        success_message = "Reservation confirmed! Your code is: " + reservation_code
        flash(success_message)

        # Redirect the user back to the seat reservation page
        return redirect(url_for('seat_reservation'))

    # render
    return render_template('seat_reservation.html', seating_chart=seating_chart)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)