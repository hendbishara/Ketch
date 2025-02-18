# multi_store_scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
from sqlalchemy import create_engine, text
from clustering import ClusteringAlgorithm
from dijkstra_v2 import DijkstraV2
from concurrent.futures import ThreadPoolExecutor

class MultiStoreDeliveryScheduler:
    def __init__(self, db_connection_string: str):
        self.engine = create_engine(db_connection_string)
        self.scheduler = BackgroundScheduler()
        self.setup_scheduler()
        
    def setup_scheduler(self):
        # Morning clustering job at 9 AM
        self.scheduler.add_job(
            self.process_all_stores_morning,
            CronTrigger(hour=9, minute=0)
        )
        
        # Evening processing job at 9 PM
        self.scheduler.add_job(
            self.process_all_stores_evening,
            CronTrigger(hour=21, minute=0)
        )
    
    def get_active_stores(self) -> List[Dict]:
        """Get all active stores from the database"""
        query = """
        SELECT store_id, name, latitude, longitude 
        FROM stores 
        WHERE status = 'active'
        """
        with self.engine.connect() as conn:
            stores_df = pd.read_sql(query, conn)
            return stores_df.to_dict('records')
    
    def get_store_pending_orders(self, store_id: int) -> pd.DataFrame:
        """Get pending orders for a specific store"""
        query = """
        SELECT * FROM orders 
        WHERE store_id = :store_id 
        AND status = 'pending' 
        AND created_at >= CURRENT_DATE
        """
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn, params={'store_id': store_id})
    
    def process_store_morning(self, store: Dict):
        """Process morning clustering for a single store"""
        try:
            store_id = store['store_id']
            print(f"Processing morning clustering for store {store_id}")
            
            # Get pending orders for this store
            orders_df = self.get_store_pending_orders(store_id)
            
            if orders_df.empty:
                print(f"No pending orders for store {store_id}")
                return
            
            # Initialize clustering with store-specific parameters
            clustering = ClusteringAlgorithm()
            store_location = (store['latitude'], store['longitude'])
            
            # Create clusters for this store's orders
            clusters = clustering.create_clusters(
                orders_df,
                store_location=store_location
            )
            
            # Update database with cluster assignments
            for cluster in clusters:
                # Add store_id to cluster record
                self.update_cluster_status(cluster.id, {
                    'store_id': store_id,
                    'current_capacity': cluster.current_capacity,
                    'status': 'open' if cluster.has_capacity() else 'full'
                })
                
                # Update orders with cluster assignments
                for order_id in cluster.order_ids:
                    self.update_order_status(
                        order_id, 
                        'clustered', 
                        cluster.id,
                        store_id
                    )
            
            # Notify users about clustering results
            user_updates = [
                {
                    'user_id': order.user_id,
                    'order_id': order.id,
                    'store_id': store_id,
                    'status': 'clustered',
                    'cluster_id': order.cluster_id
                }
                for order in orders_df.itertuples()
            ]
            self.notify_users(user_updates)
            
        except Exception as e:
            print(f"Error processing store {store_id} morning clustering: {e}")
            # Implement error handling and notifications
    
    def process_store_evening(self, store: Dict):
        """Process evening routing for a single store"""
        try:
            store_id = store['store_id']
            print(f"Processing evening routing for store {store_id}")
            
            # Get all clusters for this store that meet criteria
            query = """
            SELECT c.*, COUNT(o.order_id) as order_count
            FROM clusters c
            JOIN orders o ON c.cluster_id = o.cluster_id
            WHERE c.store_id = :store_id
            AND o.status = 'clustered'
            GROUP BY c.cluster_id
            HAVING c.current_capacity > c.max_capacity/3
            """
            
            with self.engine.connect() as conn:
                clusters_df = pd.read_sql(query, conn, params={'store_id': store_id})
            
            store_location = (store['latitude'], store['longitude'])
            
            # Process each eligible cluster
            for cluster in clusters_df.itertuples():
                # Get cluster orders
                cluster_orders_query = """
                SELECT * FROM orders 
                WHERE cluster_id = :cluster_id 
                AND status = 'clustered'
                AND store_id = :store_id
                """
                with self.engine.connect() as conn:
                    cluster_orders = pd.read_sql(
                        cluster_orders_query, 
                        conn, 
                        params={
                            'cluster_id': cluster.cluster_id,
                            'store_id': store_id
                        }
                    )
                
                # Run Dijkstra V2 with store location
                dijkstra = DijkstraV2()
                optimized_routes = dijkstra.optimize_routes(
                    cluster_orders,
                    store_location=store_location
                )
                
                # Update orders with route information
                for route in optimized_routes:
                    for order in route.orders:
                        self.update_order_status(
                            order.id, 
                            'routed',
                            cluster.cluster_id,
                            store_id
                        )
                
                # Notify store about their orders
                self.notify_store(store_id, {
                    'cluster_id': cluster.cluster_id,
                    'routes': optimized_routes
                })
                
                # Notify users about their order status
                user_updates = [
                    {
                        'user_id': order.user_id,
                        'order_id': order.id,
                        'store_id': store_id,
                        'status': 'routed',
                        'estimated_delivery': route.estimated_delivery
                    }
                    for route in optimized_routes
                    for order in route.orders
                ]
                self.notify_users(user_updates)
                
        except Exception as e:
            print(f"Error processing store {store_id} evening routing: {e}")
            # Implement error handling and notifications
    
    def process_all_stores_morning(self):
        """Process morning clustering for all stores in parallel"""
        stores = self.get_active_stores()
        with ThreadPoolExecutor(max_workers=min(len(stores), 10)) as executor:
            executor.map(self.process_store_morning, stores)
    
    def process_all_stores_evening(self):
        """Process evening routing for all stores in parallel"""
        stores = self.get_active_stores()
        with ThreadPoolExecutor(max_workers=min(len(stores), 10)) as executor:
            executor.map(self.process_store_evening, stores)
    
    def start(self):
        self.scheduler.start()
        
    def stop(self):
        self.scheduler.shutdown()

# Database helper methods remain similar but add store_id
    def update_cluster_status(self, cluster_id: int, status: Dict):
        query = """
        UPDATE clusters 
        SET current_capacity = :current_capacity,
            status = :status,
            store_id = :store_id,
            last_updated = CURRENT_TIMESTAMP
        WHERE cluster_id = :cluster_id
        """
        with self.engine.connect() as conn:
            conn.execute(text(query), {
                'cluster_id': cluster_id,
                'current_capacity': status['current_capacity'],
                'status': status['status'],
                'store_id': status['store_id']
            })
            conn.commit()
    
    def update_order_status(self, order_id: int, status: str, cluster_id: int, store_id: int):
        query = """
        UPDATE orders 
        SET status = :status,
            cluster_id = :cluster_id,
            store_id = :store_id,
            last_updated = CURRENT_TIMESTAMP
        WHERE order_id = :order_id
        """
        with self.engine.connect() as conn:
            conn.execute(text(query), {
                'order_id': order_id,
                'status': status,
                'cluster_id': cluster_id,
                'store_id': store_id
            })
            conn.commit()

# Usage example:
if __name__ == "__main__":
    db_connection_string = "postgresql://user:password@localhost:5432/ketch_db"
    scheduler = MultiStoreDeliveryScheduler(db_connection_string)
    scheduler.start()