import db_methods
import mysql.connector
import random

# List of user data with name, email, and address
users = [
    # 🌆 New York Cluster
    ("John Doe", "john.doe@example.com", "Times Square, New York, USA"),
    ("Jane Smith", "jane.smith@example.com", "Empire State Building, New York, USA"),
    ("Alice Johnson", "alice.johnson@example.com", "Wall Street, New York, USA"),
    ("Bob Brown", "bob.brown@example.com", "Brooklyn Bridge, New York, USA"),
    ("Charlie Davis", "charlie.davis@example.com", "Central Park, New York, USA"),
    
    # 🏙️ Additional New York users (within 2.5 km of existing points)
    ("Michael Scott", "michael.scott@example.com", "Madison Square Garden, New York, USA"),  # Near Times Square
    ("Pam Beesly", "pam.beesly@example.com", "Bryant Park, New York, USA"),  # Near Empire State Building
    ("Jim Halpert", "jim.halpert@example.com", "One World Trade Center, New York, USA"),  # Near Wall Street
    ("Dwight Schrute", "dwight.schrute@example.com", "South Street Seaport, New York, USA"),  # Near Brooklyn Bridge
    ("Kevin Malone", "kevin.malone@example.com", "The Met Museum, New York, USA"),  # Near Central Park
    ("Oscar Martinez", "oscar.martinez@example.com", "Flatiron Building, New York, USA"),  # Near Madison Square Garden
    ("Angela Martin", "angela.martin@example.com", "Battery Park, New York, USA"),  # Near Wall Street
    ("Ryan Howard", "ryan.howard@example.com", "Columbus Circle, New York, USA"),  # Near Central Park
    ("Kelly Kapoor", "kelly.kapoor@example.com", "Grand Central Terminal, New York, USA"),  # Near Empire State Building
    ("Toby Flenderson", "toby.flenderson@example.com", "Hudson Yards, New York, USA"),  # Near Times Square
    ("Meredith Palmer", "meredith.palmer@example.com", "Union Square, New York, USA"),  # Near Flatiron Building
    ("Stanley Hudson", "stanley.hudson@example.com", "SoHo, New York, USA"),  # Near One World Trade Center
    
    # 🌉 San Francisco Cluster
    ("David Wilson", "david.wilson@example.com", "Golden Gate Bridge, San Francisco, USA"),
    ("Eva Martinez", "eva.martinez@example.com", "Alcatraz Island, San Francisco, USA"),
    ("Frank Lopez", "frank.lopez@example.com", "Silicon Valley, California, USA"),

    # 🏙️ Additional San Francisco users (within 2.5 km)
    ("Phyllis Vance", "phyllis.vance@example.com", "Fisherman’s Wharf, San Francisco, USA"),  # Near Alcatraz
    ("Andy Bernard", "andy.bernard@example.com", "Coit Tower, San Francisco, USA"),  # Near Golden Gate
    ("Darryl Philbin", "darryl.philbin@example.com", "Union Square, San Francisco, USA"),  # Near Market Street
    ("Creed Bratton", "creed.bratton@example.com", "Chinatown, San Francisco, USA"),  # Near Financial District
]





# Add each user one at a time
for name, email, address in users:
    db_methods.add_user(name, email, address)



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


db_methods.update_order_details_with_random_values()


