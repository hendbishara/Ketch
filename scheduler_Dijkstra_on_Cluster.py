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
from geopy.geocoders import Nominatim
import threading
from pytz import timezone
from geopy.distance import geodesic
from time import sleep


version = "V1"
radius = 1

class MultiStoreDeliveryScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.setup_scheduler()
        
    def setup_scheduler(self):
        # Morning clustering job at 9 AM
        self.scheduler.add_job(
            self.process_all_stores_morning,
            CronTrigger(hour=16, minute=46,timezone=timezone('Asia/Jerusalem'))
            
        )
        
        # Evening processing job at 9 PM
        self.scheduler.add_job(
            self.process_all_stores_evening,
            CronTrigger(hour=17, minute=7,timezone=timezone('Asia/Jerusalem'))
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
            geolocator = Nominatim(user_agent="multi_store_scheduler")
            location = geolocator.geocode(store['warehouse_location'])
            if location is None:
                raise Exception("Warehouse location not available!") 
            
            store_location = (location.latitude,location.longitude)
            
            # Create clusters for this store's orders
            clustering.build_clusters()
            
            # Update database with cluster assignments
            for cluster in clustering.clusters:
                update_cluster(cluster.id, cluster.coordinates)
                for req_id in cluster.orders:
                    update_cluster_id(req_id,cluster.id)
            
            clustering.create_map()            
            # Notify users about clustering results
            #TODO: check which clusters are not at full capacity, present stores with items available in each cluster
            
            #notify users by email + show in frontend
            
        except Exception as e:
            print(f"Error processing store {store_id} morning clustering: {e}")
            # Implement error handling and notifications
    
    def process_store_evening(self, store: Dict):
        """Process evening routing for a single store"""
        try:
            store_id = store['store_id']
            print(f"Processing evening routing for store {store_id}")
            
            #fetch clusters and add new requests to clusters
            clustering = ClusterManager(radius,store['total_capacity'],store_id)
            
            clustering.fetch_clusters()
            
            
            #get clusters with cluster_capacity < max_capacity\3 and all orders still have time 
            #TODO: implement this functionality
            
            #run dijkstra on clusters
            geolocator = Nominatim(user_agent="multi_store_scheduler")
            #sleep(1)  
            location = geolocator.geocode(store['warehouse_location'])

            if location:
                store_location = (location.latitude, location.longitude)
            else:
                print(f"Could not find location for store {store_id}")
                return
            
            clustering.create_map()
            
            #check clusters capacity and wait time and only send relevant clusters to dijkstra
            ready_clusters = self.check_cluster_capacity_and_time(store['total_capacity'])
            
            dijk = Modified_Dijkstra(ready_clusters,store['total_capacity'],store_location,version)
            
            orders = dijk.get_orders()
            
            for l in orders:
                print(list(l))
            
            #TODO: from orders make orders from cluster id send to stores and show to users in front end
            
            #TODO: implement pricing method, update delivery price in DB and show for user in frontend
            
            for l in orders:
                print(list(l))
            
            
            #reset clusters table in DB
            reset_clusters()
            
                
        except Exception as e:
            print(f"Error processing store {store_id} evening routing: {e}")
            # Implement error handling and notifications
    
    
    def check_cluster_capacity_and_time(self,clusters, max_capacity):
        time_has_run_out = False
        send_clusters = []
        for cluster in clusters:
            if cluster.total_capacity < max_capacity/3:
                for order in cluster.orders:
                    time_stamp, max_wait = get_order_time(order)
                    if not self.is_today_or_future(time_stamp,max_wait):
                        time_has_run_out = True
                        break
                if time_has_run_out:
                    send_clusters.append(cluster)
                    time_has_run_out = False
            else:
                send_clusters.append(cluster)
        return send_clusters
                        
    
    def is_today_or_future(self, timestamp: str, days: int) -> bool:
        # Parse the input timestamp (assuming 'YYYY-MM-DD' format)
        original_date = datetime.strptime(timestamp, '%Y-%m-%d')
        
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