# multi_store_scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
from sqlalchemy import create_engine, text
from Clustering.cluster_manager import ClusterManager
from backend.Algorithms.Dijkstra import Modified_Dijkstra
from concurrent.futures import ThreadPoolExecutor
'''
from Clustering.db_methods import update_cluster_id
from Clustering.db_methods import get_active_stores
from Clustering.db_methods import get_order_time
from Clustering.db_methods import reset_clusters
from Clustering.db_methods import update_cluster
from Clustering.db_methods import get_items_below_capacity
from Clustering.db_methods import get_users_in_radius
from Clustering.db_methods import get_store_coordinates
from Clustering.db_methods import update_combined_orders_in_db
from Clustering.db_methods import get_price_for_store
from Clustering.db_methods import update_final_price
'''
from Clustering.db_methods import DatabaseManager
import mysql.connector
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import threading
from pytz import timezone
from geopy.distance import geodesic
from time import sleep
import signal


version = "V1"
radius = 1.2

show_map = False
reset_clusters = False


def get_connection():
    try:
        return mysql.connector.connect(
            host="turntable.proxy.rlwy.net",
            user="root", 
            password="QidNZDIznmxgXewmxVnbzMVkFVZoyHZs",  
            database="railway",
            port=21931,
            connection_timeout=30,
            autocommit=True
        )
    except Exception as e:
        print(f"Error creating database connection: {e}")
        return None

class MultiStoreDeliveryScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.db_manager = DatabaseManager()
        self.setup_scheduler()
        self.stores_clusters_map = {}
        self.connection = get_connection()
        
    def setup_scheduler(self):
        # Morning clustering job at 9 AM
        self.scheduler.add_job(
            self.process_all_stores_morning,
            CronTrigger(hour=13, minute=8,timezone=timezone('Asia/Jerusalem'))
            
        )
        
        # Evening processing job at 9 PM
        self.scheduler.add_job(
            self.process_all_stores_evening,
            CronTrigger(hour=13, minute=12,timezone=timezone('Asia/Jerusalem'))
        )
    
    def check_connection(self):
        """Check if connection is alive, reconnect if necessary"""
        if self.connection is None or not self.connection.is_connected():
            self.connection = get_connection()
            return self.connection
            
        try:
            # Try a simple query to check connection
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return self.connection
        except mysql.connector.Error:
            # Connection is lost, create a new one
            try:
                self.connection.close()
            except:
                pass
            self.connection = get_connection()
            return self.connection
    
    
    def process_store_morning(self, store: Dict):
        """Process morning clustering for a single store"""
    
        print("processing morning stores")
        try:
            
            # Ensure connection is valid
            self.connection = self.check_connection()
            if self.connection is None:
                raise Exception("Could not establish database connection")
            
            store_id = store['store_id']
            print(f"Processing morning clustering for store {store_id}")
            
            # Initialize clustering with store-specific parameters
            clustering = ClusterManager(radius,store['total_capacity'],store_id,self.db_manager,self.connection)

            self.stores_clusters_map[store_id] = clustering

            store_coordinates = clustering.db_manager.get_store_coordinates(self.connection,store_id)
            print(f"Store coordinates for store {store_id}: {store_coordinates}")

            if store_coordinates is None:
                raise Exception(f"store{store_id} location not available!")
            
            # Create clusters for this store's orders
            clustering.build_clusters()

            if not clustering.clusters:
                print(f"No clusters were created for store {store_id}")
                return
            if show_map:
                clustering.create_map()
            # Update database with cluster assignments

            '''
            for cluster in clustering.clusters:
                price = self.calculate_price(cluster,store_id,self.connection)
                print(f"cluster coordinates: {cluster.coordinates}")
                self.db_manager.update_cluster(self.connection,store_id, cluster.id, cluster.coordinates, len(cluster.orders),price)
                for req_id in cluster.orders:
                    self.db_manager.update_cluster_id(self.connection,req_id,cluster.id)
                    self.db_manager.update_final_price(self.connection,req_id,price)
            '''
            
            
            '''
            available_clusters = []
            for cluster in clustering.clusters:
                if cluster.total_capacity < store['total_capacity']:
                    available_clusters.append(cluster)          
            
            for cluster in available_clusters:
                # Get users within the same radius of the cluster
                users_in_radius = self.db_manager.get_users_in_radius(connection,cluster.coordinates, radius)
                
                # Fetch items from the items table that match the capacity left in the cluster
                items_in_cluster = self.db_manager.get_items_below_capacity(connection,cluster.total_capacity)
            '''    
            
        except Exception as e:
            print(f"Error processing store {store_id} morning clustering: {e}")
            # Implement error handling and notifications
            import traceback
            print(f"Error processing store {store_id} morning clustering: {str(e)}")
            print(traceback.format_exc()) # Print the full traceback for debugging
    
    def process_store_evening(self, store: Dict):
        """Process evening routing for a single store"""
        
        for key in self.stores_clusters_map.keys():
            print(key)
        try:
            
            # Ensure connection is valid
            connection = self.check_connection()
            if connection is None:
                raise Exception("Could not establish database connection")
            
            store_id = store['store_id']
            print(f"Processing evening routing for store {store_id}")
            
            #fetch clusters and add new requests to clusters
            if store_id not in self.stores_clusters_map.keys():
                clustering = ClusterManager(radius,store['total_capacity'],store_id,self.db_manager,self.connection)
                
            
            else:
                clustering = self.stores_clusters_map[store_id]
                print("found the clsuter manager!!!!!!!")
                for cluster in clustering.clusters:
                    print(f"cluster id: {cluster.id}")
                    print(f"cluster capacity{cluster.total_capacity}")
                
            clustering.fetch_clusters()
            
            store_coordinates = self.db_manager.get_store_coordinates(self.connection,store_id)
            print(store_coordinates)
            if store_coordinates is None:
                raise Exception(f"Store {store_id} location not available!")
            
            #check clusters capacity and wait time and only send relevant clusters to dijkstra
            cap = store['total_capacity']
            ready_clusters = self.check_cluster_capacity_and_time(clustering.clusters,cap,self.connection)
            
            dijk = Modified_Dijkstra(ready_clusters, cap, store_coordinates, version)
            orders = dijk.get_orders()
            
            for l in orders:
                print(list(l))
            
            #TODO: from orders make orders from cluster id send to stores and show to users in front end
            self.db_manager.update_combined_orders_in_db(self.connection,orders,clustering.clusters)
            #TODO: implement pricing method, update delivery price in DB and show for user in frontend
            for cluster in clustering.clusters:
                price = self.calculate_price(cluster,store_id,self.connection)
                for req_id in cluster.orders:
                    self.db_manager.update_final_price(self.connection,req_id,price)

            #reset clusters table in DB
            if reset_clusters:
                self.db_manager.reset_clusters(self.connection)
            del self.stores_clusters_map[store_id]
            
        except Exception as e:
            print(f"Error processing store {store_id} evening routing: {e}")
            # Implement error handling and notifications
    
    def check_cluster_capacity_and_time(self,clusters, max_capacity,connection):
        time_has_run_out = False
        send_clusters = []
        
        try:
            #ensure connection is valid
            self.connection = self.check_connection()
            if connection is None:
                raise Exception("Could not establish database connection")
        except Exception as e:
            print(e)
        
        for cluster in clusters:
            print("im here!")
            print(cluster.total_capacity)
            if not cluster.orders:
                continue
            if cluster.total_capacity < max_capacity/3:
                for order in cluster.orders:
                    time_stamp, max_wait = self.db_manager.get_order_time(connection,order)
                    if time_stamp is None or max_wait is None:
                        print(f"Skipping order {order} due to missing time_stamp or max_wait")
                        continue  # Skip this order safely
                    print("get order time function is ok")
                    if not self.is_today_or_future(time_stamp,max_wait):
                        print("time func is ok")
                        time_has_run_out = True
                        break
                if time_has_run_out:
                    send_clusters.append(cluster)
                    time_has_run_out = False
            else:
                send_clusters.append(cluster)
        return send_clusters
                         
    def calculate_price(self,cluster,store,connection):
        
        try:
            #ensure connection is valid
            self.connection = self.check_connection()
            if connection is None:
                raise Exception("Could not establish database connection")
        except Exception as e:
            print(e)
        
        price_per_km = float(self.db_manager.get_price_for_store(self.connection,store))

        store_coordinates = self.db_manager.get_store_coordinates(self.connection, store)
        print(f"DEBUG: Distance Calculation - Cluster {cluster.id} coordinates: {cluster.coordinates}, Store {store} coordinates: {store_coordinates}")


        dist = geodesic(cluster.coordinates,store_coordinates).km
        print(f"DEBUG: Distance Calculation - Cluster {cluster.id} coordinates: {cluster.coordinates}, Store {store} coordinates: {self.db_manager.get_store_coordinates(self.connection, store)}")

        number_of_participants = len(cluster.orders)
        return (price_per_km*dist)/number_of_participants
    
    def is_today_or_future(self, timestamp, days: int) -> bool:
        # If timestamp is a string, convert it to a datetime object
        if isinstance(timestamp, str):
            original_date = datetime.strptime(timestamp, '%Y-%m-%d')
        else:
            original_date = timestamp  # Already a datetime object

        # Calculate the new date by adding days
        new_date = original_date + timedelta(days=days)

        # Get today's date (without the time part)
        today = datetime.today().date()

        # Compare the new date with today
        return new_date.date() > today                  
    
    

    def process_all_stores_morning(self):
        """Process morning clustering for all stores"""
        print("in Process all stores morning!")
        
        if self.connection is None:
            self.connection = get_connection()
            '''
            print("Error: Could not establish database connection for morning processing")
            return
            '''
        try:
            stores = self.db_manager.get_active_stores(self.connection)
            
            for store in stores:
                self.process_store_morning(store)
                # Ensure connection is still valid
                self.connection = self.check_connection()
                
        except Exception as e:
            print(f"Error in process_all_stores_morning: {e}")
            import traceback
            print(traceback.format_exc())
        finally:
        
                self.connection.close()
                self.connection = None
        
    
    def process_all_stores_evening(self):
        """Process evening routing for all stores"""
        
        if self.connection is None:
            self.connection = get_connection()
            '''
            print("Error: Could not establish database connection for evening processing")
            return
            '''
            
        try:
            stores = self.db_manager.get_active_stores(self.connection)
            
            for store in stores:
                self.process_store_evening(store)
                # Ensure connection is still valid
                self.connection = self.check_connection()
                
        except Exception as e:
            print(f"Error in process_all_stores_evening: {e}")
            import traceback
            print(traceback.format_exc())
        finally:
            try:
                if self.connection:
                    self.connection.close()
            except:
                pass

    
    def start(self):
        self.scheduler.start()
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
    def shutdown(self, signum, frame):
        print("Scheduler shutting down...")
        self.stop()
        exit(0)
        
    def stop(self):
        self.scheduler.shutdown()

    

# Usage example:
if __name__ == "__main__":
    scheduler = MultiStoreDeliveryScheduler()
    scheduler.start()
    
    try:
        stop_event = threading.Event()
        stop_event.wait()  # Blocks until manually stopped
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler shutting down...")
        scheduler.stop()