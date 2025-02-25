# Ketch
📝 Project Overview
In this project, we developed an optimized routing system that leverages a modified version of Dijkstra’s algorithm to efficiently manage and deliver orders from a warehouse to multiple clusters of customers.

Our approach ensures:
✅ Optimized delivery paths by minimizing cost using distance and capacity constraints.
✅ Efficient clustering to group deliveries in a way that reduces total transportation loss.
✅ Three different versions of Dijkstra's algorithm, each improving efficiency and accuracy.

This system is useful for logistics, e-commerce, and supply chain management, where efficient delivery is crucial.

💡 The Idea Behind the Project
Traditional shortest path algorithms, like Dijkstra's Algorithm, only focus on distance. However, in real-world logistics:

Capacity constraints exist (e.g., a truck can only carry a certain number of items).
Clusters of delivery points need to be optimized for better route planning.
Minimizing transportation loss (distance traveled vs. order capacity) is crucial.
🔹 Our Approach
We modified Dijkstra’s algorithm to incorporate both distance and capacity when choosing the optimal delivery route.
Orders are grouped into clusters, and delivery paths are generated to minimize the loss function:
𝐿
𝑜
𝑠
𝑠
=
𝑇
𝑜
𝑡
𝑎
𝑙
 
𝐷
𝑖
𝑠
𝑡
𝑎
𝑛
𝑐
𝑒
𝑇
𝑜
𝑡
𝑎
𝑙
 
𝐶
𝑎
𝑝
𝑎
𝑐
𝑖
𝑡
𝑦
Loss= 
TotalCapacity
TotalDistance
​
 
We tested three different versions of the algorithm to determine the most efficient routing strategy.

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


