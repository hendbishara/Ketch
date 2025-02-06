import mysql.connector
from geopy.geocoders import Nominatim
from datetime import datetime
import random

# Initialize Geolocator
geolocator = Nominatim(user_agent="geo_clustering")

# Connection setup function (avoid repetition)
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",      # Change this if you have a different MySQL user
        password="Root2121!",  # Set your MySQL root password
        database="geo_clustering"
    )

def add_user(name, email, address):
    db = get_connection()
    cursor = db.cursor()

    # Check if the user with the provided email already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        print(f"User with email {email} already exists. Skipping user creation.")
        cursor.close()
        db.close()
        return

    # Get latitude and longitude
    location = geolocator.geocode(address)
    if location:
        latitude, longitude = location.latitude, location.longitude

        # Insert into the users table
        sql = "INSERT INTO users (name, email, address, latitude, longitude) VALUES (%s, %s, %s, %s, %s)"
        values = (name, email, address, latitude, longitude)
        
        cursor.execute(sql, values)
        db.commit()
        
        print(f"User {name} added with coordinates ({latitude}, {longitude})")
    else:
        print(f"Could not geocode address: {address}")
    
    cursor.close()
    db.close()

def add_new_order(order_id, user_id, order_details, latitude, longitude):
    """ Adds a new order only if it does not already exist in the database. """

    db = get_connection()
    cursor = db.cursor()

    try:
        # ✅ Step 1: Check if the order already exists
        cursor.execute("SELECT id FROM orders WHERE id = %s", (order_id,))
        existing_order = cursor.fetchone()

        if existing_order:
            print(f"Order {order_id} already exists. Skipping insertion.")
            return  # Exit function if order already exists

        # ✅ Step 2: Insert the new order
        cursor.execute("""
            INSERT INTO orders (id, user_id, order_details, timestamp)
            VALUES (%s, %s, %s, NOW())
        """, (order_id, user_id, order_details))

        # ✅ Step 3: Update the user's coordinates in the users table
        cursor.execute("""
            UPDATE users SET latitude = %s, longitude = %s WHERE id = %s
        """, (latitude, longitude, user_id))

        # ✅ Commit changes
        db.commit()
        print(f"New order {order_id} for user {user_id} added successfully.")

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")

    finally:
        cursor.close()
        db.close()



def get_order_capacity(order_id):
    """ Fetches the capacity of an order from the database """
    connection = get_connection()  # Replace with actual DB connection

    cursor = connection.cursor()

    try:
        cursor.execute("SELECT order_details FROM orders WHERE id = %s", (order_id,))
        result = cursor.fetchone()
        if result:
            return int(result[0])  # Convert to integer capacity
        return None  # Default capacity if not found
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def get_all_users():
    db = get_connection()
    cursor = db.cursor()

    # Query to fetch all users
    query = "SELECT * FROM users"
    cursor.execute(query)
    users = cursor.fetchall()

    cursor.close()
    db.close()

    return users

def get_all_orders():
    # Connect to your MySQL database
    db = get_connection()
    cursor = db.cursor()

    # SQL query to fetch all orders with order_id, user_id, latitude, and longitude
    cursor.execute("""
        SELECT id, user_id FROM orders
    """)
    
    # Fetch all the results
    orders = cursor.fetchall()

    cursor.close()
    db.close()

    return orders

def get_user_address(user_id):
    db = get_connection()

    cursor = db.cursor()
    cursor.execute("SELECT address FROM users WHERE id = %s", (user_id,))
    address = cursor.fetchone()

    cursor.close()
    db.close()

    return address[0] if address else None

def get_user_addresses():
    db = get_connection()
    cursor = db.cursor()
    
    cursor.execute("SELECT id, address FROM users")
    user_addresses = {user_id: address for user_id, address in cursor.fetchall()}

    cursor.close()
    db.close()

    return user_addresses


def get_user_locations():
    conn = get_connection()  # Make sure to use your connection method
    cursor = conn.cursor()

    cursor.execute("SELECT id, latitude, longitude FROM users")
    user_locations = {}

    for user_id, latitude, longitude in cursor.fetchall():
        user_locations[user_id] = (latitude, longitude)

    return user_locations

def get_user_locations_vis():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Query to fetch user locations (address, latitude, longitude)
    cursor.execute("SELECT id, address, latitude, longitude FROM users")
    rows = cursor.fetchall()
    
    user_locations = {}
    
    for row in rows:
        user_id, address, latitude, longitude = row
        user_locations[user_id] = (address, (latitude, longitude))
    
    cursor.close()
    conn.close()
    
    return user_locations
def get_user_id_from_order(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Query to fetch user locations (address, latitude, longitude)
    cursor.execute("SELECT user_id FROM orders where id = %s",(order_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result: return result[0]
    else: return None


# In db_methods.py
def get_address_for_user(user_id):
    conn = get_connection()  # Using your existing database connection method
    cursor = conn.cursor()

    cursor.execute("SELECT address FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()

    if result:
        return result[0]
    return None

# In db_methods.py
def get_user_coordinates(user_id):
    conn = get_connection()  # Assuming you're using your existing database connection
    cursor = conn.cursor()

    cursor.execute("SELECT latitude, longitude FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()

    if result:
        return result  # Return the latitude and longitude as a tuple
    return None  # Return None if no coordinates are found for that user

def update_order_details_with_random_values():
    """ Updates all order_details values with a random number between 0 and 15 """
    connection = get_connection()  # Replace with actual DB connection
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT id FROM orders")  # Get all order IDs
        orders = cursor.fetchall()

        for (order_id,) in orders:
            random_value = random.randint(1, 6)  # Generate a random number
            cursor.execute("UPDATE orders SET order_details = %s WHERE id = %s", (random_value, order_id))

        connection.commit()  # Save changes
        print("Updated all order_details with random values.")

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    
    finally:
        cursor.close()
        connection.close()


'''
def create_orders_for_all_users():
    # Retrieve all users
    users = get_all_users()

    # Generate orders for each user
    for user in users:
        user_id, name, email, address, latitude, longitude = user
        order_details = f"Order details for {name} at {address}"

        # Generate order id (for simplicity, we'll use user_id as order_id)
        order_id = user_id  # You can modify this to generate an actual unique order_id

        # Add the order to the database
        add_new_order(order_id, user_id, order_details, latitude, longitude)

        print(f"Order created for {name} with user ID {user_id}.")

'''

