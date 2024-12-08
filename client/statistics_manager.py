class Stats_Manager:

    '''
    Description: Manages and tracks various statistics related to DNS requests, VPN status, server status, and filter settings. 
    Provides methods for retrieving and processing data such as blocked domains, top visited domains, and DNS logs. 

    '''

    def __init__(self):
        # Initialize data structures for statistics
        self.dns_data_list={}
        self.vpn_status = "Disconnected"
        self.server_status = "Stopped"
        self.filter_status = "No Filters"
        
        # Placeholder for domain statistics
        self.blocked_domains = []
        
        # Top 10 visited domains, ranked by traffic
        self.top_visited = []

        self.top_blocked = []
        
        self.data_total = []

        # Total uploaded and downloaded data
        self.upload_total = "2GB"
        self.download_total = "5GB"

    def update_vpn_status(self, status):
        self.vpn_status = status

    def update_server_status(self, status):
        self.server_status = status

        #Update Filter Status

    def update_filter_status(self, filters):
        enabled_filters = [f for f in filters if filters[f]]
        if enabled_filters:
            self.filter_status = f"Enabled filters: {', '.join(enabled_filters)}"
        else:
            self.filter_status = "No Filters Enabled"


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



    def log_stats(self):
        # Optionally log the stats for debugging purposes
        print(f"VPN Status: {self.vpn_status}")
        print(f"Server Status: {self.server_status}")
        print(f"Filter Status: {self.filter_status}")

    
    def dns_data(self):
        # Open and read the DNS log file
        try:

            with open('client/data/dns_log.txt', 'r') as file:
                lines=file.readlines() 

            for i in range(len(lines)-1):
                curr_line = lines[i].split()
                next_line = lines[i+1].split()
                
                if not curr_line[6].startswith('query'):
                    continue 
                domain_name = curr_line[7]

                if domain_name not in self.dns_data_list: 
                    self.dns_data_list[domain_name] = {'allowed': 0,'denied': 0}

                if next_line[6] == "forwarded": 
                    self.dns_data_list[domain_name]['allowed'] += 1
                
                elif next_line[6] == "config": 
                    self.dns_data_list[domain_name]['denied'] += 1
                    
        except FileNotFoundError:
            print("Error: dns_log.txt file not found.")
        except Exception as e:
            print(f"Error reading dns_log.txt: {e}")

    def get_dns_data(self):
        # Return the stored DNS data
        return self.dns_data_list
        

