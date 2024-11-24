from cloud.aws_interface import AwsInterface
import asyncio
import subprocess

class Cloud_Manager():
    def __init__(self):
        self.locations = ["None"]
        self.api_key = []
        self.is_ready = False
        self.is_monitored = False
        self.server_id = None
        self.server_ip = None
        self.server_location = None
        self.server_status = "Offline"
        self.server_cert = None # probably move to vpn manager
        self.server_ssh_key = None
        self.cloud = None
        return
    
    def setup(self, credentials):
        cloud_name = credentials[0]
        api_key = [credentials[1], credentials[2]]
        #Select Cloud_Interface implementation based on API selection
        if cloud_name == "AWS":
            self.cloud = AwsInterface()
        else:
            raise ValueError("Cloud not supported")
        # Test given api key
        self.api_key = api_key
        try:
            self.cloud.test_key(self.api_key)
        except:
            raise ValueError("API key test failed")
        # Get valid server locations
        try:
            self.get_locations()
        except Exception as e:
            print(e)
            raise Exception("Unable to get locations")
        # Cloud manager is now ready
        self.is_ready = True
        return

    # def update(self):
    #     if not self.is_ready:
    #         return
    #     if self.server_id is None:
    #         return
    #     self.is_ready = False
    #     self.server_status = self.cloud.get_status(self.api_key, self.server_id, self.server_location)
        
    #     self.is_ready = True
    #     return
    
    # Server status: initializing -> ok 
    async def monitor_server(self):
        if self.is_monitored:
            return
        self.is_monitored = True
        while self.is_ready and self.server_id is not None:
            try:
                self.server_status = await asyncio.to_thread(self.cloud.get_status, self.api_key, self.server_id, self.server_location)
            except Exception as e:
                print("Error monitoring server:", e)
            await asyncio.sleep(3)
        self.is_monitored = False
        return

    def create_server(self):
        self.server_ssh_key = self.cloud.create_ssh_key("CIS375VPNKEY", self.api_key, self.server_location)
        instance = self.cloud.create_server(self.server_ssh_key[0], self.api_key, self.server_location)
        self.server_id = instance["server_id"]
        self.server_ip = instance["server_ip"]
        return

    def delete_server(self):
        self.cloud.delete_server()
        return

    #return list of locations (strings)  
    def get_locations(self):
        self.locations = self.cloud.get_locations(self.api_key)
        self.server_location = self.locations[0]