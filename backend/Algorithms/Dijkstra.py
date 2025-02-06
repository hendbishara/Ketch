import networkx as nx
from geopy.geocoders import Nominatim
from geopy.distance import distance
import heapq
import math

class Modified_Dijkstra:
    def __init__(self,clusters,max_capacity, warehouse_coords):
        #we assume that the clusters we recieve have the centroid coordinates of each cluster and the total capacity of each cluster and cluster ID
        #s is the coordinates of the warehouse
        self.clusters = clusters
        self.max_c = max_capacity
        self.g = nx.DiGraph()
        self.Q = []
        self.warehouse_coords = warehouse_coords
        
        
        
    def create_graph_from_clusters(self):
        self.g.add_node("WareHouse", capacity = 0,path_C = 0, path_d = 0, loss = 0, pi = None, coords = self.warehouse_coords)
        for c in self.clusters:
            self.g.add_node(c.id, capacity = c.capacity, path_C = 0, path_d = math.inf, loss = math.inf, pi = None, coords = c.coordinates)

        for node in self.g.nodes():
            for node2 in self.g.nodes():
                tmp = distance(self.g.nodes[node]['coords'], self.g.nodes[node2]['coords']).kilometers
                if node != node2 and node2 != "WareHouse":
                    self.g.add_edge(node,node2,weight = tmp)
    
        heapq.heappush(self.Q,(0,"WareHouse"))
    
    def Dijkstra_version1(self):
        #initialize graph
        self.create_graph_from_clusters()
        
        #initialize a set to keep track of visited nodes
        visited = set()
        
        
        while len(self.Q) != 0:
            k , u_id = heapq.heappop(self.Q) #extract min
            #skip outdated or already processed entries
            if u_id in visited:
                continue
            visited.add(u_id)
            #access the node's data
            u = self.g.nodes[u_id]
            
            for v_id in self.g.neighbors(u_id):
                v = self.g.nodes[v_id]  # Access the neighboring node data
                # Relaxation condition
                new_path_C = u['path_C'] + v['capacity']
                new_path_d = u['path_d'] + self.g[u_id][v_id]['weight']
                new_loss = new_path_d / new_path_C
                
                if new_loss < v['loss'] and new_path_C <= self.max_c:
                # Update node properties
                    v['loss'] = new_loss
                    v['path_C'] = new_path_C
                    v['path_d'] = new_path_d
                    v['pi'] = u_id
                
                    # Push the updated node to the priority queue
                    heapq.heappush(self.Q, (new_loss, v_id))
    
    def Dijkstra_version2(self):
        #initialize graph
        self.create_graph_from_clusters()
        
        #initialize a set to keep track of visited nodes
        visited = set()
        
        #initialize a set to keep track of already assigned nodes
        assigned_nodes = set()
        
        while len(self.Q) != 0:
            k , u_id = heapq.heappop(self.Q) #extract min
            #skip outdated or already processed entries
            if u_id in visited:
                continue
            visited.add(u_id)
            #access the node's data
            u = self.g.nodes[u_id]
            
            # Ensure distinct paths: if `v_id` is already assigned, skip it
            if u_id in assigned_nodes:
                continue
            
            for v_id in self.g.neighbors(u_id):
                
                v = self.g.nodes[v_id]  # Access the neighboring node data
                
                # Relaxation condition
                new_path_C = u['path_C'] + v['capacity']
                new_path_d = u['path_d'] + self.g[u_id][v_id]['weight']
                new_loss = new_path_d / new_path_C
                
                if new_loss < v['loss'] and new_path_C <= self.max_c:
                # Update node properties
                    v['loss'] = new_loss
                    v['path_C'] = new_path_C
                    v['path_d'] = new_path_d
                    v['pi'] = u_id
                
                    # Push the updated node to the priority queue
                    heapq.heappush(self.Q, (new_loss, v_id))
                    
                    # Mark node as assigned so it cannot be part of another path
                    assigned_nodes.add(v_id)
    
    
    def Dijkstra_version3(self):
        # Initialize graph
        self.create_graph_from_clusters()

        # Set to track visited nodes
        visited = set()

        while len(self.Q) != 0:
            k, u_id = heapq.heappop(self.Q)  # Extract min

            # Skip already processed nodes
            if u_id in visited:
                continue
            visited.add(u_id)

            # Access the node's data
            u = self.g.nodes[u_id]

            best_v_id = None  # Store the best neighbor for u
            best_loss = math.inf
            best_path_C = 0
            best_path_d = 0

            for v_id in self.g.neighbors(u_id):
                v = self.g.nodes[v_id]  # Access the neighboring node data

                # Compute new path properties
                new_path_C = u['path_C'] + v['capacity']
                new_path_d = u['path_d'] + self.g[u_id][v_id]['weight']
                new_loss = new_path_d / new_path_C

                # Check if this neighbor is the best candidate
                if new_path_C <= self.max_c and new_loss < best_loss:
                    best_loss = new_loss
                    best_v_id = v_id
                    best_path_C = new_path_C
                    best_path_d = new_path_d

            # If a valid best neighbor exists, assign `pi` and update values
            if best_v_id is not None:
                v = self.g.nodes[best_v_id]
                v['loss'] = best_loss
                v['path_C'] = best_path_C
                v['path_d'] = best_path_d
                v['pi'] = u_id  # Assign u as parent

                # Push the best neighbor to the priority queue
                heapq.heappush(self.Q, (best_loss, best_v_id))

        
        
    def get_graph(self):
        return self.g
    