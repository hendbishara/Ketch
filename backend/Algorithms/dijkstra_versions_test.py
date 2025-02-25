import random
import time
import networkx as nx
import matplotlib.pyplot as plt
from Dijkstra import Modified_Dijkstra
import sys
import os
import logging




# Get absolute path to Clustering/
clustering_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Clustering"))

# Add to sys.path
sys.path.append(clustering_path)

# Now import the module
import clustering_simulation
import cluster_manager


# Define a dummy Cluster class to simulate the clusters used in your algorithm
class Cluster:
    def __init__(self, cluster_id, coordinates, capacity):
        self.id = cluster_id
        self.coordinates = coordinates
        self.total_capacity = capacity

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
test_clusters = generate_test_clusters(20)

simulation = clustering_simulation.Simulation(cluster_manager.ClusterManager(1, 20))
clusters = simulation.run_clustering()

# Initialize the Modified Dijkstra object
max_capacity = 100  # Define a max capacity limit
dijkstra_test_V1 = Modified_Dijkstra(clusters, max_capacity, warehouse_coords, "V1")
dijkstra_test_V2 = Modified_Dijkstra(clusters, max_capacity, warehouse_coords, "V2")
dijkstra_test_V3 = Modified_Dijkstra(clusters, max_capacity, warehouse_coords, "V3")
dijkstra_test_Basic = Modified_Dijkstra(clusters,max_capacity, warehouse_coords, "Base")

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
dijkstra_v1_result = time_algorithm(dijkstra_test_V1.get_orders, "Dijkstra V1")
print("orders V1:")
#orders_v1 = dijkstra_test_V1.get_orders()
for lst in dijkstra_v1_result:
    print(list(lst))
dijkstra_test_V1.check_capacity_constraint()    

print("capacities for V1: ")
print(dijkstra_test_V1.get_orders_capacities())
print("distances for V1: ")
print(dijkstra_test_V1.get_orders_dist())
print("losses for V1: ")
print(dijkstra_test_V1.get_orders_loss())
print("Average loss on V1: " + str(dijkstra_test_V1.get_Avg_loss_on_nodes()))

    
print("Running Dijkstra Version 2...")
dijkstra_v2_result = time_algorithm(dijkstra_test_V2.get_orders, "Dijkstra V2")
print("orders V2:")
#dijkstra_v2_result = dijkstra_test_V2.get_orders()
for lst in dijkstra_v2_result:
    print(list(lst))
dijkstra_test_V2.check_capacity_constraint()
print("capacities for V2: ")
print(dijkstra_test_V2.get_orders_capacities())
print("distances for V2: ")
print(dijkstra_test_V2.get_orders_dist())
print("losses for V2: ")
print(dijkstra_test_V2.get_orders_loss())
print("Average loss on V2: " + str(dijkstra_test_V2.get_Avg_loss_on_nodes()))

print("Running Dijkstra Version 3...")
dijkstra_v3_result = time_algorithm(dijkstra_test_V3.get_orders, "Dijkstra V3")
print("orders V3:")
#orders_v3 = dijkstra_test_V3.get_orders()
for lst in dijkstra_v3_result:
    print(list(lst))
dijkstra_test_V3.check_capacity_constraint()
print("capacities for V3: ")
print(dijkstra_test_V3.get_orders_capacities())
print("distances for V3: ")
print(dijkstra_test_V3.get_orders_dist())
print("losses for V3: ")
print(dijkstra_test_V3.get_orders_loss())
print("Average loss on V3: " + str(dijkstra_test_V3.get_Avg_loss_on_nodes()))

print("Running Dijkstra Basic: ")    
orders_basic = dijkstra_test_Basic.get_orders()
print("orders basic: ")
#orders_basic = dijkstra_test_Basic.get_orders()
for lst in orders_basic:
    print(list(lst))

print("capacities for Basic: ")
print(dijkstra_test_Basic.get_orders_capacities())
print("distances for Basic: ")
print(dijkstra_test_Basic.get_orders_dist())
print("losses for Basic: ")
print(dijkstra_test_Basic.get_orders_loss())
print("Average loss on Basic: " + str(dijkstra_test_Basic.get_Avg_loss_on_nodes()))


# Plot initial and final graphs
print("Visualizing Graphs...")
#plot_graph(dijkstra_test.build_graph(), "Initial Cluster Graph")
#plot_graph(dijkstra_test.build_result_graph(baseline_result), "Baseline Result Graph")
plot_graph(dijkstra_test_V1.build_graph(), "Dijkstra V1 Result Graph")
plot_graph(dijkstra_test_V2.build_graph(), "Dijkstra V2 Result Graph")
plot_graph(dijkstra_test_V3.build_graph(), "Dijkstra V3 Result Graph")
