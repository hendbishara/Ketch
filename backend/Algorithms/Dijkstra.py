import networkx as nx
from geopy.geocoders import Nominatim
from geopy.distance import distance
import heapq
import math
from collections import deque


class Modified_Dijkstra:
    
    def __init__(self,clusters,max_capacity, warehouse_coords,version):
        #we assume that the clusters we recieve have the centroid coordinates of each cluster and the total capacity of each cluster and cluster ID
        
        self.clusters = clusters
        self.max_c = max_capacity  # Maximum capacity allowed per path
        self.g = nx.DiGraph()  
        self.Q = [] # Priority queue for Dijkstra’s algorithm
        self.warehouse_coords = warehouse_coords
        self.orders = [] # Stores the final delivery orders
        self.total_orders_capacity = [] # Stores total capacity for each order
        self.total_orders_dist = [] # Stores total distance for each order
        self.total_orders_loss = []  # Stores the computed loss for each order
        self.version = version # Specifies which version of Dijkstra to use
    
    
    def base_algo(self):
        """base line algorithm that combines orders in each cluster, used to have a base line comparison for the huiristic calculations using the different versions of dijkstra"""
        for cluster in self.clusters:
            self.orders.append(("WareHouse", cluster.id)) # Direct delivery from warehouse
            self.total_orders_capacity.append(cluster.total_capacity) # Store cluster capacity
            dist = distance(self.warehouse_coords,cluster.coordinates).km
            self.total_orders_dist.append(dist)
            self.total_orders_loss.append(dist/cluster.total_capacity) #compute loss
        
      
    def create_graph_from_clusters(self):
        """initializes graph where each cluster is a node  
        Nodes represent clusters, and edges represent the distance between clusters.
        If a cluster exceeds `max_capacity`, it is directly assigned to the warehouse.""" 
        #make sure all fields are in initiale state
        self.total_orders_capacity = []
        self.total_orders_dist = []
        self.total_orders_loss = []
        self.g = nx.DiGraph() #initialize a new graph
        self.Q = []
        #strat building the graph
        # Add warehouse as the starting node
        self.g.add_node("WareHouse", capacity = 0,path_C = 0, path_d = 0, loss = 0, pi = None, coords = self.warehouse_coords)
        for c in self.clusters:
            if(c.total_capacity >= self.max_c):
                # If cluster exceeds max capacity(full), treat it as an immediate order
                self.orders.append(("WareHouse",c.id))
                self.total_orders_capacity.append(c.total_capacity)
                dist = distance(self.warehouse_coords,c.coordinates).km
                self.total_orders_dist.append(dist)
                self.total_orders_loss.append(dist/c.total_capacity)
                continue # Do not add this cluster as a graph node

            # Add cluster as a graph node
            self.g.add_node(c.id, capacity = c.total_capacity, path_C = 0, path_d = math.inf, loss = math.inf, pi = None, coords = c.coordinates)


        for node in self.g.nodes(): # Add edges between nodes (clusters)
            for node2 in self.g.nodes():
                tmp = distance(self.g.nodes[node]['coords'], self.g.nodes[node2]['coords']).kilometers
                if node != node2 and node2 != "WareHouse":
                    self.g.add_edge(node,node2,weight = tmp)
    # Push the warehouse node to the priority queue
        heapq.heappush(self.Q,(0,"WareHouse"))
    
    def Dijkstra_version1(self):
        """modified dijkstra version 1, we run the modified dijkstra where the loss function is 
        path distance/ path capacity, to ensure distinct paths we filter the paths when combining the orders.
        returns a set of the combined orders"""

        # Initialize the graph
        self.create_graph_from_clusters()
        
        #initialize a set to keep track of visited nodes
        visited = set()  # Track visited nodes
        
        
        while len(self.Q) != 0:
            k , u_id = heapq.heappop(self.Q) #Extract the node with the smallest loss (extract min)
            #skip outdated or already processed entries
            if u_id in visited:
                continue 
            visited.add(u_id)
            #access the node's data
            u = self.g.nodes[u_id]
            
            for v_id in self.g.neighbors(u_id):
                #prevent cycles:
                if v_id in visited:
                    continue  
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
                    v['pi'] = u_id # Set parent node
                
                    # Push the updated node to the priority queue
                    heapq.heappush(self.Q, (new_loss, v_id))
        self.combine_orders_V1(self.build_graph())
    
    def Dijkstra_version2(self):
        """modified version of dijkstra that keeps track of nodes that where assigned aas parents, and does not allow 2 nodes to have the same parent unless its the warehouse
        returns a set of the combined orders"""
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
            
            #print("current node ot of heap is: " + str(u_id))
            
            for v_id in self.g.neighbors(u_id):
                # Ensure distinct paths: if u_id` is already assigned, skip it
                if u_id != "WareHouse":   
                    if u_id in assigned_nodes:
                        continue
                if v_id in visited:
                    continue
                
                #print("current neighbor is: " + str(v_id))
                
                v = self.g.nodes[v_id]  # Access the neighboring node data
                
                # Relaxation condition
                new_path_C = u['path_C'] + v['capacity']
                new_path_d = u['path_d'] + self.g[u_id][v_id]['weight']
                new_loss = new_path_d / new_path_C
                
                if new_loss < v['loss'] and new_path_C <= self.max_c:
                    if (v_id != u['pi']):
                    # Update node properties
                        #print("inside if condition!")
                        prev_pi = v['pi']
                        v['loss'] = new_loss
                        v['path_C'] = new_path_C
                        v['path_d'] = new_path_d
                        v['pi'] = u_id
                
                        # Push the updated node to the priority queue
                        heapq.heappush(self.Q, (new_loss, v_id))
                        
                        # Mark node as assigned so it cannot be part of another path
                        if u_id != "WareHouse":
                            assigned_nodes.add(u_id)
                        if prev_pi !=None and prev_pi != "WareHouse":
                            assigned_nodes.remove(prev_pi)
        self.combined_orders(self.build_graph())
    
    def Dijkstra_version3(self):
        """ runs the modified dijkstra algorithm while it keeps track if the minimal loss of all neighbors of a certain node and assigns it as a parent to only one node
    (that with the minimal loss) ensuring distict paths. returns a set of the combined orders"""
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
                if v_id in visited:
                    continue
                
                v = self.g.nodes[v_id]  # Access the neighboring node data

                
                # Compute new path properties
                new_path_C = u['path_C'] + v['capacity']
                new_path_d = u['path_d'] + self.g[u_id][v_id]['weight']
                new_loss = new_path_d / new_path_C

                # Check if this neighbor is the best candidate
                if u_id != "WareHouse":
                    if new_path_C <= self.max_c and new_loss < best_loss:
                        best_loss = new_loss
                        best_v_id = v_id
                        best_path_C = new_path_C
                        best_path_d = new_path_d
                else:
                    if new_loss < v['loss'] and new_path_C <= self.max_c:
                        # Update node properties
                        v['loss'] = new_loss
                        v['path_C'] = new_path_C
                        v['path_d'] = new_path_d
                        v['pi'] = u_id
                        heapq.heappush(self.Q, (new_loss, v_id))
                    
            if u_id!= "WareHouse":
                # If a valid best neighbor exists, assign `pi` and update values
                if best_v_id is not None:
                    v = self.g.nodes[best_v_id]
                    v['loss'] = best_loss
                    v['path_C'] = best_path_C
                    v['path_d'] = best_path_d
                    v['pi'] = u_id  # Assign u as parent

                    # Push the best neighbor to the priority queue
                    heapq.heappush(self.Q, (best_loss, best_v_id))
            
        self.combined_orders(self.build_graph())

        
        
    def get_graph(self):
        return self.g
    
    
    def get_path(self, target_node):
        """ Returns the path from the warehouse to the target node as a list. """
        if target_node not in self.g.nodes:
            return None  # If the node does not exist in the graph

        path = []
        current = target_node

        while current is not None:
            path.append(current)
            current = self.g.nodes[current]['pi']  # Move to the parent node

        return list(reversed(path))  # Reverse to get path from source to target
    
    
    def build_graph(self):
        # Build the new graph where edges are based on `pi` pointers
        bfs_graph = nx.DiGraph()
        for node in self.g.nodes():
            bfs_graph.add_node(node)  # Copy all nodes
            if self.g.nodes[node]['pi'] is not None:  # Add edges based on `pi`
                bfs_graph.add_edge(self.g.nodes[node]['pi'], node)
        return bfs_graph
        
    

    
    def combined_orders(self,bfs_graph):
        """create combined orders for version 2 and 3 of the modified dijkstra,
        in these vesions we assume that each node can be only one a pi value which means the graph we build here is a tree where no node that
        is not the warehouse hase an out degree > 1"""
        
        
        # find all leaf nodes:
        leaf_nodes = [node for node in bfs_graph.nodes() if bfs_graph.out_degree(node) == 0 and node != "WareHouse"]
        
        # backtarck from each leaf to construct full order 
        for leaf in leaf_nodes:
            path = []
            current = leaf
            total_loss = self.g.nodes[current]['loss']
            total_capacity = self.g.nodes[current]['path_C']
            total_dist = self.g.nodes[current]['path_d']
            while current is not None:
                path.append(current)
                current = self.g.nodes[current]['pi']
                #print(current)
            self.orders.append(reversed(path))
            self.total_orders_capacity.append(total_capacity)
            self.total_orders_dist.append(total_dist)
            self.total_orders_loss.append(total_loss)
            
    
    def combine_orders_V1(self, bfs_graph):
        """Combine orders from the modified Dijkstra version 1 where one node can be a parent to more 
        than one other node. In this combining function, we check if a node is a parent to more than one node,
        check the loss of all its children if delivered from the warehouse directly, and choose the max(loss) to keep
        as its child."""
        
        # Go over all nodes, check if out-degree > 1 
        for node in bfs_graph.nodes():
            if bfs_graph.out_degree(node) > 1:
                #print(node)
                # Collect modifications in a temporary list
                modifications = []
                
                max_loss = -1
                max_node = None
                for neighbor in list(bfs_graph.successors(node)):  
                    dist = self.g["WareHouse"][neighbor]['weight']
                    capacity = self.g.nodes[neighbor]['capacity']
                    curr_loss = dist / capacity

                    if max_loss == -1:
                        max_loss = curr_loss
                        max_node = neighbor
                        continue

                    if curr_loss < max_loss:
                        modifications.append((node, neighbor, "WareHouse"))
                        self.g.nodes[neighbor]['pi'] = "WareHouse"
                    else:
                        if max_node is not None:
                            modifications.append((node, max_node, "WareHouse"))
                            self.g.nodes[max_node]['pi'] = "WareHouse"
                            max_loss = curr_loss
                            max_node = neighbor
                
                # Apply all modifications outside the loop
                for node, to_remove, to_add in modifications:
                    bfs_graph.remove_edge(node, to_remove)
                    bfs_graph.add_edge(to_add, to_remove)

        # We get a tree where no node, except the warehouse, has an out-degree > 1
        # Call on the combined_orders function
        self.combined_orders(bfs_graph)

        
    def get_orders(self):
        """
        Runs the selected algorithm version and returns the final order list.
        """
        if self.version == "Base":
            self.base_algo()
        elif self.version == "V1":
            self.Dijkstra_version1()
        elif self.version == "V2":
            self.Dijkstra_version2()
        elif self.version == "V3":
            self.Dijkstra_version3()
        else:
            print("NO proper version was implied, Base version is run")
            self.base_algo()
        return self.orders
    
    
    def get_Avg_loss_on_nodes(self):
        """
    Computes the average loss for all nodes in the graph.

    Loss is defined as: loss = total path distance / total path capacity.

    Returns:
    - The average loss value across all nodes in the graph.
    - If the "Base" version is used, it calculates the average loss from precomputed total order losses.
    """
    # If using the baseline version, calculate the average loss from the total order losses

        if self.version == "Base":
            return sum([distance for distance in self.total_orders_loss]) / len(self.total_orders_loss)
        total_loss = 0
        num_of_nodes = len(self.g.nodes())
        for node in self.g.nodes:
            total_loss += self.g.nodes[node]['loss']
        return total_loss/num_of_nodes
    
    def get_orders_capacities(self):
        return self.total_orders_capacity
    
    def get_orders_dist(self):
        return self.total_orders_dist
    
    def get_orders_loss(self):
        return self.total_orders_loss
    
    
    """Run this function only after running the algorithm, checks if all paths comply to the max capacity constraint"""
    def check_capacity_constraint(self):
        for i in range(len(self.total_orders_capacity)):
            if self.total_orders_capacity[i]>self.max_c:
                print("Capacity Constraint is not met on path: " + str(i) + " with actual capacity = " + str(self.total_orders_capacity[i]))
        print("All capacities were checked")
        
            
            
                          
        
        
        