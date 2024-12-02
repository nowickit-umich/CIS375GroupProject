import paramiko

# Filter_Manager class intended to add, delete, enable, disable, and send block lists to a server, the block lists are saved in this format:
# sample_list = {
#    'enabled': True,
#    'domain_names': [
#        {'name': 'www.google.com', 'block_mode': 'single_domain'},
#        {'name': 'www.youtube.com', 'block_mode': 'all_subdomains'}
#    ]
#}

class Filter_Manager:
    def __init__(self):
        self.block_list = [] # List of dictionaries containing individual block lists with an 'enabled' key and 'domain_names' key 
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
        
        with open('enabled_lists.txt', 'w') as f: # Loop over every enabled list and add an entry in the text file for each domain found in the list based on the specified block mode
            for list in enabled_lists:
                for domain in list['domain_names']:
                    domain_name = domain['name']
                    block_mode = domain['block_mode']

                    if block_mode == 'single_domain':
                        blocked_domain = f"address={domain_name}/"
                    else:  
                        blocked_domain = f"address=/{domain_name}/"

                    f.write(blocked_domain + '\n')

        try:
            
            key = paramiko.RSAKey.from_private_key_file("data/sshkey.pem")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(hostname=self.server_host, username="ubuntu", pkey=key)
            sftp = ssh.open_sftp()
            
            sftp_file_path = "/etc/dnsmasq.d/enabled_lists.txt"
            sftp.put('enabled_lists.txt', sftp_file_path)
            
            sftp.close()
            ssh.close()

            print("Enabled block lists successfully sent to the server.")

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

