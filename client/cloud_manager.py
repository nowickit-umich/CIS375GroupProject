from cloud.aws_interface import AwsInterface

class Cloud_Manager():
    def __init__(self):
        self.locations = ["None"]
        self.api_key = []
        self.is_ready = False
        self.server_id = None
        self.server_ip = None
        self.server_location = None
        self.server_status = "Offline"
        self.server_cert = None
        self.cloud = None
        return
    
    async def setup(self, cloud_name, api_key):
        #Select Cloud_Interface implementation based on API selection
        if cloud_name == "AWS":
            self.cloud = AwsInterface()
        else:
            raise ValueError("Cloud not supported")
        # Test given api key
        self.api_key = api_key
        try:
            await self.cloud.test_key(self.api_key)
        except:
            raise ValueError("API key test failed")
        # Get valid server locations
        try:
            self.locations = await self.get_locations()
        except Exception as e:
            print(e)
            raise Exception("Unable to get locations")
        # Cloud manager is now ready
        self.is_ready = True
        return
    
    async def update(self, dt):
        if not self.is_ready:
            return
        if self.server_id is None:
            return
        self.is_ready = False
        self.server_status = await self.cloud.get_status(self.api_key, self.server_id, self.server_location)
        # if self.server_status == "Offline":
        #     self.server_status = "Starting"
        # else:
        #     self.server_status = "Offline"
        self.is_ready = True
        return

    def create_server(self, region):
        self.server_status = "Starting"
        self.server_id = self.cloud.create_server(region)
        return

    def delete_server(self):
        self.cloud.delete_server()
        return
    
    def start_server(self):
        self.cloud.start_server()
        return
    
    def stop_server(self):
        self.cloud.stop_server()
        return

    #return list of locations (strings)  
    async def get_locations(self):
        return await self.cloud.get_locations(self.api_key)