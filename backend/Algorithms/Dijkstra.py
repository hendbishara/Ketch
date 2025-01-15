import networkx as nx
from geopy.geocoders import Nominatim
from geopy.distance import distance
import heapq
import math

class Modified_Dijkstra:
    def __init__(self,clusters,max_capacity, s):
        #we assume that the clusters we recieve have the centroid coordinates of each cluster and the total capacity of each cluster and cluster ID
        #s is the coordinates of the warehouse
        self.clusters = clusters
        self.max_c = max_capacity
        self.g = nx.DiGraph()
        self.Q = heapq()
        self.s = s
        
        
        
    def create_graph_from_clusters(self):
        self.g.add_node("WareHouse", capacity = 0,path_C = 0, path_d = 0, loss = 0, pi = None, coords = c.coordinates)
        for c in self.clusters:
            self.g.add_node(c.id, capacity = c.capacity, path_C = 0, path_d = math.inf, loss = math.inf, pi = None, coords = c.coordinates)

        for node in self.g.nodes():
            for node2 in self.g.nodes():
                tmp = distance(node.coords,node2.coords).kilometers
                if node != node2:
                    self.g.add_edge(node,node2,weight = tmp)
    
        heapq.heappush(self.Q,(0,self.g.nodes["WareHouse"]))
    
    def Dijkstra(self):
        self.create_graph_from_clusters()
        while len(self.Q) != 0:
            k , u = heapq.heappop(self.Q) #extract min
            for v in nx.neighbors(u):
                if v.loss == math.inf:
                    v.path_C += u.path_C
                    v.path_d = g[u][v]['weight']
                    v.loss = v.path_d/v.path_C
                    v.pi = u
                    heapq.heappush(self.Q,(v.loss,v))
                elif ((u.path_d + g[u][v]['weight'])/(u.path_C + v.capacity)) < (v.loss and u.path_C + v.capacity <= self.max_c):
                    v.pi = u
                    key = v.loss
                    v.loss = (u.path_d + g[u][v]['weight'])/(u.path_C + v.capacity)
                    v.path_C = u.path_C + v.capacity
                    v.path_d = u.path_d + g[u][v]['weight']
                    #need to decrease key 