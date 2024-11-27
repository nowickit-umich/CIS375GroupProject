class Stats_Manager:
    def __init__(self):
        # Initialize the managers for interacting with stats
        #self.vpn_manager = vpn_manager
        #self.cloud_manager = cloud_manager
        #self.filter_manager = filter_manager
        
        # Initialize data structures for statistics
        self.vpn_status = "Disconnected"
        self.server_status = "Stopped"
        self.filter_status = "No Filters"

    def update_vpn_status(self, status):
        # Update the VPN status
        self.vpn_status = status

    def update_server_status(self, status):
        # Update the server status
        self.server_status = status

    def update_filter_status(self):
        # Update the filter status based on enabled/disabled lists
        enabled_filters = [f['name'] for f in self.filter_manager.block_list if f['enabled']]
        if enabled_filters:
            self.filter_status = f"Enabled filters: {', '.join(enabled_filters)}"
        else:
            self.filter_status = "No Filters Enabled"
        
    def get_vpn_status(self):
        return self.vpn_status

    def get_server_status(self):
        return self.server_status

    def get_filter_status(self):
        return self.filter_status

    def log_stats(self):
        # Optionally log the stats for debugging purposes
        print(f"VPN Status: {self.vpn_status}")
        print(f"Server Status: {self.server_status}")
        print(f"Filter Status: {self.filter_status}")
