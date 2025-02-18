# MySQL Database Schema - Railway

## Overview
This document provides a summary of the MySQL database schema for the `railway` database. The schema includes five main tables: `users`, `stores`, `items`, `active_requests`, and `request_items`. These tables are structured to support user accounts, store inventories, and order processing.

---

## Tables and Relationships

### 1️⃣ Users Table (`users`)
Stores user account details.

| Column      | Type     | Description |
|------------|---------|-------------|
| `user_id`   | INT (PK)  | Unique user identifier. |
| `user_name` | VARCHAR  | Username (cannot be NULL). |
| `password`  | VARCHAR  | Encrypted password. |
| `location`  | VARCHAR  | User’s delivery location (optional). |
| `picture`   | BLOB     | Profile picture (optional). |

🔹 **Relation:**
- `user_id` is referenced in `active_requests` to link a request to a user.

---

### 2️⃣ Stores Table (`stores`)
Stores details of various stores.

| Column               | Type       | Description |
|----------------------|-----------|-------------|
| `store_id`          | INT (PK)  | Unique store identifier. |
| `store_name`        | VARCHAR   | Name of the store. |
| `total_capacity`    | INT       | Total item storage capacity. |
| `warehouse_location`| TEXT      | Store’s warehouse location. |
| `delivery_fee`      | DECIMAL   | Delivery fee charged by the store. |

🔹 **Relation:**
- `store_id` is referenced in:
  - `items` (to assign items to a store).
  - `active_requests` (to link orders to a store).

---

### 3️⃣ Items Table (`items`)
Stores product details available in different stores.

| Column     | Type       | Description |
|-----------|-----------|-------------|
| `item_id` | INT (PK)  | Unique item identifier. |
| `store_id`| INT (FK)  | The store where the item is available. |
| `capacity`| INT       | Number of units available. |
| `price`   | DECIMAL   | Price per unit of the item. |

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
| `total_capacity` | INT    | Total number of items in request. |
| `max_wait`    | INT       | Maximum wait time allowed for the order. |
| `status`      | TINYINT   | Request status (`0` default). |
| `cluster_id`  | INT       | Grouping of requests (`-1` default). |
| `time_stamp`  | TIMESTAMP | Request creation time (auto). |
| `delivery_price` | DECIMAL | Total delivery price for the order. |

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

## 🔗 Relationships Between Tables
```
Users ───(1:M)─── Active_Requests ───(M:1)─── Stores
           │                            │
           │                            └───(1:M)─── Items
           │
           └───(1:M)─── Request_Items ───(M:1)─── Items
```

### **🚀 Summary of System Workflow**
- **Users** place **requests** (`active_requests`) to stores.
- Each **request** contains **items** (`request_items`).
- Each **item** belongs to a **store** (`stores`).
- A **delivery price** is calculated for each request.


