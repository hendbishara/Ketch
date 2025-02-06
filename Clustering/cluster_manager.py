import networkx as nx
from 
geopy.distance import geodesic
import db_methods
import matplotlib.pyplot as plt

class ClusterManager:
    def __init__(self, radius_km, db_connection=None):
        self.radius_km = radius_km
        self.clusters = []  # This will hold the clusters as an array
        self.db_connection = db_connection  # This will hold the database connection

    def build_clusters(self):
        orders = db_methods.get_all_orders()  # Fetch all orders
        clusters = []

        for order in orders:
            order_id, user_id = order  # Now only fetching order_id and user_id from orders

            # Fetch user coordinates (latitude and longitude) based on user_id
            user_coordinates = db_methods.get_user_coordinates(user_id)
            if not user_coordinates:
                continue  # Skip if user coordinates not found
            
            latitude, longitude = user_coordinates  # Extract latitude and longitude
            order_coord = (latitude, longitude)  # Coordinates from the users table
            user_address = db_methods.get_address_for_user(user_id)  # Get the user's address
            #print(order_coord)
            added_to_cluster = False
            # Check if the order fits into any existing cluster
            for cluster in clusters:
                for addr, addr_coord in cluster:
                    distance = geodesic(order_coord, addr_coord).km
                    if distance <= self.radius_km:
                        cluster.append((user_address, addr_coord))  # Add address instead of coordinates
                        added_to_cluster = True
                        break
                if added_to_cluster:
                    break

            # If the order didn't fit into any cluster, create a new cluster
            if not added_to_cluster:
                clusters.append([(user_address, order_coord)])  # New cluster with user address and order
        self.clusters = clusters

    def get_clusters(self):
        return self.clusters




