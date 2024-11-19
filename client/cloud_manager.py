from cloud.aws_interface import AwsInterface

class Cloud_Manager():
    def __init__(self):
        pass

    async def setup(self, cloud_name, api_key):
        #Select Cloud_Interface implementation based on API selection
        if cloud_name == "AWS":
            self.cloud = AwsInterface()
        else:
            raise ValueError("Cloud not supported")

        self.api_key = api_key
        try:
            await self.cloud.test_key(self.api_key)
        except:
            raise ValueError("API key test failed")
        return

    def create_server(self, region):
        self.cloud.create_server(region)
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
    def available_locations(self):
        return []