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
from geopy.geocoders import Nominatim
import threading
from pytz import timezone
from geopy.distance import geodesic
from time import sleep
import signal


version = "V1"
radius = 1

class MultiStoreDeliveryScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.setup_scheduler()
        self.stores_clusters_map = {}
        
    def setup_scheduler(self):
        # Morning clustering job at 9 AM
        self.scheduler.add_job(
            self.process_all_stores_morning,
            CronTrigger(hour=22, minute=23,timezone=timezone('Asia/Jerusalem'))
            
        )
        
        # Evening processing job at 9 PM
        self.scheduler.add_job(
            self.process_all_stores_evening,
            CronTrigger(hour=22, minute=30,timezone=timezone('Asia/Jerusalem'))
        )
    
    
    
    def process_store_morning(self, store: Dict):
        """Process morning clustering for a single store"""
        print("processing morning stores")
        try:
            store_id = store['store_id']
            print(f"Processing morning clustering for store {store_id}")
            
            #print(store)
            # Initialize clustering with store-specific parameters
            clustering = ClusterManager(radius,store['total_capacity'],store_id)
            self.stores_clusters_map[store_id] = clustering
            #geolocator = Nominatim(user_agent="multi_store_scheduler")
            #location = geolocator.geocode(store['warehouse_location'])
            #location  = (store['latitude'],store['longitude']) if store['latitude'] and store['longitude'] else None
            #if location is None:
             #   raise Exception("Warehouse location not available!") 
            
            #store_location = (location.latitude,location.longitude)
            #store_location = location

            store_coordinates = get_store_coordinates(store_id)
            if store_coordinates is None:
                raise Exception(f"store{store_id} location not available!")
            
            # Create clusters for this store's orders
            clustering.build_clusters()
            
            # Update database with cluster assignments
            for cluster in clustering.clusters:
                update_cluster(cluster.id, cluster.coordinates)
                price = self.calculate_price(cluster,store_id)
                for req_id in cluster.orders:
                    update_cluster_id(req_id,cluster.id)
                    update_final_price(req_id,price)
            
            #clustering.create_map()
            available_clusters = []
            for cluster in clustering.clusters:
                if cluster.total_capacity < store['total_capacity']:
                    available_clusters.append(cluster)          
            # Notify users about clustering results
            #TODO: check which clusters are not at full capacity, present stores with items available in each cluster
            # Notify users about available clusters and discounts
            for cluster in available_clusters:
                # Get users within the same radius of the cluster
                users_in_radius = get_users_in_radius(cluster.coordinates, radius)
                
                # Fetch items from the items table that match the capacity left in the cluster
                items_in_cluster = get_items_below_capacity(cluster.total_capacity)
                
                # Prepare the notification message
                
                '''
                # Send notifications to users
                for user in users_in_radius:
                    self.notify_user(user['email'], message)
                 '''  
            #notify users by email + show in frontend
            
        except Exception as e:
            print(f"Error processing store {store_id} morning clustering: {e}")
            # Implement error handling and notifications
    
    def process_store_evening(self, store: Dict):
        """Process evening routing for a single store"""
        for key in self.stores_clusters_map.keys():
            print(key)
        try:
            store_id = store['store_id']
            print(f"Processing evening routing for store {store_id}")
            
            #fetch clusters and add new requests to clusters
            if store_id not in self.stores_clusters_map.keys():
                clustering = ClusterManager(radius,store['total_capacity'],store_id)
                
            
            else:
                clustering = self.stores_clusters_map[store_id]
                print("found the clsuter manager!!!!!!!")
                for cluster in clustering.clusters:
                    print(f"cluster id: {cluster.id}")
                    print(f"cluster capacity{cluster.total_capacity}")
                
                    
                    
            
            #print(clustering.global_cluster_id)
            clustering.fetch_clusters()
            
            
            #get clusters with cluster_capacity < max_capacity\3 and all orders still have time 
            #TODO: implement this functionality
            
            #run dijkstra on clusters
            #sleep(1)  
            store_coordinates = get_store_coordinates(store_id)
            print(store_coordinates)
            if store_coordinates is None:
                raise Exception(f"Store {store_id} location not available!")
            
            #check clusters capacity and wait time and only send relevant clusters to dijkstra
            cap = store['total_capacity']
            ready_clusters = self.check_cluster_capacity_and_time(clustering.clusters,cap)
            
            dijk = Modified_Dijkstra(ready_clusters, cap, store_coordinates, version)
            orders = dijk.get_orders()
            
            for l in orders:
                print(list(l))
            
            #TODO: from orders make orders from cluster id send to stores and show to users in front end
            update_combined_orders_in_db(orders,clustering.clusters)
            #TODO: implement pricing method, update delivery price in DB and show for user in frontend
            for cluster in clustering.clusters:
                price = self.calculate_price(cluster,store_id)
                for req_id in cluster.orders:
                    update_final_price(req_id,price)

            #reset clusters table in DB
            reset_clusters()
            del self.stores_clusters_map[store_id]
            
        except Exception as e:
            print(f"Error processing store {store_id} evening routing: {e}")
            # Implement error handling and notifications
    
    def check_cluster_capacity_and_time(self,clusters, max_capacity):
        time_has_run_out = False
        send_clusters = []
        for cluster in clusters:
            print("im here!")
            print(cluster.total_capacity)
            if not cluster.orders:
                continue
            if cluster.total_capacity < max_capacity/3:
                for order in cluster.orders:
                    time_stamp, max_wait = get_order_time(order)
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
                         
    def calculate_price(self,cluster,store):
        price_per_km = float(get_price_for_store(store))
        dist = geodesic(cluster.coordinates,get_store_coordinates(store)).km
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
        """Process morning clustering for all stores in parallel"""
        print("in Process all stores morning!")
        stores = get_active_stores()
        
        for store in stores:
            self.process_store_morning(store)
            #sleep(1)  # Ensure at least 1 second between requests
        
        #with ThreadPoolExecutor(max_workers=min(len(stores), 10)) as executor:
        #    executor.map(self.process_store_morning, stores)
    
    def process_all_stores_evening(self):
        """Process evening routing for all stores in parallel"""
        stores = get_active_stores()
        for store in stores:
            self.process_store_evening(store)
            #sleep(1)  # Ensure at least 1 second between requests


    
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