import networkx as nx
from geopy.distance import geodesic
from .db_methods import *
import matplotlib.pyplot as plt
import folium
import webbrowser
import os
import numpy as np

               
class Cluster:

    def __init__(self, centroid, first_order_id, first_order_capacity, cluster_id):
        self.id = cluster_id  # Assign global cluster ID
        self.orders = {first_order_id}  # Set of order IDs in this cluster
        self.coordinates = centroid  # Centroid (coordinates of the first order)
        self.coordinates = centroid  # Centroid (coordinates of the first order)
        self.total_capacity = first_order_capacity  # Total capacity of orders in this cluster
        #self.max_capacity = 20  # Maximum capacity constraint
        #self.radius_km = 1  # Radius in kilometers

    def add_order(self, order_id, order_capacity):
        """ Adds an order to the cluster if it fits the criteria """
        self.orders.add(order_id)
        self.total_capacity += order_capacity  # Increase total capacity


class ClusterManager:

    
    def __init__(self, radius_km, max_capacity,store_id, db_manager: DatabaseManager,connection):
        self.radius_km = radius_km
        #self.max_capacity = 1000
        self.max_capacity = max_capacity  # Maximum capacity constraint
        self.clusters = []  # List of Cluster objects
        self.store_id = store_id
        self.global_cluster_id = 1  # Global counter for cluster IDs
        self.db_manager = db_manager
        self.connection = connection

    def build_clusters(self):
        """ Builds clusters from scratch based on existing orders """
        orders = self.db_manager.get_all_orders(self.connection,self.store_id)  or [] # Fetch all orders
    
        self.clusters = []  # Reset clusters
        self.global_cluster_id = 1  # Reset global cluster ID

        for order in orders:
            req_id=order['req_id'] 
            user_id = order['user_id']  # Extract order ID and user ID
            print(f"Processing order {req_id} for user {user_id}")
            # Fetch user coordinates (latitude, longitude)
            user_coordinates = self.db_manager.get_user_coordinates(self.connection,user_id)
            if not user_coordinates:
                continue  # Skip if user has no coordinates
            
            latitude, longitude = user_coordinates  # Extract coordinates
            order_coord = (latitude, longitude)  # Order coordinates
            order_capacity = self.db_manager.get_order_capacity(self.connection,req_id)  # Get order capacity

            self.add_order_to_cluster(req_id, order_coord, order_capacity)  # Add order

    def add_order_to_cluster(self, order_id, order_coord, order_capacity):
        """ Attempts to add a new order to an existing cluster or creates a new cluster """
        added_to_cluster = False

        for cluster in self.clusters:
            if cluster.total_capacity + order_capacity > self.max_capacity:
                continue  # Skip cluster if adding the order exceeds max capacity
            
            distance = geodesic(order_coord, cluster.coordinates).km
            print(f"Distance from order {order_id} to cluster {cluster.id}: {distance} km")

            if distance <= self.radius_km:
                cluster.add_order(order_id, order_capacity)
                added_to_cluster = True
                print(f"Added order {order_id} to existing cluster {cluster.id}")
                break

        # If no existing cluster fits, create a new one
        if not added_to_cluster:
            new_cluster = Cluster(order_coord, order_id, order_capacity,self.global_cluster_id)
            self.global_cluster_id += 1
            self.clusters.append(new_cluster)
            print(f"Created new cluster {new_cluster.id} for order {order_id}")

    def get_clusters(self):
        return self.clusters
    
    def fetch_clusters(self):
        """fetch new requests and add them to already available clusters or create a new cluster for them"""
        print("curr cluster counter: " + str(self.global_cluster_id))
        requests = self.db_manager.get_requests(self.connection,self.store_id)
        for req in requests:
            req_id = req['req_id']
            clus_id = req['cluster_id']
            cap = self.db_manager.get_order_capacity(self.connection,req_id)
            if clus_id == -1:
                order_coord = self.db_manager.get_user_coordinates(self.connection,req['user_id'])
                cap = self.db_manager.get_order_capacity(self.connection,req['req_id'])
                self.add_order_to_cluster(req['req_id'], order_coord, cap)

            


    def create_map(self):
        if not self.clusters:
            print("No clusters available to create a map.")
            return

        # Center the map around the first cluster's centroid
        first_cluster = self.clusters[0]
        map_center = first_cluster.coordinates
        map_obj = folium.Map(location=map_center, zoom_start=12)

        # Iterate through each cluster to add markers and lines
        for cluster in self.clusters:
            if cluster.coordinates:
                # ✅ Add a red circle marker for the cluster centroid
                folium.CircleMarker(
                    location=cluster.coordinates,
                    radius=10,  # Bigger for better visibility
                    color='red',
                    fill=True,
                    fill_color='red',
                    fill_opacity=0.8,
                    popup=f"Cluster ID: {cluster.id}\nTotal Capacity: {cluster.total_capacity}"
                ).add_to(map_obj)

            # ✅ Add green markers for orders and draw lines to the centroid
            for order_id in cluster.orders:
                # Fetch user ID from the order
                user_id = self.db_manager.get_user_id_from_order(self.connection,order_id)
                if not user_id:
                    continue

                # Fetch user coordinates
                user_coord = self.db_manager.get_user_coordinates(self.connection,user_id)
                if not user_coord:
                    continue

                # ✅ Add green marker for the user's address
                folium.Marker(
                    location=user_coord,  
                    popup=f"Order ID: {order_id}\nCoordinates: {user_coord}",
                    icon=folium.Icon(color='green', icon='cloud', prefix='fa')
                ).add_to(map_obj)

                # ✅ Draw a line between the order and the cluster centroid
                folium.PolyLine(
                    [user_coord, cluster.coordinates],  # Order → Centroid
                    color="blue",
                    weight=2.5,
                    opacity=0.8
                ).add_to(map_obj)

        # ✅ Save and open the map
        map_path = os.path.join(os.getcwd(), "cluster_map.html")
        map_obj.save(map_path)
        print(f"Map has been saved as '{map_path}'.")

        if os.path.exists(map_path):
            print(f"Opening map at {map_path}")
            webbrowser.open(f'file://{map_path}', new=2)
        else:
            print(f"Error: The map file was not created at {map_path}.")





