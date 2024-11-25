from abc import ABC, abstractmethod
import platform

class VPN_Interface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def connect():
        pass

    @abstractmethod
    def disconnect():
        pass

    @abstractmethod
    def create_profile():
        pass



