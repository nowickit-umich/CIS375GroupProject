import platform

class VPN_Manager():
    def __init__(self):
        self.is_ready = False
        self.is_connected = False
        self.profile_name = "CIS375VPN"
        
        if platform.system() == "Windows":
            from vpn.windows_vpn import Windows_VPN
            self.vpn = Windows_VPN()
        else:
            print("ERROR: Platform ", platform.system(), " not supported")
            quit()
        pass

    async def update(self):
        if not self.is_ready:
            return
        self.is_ready = False
        await self.status()
        self.is_ready = True
        return

    async def connect(self, server_address):
        await self.vpn.create_profile(self.profile_name, server_address, "data/vpn.pbk")
        await self.vpn.connect()
        return
    
    async def disconnect(self):
        await self.vpn.disconnect(self.profile_name)
        return
    
    # sets connection status of the vpn
    async def status(self):
        self.is_conneted = await self.vpn.status()
        return