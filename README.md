# Ketch

# 📝 Project Overview:

This project focuses on optimizing shared delivery routes to reduce transportation costs and improve efficiency. By leveraging a modified version of Dijkstra’s algorithm, we calculate the most cost-effective and shortest delivery paths while clustering nearby orders.

Traditional delivery models often result in inefficient routing and increased costs due to separate handling of individual orders. Our approach seeks to address these challenges by:

Minimizing overall delivery costs through shared transportation.

Optimizing delivery paths by considering order proximity and shortest distances.

Ensuring efficient capacity utilization to reduce the number of trips required.

This solution is particularly relevant for logistics, e-commerce, and supply chain management, where route efficiency directly impacts operational costs.

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


