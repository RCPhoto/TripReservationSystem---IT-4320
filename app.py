import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session

##file path with universal acceptance (dynamic)
db_file_path = os.path.join(os.path.dirname(__file__), "reservations.db")

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

# def apply_schema_to_db(db_file, schema_file):
#     """Applies a schema from an SQL file to an existing SQLite database."""
#     try:
#         with sqlite3.connect(db_file) as conn:
#             cursor = conn.cursor()
#             with open(schema_file, 'r') as f:
#                 sql_script = f.read()
#             cursor.executescript(sql_script)
#             conn.commit()
#             print("Schema applied successfully")
#     except Exception as e:
#         print(f"Error applying schema: {e}")

#schema_file_path = "schema.sql"
#db_file_path = "reservations.db"

# Apply the schema to the database
#apply_schema_to_db(db_file_path, schema_file_path)
query_db("SELECT * FROM Admins")
app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.context_processor
def inject_logged_in():
    return {
        'logged_in': session.get('logged_in', False),
        'username': session.get('username', '')
    }

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html', logged_in=session.get('logged_in'), username=session.get('username'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    # Check if the admin is already logged in
    if 'logged_in' in session and session['logged_in']:
        # Add a variable to pass the error message to the template
        error_message = 'You are already logged in. Please log out to switch accounts.'
        return render_template('admin_login.html', error_message=error_message)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Remember to hash passwords!

        admin = query_db('SELECT * FROM Admins WHERE username = ?', (username,), one=True)
        if admin and admin['password'] == password:
            # Set a session to indicate that the user is logged in
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            error_message = 'Invalid username or password'
            return render_template('admin_login.html', error_message=error_message)

    return render_template('admin_login.html', error_message=None)

def get_cost_matrix():
    # Generate the cost matrix for 12 rows and 4 columns
    return [[100, 75, 50, 100] for _ in range(12)]

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        flash('You need to be logged in to access the admin dashboard', 'danger')
        return redirect(url_for('admin_login'))

    username = session.get('username')
    # Get the cost matrix
    cost_matrix = get_cost_matrix()

    # Get the reserved seats from the database
    reservations = query_db("SELECT seatRow, seatColumn FROM reservations")

    # Calculate total sales
    total_sales = 0.0
    seating_chart = [["O" for _ in range(4)] for _ in range(12)]  # Initialize seating chart with available seats (O)

    for reservation in reservations:
        row = reservation['seatRow'] - 1
        column = reservation['seatColumn'] - 1
        seating_chart[row][column] = "X"  # Mark the seat as reserved
        total_sales += cost_matrix[row][column]  # Add the seat's cost to the total sales

    # Format total sales to two decimal places
    total_sales_formatted = f"${total_sales:.2f}"

    # Render the dashboard with the seating chart and total sales
    return render_template('admin_dashboard.html', seating_chart=seating_chart, total_sales=total_sales_formatted, username=username, logged_in=True)

@app.route('/admin_logout', methods=['POST'])
def admin_logout():
    # Remove the session to log out
    session.pop('logged_in', None)
    session.pop('username', None)  # Clear the username
    flash('Logged out successfully.', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/test_query')  # Add a new route for testing
def test_query():
    # Example queries to test (replace with your actual queries)
    query_db("INSERT INTO Admins (username, password) VALUES ('tree', 'tree')")
    query_db("SELECT * FROM Admins")  

    return "Queries executed (check your terminal)"

# seat function route
@app.route('/seat_reservation', methods=['GET', 'POST'])
def seat_reservation():
    seating_chart = [["O", "O", "O", "O"] for _ in range(12)]
    reservations = query_db("SELECT seatRow, seatColumn FROM reservations")

    for r in reservations:
        seating_chart[r['seatRow'] - 1][r['seatColumn'] - 1] = "X"

    errors = {}
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        seat_row = request.form.get('seat_row', '').strip()
        seat_column = request.form.get('seat_column', '').strip()

        # Validate input
        if not first_name:
            errors['first_name_error'] = "First name is required."
        if not last_name:
            errors['last_name_error'] = "Last name is required."
        if not seat_row:
            errors['seat_row_error'] = "Please select a row."
        if not seat_column:
            errors['seat_column_error'] = "Please select a column."

        if seat_row and seat_column:
            try:
                seat_row = int(seat_row)
                seat_column = int(seat_column)
                if seating_chart[seat_row - 1][seat_column - 1] == "X":
                    errors['seat_row_error'] = f"Seat Row {seat_row}, Column {seat_column} is already reserved."
            except (ValueError, IndexError):
                errors['seat_row_error'] = "Invalid row or column selection."

        # If no errors, reserve the seat
        if not errors:
            # Generate eTicket
            constant = "INFOTC4320"
            e_ticket = ''.join(a + b for a, b in zip(first_name, constant)) + first_name[len(constant):]
            full_name = f"{first_name} {last_name}"
            query = """
                INSERT INTO reservations (passengerName, seatRow, seatColumn, eTicketNumber)
                VALUES (?, ?, ?, ?)
            """
            query_args = (full_name, seat_row, seat_column, e_ticket)
            query_db(query, query_args)

            flash(f"Seat reserved! Your eTicket: {e_ticket}", "success")
            return redirect(url_for('seat_reservation'))

    # Pass errors and str function explicitly to template
    return render_template('seat_reservation.html', seating_chart=seating_chart, errors=errors, str=str, logged_in=session.get('logged_in'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)