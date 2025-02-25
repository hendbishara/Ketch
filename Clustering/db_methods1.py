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
    
    query = """SELECT ar.req_id, ar.store_id, SUM(ri.quantity * i.capacity) as total_capacity
    FROM 
        active_requests ar
        JOIN request_items ri ON ar.req_id = ri.req_id
        JOIN items i ON ri.item_id = i.item_id AND ar.store_id = i.store_id
    WHERE 
        ar.req_id = %s
    GROUP BY 
        ar.req_id, ar.store_id;"""

    try:
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        if result:
            return int(result[2])  # Convert to integer capacity
        return 0  # Default capacity if not found
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return 0
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

    # SQL query to fetch all orders with order_id, user_id
    cursor.execute("""
        SELECT req_id, user_id FROM active_requests WHERE store_id = %s and status = 0
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
'''
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
'''

def get_user_coordinates(user_id):
    """Fetch latitude and longitude for a given user from the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT latitude, longitude FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result and result[0] is not None and result[1] is not None:
        return result  # (latitude, longitude)
    return None  # Return None if no coordinates found

def get_store_coordinates(store_id):
    """Get store coordinates from the database"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
    SELECT latitude, longitude 
    FROM stores 
    WHERE store_id = %s
    """
    
    try:
        cursor.execute(query, (store_id,))
        result = cursor.fetchone()
        if result and result['latitude'] is not None and result['longitude'] is not None:
            return result['latitude'],result['longitude']
        return None
    except mysql.connector.Error as e:
        print(f"Database error in get_store_coordinates: {e}")
        return None
    finally:
        cursor.close()
        connection.close()



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
#DONE!
def get_users_in_radius(center_coordinates, radius_km):
    """ Fetch users within the given radius. (Assuming geolocation in DB) """
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    lat, lon = center_coordinates
    query = """
        SELECT user_id
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
        SELECT store_id, store_name, warehouse_location, total_capacity, latitude, longitude
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
    
    try:
        query = """UPDATE active_requests SET cluster_id = %s WHERE req_id = %s"""
        cursor.execute(query,(cluster_id,req_id))
        connection.commit()  # Add this line to commit the changes
        print(f"Updated cluster_id to {cluster_id} for request {req_id}")  # Add logging
    except mysql.connector.Error as e:
        print(f"Error updating cluster_id: {e}")
        connection.rollback()  # Rollback on error
    finally:
        cursor.close()
        connection.close()

def get_clusters(store_id):
    """get for all req_ids cluster_ids for the specific store"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """SELECT req_id, cluster_id, user_id FROM active_requests WHERE store_id = %s"""
    
    cursor.execute(query,(store_id,))
    
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return result


def get_order_time(order):
    """Get timestamp of order and max waiting time."""
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """SELECT time_stamp, max_wait FROM active_requests WHERE req_id = %s"""
    cursor.execute(query, (order,))
    
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result is None:
        print(f"Error: No order found with req_id {order}")
        return None, None  # Return safe values instead of crashing

    return result["time_stamp"], result["max_wait"]

def get_requests(store_id):
    """get all requests for the specific store"""
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """SELECT req_id, user_id, cluster_id FROM active_requests WHERE store_id = %s and status = 0"""
    
    cursor.execute(query,(store_id,))
    
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return result

def get_price_for_store(store):
    """Fetch the price for a specific store"""
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """SELECT delivery_fee FROM stores WHERE store_id = %s"""
    
    cursor.execute(query,(store,))
    
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return result["delivery_fee"]

def update_final_price(req_id,price):
    """update the final price for the specific request"""
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = """UPDATE active_requests SET final_delivery_fee = %s WHERE req_id = %s"""
        cursor.execute(query,(price,req_id))
        connection.commit()  # Add this line to commit the changes
        print(f"Updated final price to {price} for request {req_id}")  # Add logging
    except mysql.connector.Error as e:
        print(f"Error updating final price: {e}")
        connection.rollback()  # Rollback on error
    finally:
        cursor.close()
        connection.close()

def update_combined_orders_in_db(orders,clusters):
    conn = get_connection()
    cursor = conn.cursor()
    for order in orders:
        comb_ord_id = get_last_combined_order_id(conn,cursor) + 1
        print(f"Combining orders: {order} into combined order {comb_ord_id}")
        for clus_id in order:
            if clus_id == "WareHouse":
                continue
            else:
                for cluster in clusters:
                    if cluster.id == clus_id:
                        curr_clus = cluster
                        break
                for ord in curr_clus.orders:
                    print(f"Updating order {ord} to combined order {comb_ord_id}")
                    update_active_order(ord,comb_ord_id,conn,cursor)
                    update_order_status(ord,1,conn,cursor)
    conn.commit()
    cursor.close()
    conn.close()
                
def get_last_combined_order_id(conn,cursor):
     # Get the last order_id from the table (or start from 1 if empty)
    cursor.execute("SELECT MAX(order_id) FROM combined_orders")
    last_order_id = cursor.fetchone()[0]  # Fetch the max order_id
    last_order_id = last_order_id if last_order_id is not None else 0  # Avoid None issue
    return last_order_id

def update_active_order(req_id,comb_ord_id,conn,cursor):

    query = "INSERT INTO combined_orders (order_id, req_id) VALUES (%s, %s)"

    cursor.execute(query, (comb_ord_id, req_id))
    conn.commit()


def update_order_status(req_id,status,conn,cursor):

    query = "UPDATE active_requests SET status = %s WHERE req_id = %s"

    cursor.execute(query, (status, req_id))
    conn.commit()


'''
def update_cluster(id, coordinates):
    """Update cluster's coordinates using MySQL POINT type."""
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Ensure the coordinates are valid numbers
        if not all(isinstance(coord, (int, float)) for coord in coordinates):
            raise ValueError(f"Invalid coordinates: {coordinates}")
        
        # Format the coordinates for the POINT type
        point_str = f"POINT({coordinates[0]} {coordinates[1]})"
        print(f"Updating cluster {id} with POINT: {point_str}")
        
        query = """INSERT INTO clusters (cluster_id, centroid) 
                   VALUES (%s, ST_GeomFromText(%s)) 
                   ON DUPLICATE KEY UPDATE centroid = ST_GeomFromText(%s)"""
        
        cursor.execute(query, (id, point_str, point_str))
        connection.commit()
        
        print(f"Successfully updated cluster {id} with coordinates {coordinates}")
        
    except (mysql.connector.Error, ValueError) as e:
        print(f"Error updating cluster_coordinates: {e}")
        connection.rollback()
        
    finally:
        cursor.close()
        connection.close()
'''

def update_cluster(id, coordinates):
    """Update cluster's latitude and longitude in the clusters table."""
    latitude, longitude = coordinates
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        print(f"Updating cluster {id} with Latitude: {latitude}, Longitude: {longitude}")
        
        query = """INSERT INTO clusters (cluster_id, latitude, longitude) 
                   VALUES (%s, %s, %s) 
                   ON DUPLICATE KEY UPDATE latitude = VALUES(latitude), longitude = VALUES(longitude)"""
        
        cursor.execute(query, (id, latitude, longitude))
        connection.commit()
        
        print(f"Successfully updated cluster {id} with latitude={latitude}, longitude={longitude}")
        
    except (mysql.connector.Error, ValueError) as e:
        print(f"Error updating cluster coordinates: {e}")
        connection.rollback()
        
    finally:
        cursor.close()
        connection.close()



def reset_clusters():
    """Reset clusters table"""
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """TRUNCATE TABLE clusters"""
    
    cursor.execute(query)
    connection.commit()
    
    cursor.close()
    connection.close()

def get_cluster_centroid(cluster_id):
    """Retrieve the centroid as a tuple using ST_X and ST_Y."""
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = """SELECT ST_X(centroid) AS x, ST_Y(centroid) AS y 
                   FROM clusters WHERE cluster_id = %s"""
        cursor.execute(query, (cluster_id,))
        result = cursor.fetchone()
        
        if result and result['x'] is not None and result['y'] is not None:
            return (result['x'], result['y'])
        
        print(f"No centroid found for cluster {cluster_id}")
        return None
    
    except mysql.connector.Error as e:
        print(f"Error fetching centroid: {e}")
        return None
        
    finally:
        cursor.close()
        connection.close()



def update_user_location(user_id, location, latitude, longitude):
    conn = get_connection()
    cursor = conn.cursor()

    # Update the user's location, latitude, and longitude in the database
    query = """
        UPDATE users
        SET location = %s, latitude = %s, longitude = %s
        WHERE user_id = %s
    """
    cursor.execute(query, (location, latitude, longitude, user_id))

    # Commit the changes
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    print(f"Updated User {user_id} location: {location}, {latitude}, {longitude}")



