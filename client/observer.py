from abc import abstractmethod

class Observer():
    @abstractmethod
    def update(self, cm, vm):
        return
    
class Subject():
    def __init__(self, observers: list):
        self.observers = observers
        return
    
    def add_observer(self, observer: Observer):
        self.observers.append(observer)
        return
    
    def del_observer(self, observer: Observer):
        for o in self.observers:
            if o == observer:
                self.observers.remove(o)
        return

    def notify(self, cm, vm):
        for o in self.observers:
            o.update(cm, vm)
        return
