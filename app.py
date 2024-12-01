import os
import sqlite3

def apply_schema_to_db(db_file, schema_file):
    """Applies a schema from an SQL file to an existing SQLite database.

    Args:
        db_file (str): The path to the SQLite database file (.db).
        schema_file (str): The path to the SQL schema file (.sql).
    """
    try:
        # Connect to the existing database
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            print(os.getcwd())
            # Read and execute the schema file
            with open(schema_file, 'r') as f:
                sql_script = f.read()
            cursor.executescript(sql_script)

            conn.commit()
            print("Schema applied successfully")

    except Exception as e:
        print(f"Error applying schema: {e}")

def main():
    # Paths to your files
    schema_file_path = "schema.sql"
    db_file_path = "reservations.db"

    # Apply the schema to the database
    apply_schema_to_db(db_file_path, schema_file_path)


main()
        app.run(host='0.0.0.0', port=5000, debug=True)

main()
