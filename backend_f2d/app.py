from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from geopy.distance import geodesic
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MySQL Database Connection Configuration
def get_db_connection():
    return mysql.connector.connect(
        host="turntable.proxy.rlwy.net",
        user="root",
        password="QidNZDIznmxgXewmxVnbzMVkFVZoyHZs",
        database="railway",
        port=21931,
        connection_timeout=30
    )

def calculate_delivery_fee(user_id, store_id):
    """Fetches user/store locations, calculates distance using geopy, and determines delivery fee."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get user coordinates
        cursor.execute("SELECT latitude, longitude FROM users WHERE user_id = %s", (user_id,))
        user_location = cursor.fetchone()
        print(f"🟢 User ID: {user_id}, Location Data: {user_location}")

        if not user_location or None in user_location:
            print(f"❌ Error: User ID {user_id} not found or has NULL coordinates")
            return None, f"User ID {user_id} not found or has missing location"

        user_lat, user_lon = map(float, user_location)  # Convert Decimal to float

        # Get store coordinates and delivery fee per km
        cursor.execute("SELECT latitude, longitude, delivery_fee FROM stores WHERE store_id = %s", (store_id,))
        store_data = cursor.fetchone()
        print(f"🟢 Store ID: {store_id}, Store Data: {store_data}")

        if not store_data or None in store_data:
            print(f"❌ Error: Store ID {store_id} not found or has NULL coordinates")
            return None, f"Store ID {store_id} not found or has missing location"

        store_lat, store_lon, delivery_fee_per_km = store_data
        store_lat, store_lon, delivery_fee_per_km = float(store_lat), float(store_lon), float(delivery_fee_per_km)  # Convert Decimal to float

        # Compute distance using geopy
        distance_km = geodesic((user_lat, user_lon), (store_lat, store_lon)).km
        print(f"📏 Distance between User {user_id} and Store {store_id}: {distance_km:.2f} km")

        # Compute total delivery fee
        total_fee = round(distance_km * delivery_fee_per_km, 2)
        print(f"💰 Calculated Delivery Fee: ${total_fee}")

        return total_fee, None

    except Exception as e:
        print("❌ Error in delivery fee calculation:", e)
        return None, "Error calculating delivery fee"

    finally:
        cursor.close()
        conn.close()

@app.route("/api/request", methods=["POST"])
def request_order():
    """Handles a new order request, validates items, and saves the order in `active_requests` and `requested_items` tables."""
    data = request.json
    user_id = data.get("userId")
    store_id = data.get("storeId")
    max_wait = data.get("timeToWait", 0)  # Get max_wait from request
    items = data.get("items", [])  # Get list of items

    if not user_id or not store_id or not items:
        return jsonify({"error": "Missing required fields or items"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ Validate that all item numbers exist in the `items` table
        item_numbers = [item["itemNumber"] for item in items]
        cursor.execute("SELECT item_id FROM items WHERE store_id = %s AND item_id IN (%s)" % (
            store_id, ','.join(['%s'] * len(item_numbers))
        ), tuple(item_numbers))

        valid_items = set(row[0] for row in cursor.fetchall())
        invalid_items = [item for item in item_numbers if item not in valid_items]

        if invalid_items:
            return jsonify({"error": "Invalid item numbers", "invalidItems": invalid_items}), 400

        # ✅ Get the last request ID and increment it for the new request
        cursor.execute("SELECT COALESCE(MAX(req_id), 0) + 1 FROM active_requests")
        new_req_id = cursor.fetchone()[0]

        # ✅ Calculate delivery fee
        delivery_price, error = calculate_delivery_fee(user_id, store_id)
        if error:
            return jsonify({"error": error}), 400  # Return error if fee calculation fails

        # ✅ Insert the request into `active_requests`
        cursor.execute("""
            INSERT INTO active_requests 
            (req_id, user_id, store_id, max_wait, status, cluster_id, time_stamp, delivery_price, final_delivery_fee, process_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (new_req_id, user_id, store_id, max_wait, 0, -1, datetime.now(), delivery_price, 0, None))

        # ✅ Insert items into `requested_items`
        for item in items:
            cursor.execute("""
                INSERT INTO request_items (req_id, item_id, quantity) 
                VALUES (%s, %s, %s)
            """, (new_req_id, item["itemNumber"], item["quantity"]))

        conn.commit()

        return jsonify({"success": True, "message": "Order request submitted successfully!"})

    except mysql.connector.Error as e:
        print("❌ Database Error:", e)
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        print("❌ Unexpected Error:", e)
        return jsonify({"error": "Server error"}), 500

    finally:
        cursor.close()
        conn.close()




