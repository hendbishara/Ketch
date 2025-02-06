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

    def build_and_show_graph(self, radius_km=5):
        clusters = self.clusters  # Assuming clusters is a list of lists of address-coordinate pairs
        G = nx.Graph()  # Initialize a new graph

        # Iterate through each cluster
        for cluster in clusters:
            if len(cluster) < 2:  # Skip clusters with fewer than 2 elements (no edges to add)
                continue
            
            # Use the first address in the cluster as the centroid
            centroid_address, centroid_coordinates = list(cluster)[0]
            centroid_coordinates = tuple(map(float, centroid_coordinates))  # Ensure it’s a tuple of floats
            
            # Iterate through the rest of the addresses in the cluster
            for address, coordinates in cluster:
                coordinates = tuple(map(float, coordinates))  # Ensure coordinates are in float format
                
                if coordinates == centroid_coordinates:  # Skip the centroid itself to avoid distance = 0
                    continue
                
                # Print coordinates for debugging
                print(f"Calculating distance between {centroid_address} and {address}")
                print(f"Centroid Coordinates: {centroid_coordinates}, Address Coordinates: {coordinates}")
                
                # Calculate the distance from the centroid to this address
                distance = geodesic(centroid_coordinates, coordinates).km
                print(f"Distance: {distance} km")
                
                # Add edge if the distance is within the radius
                if distance <= radius_km:
                    G.add_edge(centroid_address, address, weight=distance)
                    print(f"Adding edge between {centroid_address} and {address} with distance {distance} km")
        
        # Now plot the graph
        pos = nx.spring_layout(G, seed=42)  # Adjust layout for better positioning
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=10, font_weight="bold", edge_color="gray")
        
        # Draw edge labels (show distances on edges)
        edge_labels = nx.get_edge_attributes(G, 'weight')  # Get the weights (distances) of the edges
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color="red")

        # Show the plot
        plt.title("Clusters Graph with Distances from Centroid")
        plt.show()
        


    def get_clusters(self):
        return self.clusters




