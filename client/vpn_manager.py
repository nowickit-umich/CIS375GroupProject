from vpn.windows_vpn import Windows_VPN
import platform

class VPN_Manager():
    def __init__(self):
        if platform.system() == "Windows":
            self.vpn = Windows_VPN()
        else:
            print("ERROR: Platform ", platform.system(), " not supported")
            quit()
        pass

    async def connect(self):
        await self.vpn.create_profile()
        return
    
    def disconnect(self):
        self.vpn.disconnect()
        return
    
