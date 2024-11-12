from cloud.aws_interface import AwsInterface

class Cloud_Manager():
    def __init__(self):
        #Select Cloud_Interface implementation based on API selection TODO
        self.cloud = AwsInterface()
        return

    def create_server(self):
        self.cloud.create_server()
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
    
    def get_status():
        return
    
    def get_cert():
        return
    
