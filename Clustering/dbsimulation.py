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

    # Additional New York Users (Near Existing Clusters)
    ("Michael Scott", "michael.scott@example.com", "Madison Square Garden, New York, USA"),
    ("Pam Beesly", "pam.beesly@example.com", "Bryant Park, New York, USA"),
    ("Jim Halpert", "jim.halpert@example.com", "One World Trade Center, New York, USA"),
    ("Dwight Schrute", "dwight.schrute@example.com", "South Street Seaport, New York, USA"),
    ("Kevin Malone", "kevin.malone@example.com", "The Met Museum, New York, USA"),
    ("Oscar Martinez", "oscar.martinez@example.com", "Flatiron Building, New York, USA"),
    ("Angela Martin", "angela.martin@example.com", "Battery Park, New York, USA"),
    ("Ryan Howard", "ryan.howard@example.com", "Columbus Circle, New York, USA"),
    ("Kelly Kapoor", "kelly.kapoor@example.com", "Grand Central Terminal, New York, USA"),
    ("Toby Flenderson", "toby.flenderson@example.com", "Hudson Yards, New York, USA"),
    ("Meredith Palmer", "meredith.palmer@example.com", "Union Square, New York, USA"),
    ("Stanley Hudson", "stanley.hudson@example.com", "SoHo, New York, USA"),
    ("Darryl Philbin", "darryl.philbin@example.com", "Lower East Side, New York, USA"),
    ("Erin Hannon", "erin.hannon@example.com", "Chinatown, New York, USA"),
    ("Andy Bernard", "andy.bernard@example.com", "Washington Square Park, New York, USA"),
    ("Phyllis Vance", "phyllis.vance@example.com", "Little Italy, New York, USA"),
    ("Creed Bratton", "creed.bratton@example.com", "Greenwich Village, New York, USA"),
    ("Jan Levinson", "jan.levinson@example.com", "Chelsea Market, New York, USA"),
    ("Holly Flax", "holly.flax@example.com", "West Village, New York, USA"),
    ("Gabe Lewis", "gabe.lewis@example.com", "Rockefeller Plaza, New York, USA"),
    ("Karen Filippelli", "karen.filippelli@example.com", "Bowery, New York, USA"),
    ("Roy Anderson", "roy.anderson@example.com", "Fifth Avenue, New York, USA"),
    ("David Wallace", "david.wallace@example.com", "Upper West Side, New York, USA"),
    ("Clark Green", "clark.green@example.com", "Meatpacking District, New York, USA"),
    ("Pete Miller", "pete.miller@example.com", "East Village, New York, USA"),
    ("Nate Nickerson", "nate.nickerson@example.com", "Tribeca, New York, USA"),
    ("Jo Bennett", "jo.bennett@example.com", "Financial District, New York, USA"),
    ("Robert California", "robert.california@example.com", "Murray Hill, New York, USA"),
    ("Todd Packer", "todd.packer@example.com", "Gramercy Park, New York, USA"),
    ("Mose Schrute", "mose.schrute@example.com", "Stuyvesant Town, New York, USA"),
    ("Devon White", "devon.white@example.com", "Hudson River Park, New York, USA"),
    ("Cathy Simms", "cathy.simms@example.com", "Carnegie Hall, New York, USA"),
    ("Hank Tate", "hank.tate@example.com", "Radio City Music Hall, New York, USA"),
    
    # 🌉 San Francisco Cluster
    ("David Wilson", "david.wilson@example.com", "Golden Gate Bridge, San Francisco, USA"),
    ("Eva Martinez", "eva.martinez@example.com", "Alcatraz Island, San Francisco, USA"),
    ("Frank Lopez", "frank.lopez@example.com", "Silicon Valley, California, USA"),

    # Additional San Francisco Users (Within 2.5 km)
    ("Phyllis Vance", "phyllis.vance@example.com", "Fisherman’s Wharf, San Francisco, USA"),
    ("Andy Bernard", "andy.bernard@example.com", "Coit Tower, San Francisco, USA"),
    ("Darryl Philbin", "darryl.philbin@example.com", "Union Square, San Francisco, USA"),
    ("Creed Bratton", "creed.bratton@example.com", "Chinatown, San Francisco, USA"),
    ("Jo Bennett", "jo.bennett@example.com", "Embarcadero, San Francisco, USA"),
    ("Holly Flax", "holly.flax@example.com", "Lombard Street, San Francisco, USA"),
    ("Michael Scott", "michael.scott@example.com", "Haight-Ashbury, San Francisco, USA"),
    ("Pam Beesly", "pam.beesly@example.com", "Mission District, San Francisco, USA"),
    ("Jim Halpert", "jim.halpert@example.com", "Twin Peaks, San Francisco, USA"),
    ("Dwight Schrute", "dwight.schrute@example.com", "Marina District, San Francisco, USA"),
    ("Kevin Malone", "kevin.malone@example.com", "Golden Gate Park, San Francisco, USA"),
    ("Angela Martin", "angela.martin@example.com", "Presidio, San Francisco, USA"),
    ("Ryan Howard", "ryan.howard@example.com", "South Beach, San Francisco, USA"),
    ("Kelly Kapoor", "kelly.kapoor@example.com", "Russian Hill, San Francisco, USA"),
    ("Toby Flenderson", "toby.flenderson@example.com", "North Beach, San Francisco, USA"),
    ("Meredith Palmer", "meredith.palmer@example.com", "Japantown, San Francisco, USA"),
    ("Stanley Hudson", "stanley.hudson@example.com", "Financial District, San Francisco, USA"),
    ("Oscar Martinez", "oscar.martinez@example.com", "Tenderloin, San Francisco, USA"),
    ("Jan Levinson", "jan.levinson@example.com", "Nob Hill, San Francisco, USA"),
    ("Robert California", "robert.california@example.com", "SOMA, San Francisco, USA"),
    ("Clark Green", "clark.green@example.com", "Castro District, San Francisco, USA"),
    ("Pete Miller", "pete.miller@example.com", "Bayview, San Francisco, USA"),
    ("Nate Nickerson", "nate.nickerson@example.com", "Dogpatch, San Francisco, USA"),
    ("Roy Anderson", "roy.anderson@example.com", "Noe Valley, San Francisco, USA"),
    ("David Wallace", "david.wallace@example.com", "Bernal Heights, San Francisco, USA"),
    ("Todd Packer", "todd.packer@example.com", "Ocean Beach, San Francisco, USA"),
    ("Mose Schrute", "mose.schrute@example.com", "Balboa Park, San Francisco, USA"),
    ("Cathy Simms", "cathy.simms@example.com", "Fort Mason, San Francisco, USA"),
    ("Hank Tate", "hank.tate@example.com", "Alamo Square, San Francisco, USA"),
    ("Gabe Lewis", "gabe.lewis@example.com", "Pier 39, San Francisco, USA"),
]




'''
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
db_methods.create_items_table()
'''
#db_methods.add_user("Abdallah Saida", "abed.saida.9@gmail.com", "Herald Square, New York, USA")
