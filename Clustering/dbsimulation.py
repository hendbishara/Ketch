import db_methods
import mysql.connector

# List of user data with name, email, and address
users = [
    ("John Doe", "john.doe@example.com", "Times Square, New York, USA"),
    ("Jane Smith", "jane.smith@example.com", "Empire State Building, New York, USA"),
    ("Alice Johnson", "alice.johnson@example.com", "Wall Street, New York, USA"),
    ("Bob Brown", "bob.brown@example.com", "Brooklyn Bridge, New York, USA"),
    ("Charlie Davis", "charlie.davis@example.com", "Central Park, New York, USA"),
    ("David Wilson", "david.wilson@example.com", "Golden Gate Bridge, San Francisco, USA"),
    ("Eva Martinez", "eva.martinez@example.com", "Alcatraz Island, San Francisco, USA"),
    ("Frank Lopez", "frank.lopez@example.com", "Silicon Valley, California, USA"),
    ("Grace Taylor", "grace.taylor@example.com", "Rockefeller Center, New York, USA"),
    ("Hank Anderson", "hank.anderson@example.com", "Broadway, New York, USA")
]


'''
# Add each user one at a time
for name, email, address in users:
    db_methods.add_user(name, email, address)
'''


def create_orders_for_all_users():
    # Step 1: Retrieve all users from the users table
    users = db_methods.get_all_users()

    # Step 2: Generate an order for each user and insert it into the orders table
    for user in users:
        user_id, name, email, address, latitude, longitude = user

        # Create a simple order for each user (you can customize the order details)
        order_details = f"Order details for {name} at {address}"

        # Step 3: Insert the order into the orders table
        #db_methods.add_new_order(user_id, order_details)
        order_id = user_id
        db_methods.add_new_order(order_id, user_id, order_details, latitude, longitude)

        print(f"Order created for {name} with user ID {user_id}.")

# Call the function to generate orders for all users
create_orders_for_all_users()

