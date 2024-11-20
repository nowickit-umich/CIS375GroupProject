from cloud_manager import Cloud_Manager
from vpn_manager import VPN_Manager
import asyncio

#cm = Cloud_Manager("key")
vm = VPN_Manager()

#cm.create_server("us-east-2")
asyncio.run(vm.connect())

quit()