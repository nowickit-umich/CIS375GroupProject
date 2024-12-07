from abc import ABC, abstractmethod

class CloudInterface(ABC):
    #Create a new server
    @abstractmethod
    def create_server():
        pass
    
    #Delete the server 
    @abstractmethod
    def delete_server():
        pass

    #Start the server
    @abstractmethod
    def start_server():
        pass

    #Stop the server
    @abstractmethod
    def stop_server():
        pass

    #setup cloud enviornment
    @abstractmethod
    def test_key(self, api_key):
        pass

    #Remove all resources from the cloud service
    @abstractmethod
    def terminate_cloud():
        pass

    @abstractmethod
    def get_locations(self, api_key):
        pass

