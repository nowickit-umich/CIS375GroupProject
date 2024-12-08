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

    #return true if api_key is valid
    @abstractmethod
    def test_key(self, api_key):
        pass

    #return the status of the server
    @abstractmethod
    def get_status(self, api_key):
        pass

    @abstractmethod
    def create_ssh_key(self, api_key):
        pass

    #Remove all resources from the cloud service TODO
    @abstractmethod
    def terminate_cloud():
        pass

    #Return a list of valid server locations
    @abstractmethod
    def get_locations(self, api_key):
        pass


