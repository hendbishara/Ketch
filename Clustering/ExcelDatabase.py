import pandas as pd
from datetime import datetime

class ExcelDatabase:
    def __init__(self, file_path):
        self.file_path = file_path

        # Check if the file exists, otherwise create an empty DataFrame and save it
        try:
            pd.read_excel(self.file_path)
        except FileNotFoundError:
            df = pd.DataFrame(columns=["ID", "Username", "Email", "Password", "Created_At","Address"])
            df.to_excel(self.file_path, index=False)

    def add_user(self, username, email, password, address):
        """Add a new user to the database."""
        data = pd.read_excel(self.file_path)

        new_user = {
            "ID": len(data) + 1,
            "Username": username,
            "Email": email,
            "Password": password,
            "Address": address,
            "Created_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        data = data.append(new_user, ignore_index=True)
        data.to_excel(self.file_path, index=False)
        return "User added successfully!"

    def get_users(self):
        """Retrieve all users as a DataFrame."""
        return pd.read_excel(self.file_path)

    def get_user_by_email(self, email):
        """Retrieve a user by email."""
        data = pd.read_excel(self.file_path)
        user = data[data["Email"] == email]
        return user if not user.empty else None
    
    def get_user_by_address(self,address):
        data = pd.read_excel(self.file_path)
        address = data[data["Address"] == address]
        return address if not address.empty else None

    def delete_user(self, user_id):
        """Delete a user by ID."""
        data = pd.read_excel(self.file_path)
        data = data[data["ID"] != user_id]
        data.to_excel(self.file_path, index=False)
        return "User deleted successfully!"
