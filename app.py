import sqlite3
from flask import Flask, render_template, request, redirect, url_for

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

# Paths to your files (update with your actual paths)
schema_file_path = "schema.sql"  
db_file_path = "reservations.db" 

# Apply the schema to the database
apply_schema_to_db(db_file_path, schema_file_path)

app = Flask(__name__)

# --- Database Helper Functions ---
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

# --- Flask Routes ---

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get form data
        name = request.form["name"]
        email = request.form["email"]

        # ... other form fields ... 

        # Insert data into database (example)
        conn = get_db_connection()
        conn.execute("INSERT INTO reservations (name, email) VALUES (?, ?)", (name, email)) 
        conn.commit()
        conn.close()

        return redirect(url_for('index'))  # Redirect after successful submission

    else:  # GET request
        # Fetch reservations from database (example)
        reservations = query_db("SELECT * FROM reservations")
        return render_template("index.html", reservations=reservations)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
        app.run(host='0.0.0.0', port=5000, debug=True)

main()
