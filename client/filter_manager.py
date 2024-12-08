import paramiko
import os
import logging
logger = logging.getLogger(__name__)

class Filter_Manager:
    '''
        Description: Manages the filters  of the VPN server by maintaining a list across sessions, and allowing the ability to enable and disable them.
    '''
    def __init__(self, server_address="localhost"):
        self.block_list = [] #list of block lists = dicts containing name and enabled/disabled status
        self.server_host = server_address #server address passed as parameter when instance of filter manager created
        self.is_updated = False
        # initialize block lists
        self.get_block_lists()

    def get_block_lists(self):
        '''
        Description: Searches the block list directory(data/block/) and appends all block lists to block_list and sets them to disabled by default
        
        return: None
        '''
        if os.path.exists('data/block/'): #check if path exists, if so, loop through directory and append all lists to block_list, disabled by default
            for list_name in os.listdir('data/block/'):
                # verify extension
                if list_name.endswith(".block"):
                    # add list
                    self.block_list.append({"name": list_name, "enabled": False})
                    logger.debug(f"Found Client block list {list_name}")
        else:
            logger.error("Block list path not found")

    def enable_list(self, list_name):
        '''
        Description: Searches block_list for the given list_name, and if it is found, enable it.

        param list_name: a given list found in block_list
        return: None
        '''
        for list in self.block_list: #iterate through block_list, if list_name is found, enable it, else, print error
            if list['name'] == list_name + ".block":
                list['enabled'] = True
                logger.info(f"Enabled block list: {list_name}")
                return
        logger.error(f"Block list {list_name} not found")

    def disable_list(self, list_name): 
        '''
        Description: Searches block_list for the given list_name, and if it is found, disable it.

        param list_name: a given list found in block_list
        return: None
        '''
        for list in self.block_list:  #iterate through block_list, if list_name is found, disable it, else, print error
            if list['name'] == list_name + ".block":
                list['enabled'] = False
                logger.info(f"Disabled block list: {list_name}")
                return
        logger.error(f"Block list {list_name} not found")

    def send_update(self):
        '''
        Description: Function used to pass enabled lists to the server, and passes empty files to the server for disabled lists.

        return: None
        '''
        enabled_lists = [] #create list containing only enabled lists
        disabled_lists = [] #create list containing only disabled lists
        for list in self.block_list:
            if(list['enabled'] == True):
                enabled_lists.append(list)
            elif (list['enabled'] == False):
                disabled_lists.append(list)

        try:
            key = paramiko.RSAKey.from_private_key_file("data/sshkey.pem")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ssh.connect(hostname=self.server_host, username="ubuntu", pkey=key)
            sftp = ssh.open_sftp()
            try:
                sftp.stat('/home/ubuntu/dnsmasq/')
            except:
                sftp.mkdir('/home/ubuntu/dnsmasq/')

            for list in enabled_lists: #looping through enabled lists, copy the list and send to remote spot in server
                local_path = 'data/block/' + list['name']
                remote_path = '/home/ubuntu/dnsmasq/' + list['name']

                sftp.put(local_path, remote_path)

            for list in disabled_lists: #looping through disabled lists, copy an empty list, and send to the server
                local_path = 'data/block/empty.txt'
                remote_path = '/home/ubuntu/dnsmasq/' + list['name']

                sftp.put(local_path, remote_path)
            
            sftp.put('data/block/empty.txt', '/home/ubuntu/dnsmasq/flag')
            sftp.close()
            ssh.close()

            logger.info("Enabled block lists successfully sent to the server.")

        except Exception as e:
            logger.error(f"Error sending update: {e}")
            sftp.close()
            ssh.close()
    
    def get_server_lists(self):
        '''
        Description: Function used to get the current lists found in the server if they have been updated in the past.

        return: None
        '''
        if not self.is_updated:
            # ensure server files are consistent with client
            self.send_update()
            self.is_updated = True
            return
        current_block_list = []
        key = paramiko.RSAKey.from_private_key_file("data/sshkey.pem")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(hostname=self.server_host, username="ubuntu", pkey=key)
        sftp = ssh.open_sftp()
        try:
            lists = sftp.listdir_attr('/home/ubuntu/dnsmasq/')
        except Exception as e:
            logger.error(f"Unable to get server block lists {e}")

        for list in lists:
            # skip non block files
            if not list.filename.endswith(".block"):
                logger.debug(f"Skipping file {list.filename}")
                continue
            if list.st_size == 0:
                current_block_list.append({"name": list.filename, "enabled": False})
                logger.debug(f"{list.filename}: Disabled")
            else:
                current_block_list.append({"name": list.filename, "enabled": True})
                logger.debug(f"{list.filename}: Enabled")
                
        self.block_list = current_block_list
        sftp.close()
        ssh.close()

