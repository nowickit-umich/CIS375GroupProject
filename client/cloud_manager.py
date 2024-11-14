from cloud.aws_interface import AwsInterface

class Cloud_Manager():
    def __init__(self, api_key):
        #Select Cloud_Interface implementation based on API selection TODO
        self.api_key = self.get_api_key()
        if self.api_key == []:
            pass
            # no key saved
        self.cloud = AwsInterface()
        if self.cloud.init_cloud() != 0:
            print("Error connecting to cloud")
            return
        return
    
    def get_api_key(self):
        # store as <cloudType> <public> <private>
        try:
            file = open("apikey")
        except:
            return []
        return file.readline().split()

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