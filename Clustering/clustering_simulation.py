import random
from geopy.distance import geodesic
import db_methods
#from cluster_manager import ClusterManager
from cluster_manager2 import ClusterManager

class Simulation:
    def __init__(self, cluster_manager):
        self.cluster_manager = cluster_manager


# Simulation usage:
cluster_manager2 = ClusterManager(1,20)  # Initialize with desired radius
cluster_manager2.build_clusters()  # Build initial clusters from existing data
cluster_manager2.create_map()

'''
simulation = Simulation(cluster_manager)
simulation.run_simulation(50)  # Simulate adding 50 random orders
'''