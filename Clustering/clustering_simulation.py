import random
from geopy.distance import geodesic
import db_methods
from cluster_manager import ClusterManager
import Send_note
#from routing import RoutePlanner
#import openrouteservice

API_KEY = "5b3ce3597851110001cf624801095298be2b4fd9aad1382911873455"

class Simulation:
    def __init__(self, cluster_manager):
        self.cluster_manager = cluster_manager

    def run_clustering(self): 
        self.cluster_manager.build_clusters()  # Build initial clusters from existing data
        self.cluster_manager.create_map()
        return self.cluster_manager.get_clusters()



# Simulation usage:
#simulation = Simulation(ClusterManager(1, 20))
#clusters = simulation.run_clustering()
#planner = RoutePlanner(API_KEY, simulation.cluster_manager)
#planner.build_graph()
# Example Usage
# Assume clusters are built already
#for cluster in cluster_manager2.get_clusters():
    
#    Send_note.notify_users_about_cluster_items(cluster)
'''
simulation = Simulation(cluster_manager)
simulation.run_simulation(50)  # Simulate adding 50 random orders
'''