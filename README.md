# Ketch
# 📦 Shared Delivery Optimization Using a Modified Dijkstra Algorithm

## 📝 Project Overview
This project focuses on optimizing **shared delivery routes** to reduce transportation costs and improve efficiency. By leveraging **a modified version of Dijkstra’s algorithm**, we calculate the most cost-effective and shortest delivery paths while clustering nearby orders.

Traditional delivery models often result in inefficient routing and increased costs due to separate handling of individual orders. Our approach addresses these challenges by:
- **Minimizing overall delivery costs** through shared transportation.
- **Optimizing delivery paths** by considering order proximity and shortest distances.
- **Ensuring efficient capacity utilization** to reduce the number of trips required.

This solution is particularly relevant for **logistics, e-commerce, and supply chain management**, where route efficiency directly impacts operational costs.

---

## 💡 Problem Statement & Objectives
### Challenges in Traditional Delivery Models
- Orders are often delivered **individually**, leading to **high fuel consumption** and increased delivery costs.
- Delivery paths are **not optimized** for multiple orders, resulting in longer travel distances.
- Delivery capacity is **underutilized**, requiring additional trips.

### Proposed Solution
Our model addresses these inefficiencies by:
✅ **Grouping nearby orders into clusters**, allowing multiple deliveries per trip.  
✅ **Using real-world distance calculations** to determine the most efficient routes.  
✅ **Optimizing vehicle capacity** to minimize the number of delivery trips.  
✅ **Applying a modified version of Dijkstra’s algorithm** to ensure optimal route selection.

By integrating these components, we aim to enhance the efficiency of last-mile delivery operations and significantly reduce logistics costs.

---

## 🛠️ Technologies Used
- **Python** – Core programming language for algorithm development.
- **NetworkX** – Graph-based routing and path optimization.
- **Geopy** – Distance measurement for real-world coordinates.
- **Heapq** – Efficient priority queue implementation for Dijkstra’s algorithm.
- **React.js** – Frontend for route visualization.
- **Flask / FastAPI** – Backend API services for processing delivery data.
- **MySQL / PostgreSQL** – Database management for storing orders and clustering data.

---

## 📊 Methodology
### 1️⃣ Graph Representation
- The system constructs a **graph where:**
  - **Nodes** represent clusters of delivery orders.
  - **Edges** represent distances between clusters.
- A **directed graph** is created using **NetworkX**, incorporating properties such as **capacity, distance, and cost-loss values**.

### 2️⃣ Order Clustering
- Orders are grouped based on **geographic proximity** and **volume constraints**.
- A **maximum delivery capacity** is imposed to prevent inefficient resource allocation.

### 3️⃣ Modified Dijkstra’s Algorithm
We implement **three variations** of Dijkstra’s algorithm to identify the most efficient shared delivery routes:

| Algorithm Version | Description |
|-------------------|------------|
| **Version 1 (V1)** | Uses a loss function (distance/capacity) to optimize shared deliveries. |
| **Version 2 (V2)** | Ensures each node is assigned a unique parent, except for the warehouse. |
| **Version 3 (V3)** | Selects the best possible parent based on the minimum loss among all paths. |

### 4️⃣ Route Optimization & Cost Reduction
1. **Orders are assigned to clusters** based on proximity and shared delivery potential.
2. **A weighted graph is constructed**, with the warehouse serving as the starting node.
3. **The modified Dijkstra algorithm executes**, generating optimal paths with cost constraints.
4. **Orders are consolidated** into shared deliveries, minimizing the total number of trips required.

---

# 📝 Project Overview:
📦 Shared Delivery Optimization Using a Modified Dijkstra Algorithm

This project focuses on optimizing shared delivery routes to reduce transportation costs and improve efficiency. By leveraging a modified version of Dijkstra’s algorithm, we calculate the most cost-effective and shortest delivery paths while clustering nearby orders.

Traditional delivery models often result in inefficient routing and increased costs due to separate handling of individual orders. Our approach seeks to address these challenges by:

Minimizing overall delivery costs through shared transportation.
Optimizing delivery paths by considering order proximity and shortest distances.
Ensuring efficient capacity utilization to reduce the number of trips required.
This solution is particularly relevant for logistics, e-commerce, and supply chain management, where route efficiency directly impacts operational costs.

💡 Problem Statement & Objectives
Challenges in Traditional Delivery Models
Orders are often delivered individually, leading to high fuel consumption and increased delivery costs.
Delivery paths are not optimized for multiple orders, resulting in longer travel distances.
Delivery capacity is underutilized, requiring additional trips.
Proposed Solution
Our model addresses these inefficiencies by:
✅ Grouping nearby orders into clusters, allowing multiple deliveries per trip.
✅ Using real-world distance calculations to determine the most efficient routes.
✅ Optimizing vehicle capacity to minimize the number of delivery trips.
✅ Applying a modified version of Dijkstra’s algorithm to ensure optimal route selection.

By integrating these components, we aim to enhance the efficiency of last-mile delivery operations and significantly reduce logistics costs.

🛠️ Technologies Used
Python – Core programming language for algorithm development.
NetworkX – Graph-based routing and path optimization.
Geopy – Distance measurement for real-world coordinates.
Heapq – Efficient priority queue implementation for Dijkstra’s algorithm.
React.js – Frontend for route visualization.
Flask / FastAPI – Backend API services for processing delivery data.
MySQL / PostgreSQL – Database management for storing orders and clustering data.
📊 Methodology
1️⃣ Graph Representation
The system constructs a graph where:
Nodes represent clusters of delivery orders.
Edges represent distances between clusters.
A directed graph is created using NetworkX, incorporating properties such as capacity, distance, and cost-loss values.
2️⃣ Order Clustering
Orders are grouped based on geographic proximity and volume constraints.
A maximum delivery capacity is imposed to prevent inefficient resource allocation.
3️⃣ Modified Dijkstra’s Algorithm
We implement three variations of Dijkstra’s algorithm to identify the most efficient shared delivery routes:

Algorithm Version	Description
Version 1 (V1)	Uses a loss function (distance/capacity) to optimize shared deliveries.
Version 2 (V2)	Ensures each node is assigned a unique parent, except for the warehouse.
Version 3 (V3)	Selects the best possible parent based on the minimum loss among all paths.
4️⃣ Route Optimization & Cost Reduction
Orders are assigned to clusters based on proximity and shared delivery potential.
A weighted graph is constructed, with the warehouse serving as the starting node.
The modified Dijkstra algorithm executes, generating optimal paths with cost constraints.
Orders are consolidated into shared deliveries, minimizing the total number of trips required.

# connect to the database using mysql:
Open MySQL Workbench.
Click "New Connection".
Enter the following details:
Connection Name: Railway MySQL
Hostname: turntable.proxy.rlwy.net
Port: 21931
Username: root
Password: QidNZDIznmxgXewmxVnbzMVkFVZoyHZs
Default Schema (Optional): railway
Click "Test Connection".
If the test is successful, click OK.
mysql -u root -p -h turntable.proxy.rlwy.net -P 21931 railway
# To add:
1. add a function that after we build clusters checks if there is a cluster with capacity < max_capacity and send a notification for all users in the cliuster's radius. add a list of items the user can choose from. find how to prevent two users or more to fill the cluster. 


