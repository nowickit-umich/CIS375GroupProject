import socket
import pickle 

class Filter_Manager:
    def __init__(self):
        self.block_list = [] # List of dictionaries containing individual block lists
        self.server_host = 'localhost'  
        self.server_port = 44444

    def add_block_list(self, list): # Add a list to the list of block lists
        try:
            self.block_list.append(list)
        except Exception as e:
            print(f"Error adding block list: {e}")
            
    def delete_block_list(self, list): # Delete a list from the list of block lists
        try:
            self.block_list.remove(list)
        except Exception as e:
            print(f"Error deleting block list: {e}")
    
    def send_update(self): # Send all enabled block lists to the server

        enabled_lists = [] # Loop over all lists, and get only enabled lists
        for list in self.block_list:
            if(list['enabled'] == True):
                enabled_lists.append(list)

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.server_host, self.server_port)) 

            enabled_lists = pickle.dumps(enabled_lists)  # Encoding to send from client to server

            client.sendall(enabled_lists)  

            # client.close()  

        except Exception as e:
            print(f"Error sending update: {e}")

    
    def enable(self, list): # Enable list from list of block lists
        try:
            list['enabled'] = True

        except Exception as e:
            print(f"Error enabling block list: {e}")

    
    def disable(self, list): # Disable list from list of block lists
        try:
            list['enabled'] = False

        except Exception as e:
            print(f"Error disabling block list: {e}")

