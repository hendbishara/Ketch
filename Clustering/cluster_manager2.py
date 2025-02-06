import networkx as nx
from geopy.distance import geodesic
import db_methods
import matplotlib.pyplot as plt

class Cluster:
    
    global_cluster_id = 1  # Global counter for cluster IDs

    def __init__(self, centroid, first_order_id, first_order_capacity):
        self.cluster_id = Cluster.global_cluster_id  # Assign global cluster ID
        Cluster.global_cluster_id += 1  # Increment global ID for the next cluster
        self.orders = {first_order_id}  # Set of order IDs in this cluster
        self.centroid = centroid  # Centroid (coordinates of the first order)
        self.total_capacity = first_order_capacity  # Total capacity of orders in this cluster

    def add_order(self, order_id, order_capacity):
        """ Adds an order to the cluster if it fits the criteria """
        self.orders.add(order_id)
        self.total_capacity += order_capacity  # Increase total capacity


class ClusterManager:
    def __init__(self, radius_km, max_capacity, db_connection=None):
        self.radius_km = radius_km
        self.max_capacity = max_capacity  # Maximum capacity constraint
        self.clusters = []  # List of Cluster objects
        self.db_connection = db_connection  # Database connection

    def build_clusters(self):
        """ Builds clusters from scratch based on existing orders """
        orders = db_methods.get_all_orders()  # Fetch all orders
        self.clusters = []  # Reset clusters
        Cluster.global_cluster_id = 1  # Reset global cluster ID

        for order in orders:
            order_id, user_id = order  # Extract order ID and user ID

            # Fetch user coordinates (latitude, longitude)
            user_coordinates = db_methods.get_user_coordinates(user_id)
            if not user_coordinates:
                continue  # Skip if user has no coordinates
            
            latitude, longitude = user_coordinates  # Extract coordinates
            order_coord = (latitude, longitude)  # Order coordinates
            order_capacity = db_methods.get_order_capacity(order_id)  # Get order capacity

            self.add_order_to_cluster(order_id, order_coord, order_capacity)  # Add order

    def add_order_to_cluster(self, order_id, order_coord, order_capacity):
        """ Attempts to add a new order to an existing cluster or creates a new cluster """
        added_to_cluster = False

        for cluster in self.clusters:
            if cluster.total_capacity + order_capacity > self.max_capacity:
                continue  # Skip cluster if adding the order exceeds max capacity
            
            distance = geodesic(order_coord, cluster.centroid).km
            print(f"Distance from order {order_id} to cluster {cluster.cluster_id}: {distance} km")

            if distance <= self.radius_km:
                cluster.add_order(order_id, order_capacity)
                added_to_cluster = True
                print(f"Added order {order_id} to existing cluster {cluster.cluster_id}")
                break

        # If no existing cluster fits, create a new one
        if not added_to_cluster:
            new_cluster = Cluster(order_coord, order_id, order_capacity)
            self.clusters.append(new_cluster)
            print(f"Created new cluster {new_cluster.cluster_id} for order {order_id}")

    def get_clusters(self):
        return self.clusters
