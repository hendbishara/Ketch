import mysql.connector
from geopy.geocoders import Nominatim
from datetime import datetime
import random

# Initialize Geolocator
geolocator = Nominatim(user_agent="geo_clustering")

# Connection setup function (avoid repetition)
def get_connection():
    return mysql.connector.connect(
        host="turntable.proxy.rlwy.net",
        user="root", 
        password="QidNZDIznmxgXewmxVnbzMVkFVZoyHZs",  
        database="railway",
        port = 21931,
        connection_timeout = 30
    )


def get_order_capacity(order_id):
    """ Fetches the capacity of an order from the database """
    connection = get_connection()  # Replace with actual DB connection

    cursor = connection.cursor()
    
    query = """SELECT ri.req_id, SUM(i.capacity * ri.quantity) AS total_capacity
            FROM request_items ri
            JOIN items i ON ri.item_id = i.item_id
            WHERE req_id = %s
            GROUP BY ri.req_id;"""

    try:
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        if result:
            return int(result[1])  # Convert to integer capacity
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

def get_all_orders(store_id):
    # Connect to your MySQL database
    db = get_connection()
    cursor = db.cursor()

    # SQL query to fetch all orders with order_id, user_id, latitude, and longitude
    cursor.execute("""
        SELECT req_id, user_id FROM active_requests WHERE store_id = %s
    """,(store_id,))
    
    # Fetch all the results
    orders = cursor.fetchall()

    cursor.close()
    db.close()

    return orders



def get_user_id_from_order(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Query to fetch user locations (address, latitude, longitude)
    cursor.execute("SELECT user_id FROM active_requests where req_id = %s",(order_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result: return result[0]
    else: return None


# In db_methods.py
def get_address_for_user(user_id):
    conn = get_connection()  # Using your existing database connection method
    cursor = conn.cursor()

    cursor.execute("SELECT location FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()

    if result:
        return result[0]
    return None

# In db_methods.py
def get_user_coordinates(user_id):
    conn = get_connection()  # Assuming you're using your existing database connection
    cursor = conn.cursor()

    cursor.execute("SELECT location FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()

    if result:
        try:
            location = geolocator.geocode(result)
            if location is None:
                raise Exception(f"invalid location for user:{user_id}")
            
        except Exception as e:
            print("invalid location")
            return None
            
        
        return (location.latitude,location.longitude)  # Return the latitude and longitude as a tuple
    return None  # Return None if no coordinates are found for that user



def get_items_below_capacity(max_capacity):
    """ Fetch items from the database that fit within the given capacity. """
    connection = get_connection()  # Your database connection method
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT item_id, capacity FROM items WHERE capacity <= %s", (max_capacity,))
    items = cursor.fetchall()

    cursor.close()
    connection.close()
    return items

#TODO: fix for new data base
def get_users_in_radius(center_coordinates, radius_km):
    """ Fetch users within the given radius. (Assuming geolocation in DB) """
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    lat, lon = center_coordinates
    query = """
        SELECT name, email
        FROM users
        WHERE ST_Distance_Sphere(
            point(longitude, latitude),
            point(%s, %s)
        ) <= %s * 1000
    """
    cursor.execute(query, (lon, lat, radius_km))
    users = cursor.fetchall()

    cursor.close()
    connection.close()
    return users


def get_active_stores():
        """Get all active stores from the database"""
        
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT store_id, store_name, warehouse_location, total_capacity
        FROM stores
        WHERE store_id IN (SELECT store_id FROM active_requests);
        """
        
        cursor.execute(query)
        stores = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return stores
        
        
        
        
def update_cluster_id(req_id,cluster_id):
    """update cluster id for the specific req_id"""
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """UPDATE active_requests SET cluster_id = %s WHERE req_id = %s"""
    
    cursor.execute(query,(cluster_id,req_id))
    
    cursor.close()
    connection.close()

def get_clusters(store_id):
    """get for all req_ids cluster_ids for the specific store"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """SELECT req_id cluster_id user_id FROM active_requests WHERE store_id = %s"""
    
    cursor.execute(query,(store_id,))
    
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return result
    
        



