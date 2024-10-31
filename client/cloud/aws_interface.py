from cloud.cloud_interface import CloudInterface 

class AwsInterface(CloudInterface):
    def create_server(self):
        print("\n CREATE SERVER \n")
        pass
    
    def delete_server(self):
        print("\n DELETE SERVER \n")
        pass
   
    def start_server(self):
        print("\n START SERVER \n")
        pass

    def stop_server(self):
        print("\n STOP SERVER \n")
        pass

    def init_cloud(self):
        pass

    def terminate_cloud(self):
        pass
