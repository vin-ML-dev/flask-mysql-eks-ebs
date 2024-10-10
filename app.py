from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

# Database connection details from environment variables
db_config = {
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'dbpassword11'),
    'host': os.getenv('MYSQL_HOST', 'mysql'),
    'database': os.getenv('MYSQL_DB', 'usermgmt')
}

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

def create_users_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # SQL statement to create users table if it doesn't exist
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL
    );
    '''
    try:
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'users' ensured in the database.")
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")
    finally:
        cursor.close()
        connection.close()

# Ensure the users table exists when the application starts
#create_users_table()

@app.route('/')
def index():
    return "Welcome to the Flask User Management Microservice!"

# Insert a new user
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    
    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400
    
    create_users_table()   #create table
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
        connection.commit()
        return jsonify({"message": "User added successfully"}), 201
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"error": "Failed to insert user"}), 500
    finally:
        cursor.close()
        connection.close()

# Fetch all users
@app.route('/list_users', methods=['GET'])
def get_users():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        return jsonify(users), 200
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"error": "Failed to fetch users"}), 500
    finally:
        cursor.close()
        connection.close()

# Delete a user by ID
@app.route('/del_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User deleted successfully"}), 200
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"error": "Failed to delete user"}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
