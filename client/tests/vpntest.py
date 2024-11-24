from cloud_manager import Cloud_Manager
from vpn_manager import VPN_Manager
import asyncio
import platform

from vpn.windows_vpn import Windows_VPN

import sys
import time

# Redirect stderr to stdout
sys.stderr = sys.stdout


#cm = Cloud_Manager("key")
#vm = VPN_Manager()
vi = Windows_VPN()

print("CREATE")
vi.create_profile("CIS375VPN", "18.118.17.9", "data/vpn.pbk")
time.sleep(2)
print("CONNECT")
vi.connect("CIS375VPN", "user", "passtest4321", "data/vpn.pbk")
time.sleep(1)
print("STATUS")
print("STATUS:", vi.status("CIS375VPN"))
time.sleep(2)
print("STATUS")
print("STATUS:", vi.status("CIS375VPN"))
time.sleep(2)
print("STATUS")
print("STATUS:", vi.status("CIS375VPN"))
time.sleep(2)
print("STATUS")
print("STATUS:", vi.status("CIS375VPN"))
time.sleep(2)
print("DISCONN")
print("DISC:", vi.disconnect("CIS375VPN"))

quit()