import networkx as nx
#from geopy.geocoders import Nominatim
#from geopy.distance import distance
import random
import math
import matplotlib.pyplot as plt
from Dijkstra import Modified_Dijkstra

# Define a simple cluster class for testing
class Cluster:
    def __init__(self, cluster_id, coordinates, capacity):
        self.id = cluster_id
        self.coordinates = coordinates
        self.capacity = capacity

# Generate random clusters for testing
def generate_test_clusters(num_clusters, warehouse_coords):
    clusters = []
    for i in range(num_clusters):
        # Random coordinates within a rough range
        lat = warehouse_coords[0] + random.uniform(-0.5, 0.5)
        lon = warehouse_coords[1] + random.uniform(-0.5, 0.5)
        capacity = random.randint(1, 10)  # Random capacity for each cluster
        clusters.append(Cluster(f"Cluster_{i+1}", (lat, lon), capacity))
    return clusters

# Test the Modified_Dijkstra implementation
def test_modified_dijkstra():
    # Warehouse coordinates
    warehouse_coords = (40.7128, -74.0060)  # Example: New York City

    # Generate test clusters
    num_clusters = 10
    clusters = generate_test_clusters(num_clusters, warehouse_coords)

    # Maximum delivery capacity
    max_capacity = 10

    # Initialize Modified_Dijkstra
    dijkstra = Modified_Dijkstra(clusters, max_capacity, warehouse_coords)

    # Run Dijkstra algorithm
    dijkstra.Dijkstra()

    # Retrieve the graph and print the results
    graph = dijkstra.get_graph()

    # Print node details
    print("Node Details:")
    for node, data in graph.nodes(data=True):
        print(f"Node: {node}, Data: {data}")

    # Print edges with weights
    print("\nEdge Details:")
    for u, v, weight in graph.edges(data=True):
        print(f"From {u} to {v}, Weight: {weight}")

    # Visualization of the graph
    pos = {node: data['coords'] for node, data in graph.nodes(data=True)}  # Get coordinates as positions
    plt.figure(figsize=(10, 10))

    # Draw the nodes with labels
    nx.draw_networkx_nodes(graph, pos, node_size=500, node_color='skyblue', alpha=0.7)
    nx.draw_networkx_labels(graph, pos, font_size=12, font_weight='bold')

    # Draw the edges with weights
    nx.draw_networkx_edges(graph, pos, width=2, edge_color='gray')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels={(u, v): f"{d['weight']:.2f}" for u, v, d in graph.edges(data=True)})

    # Title and display
    plt.title("Graph Visualization of the Modified Dijkstra")
    plt.axis('off')  # Hide the axes
    plt.show()

# Run the test
if __name__ == "__main__":
    test_modified_dijkstra()
