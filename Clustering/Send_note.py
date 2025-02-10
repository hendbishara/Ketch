import smtplib
import mysql.connector
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import db_methods  # Your existing database helper methods
from Clustering.cluster_manager import ClusterManager  # Your existing ClusterManager class

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "abed.saida.9@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "uure mwja blac ghmf"  # Replace with app password

def send_email(to_email, subject, body):
    """ Sends an email via SMTP. """
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        
        print(f"Email sent successfully to {to_email}")

    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")

def notify_users_about_cluster_items(cluster):
    """
    Sends notifications to users near a cluster if the cluster has available capacity.
    """
    remaining_capacity = cluster.max_capacity - cluster.total_capacity
    if remaining_capacity <= 0:
        return  # No capacity left, no need to notify

    # Fetch available items that fit within the remaining capacity
    available_items = db_methods.get_items_below_capacity(remaining_capacity)
    if not available_items:
        return  # No available items

    item_list = "\n".join([f"- {item['name']} (Capacity: {item['capacity']})" for item in available_items])

    # Fetch nearby users within the cluster's radius
    nearby_users = db_methods.get_users_in_radius(cluster.centroid, cluster.radius_km)

    subject = "🚚 Delivery Opportunity: Join the Incoming Cluster Order!"
    email_body = f"""
    Hey there! 

    It looks like a delivery is scheduled for your area. If you'd like to join, 
    you can choose from the following available items:

    {item_list}

    Act fast before the capacity is full!
    """

    # Send emails to each nearby user
    for user in nearby_users:
        user_email = user["email"]
        send_email(user_email, subject, email_body)


