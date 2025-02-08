import random
from geopy.distance import geodesic
import db_methods
from cluster_manager2 import ClusterManager
import Send_note

class Simulation:
    def __init__(self, cluster_manager):
        self.cluster_manager = cluster_manager


# Simulation usage:
cluster_manager2 = ClusterManager(1,20)  # Initialize with desired radius
cluster_manager2.build_clusters()  # Build initial clusters from existing data
cluster_manager2.create_map()

# Example Usage
# Assume clusters are built already
#for cluster in cluster_manager2.get_clusters():
    
#    Send_note.notify_users_about_cluster_items(cluster)
'''
simulation = Simulation(cluster_manager)
simulation.run_simulation(50)  # Simulate adding 50 random orders
'''