import platform

class VPN_Manager():
    def __init__(self):
        if platform.system() == "Windows":
            from vpn.windows_vpn import Windows_VPN
            self.vpn = Windows_VPN()
        else:
            print("ERROR: Platform ", platform.system(), " not supported")
            quit()
        pass

    def connect(self):
        self.vpn.connect()
        return
    
    def disconnect(self):
        self.vpn.disconnect()
        return
    
    # return the connection status of the vpn
    # True = connected
    # False = disconnected
    def status():
        return