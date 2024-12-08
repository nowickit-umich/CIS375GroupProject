from abc import ABC, abstractmethod

class VPN_Interface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def connect(self, profile_name, username, password, profile_path):
        pass

    @abstractmethod
    def disconnect(self, profile_name):
        pass

    @abstractmethod
    def create_profile(self, profile_name, server_address, profile_path):
        pass

    @abstractmethod
    def delete_profile(self, profile_name):
        pass

    @abstractmethod
    def install_cert(self, path):
        pass

    @abstractmethod
    def status(self, profile_name):
        pass


