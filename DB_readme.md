# MySQL Database Schema - Railway 

## Overview
This document provides an updated summary of the MySQL database schema for the `railway` database. The schema includes seven main tables: `users`, `stores`, `items`, `active_requests`, `request_items`, `clusters`, and `combined_orders`. These tables support user accounts, store inventories, clustering, and order processing.

---

## Tables and Relationships

### 1️⃣ Users Table (`users`)
Stores user account details.

| Column      | Type     | Description |
|------------|---------|-------------|
| `user_id`   | INT (PK)  | Unique user identifier. |
| `user_name` | VARCHAR(100) | Username (cannot be NULL). |
| `password`  | VARCHAR(255) | Encrypted password. |
| `location`  | VARCHAR(255) | User’s delivery location (optional). |
| `picture`   | BLOB     | Profile picture (optional). |
| `latitude`  | DECIMAL(9,6) | User’s latitude (optional). |
| `longitude` | DECIMAL(9,6) | User’s longitude (optional). |
| `email`     | VARCHAR(255) | User email address (optional). |

🔹 **Relation:**
- `user_id` is referenced in `active_requests` to link a request to a user.

---

### 2️⃣ Stores Table (`stores`)
Stores details of various stores.

| Column               | Type       | Description |
|----------------------|-----------|-------------|
| `store_id`          | INT (PK)  | Unique store identifier. |
| `store_name`        | VARCHAR(100) | Name of the store. |
| `total_capacity`    | INT       | Total item storage capacity. |
| `warehouse_location`| TEXT      | Store’s warehouse location. |
| `delivery_fee`      | DECIMAL(10,2) | Delivery fee charged by the store. |
| `latitude`          | FLOAT     | Store latitude. |
| `longitude`         | FLOAT     | Store longitude. |

🔹 **Relation:**
- `store_id` is referenced in:
  - `items` (to assign items to a store).
  - `active_requests` (to link orders to a store).
  - `clusters` (to associate stores with clusters).

---

### 3️⃣ Items Table (`items`)
Stores product details available in different stores.

| Column     | Type       | Description |
|-----------|-----------|-------------|
| `item_id` | INT (PK)  | Unique item identifier. |
| `store_id`| INT (FK)  | The store where the item is available. |
| `capacity`| INT       | Number of units available. |
| `price`   | DECIMAL(10,2) | Price per unit of the item. |

🔹 **Relation:**
- `store_id` links an item to a store in the `stores` table.
- `item_id` is referenced in `request_items` to track orders.

---

### 4️⃣ Active Requests Table (`active_requests`)
Manages customer orders.

| Column         | Type       | Description |
|---------------|-----------|-------------|
| `req_id`      | INT (PK)  | Unique request identifier. |
| `user_id`     | INT (FK)  | User who placed the request. |
| `store_id`    | INT (FK)  | Store fulfilling the request. |
| `max_wait`    | INT       | Maximum wait time allowed for the order. |
| `status`      | TINYINT   | Request status (`0` default). |
| `cluster_id`  | INT       | Grouping of requests (`-1` default). |
| `time_stamp`  | TIMESTAMP | Request creation time. |
| `delivery_price` | DECIMAL(10,2) | Total delivery price for the order. |
| `final_delivery_fee` | FLOAT | Final computed delivery fee. |
| `process_date` | DATE | Date when the request was processed. |

🔹 **Relation:**
- `user_id` links to `users` (request is made by a user).
- `store_id` links to `stores` (request is sent to a store).
- `req_id` is referenced in `request_items` to track which items belong to the request.

---

### 5️⃣ Request Items Table (`request_items`)
Links requests with ordered items.

| Column     | Type       | Description |
|-----------|-----------|-------------|
| `req_id`  | INT (FK)  | The request that contains the item. |
| `item_id` | INT (FK)  | The ordered item. |
| `quantity`| INT       | Number of units ordered (default `1`). |

🔹 **Relation:**
- `req_id` links to `active_requests` (order that contains the item).
- `item_id` links to `items` (item that was ordered).

---

### 6️⃣ Clusters Table (`clusters`)
Groups stores into clusters based on location.

| Column         | Type       | Description |
|---------------|-----------|-------------|
| `store_id`    | INT (PK)  | Unique store identifier. |
| `cluster_id`  | INT (PK)  | Cluster identifier. |
| `latitude`    | DECIMAL(9,6) | Cluster latitude. |
| `longitude`   | DECIMAL(9,6) | Cluster longitude. |
| `partners_number` | INT | Number of partners in the cluster. |
| `expected_price` | FLOAT | Expected price for deliveries in the cluster. |

🔹 **Relation:**
- `store_id` links to `stores`.
- Used to group stores together for optimized delivery.

---

### 7️⃣ Combined Orders Table (`combined_orders`)
Links multiple requests to a single order.

| Column     | Type       | Description |
|-----------|-----------|-------------|
| `order_id` | INT (PK)  | Unique order identifier. |
| `req_id`   | INT (PK)  | Request linked to the order. |

🔹 **Relation:**
- `req_id` links to `active_requests` (requests grouped into an order).

---

## 🔗 Relationships Between Tables
```
Users ───(1:M)─── Active_Requests ───(M:1)─── Stores
           │                            │
           │                            └───(1:M)─── Items
           │
           └───(1:M)─── Request_Items ───(M:1)─── Items

Stores ───(M:1)─── Clusters
Active_Requests ───(M:1)─── Combined_Orders
```
![image](https://github.com/user-attachments/assets/774cdd04-df48-4d9e-870a-43a2b3e16e31)

### **🚀 Summary of System Workflow**
- **Users** place **requests** (`active_requests`) to stores.
- Each **request** contains **items** (`request_items`).
- Each **item** belongs to a **store** (`stores`).
- Stores are grouped into **clusters** for optimization.
- Requests can be grouped into **combined orders** (`combined_orders`).
- A **delivery price** is calculated for each request.

for more details see readme
