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


### Proposed Solution
Our model addresses these inefficiencies by:
✅ **Grouping nearby orders into clusters**, allowing multiple deliveries per trip.  
✅ **Using real-world distance calculations** to determine the most efficient routes.  
✅ **Optimizing vehicle capacity** to minimize the number of delivery trips.  
✅ **Applying a modified version of Dijkstra’s algorithm** to ensure optimal route selection.

By integrating these components, we aim to enhance the efficiency of last-mile delivery operations and significantly reduce logistics costs.

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
We implement three variations of Dijkstra’s algorithm to identify the most efficient shared delivery routes:  

| Algorithm Version | Description |
|-------------------|------------|
| **Version 1 (V1)** | Modified Dijkstra version 1, where the loss function is **path distance / path capacity**. To ensure distinct paths, we filter the paths when combining the orders. Returns a set of combined orders. |
| **Version 2 (V2)** | A modified version of Dijkstra that keeps track of nodes assigned as parents. It ensures that no two nodes share the same parent, except for the warehouse. Returns a set of combined orders. |
| **Version 3 (V3)** | This version assigns each node a parent by selecting the neighbor with the **minimal loss** among all available paths, ensuring distinct paths. Returns a set of combined orders. |


### 4️⃣ Route Optimization & Cost Reduction
1. **Orders are assigned to clusters** based on proximity and shared delivery potential.
2. **A weighted graph is constructed**, with the warehouse serving as the starting node.
3. **The modified Dijkstra algorithm executes**, generating optimal paths with cost constraints.
4. **Orders are consolidated** into shared deliveries, minimizing the total number of trips required.

---

## 🛠️ Technologies Used
- **Python** – Core programming language for algorithm development.
- **NetworkX** – Graph-based routing and path optimization.
- **Geopy** – Distance measurement for real-world coordinates.
- **Heapq** – Efficient priority queue implementation for Dijkstra’s algorithm.
- **React.js** – Frontend for route visualization.
- **Flask** – Backend API services for processing delivery data.
- **MySQL** – Relational database used for storing order and cluster data.
- **Railway Cloud** – Cloud-based MySQL database hosting, providing secure and scalable data storage.
- **React.js** – Frontend framework for route visualization.  
- **Vite.js** – Fast build tool for frontend development.  
- **CSS** – Styling for frontend components.  
---

## 🗄️ Database Connection Guide  
This project uses a **Railway Cloud MySQL database** for data storage. Follow these steps to connect:

### Connect Using MySQL Workbench**
1. Open **MySQL Workbench**.
2. Click **"New Connection"**.
3. Enter the following details:  
   - **Connection Name**: `Railway MySQL`  
   - **Hostname**: `turntable.proxy.rlwy.net`  
   - **Port**: `21931`  
   - **Username**: `root`  
   - **Password**: `QidNZDIznmxgXewmxVnbzMVkFVZoyHZs`  
   - **Default Schema (Optional)**: `railway`  
4. Click **"Test Connection"**.
5. If the test is successful, click **OK**.


## 📊 Algorithm Analyzer & Dijkstra Heuristics  

The **Algorithm Analyzer** evaluates the performance of the **Modified Dijkstra Algorithm** under different conditions. It tests multiple algorithm versions (`Base`, `V1`, `V2`, `V3`) by simulating random clusters with varying sizes and capacities. The module records key performance metrics such as:  
- **Path loss** (average & total).  
- **Node loss** for efficiency assessment.  
- **Number of orders processed**.  
- **Algorithm runtime performance**.  

### 📂 Results & Reports  
The results are saved in:  
- 📊 **Excel (`algorithm_analysis_results.xlsx`)** – Contains detailed data for further analysis.  
- 📄 **PDF Reports**:  
  - **`algorithm_analysis.pdf`** – General performance analysis.  
  - **`algorithm_analysis_50.pdf`** – Analysis for 50 clusters.  
  - **`dijkstra_huristics.pdf`** – Evaluates different Dijkstra versions.  
  - **`algorithm_analysis.xlsx`** – Includes real-world analysis of **100 orders**.  

### 🏃 Running the Heuristics Analysis  
If you want to see how the **different Dijkstra versions** work with real examples, run:  
```sh
python dijkstra_huristics.py


