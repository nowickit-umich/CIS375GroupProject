from vpn.vpn_interface import VPNInterface
import platform

class VPN_Manager():
    def __init__(self):
        #Select correct interface implementation based on platform
        print(platform.system())
        pass