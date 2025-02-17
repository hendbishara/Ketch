import networkx as nx
from geopy.geocoders import Nominatim
from geopy.distance import distance
import heapq
import math
from collections import deque


class Modified_Dijkstra:
    def __init__(self,clusters,max_capacity, warehouse_coords):
        #we assume that the clusters we recieve have the centroid coordinates of each cluster and the total capacity of each cluster and cluster ID
        self.clusters = clusters
        self.max_c = max_capacity
        self.g = nx.DiGraph()
        self.Q = []
        self.warehouse_coords = warehouse_coords
        self.orders = set()
    
    
    def base_algo(self):
        """base line algorithm that combines orders in each cluster, used to have a base line comparison for the huiristic calculations using the different versions of dijkstra"""
        return self.clusters
        
      
    def create_graph_from_clusters(self):
        """initializes graph where each cluster is a node""" 
        self.g.add_node("WareHouse", capacity = 0,path_C = 0, path_d = 0, loss = 0, pi = None, coords = self.warehouse_coords)
        for c in self.clusters:
            #check if node is full, add it as an order
            if(c.capacity >= self.max_c):
                self.orders.add(("Warhouse",c))
                continue #dont add node to the graph
            self.g.add_node(c.id, capacity = c.capacity, path_C = 0, path_d = math.inf, loss = math.inf, pi = None, coords = c.coordinates)

        for node in self.g.nodes():
            for node2 in self.g.nodes():
                tmp = distance(self.g.nodes[node]['coords'], self.g.nodes[node2]['coords']).kilometers
                if node != node2 and node2 != "WareHouse":
                    self.g.add_edge(node,node2,weight = tmp)
    
        heapq.heappush(self.Q,(0,"WareHouse"))
    
    def Dijkstra_version1(self):
        """modified dijkstra version one, we run the modified dijkstra where the loss function is 
        path distance/ path capacity, to ensure distinct paths we filter the paths when combining the orders.
        returns a set of the combined orders"""

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
        #return self.combine_orders_V1(self.build_graph())
    
    def Dijkstra_version2(self):
        """modified version of dijkstra that keeps track of nodes that where assigned aas parents, and does not allo two nodes to have the same parent unless its the warehouse
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
            
            print("current node ot of heap is: " + str(u_id))
            
            for v_id in self.g.neighbors(u_id):
                # Ensure distinct paths: if u_id` is already assigned, skip it
                if u_id != "WareHouse":   
                    if u_id in assigned_nodes:
                        continue
                if v_id in visited:
                    continue
                
                print("current neighbor is: " + str(v_id))
                
                v = self.g.nodes[v_id]  # Access the neighboring node data
                
                # Relaxation condition
                new_path_C = u['path_C'] + v['capacity']
                new_path_d = u['path_d'] + self.g[u_id][v_id]['weight']
                new_loss = new_path_d / new_path_C
                
                if new_loss < v['loss'] and new_path_C <= self.max_c:
                    if (v_id != u['pi']):
                    # Update node properties
                        print("inside if condition!")
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
            while current is not None:
                path.append(current)
                current = self.g.nodes[current]['pi']
                #print(current)
            self.orders.add(tuple(reversed(path)))

    
    
    def combine_orders_V1(self,bfs_graph):
        """combine orders from the modified dijkstra version 1 where one node can be a parent to more 
        than one other node, in this combinig function we check if a node is a parent to more than one node
        we check the loss of all its children if we deliver from the warehouse directly and choose the max(loss) to keep
        as its child"""
        
        
        # go over all nodes, check if out degree > 1 
        for node in bfs_graph.nodes():
            if bfs_graph.out_degree(node)>1:
                #go over each neighbor, check loss from warehouse and keep the edge with max loss from warehouse
                max_loss = 0
                max_node = None
                for neighbor in  bfs_graph.successors(node):
                    dist = self.g["WareHouse"][neighbor]['weight']
                    capacity = self.g.nodes[neighbor]['capacity']
                    curr_loss = dist / capacity
                    if curr_loss<max_loss:
                        bfs_graph.remove_edge(node,neighbor)
                        bfs_graph.add_edge("WareHouse",neighbor)
                    elif max_node!=None:
                        bfs_graph.remove_edge(node,max_node)
                        bfs_graph.add_edge("WareHouse",max_node)
                        max_loss = curr_loss
                        max_node = neighbor
        
        
        #we get a tree where no node that is not the warehouse hase an out degree > 1
        #call on the combined_orders function
        self.combined_orders(bfs_graph)
        
    def get_orders(self):
        return self.orders
                          
        
        
        