@app.route("/api/nearby-orders", methods=["GET"])
def get_nearby_orders():
    """Fetches clusters within 1.2km of the logged-in user and returns relevant order details,
       while excluding orders made by the user themselves."""
    user_id = request.args.get("userId", type=int)

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get logged-in user's location
        cursor.execute("SELECT latitude, longitude FROM users WHERE user_id = %s", (user_id,))
        user_location = cursor.fetchone()

        if not user_location:
            return jsonify({"error": "User not found"}), 400

        user_lat, user_lon = float(user_location[0]), float(user_location[1])
        print(f"📍 Logged-in User {user_id} Location: ({user_lat}, {user_lon})")

        # Get clusters excluding the ones the user has already requested
        cursor.execute("""
            SELECT c.store_id, c.cluster_id, c.latitude, c.longitude, c.partners_number, c.expected_price
            FROM clusters c
            WHERE c.cluster_id NOT IN (
                SELECT DISTINCT ar.cluster_id FROM active_requests ar WHERE ar.user_id = %s
            )
        """, (user_id,))

        clusters = cursor.fetchall()

        nearby_orders = []
        store_names = {1: "AllModern", 2: "Room&Board", 3: "West Elm", 4: "Living Spaces"}

        for cluster in clusters:
            store_id, cluster_id, cluster_lat, cluster_lon, partners_number, expected_price = cluster
            cluster_lat, cluster_lon, expected_price = float(cluster_lat), float(cluster_lon), float(expected_price)

            # Calculate distance between user and cluster
            distance_km = geodesic((user_lat, user_lon), (cluster_lat, cluster_lon)).km
            print(f"📏 Cluster {cluster_id} - Distance: {distance_km:.2f} km")

            if distance_km <= 1.2:  # Filter orders within 1.2km
                # Calculate delivery fee
                delivery_fee, error = calculate_delivery_fee(user_id, store_id)
                if error:
                    print(f"❌ Error calculating delivery fee for store {store_id}: {error}")
                    continue  # Skip if fee calculation fails

                delivery_fee = max(delivery_fee, 50)  # Ensure minimum delivery fee
                
                # Add order to response
                nearby_orders.append({
                    "storeName": store_names.get(store_id, "Unknown Store"),
                    "originalPrice": delivery_fee,
                    "discountedPrice": expected_price,
                    "partnersNumber": partners_number
                })

        print(f"✅ Found {len(nearby_orders)} nearby orders for user {user_id}, excluding their own orders.")

        return jsonify({"nearbyOrders": nearby_orders})

    except Exception as e:
        print("❌ Error in fetching nearby orders:", e)
        return jsonify({"error": "Failed to fetch nearby orders"}), 500

    finally:
        cursor.close()
        conn.close()



@app.route("/api/user-orders", methods=["GET"])
def get_user_orders():
    """Fetch active requests for a given user and return order details."""
    user_id = request.args.get("userId", type=int)

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch user's active requests and join with the stores table for store names
        cursor.execute("""
            SELECT ar.req_id, ar.store_id, ar.status, ar.time_stamp, ar.process_date, s.store_name
            FROM active_requests ar
            JOIN stores s ON ar.store_id = s.store_id
            WHERE ar.user_id = %s
        """, (user_id,))
        
        active_requests = cursor.fetchall()

        if not active_requests:
            return jsonify({"orders": []})  # Return empty if no orders exist

        # Store logos mapping
        store_logos = {
            "AllModern": "/assets/AllModern_logo.png",
            "Living Spaces": "/assets/living_spaces_logo.png",
            "Room&Board": "/assets/room&board_logo.png",
            "West Elm": "/assets/west_elm_logo.jpeg",
        }

        # Process active requests into a structured response
        user_orders = []
        for req_id, store_id, status, time_stamp, process_date, store_name in active_requests:
            order_status = "Order Listed" if status == 0 else "Order Processed"
            progress = 25 if status == 0 else 75  # 25% if listed, 75% if processed
            order_date = time_stamp.strftime("%m/%d/%y") if status == 0 else process_date.strftime("%m/%d/%y") if process_date else "N/A"
            logo = store_logos.get(store_name, "/assets/default_logo.png")

            user_orders.append({
                "id": req_id,
                "status": order_status,
                "progress": progress,
                "orderDate": order_date,
                "shop": store_name,
                "logo": logo
            })

        return jsonify({"orders": user_orders})

    except Exception as e:
        print("❌ Error in fetching user orders:", e)
        return jsonify({"error": "Failed to fetch user orders"}), 500

    finally:
        cursor.close()
        conn.close()



@app.route("/api/google-login", methods=["POST"])
def google_login():
    data = request.json
    email = data.get("email")
    name = data.get("name")
    profile_picture = data.get("profile_picture")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            user_id = user[0]

            # Update user location if needed
            cursor.execute("UPDATE users SET latitude = %s, longitude = %s WHERE user_id = %s",
                           (latitude, longitude, user_id))
            conn.commit()
        else:
            # Insert new user with an empty password
            cursor.execute("""
                INSERT INTO users (user_name, email, password, picture, latitude, longitude)
                VALUES (%s, %s, '', %s, %s, %s)
            """, (name, email, profile_picture, latitude, longitude))
            conn.commit()
            user_id = cursor.lastrowid  # Get new user ID

        return jsonify({"userId": user_id})

    except mysql.connector.Error as e:
        print("❌ Database Error:", e)
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        print("❌ Unexpected Error:", e)
        return jsonify({"error": "Server error"}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/api/update-location", methods=["POST"])
def update_location():
    """Updates user's location in the database based on manual input."""
    data = request.json
    user_id = data.get("userId")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not user_id or latitude is None or longitude is None:
        return jsonify({"error": "Missing user ID or location"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET latitude = %s, longitude = %s WHERE user_id = %s",
                       (latitude, longitude, user_id))
        conn.commit()

        return jsonify({"success": True, "message": "Location updated successfully!"})

    except mysql.connector.Error as e:
        print("❌ Database Error:", e)
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        print("❌ Unexpected Error:", e)
        return jsonify({"error": "Server error"}), 500

    finally:
        cursor.close()
        conn.close()




if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
