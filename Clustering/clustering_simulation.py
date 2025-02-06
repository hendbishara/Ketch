import random
from geopy.distance import geodesic
import db_methods
from cluster_manager import ClusterManager  # Assuming the ClusterManager is in a file named cluster_manager.py

class Simulation:
    def __init__(self, cluster_manager):
        self.cluster_manager = cluster_manager

    def generate_random_order(self):
        # Generate random latitude and longitude (Example: Random location within a city)
        random_lat = random.uniform(40.0, 42.0)  # Random latitude between 40 and 42
        random_lon = random.uniform(-74.0, -73.0)  # Random longitude between -74 and -73
        return random_lat, random_lon

    def run_simulation(self, num_orders=10):
        for order_id in range(1, num_orders + 1):
            # Simulate creating an order (for simplicity, using random lat/lon)
            random_lat, random_lon = self.generate_random_order()

            # Simulate adding the order to the cluster
            new_user_id = random.randint(1, 10)  # Random user ID for now
            self.cluster_manager.handle_new_order(order_id, new_user_id, random_lat, random_lon)

        # After adding all orders, visualize the clusters
        self.cluster_manager.visualize_clusters()

# Simulation usage:
cluster_manager = ClusterManager(radius_km=5)  # Initialize with desired radius
cluster_manager.build_clusters()  # Build initial clusters from existing data

cluster_manager.build_and_show_graph()
'''
simulation = Simulation(cluster_manager)
simulation.run_simulation(50)  # Simulate adding 50 random orders
'''