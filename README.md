# Ketch
# 📦 Shared Delivery Optimization Using a Modified Dijkstra Algorithm
**there is a demo video available in the repostory under the name "demo".**

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
We implement three variations of Dijkstra’s algorithm to identify the most efficient shared delivery routes, in all three versions we aim to minimise the loss function that we defined as path distance / path capacity, on each version we use a different approach for finiding a distinct path from the warehouse to each node:  

| Algorithm Version | Description |
|-------------------|------------|
| **Version 1 (V1)** | we run a modified dijkstra were the relaxation condition is according to the new loss we defined. when combining the orders we check if a certain node (not the warehouse) has an out degree>1, we compare the loss of all its children if an edge was present directly from the warehouse. we keep the chil with max(loss from warehouse) as its child and for the rest we add a direct edge from the waregouse. returns a set of combined orders  |
| **Version 2 (V2)** | A modified version of Dijkstra that keeps track of nodes assigned as parents. It ensures that no two nodes share the same parent, except for the warehouse. Returns a set of combined orders. |
| **Version 3 (V3)** | This version assigns each node a parent by selecting the neighbor with the **minimal loss** among all available paths, ensuring distinct paths. Returns a set of combined orders. |

**After comparing the versions using huristic calculations, taking into account the loss and run time, we can see that the performance of version 1 is the best so we chose to use it in our app**

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
## 🗄️ Database Schema Overview  

The database is hosted on **Railway Cloud** using **MySQL**, ensuring **scalability and secure data management** for shared delivery optimization. It enables tracking of **active requests, clustered deliveries, and store inventory**, ensuring an optimized routing and cost-sharing model.  

### 📌 **Key Database Tables**  

- **`users`** – Stores user details, including name, email, location, and coordinates.  
- **`stores`** – Contains store information such as name, total capacity, and delivery fees.  
- **`items`** – Represents products available in stores, with capacity and pricing details.  
- **`active_requests`** – Tracks ongoing delivery requests, linking users, stores, and clusters.  
- **`request_items`** – Stores the items associated with each request.  
- **`combined_orders`** – Groups multiple requests into a **shared delivery order**.  
- **`clusters`** – Manages grouped orders based on **location, estimated pricing, and partner count**.  

### 🔗 **Database Hosting & Connection**  
The database is hosted on **Railway Cloud** with **MySQL**, allowing **remote access and efficient data handling**.  

To connect to the database using MySQL Workbench:  
1. Open **MySQL Workbench**.  
2. Click **"New Connection"**.  
3. Enter the following details:  
   - **Hostname**: `turntable.proxy.rlwy.net`  
   - **Port**: `21931`  
   - **Username**: `root`  
   - **Password**: `QidNZDIznmxgXewmxVnbzMVkFVZoyHZs`  
   - **Default Schema (Optional)**: `railway`  
4. Click **"Test Connection"** → **OK** if successful.  


## 📊 Algorithm Analyzer & Dijkstra Heuristics  

The **Algorithm Analyzer** evaluates the performance of the **Modified Dijkstra Algorithm** under different conditions. It tests multiple algorithm versions (`Base`, `V1`, `V2`, `V3`) by simulating random clusters with varying sizes and capacities. The module records key performance metrics such as:  
- **Path loss** (average & total).  
- **Node loss** for efficiency assessment.  
- **Number of orders processed**.  
- **Algorithm runtime performance**.  

### 📂 Results & Reports  
The results are saved in:  
- 📊 **Excel (`algorithm_analysis_results.xlsx`)** – Contains detailed data for running the different versions of dijkstra on 100 clusters.  
- 📄 **PDF Reports**:  
  - **`algorithm_analysis.pdf`** – Graph analysis of the data obtained fron runing the different versions of dijkstra on 100 clusters (generated when runing dijkstra_huristics.py).  
  - **`algorithm_analysis_50.pdf`** – Graph analysis of the data obtained fron runing the different versions of dijkstra on 50 clusters (generated when runing dijkstra_huristics.py).   

### 🏃 Running the Heuristics Analysis  
If you want to see how the **different Dijkstra versions** work with real examples, run:  
```sh
python dijkstra_huristics.py

```
## 🛠️ MultiStoreDeliveryScheduler
The **MultiStoreDeliveryScheduler** is responsible for handling scheduled clustering and routing jobs for deliveries. The scheduler executes two primary jobs every day:
- **Morning Clustering Job:** Runs at **9:00 AM**, grouping orders into clusters based on location and store capacity.
- **Evening Routing Job:** Runs at **9:00 PM**, adds new orders to clusters and optimizes delivery routes for the clusters using a modified Dijkstra algorithm.

### **Important Note for Running the Scheduler**
If you manually trigger the scheduler or adjust its timing, ensure that there is a **20-minute gap** between the morning clustering job and the evening routing job. This delay allows all clustering processes to complete before routing begins, ensuring the algorithm functions correctly and preventing data inconsistencies.

### Running the Scheduler
To run the **MultiStoreDeliveryScheduler**, follow these steps:
1. **Install Dependencies:** Ensure required packages are installed (`pip install -r requirements.txt`).
2. **Manually set Time:** update setup_scheduler function.
3. **Start the Scheduler:** Run the script (`python MultiStoreDeliveryScheduler.py`).
4. **Monitor Logs:** Check the terminal output or logs for job execution details.
5. **Shutdown the Scheduler:** Use **Ctrl+C** or terminate the process to stop the scheduler gracefully.

The scheduler ensures efficient order grouping and optimized delivery routes, reducing costs and improving delivery efficiency.

### setting global parameters for the scheduler
1. **version:** you can set the dijkstra version here, we set the default value to V1.
2. **radius:** this is the maximum radius for each cluster, you can manually change this value.
3. **show_map:** this is a boolean value, you can set it to be true if you want the clusters to appear on a map.
4. **reset_clusters:** this is a boolean value, if set to true it resets the clusetrs table in the database before running the morning scheduler.
5. **reset_status:** this is a boolean value, if set to true it resets the status column in the active_requests table in the database, for testing purposes (status=0:order is still in process, status=1 order is processed and sent to store)


# Frontend Setup and Instructions

## Running the Frontend Step by Step

1. Navigate to the frontend folder in the terminal:
   ```sh
   cd Frontend
   ```
2. Ensure that **npm** and **Vite.js** are installed in the frontend directory. and run ```npm install @react-oauth/google```.
3. Inside the directory, start the development server by running:
   ```sh
   npm run dev
   ```
4. A **Local Host** link should appear. Press **Ctrl + Click** on it to open the frontend in your browser.

## Website Instructions

1. **Login with Google:**
   - Logging in with your Google account is required to request an order.
   - Your location in the database will be saved as your current login location.
 
2. **Store Locations and User Settings:**
   - The site has **four stores**, all located in **New York**.
   - Upon logging in, you can change your location by providing **longitude** and **latitude**.
   - For the algorithm to function correctly, set your location to **New York**, as currently active requests and users in the database are based there. Otherwise, you may not see nearby orders.
     
3. **Order Status and Nearby Orders:**
   - Default orders are already available in **Order Status** and **Nearby Orders** so you can see how the site functions.
   - Once the algorithm runs and clusters are formed, new **Nearby Orders** will appear.
   - When you submit an order, it will be visible in **Order Status**.
   - Running **Dijkstra’s Algorithm** might change the status of orders(from listed to processed).

