# database_manager.py
import mysql.connector

class DatabaseManager:
    def __init__(self):
        pass  # No persistent connection in this approach

    def execute_query(self, connection, query, params=None, fetchone=False, fetchall=False, commit=False):
        """Executes a query using a provided connection and cursor."""
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params or {})

            if fetchone:
                result = cursor.fetchone()
            elif fetchall:
                result = cursor.fetchall()
            else:
                result = None

            if commit:
                connection.commit()

            return result

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            connection.rollback()
            return None

        finally:
            cursor.close()

    def get_active_stores(self, connection):
        query = """
        SELECT store_id, store_name, warehouse_location, total_capacity, latitude, longitude
        FROM stores
        WHERE store_id IN (SELECT store_id FROM active_requests);
        """
        return self.execute_query(connection, query, fetchall=True)

    def get_store_coordinates(self, connection, store_id):
        query = "SELECT latitude, longitude FROM stores WHERE store_id = %s"
        result = self.execute_query(connection, query, (store_id,), fetchone=True)
        if result:
            # Ensure we get valid latitude and longitude values
            latitude = float(result["latitude"])
            longitude = float(result["longitude"])
            return (latitude, longitude)
        return None

    def update_cluster_id(self, connection, req_id, cluster_id):
        try:
            query = """UPDATE active_requests SET cluster_id = %s WHERE req_id = %s"""
            self.execute_query(connection, query, (cluster_id, req_id), commit=True)
            print(f"Updated cluster_id to {cluster_id} for request {req_id}")
        except mysql.connector.Error as e:
            print(f"Error updating cluster_id: {e}")
            connection.rollback()

    def update_final_price(self, connection, request_id, price):
        try:
            query = """UPDATE active_requests SET final_delivery_fee = %s WHERE req_id = %s"""
            self.execute_query(connection, query, (price, request_id), commit=True)
            print(f"Updated final price to {price} for request {request_id}")  # Add logging
        except mysql.connector.Error as e:
            print(f"Error updating final price: {e}")
            connection.rollback()

    def update_order_status(self,connection,req_id,status):

        query = "UPDATE active_requests SET status = %s WHERE req_id = %s"
        self.execute_query(connection, query, (status, req_id), commit=True)
    
    def reset_clusters(self, connection):
        query = """TRUNCATE TABLE clusters"""
        self.execute_query(connection, query, commit=True)

    def update_cluster(self,connection,store_id,id, coordinates,partners_number,expected_price):
        """Update cluster's latitude and longitude in the clusters table."""
        latitude, longitude = coordinates[0],coordinates[1]

        
        try:
            print(f"Updating cluster {id} with Latitude: {latitude}, Longitude: {longitude}")
            
            query = """INSERT INTO clusters (store_id, cluster_id, latitude, longitude, partners_number, expected_price) 
                    VALUES (%s, %s, %s,%s,%s,%s) 
                    ON DUPLICATE KEY UPDATE latitude = VALUES(latitude), longitude = VALUES(longitude),partners_number = VALUES(partners_number),expected_price = VALUES(expected_price)"""
            
            self.execute_query(connection, query, (store_id,id, latitude, longitude,partners_number,expected_price), commit=True)
            
            print(f"Successfully updated cluster {id} with latitude={latitude}, longitude={longitude}")
            
        except (mysql.connector.Error, ValueError) as e:
            print(f"Error updating cluster coordinates: {e}")
            connection.rollback()

    def get_price_for_store(self, connection, store_id):
        query = """SELECT delivery_fee FROM stores WHERE store_id = %s"""
        result = self.execute_query(connection, query, (store_id,), fetchone=True)
        return result['delivery_fee'] if result else None
    
    def get_requests(self,connection,store_id):
        """get all requests for the specific store"""
        query = """SELECT req_id, user_id, cluster_id FROM active_requests WHERE store_id = %s and status = 0"""
        return self.execute_query(connection, query, (store_id,), fetchall=True)
        
    def get_order_time(self, connection, request_id):
        query = """SELECT time_stamp, max_wait FROM active_requests WHERE req_id = %s"""
        result = self.execute_query(connection, query, (request_id,), fetchone=True)
        if result is None:
            print(f"Error: No order found with req_id {request_id}")
            return None, None  # Return safe values instead of crashing

        return result['time_stamp'],result['max_wait']
    
    def get_clusters(self,connection,store_id):
        query = """SELECT req_id, cluster_id, user_id FROM active_requests WHERE store_id = %s"""
        return self.execute_query(connection, query, (store_id,), fetchall=True)
    
    def get_order_capacity(self,connection,order_id):
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
            result = self.execute_query(connection, query, (order_id,), fetchone=True)
            if result:
                return int(result['total_capacity'])  # Convert to integer capacity
            return 0  # Default capacity if not found
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            return 0

    def get_all_users(self,connection):
        query = "SELECT * FROM users"
        return self.execute_query(connection, query, fetchall=True)
    
    def get_all_orders(self,connection,store_id):
        query = "SELECT req_id, user_id FROM active_requests WHERE store_id = %s and status = 0"
        result = self.execute_query(connection, query, (store_id,), fetchall=True)
        return result
    
    def get_user_id_from_order(self,connection,order_id):
        query = "SELECT user_id FROM active_requests where req_id = %s"
        result = self.execute_query(connection, query, (order_id,), fetchone=True)
        if result: return result['user_id'] 
        return None

    def get_address_for_user(self,connection,user_id):
        query = "SELECT location FROM users WHERE user_id = %s"
        result = self.execute_query(connection, query, (user_id,), fetchone=True)
        return result[0] if result else None
    
    def get_user_coordinates(self, connection, user_id):
        query = "SELECT latitude, longitude FROM users WHERE user_id = %s"
        result = self.execute_query(connection, query, (user_id,), fetchone=True)
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
    
    def get_items_below_capacity(self,connection,max_capacity):
        query = "SELECT item_id, capacity FROM items WHERE capacity <= %s"
        result = self.execute_query(connection, query, (max_capacity,), fetchall=True)
        return result
    
    def get_users_in_radius(self,connection,center_coordinates, radius_km):
        lat,lon = center_coordinates
        query = """
        SELECT user_id
        FROM users
        WHERE ST_Distance_Sphere(
            point(longitude, latitude),
            point(%s, %s)
        ) <= %s * 1000
    """
        result = self.execute_query(connection, query, (lon, lat, radius_km), fetchall=True)
        return result
    
    def get_cluster_centroid(self,connection,cluster_id):
        """Retrieve the centroid as a tuple using ST_X and ST_Y."""
        
        query = """SELECT ST_X(centroid) AS x, ST_Y(centroid) AS y 
                    FROM clusters WHERE cluster_id = %s"""
        result = self.execute_query(connection, query, (cluster_id,), fetchone=True)
        if result and result['x'] is not None and result['y'] is not None:
            return (result['x'], result['y'])
        
    def update_final_price(self,connection,req_id,price):
        """update the final price for the specific request"""
        
        try:
            query = """UPDATE active_requests SET final_delivery_fee = %s WHERE req_id = %s"""
            self.execute_query(connection, query, (price, req_id), commit=True)
            print(f"Updated final price to {price} for request {req_id}")  # Add logging
        except mysql.connector.Error as e:
            print(f"Error updating final price: {e}")
            connection.rollback()  # Rollback on error

    def update_combined_orders_in_db(self,connection,orders,clusters):

        for order in orders:
            comb_ord_id = self.get_last_combined_order_id(connection) + 1
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
                        self.update_active_order(ord,comb_ord_id,connection)
                        self.update_order_status(ord,1,connection)
                        self.update_date_of_proccessing(ord,connection)

    def get_last_combined_order_id(self,connection):
        # Get the last order_id from the table (or start from 1 if empty)
        query = "SELECT MAX(order_id) FROM combined_orders"
        result=self.execute_query(connection, query, fetchone=True)
        last_order_id = result[0]  # Fetch the max order_id
        last_order_id = last_order_id if last_order_id is not None else 0  # Avoid None issue
        return last_order_id

    def update_active_order(self,connection,req_id,comb_ord_id):


        query = "INSERT INTO combined_orders (order_id, req_id) VALUES (%s, %s)"

        self.execute_query(connection, query, (comb_ord_id, req_id), commit=True)

    def update_date_of_proccessing(self,ord,connection):
        query = "UPDATE active_requests SET proccess_date = CURDATE() WHERE req_id = %s"
        self.execute_query(connection, query, (ord,), commit=True)