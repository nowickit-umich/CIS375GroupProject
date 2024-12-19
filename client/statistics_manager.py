import paramiko
import os
from platformdirs import user_data_dir
app_name = "CIS375VPN"
import logging
logger = logging.getLogger(__name__)

class Stats_Manager:

    '''
    Description: Manages and tracks various statistics related to DNS requests, VPN status, server status, and filter settings. 
    Provides methods for retrieving and processing data such as blocked domains, top visited domains, and DNS logs. 

    '''
    def __init__(self):
        # Initialize data structures for statistics
        self.dns_data_list={}
        # Placeholder for domain statistics
        self.blocked_domains = []
        # Top 10 visited domains, ranked by traffic
        self.top_visited = []
        self.top_blocked = []    
        self.data_total = []

    def get_blocked_domains(self):
        # Iterate through the DNS data and return a list of blocked domains (denied > 0)
        self.blocked_domains.clear()  # Clear previous list
        for domain, data in self.dns_data_list.items():
            if data['denied'] > 0:
                self.blocked_domains.append({'domain': domain})
        return self.blocked_domains

    def get_top_visited(self):
        # Sort the domains based on the 'allowed' count in descending order
        sorted_domains = sorted(self.dns_data_list.items(), key=lambda item: item[1]['allowed'], reverse=True)

        # Get the top 10 domains based on allowed requests
        self.top_visited = [{"domain": domain, "traffic": data['allowed']} for domain, data in sorted_domains[:10]]

        return self.top_visited
    
    def get_top_blocked_domains(self):
    # Sort the domains based on the 'denied' count in descending order
        sorted_domains = sorted(self.dns_data_list.items(), key=lambda item: item[1]['denied'], reverse=True)
    
    # Get the top 10 domains based on denied requests, only append if denied > 0
        self.top_blocked = [{"domain": domain, "denied": data['denied']} 
                        for domain, data in sorted_domains[:10] if data['denied'] > 0]

        return self.top_blocked

    def get_total_data(self):
        self.data_total = []
        # Iterate through the dns_data_list to calculate the total data
        for domain, data in self.dns_data_list.items():
            if data ['denied'] > 0:
                total_data = 5 * data['denied']  # 5 MB per denied request
                self.data_total.append({"domain":domain,"total_data":total_data})  # Store in the data_total dictionary

        return self.data_total
  
    def dns_data(self):
        # Open and read the DNS log file
        try:
            app_data_path = user_data_dir(app_name)
            path = os.path.join(app_data_path, 'dns.log')
            with open(path, 'r') as file:
                lines=file.readlines() 

            for i in range(len(lines)-1):
                curr_line = lines[i].split()
                next_line = lines[i+1].split()
                try:
                    if "10.99.99.1" not in curr_line:
                        continue
                    if not curr_line[6].startswith('query'):
                        continue 
                    domain_name = curr_line[7]

                    if domain_name not in self.dns_data_list: 
                        self.dns_data_list[domain_name] = {'allowed': 0,'denied': 0}

                    if next_line[6] == "forwarded": 
                        self.dns_data_list[domain_name]['allowed'] += 1
                    
                    elif next_line[6] == "config": 
                        self.dns_data_list[domain_name]['denied'] += 1
                except IndexError:
                    continue

        except FileNotFoundError:
            logger.error("Error: dns.log file not found.")
        except Exception as e:
            logger.error(f"Error reading dns.log: {e}")
    
    def update_log(self, server_address):
        key = paramiko.RSAKey.from_private_key_file("data/sshkey.pem")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=server_address, username="ubuntu", pkey=key)
            sftp = ssh.open_sftp()
            app_data_path = user_data_dir(app_name)
            path = os.path.join(app_data_path, 'dns.log')
            sftp.get("/var/log/dns.log", path)
        except Exception as e:
            logger.error(f"Unable to get DNS logs: {e}")
        sftp.close()
        ssh.close()
        self.dns_data()
        return
        

