from abc import ABC, abstractmethod

class VPNInterface(ABC):
    @abstractmethod
    def connect():
        pass

    @abstractmethod
    def disconnect():
        pass

    @abstractmethod
    def create_profile():
        pass

    @abstractmethod
    def delete_profile():
        pass


