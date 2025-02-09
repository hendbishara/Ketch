import random
import time
import networkx as nx
import matplotlib.pyplot as plt
from Dijkstra import Modified_Dijkstra

# Define a dummy Cluster class to simulate the clusters used in your algorithm
class Cluster:
    def __init__(self, cluster_id, coordinates, capacity):
        self.id = cluster_id
        self.coordinates = coordinates
        self.capacity = capacity

# Generate random test clusters
def generate_test_clusters(num_clusters):
    clusters = []
    for i in range(num_clusters):
        lat = random.uniform(40.0, 41.0)  # Random latitude
        lon = random.uniform(-74.0, -73.0)  # Random longitude
        capacity = random.randint(1, 50)  # Random capacity
        clusters.append(Cluster(f"C{i}", (lat, lon), capacity))
    return clusters

# Define the warehouse location
warehouse_coords = (40.5, -73.5)  

# Generate 10 test clusters
test_clusters = generate_test_clusters(10)

# Initialize the Modified Dijkstra object
max_capacity = 100  # Define a max capacity limit
dijkstra_test_V1 = Modified_Dijkstra(test_clusters, max_capacity, warehouse_coords)
dijkstra_test_V2 = Modified_Dijkstra(test_clusters, max_capacity, warehouse_coords)
dijkstra_test_V3 = Modified_Dijkstra(test_clusters, max_capacity, warehouse_coords)

def time_algorithm(func, name):
    start_time = time.time()
    result = func()
    end_time = time.time()
    print(f"Execution Time ({name}): {end_time - start_time:.4f} seconds")
    return result

def plot_graph(graph, title):
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(8, 6))
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', edge_color='gray')
    plt.title(title)
    plt.show()

# Run and compare algorithms
#print("Running Baseline Algorithm...")
#baseline_result = time_algorithm(dijkstra_test.base_algo, "Baseline")
print("Running Dijkstra Version 1...")
dijkstra_v1_result = time_algorithm(dijkstra_test_V1.Dijkstra_version1, "Dijkstra V1")
print("Running Dijkstra Version 2...")
dijkstra_v2_result = time_algorithm(dijkstra_test_V2.Dijkstra_version2, "Dijkstra V2")
print("Running Dijkstra Version 3...")
dijkstra_v3_result = time_algorithm(dijkstra_test_V3.Dijkstra_version3, "Dijkstra V3")

# Plot initial and final graphs
print("Visualizing Graphs...")
#plot_graph(dijkstra_test.build_graph(), "Initial Cluster Graph")
#plot_graph(dijkstra_test.build_result_graph(baseline_result), "Baseline Result Graph")
plot_graph(dijkstra_test_V1.build_graph(), "Dijkstra V1 Result Graph")
plot_graph(dijkstra_test_V2.build_graph(), "Dijkstra V2 Result Graph")
plot_graph(dijkstra_test_V3.build_graph(), "Dijkstra V3 Result Graph")
