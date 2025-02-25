# database_manager.py
import mysql.connector

class DatabaseManager:
    def __init__(self):
        self.connection = self.get_connection()

    def get_connection(self):
        """Ensures a valid database connection."""
        try:
            connection = mysql.connector.connect(
                host="turntable.proxy.rlwy.net",
                user="root", 
                password="QidNZDIznmxgXewmxVnbzMVkFVZoyHZs",
                database="railway",
                port=21931,
                connection_timeout=28800,
                autocommit=True
            )
            print("✅ New DB connection established.")
            return connection
        except Exception as e:
            print(f"❌ Error creating database connection: {e}")
            return None

    def check_connection(self):
        """Check if connection is alive, reconnect if necessary."""
        try:
            if self.connection is None or not self.connection.is_connected():
                print("🔄 Reconnecting to DB...")
                self.connection = self.get_connection()
            return self.connection
        except Exception as e:
            print(f"❌ Connection check failed: {e}")
            return None

    def execute_query(self, query, params=None, fetchone=False, fetchall=False, commit=False):
        """Executes a query using a provided connection and cursor."""
        self.connection = self.check_connection()
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params or {})

            if fetchone:
                result = cursor.fetchone()
            elif fetchall:
                result = cursor.fetchall()
            else:
                result = None

            if commit:
                self.connection.commit()
            return result

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
            return None

        finally:
            cursor.close()

    def get_active_stores(self):
        self.connection = self.check_connection()
        query = """
        SELECT store_id, store_name, warehouse_location, total_capacity, latitude, longitude
        FROM stores
        WHERE store_id IN (SELECT store_id FROM active_requests);
        """
        return self.execute_query(query, fetchall=True)

    def get_store_coordinates(self, store_id):
        self.connection = self.check_connection()
        query = "SELECT latitude, longitude FROM stores WHERE store_id = %s"
        result = self.execute_query(query, (store_id,), fetchone=True)
        if result:
            # Ensure we get valid latitude and longitude values
            latitude = float(result["latitude"])
            longitude = float(result["longitude"])
            return (latitude, longitude)
        return None

    def update_cluster_id(self, req_id, cluster_id):
        self.connection = self.check_connection()
        try:
            query = """UPDATE active_requests SET cluster_id = %s WHERE req_id = %s"""
            self.execute_query( query, (cluster_id, req_id), commit=True)
            print(f"Updated cluster_id to {cluster_id} for request {req_id}")
        except mysql.connector.Error as e:
            print(f"Error updating cluster_id: {e}")
            self.connection.rollback()

    def update_final_price(self, request_id, price):
        self.connection = self.check_connection()
        try:
            query = """UPDATE active_requests SET final_delivery_fee = %s WHERE req_id = %s"""
            self.execute_query(query, (price, request_id), commit=True)
            print(f"Updated final price to {price} for request {request_id}")  # Add logging
        except mysql.connector.Error as e:
            print(f"Error updating final price: {e}")
            self.connection.rollback()

    def update_order_status(self,req_id,status):
        self.connection = self.check_connection()
        query = "UPDATE active_requests SET status = %s WHERE req_id = %s"
        self.execute_query(query, (status, req_id), commit=True)
    
    def reset_clusters(self):
        self.connection = self.check_connection()
        query = """TRUNCATE TABLE clusters"""
        self.execute_query(query, commit=True)

    def update_cluster(self,store_id,id, coordinates,partners_number,expected_price):
        """Update cluster's latitude and longitude in the clusters table."""
        self.connection = self.check_connection()
        latitude, longitude = coordinates[0],coordinates[1]

        
        try:
            print(f"Updating cluster {id} with Latitude: {latitude}, Longitude: {longitude}")
            
            query = """INSERT INTO clusters (store_id, cluster_id, latitude, longitude, partners_number, expected_price) 
                    VALUES (%s, %s, %s,%s,%s,%s) 
                    ON DUPLICATE KEY UPDATE latitude = VALUES(latitude), longitude = VALUES(longitude),partners_number = VALUES(partners_number),expected_price = VALUES(expected_price)"""
            
            self.execute_query(query, (store_id,id, latitude, longitude,partners_number,expected_price), commit=True)
            
            print(f"Successfully updated cluster {id} with latitude={latitude}, longitude={longitude}")
            
        except (mysql.connector.Error, ValueError) as e:
            print(f"Error updating cluster coordinates: {e}")
            self.connection.rollback()

    def get_price_for_store(self, store_id):
        self.connection = self.check_connection()   
        query = """SELECT delivery_fee FROM stores WHERE store_id = %s"""
        result = self.execute_query(query, (store_id,), fetchone=True)
        return result['delivery_fee'] if result else None
    
    def get_requests(self,store_id):
        """get all requests for the specific store"""
        self.connection = self.check_connection()
        query = """SELECT req_id, user_id, cluster_id FROM active_requests WHERE store_id = %s and status = 0"""
        return self.execute_query(query, (store_id,), fetchall=True)
        
    def get_order_time(self, request_id):
        self.connection = self.check_connection()
        query = """SELECT time_stamp, max_wait FROM active_requests WHERE req_id = %s"""
        result = self.execute_query(query, (request_id,), fetchone=True)
        if result is None:
            print(f"Error: No order found with req_id {request_id}")
            return None, None  # Return safe values instead of crashing

        return result['time_stamp'],result['max_wait']
    
    def get_clusters(self,store_id):
        self.connection = self.check_connection()
        query = """SELECT req_id, cluster_id, user_id FROM active_requests WHERE store_id = %s"""
        return self.execute_query(query, (store_id,), fetchall=True)
    
    def get_order_capacity(self,order_id):
        self.connection = self.check_connection()
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
            result = self.execute_query(query, (order_id,), fetchone=True)
            if result:
                return int(result['total_capacity'])  # Convert to integer capacity
            return 0  # Default capacity if not found
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            return 0

    def get_all_users(self):
        self.connection = self.check_connection()
        query = "SELECT * FROM users"
        return self.execute_query(query, fetchall=True)
    
    def get_all_orders(self,store_id):
        self.connection = self.check_connection()
        query = "SELECT req_id, user_id FROM active_requests WHERE store_id = %s and status = 0"
        result = self.execute_query(query, (store_id,), fetchall=True)
        return result
    
    def get_user_id_from_order(self,order_id):
        self.connection = self.check_connection()
        query = "SELECT user_id FROM active_requests where req_id = %s"
        result = self.execute_query(query, (order_id,), fetchone=True)
        if result: return result['user_id'] 
        return None

    def get_address_for_user(self,user_id):
        self.connection = self.check_connection()
        query = "SELECT location FROM users WHERE user_id = %s"
        result = self.execute_query(query, (user_id,), fetchone=True)
        return result[0] if result else None
    
    def get_user_coordinates(self, user_id):
        self.connection = self.check_connection()
        query = "SELECT latitude, longitude FROM users WHERE user_id = %s"
        result = self.execute_query(query, (user_id,), fetchone=True)
        print(f"DEBUG - get_user_coordinates for user_id {user_id}: {result}")
        
        if result is None:
            print(f"No coordinates found for user {user_id}")
            return None
        
        try:
            # Make sure the latitude and longitude keys exist
            if 'latitude' not in result or 'longitude' not in result:
                print(f"ERROR: Result doesn't contain latitude/longitude keys: {result}")
                return None
                
            # Check for null values
            if result['latitude'] is None or result['longitude'] is None:
                print(f"User {user_id} has null coordinates: lat={result['latitude']}, lon={result['longitude']}")
                return None
                
            # Return as a tuple for the existing code that expects (latitude, longitude)
            return (float(result['latitude']), float(result['longitude']))
        except Exception as e:
            print(f"Exception in get_user_coordinates: {str(e)}")
            print(f"Result type: {type(result)}, Result: {result}")
            return None
    
    def get_items_below_capacity(self,max_capacity):
        self.connection = self.check_connection()
        query = "SELECT item_id, capacity FROM items WHERE capacity <= %s"
        result = self.execute_query(query, (max_capacity,), fetchall=True)
        return result
    
    def get_users_in_radius(self,center_coordinates, radius_km):
        self.connection = self.check_connection()
        lat,lon = center_coordinates
        query = """
        SELECT user_id
        FROM users
        WHERE ST_Distance_Sphere(
            point(longitude, latitude),
            point(%s, %s)
        ) <= %s * 1000
    """
        result = self.execute_query(query, (lon, lat, radius_km), fetchall=True)
        return result
    
    def get_cluster_centroid(self,cluster_id):
        self.connection = self.check_connection()
        """Retrieve the centroid as a tuple using ST_X and ST_Y."""
        
        query = """SELECT ST_X(centroid) AS x, ST_Y(centroid) AS y 
                    FROM clusters WHERE cluster_id = %s"""
        result = self.execute_query( query, (cluster_id,), fetchone=True)
        if result and result['x'] is not None and result['y'] is not None:
            return (result['x'], result['y'])
        
    def update_final_price(self,req_id,price):
        self.connection = self.check_connection()
        """update the final price for the specific request"""
        
        try:
            query = """UPDATE active_requests SET final_delivery_fee = %s WHERE req_id = %s"""
            self.execute_query(query, (price, req_id), commit=True)
            print(f"Updated final price to {price} for request {req_id}")  # Add logging
        except mysql.connector.Error as e:
            print(f"Error updating final price: {e}")
            self.connection.rollback()  # Rollback on error

    def update_combined_orders_in_db(self,orders,clusters):

        self.connection = self.check_connection()

        for order in orders:
            comb_ord_id = self.get_last_combined_order_id() + 1
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
                        self.update_active_order(ord,comb_ord_id)
                        self.update_order_status(ord,1)
                        self.update_date_of_proccessing(ord)

    def get_last_combined_order_id(self):
        self.connection = self.check_connection()
        # Get the last order_id from the table (or start from 1 if empty)
        query = "SELECT MAX(order_id) FROM combined_orders"
        result=self.execute_query(query, fetchone=True)
        last_order_id = result[0]  # Fetch the max order_id
        last_order_id = last_order_id if last_order_id is not None else 0  # Avoid None issue
        return last_order_id

    def update_active_order(self,req_id,comb_ord_id):
        self.connection = self.check_connection()


        query = "INSERT INTO combined_orders (order_id, req_id) VALUES (%s, %s)"

        self.execute_query(query, (comb_ord_id, req_id), commit=True)

    def update_date_of_proccessing(self,ord):
        self.connection = self.check_connection()
        query = "UPDATE active_requests SET proccess_date = CURDATE() WHERE req_id = %s"
        self.execute_query( query, (ord,), commit=True)