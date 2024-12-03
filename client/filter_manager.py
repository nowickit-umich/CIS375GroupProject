import paramiko
import os

class FilterManager:
    def __init__(self):
        self.block_list = [] #list of block lists, containing name and enabled/disabled status
        self.server_host = 'localhost'  

    def get_block_lists(self):

        if os.path.exists('data/block/'): #check if path exists, if so, loop through directory and append all lists to block_list, disabled by default
            for list_name in os.listdir('data/block/'):
                    self.block_list.append({"name": list_name, "enabled": False})
        else:
            print("Error: block list path not found")


    def enable_list(self, list_name):
        
        for list in self.block_list: #iterate through block_list, if list_name is found, enable it, else, print error
            if list['name'] == list_name:
                list['enabled'] = True
                print(f"Enabled block list: {list_name}")
                return
        print(f"Error: block list {list_name} not found")

    def disable_list(self, list_name): #iterate through block_list, if list_name is found, disable it, else, print error

        for list in self.block_list:
            if list['name'] == list_name:
                list['enabled'] = False
                print(f"Disabled block list: {list_name}")
                return
        print(f"Error: block list {list_name} not found")


    def send_update(self):

        enabled_lists = [] #create list containing only enabled lists
        for list in self.block_list:
            if(list['enabled'] == True):
                enabled_lists.append(list)

        try:
            key = paramiko.RSAKey.from_private_key_file("data/sshkey.pem")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ssh.connect(hostname=self.server_host, username="ubuntu", pkey=key)
            sftp = ssh.open_sftp()

            for list in enabled_lists: #looping through enabled lists, copy the list and send to remote spot in server
                local_path = 'data/block/' + list['name']
                remote_path = '/etc/block/' + list['name']

                sftp.put(local_path, remote_path)

            sftp.close()
            ssh.close()

            print("Enabled block lists successfully sent to the server.")

        except Exception as e:
            print(f"Error sending update: {e}")

