from vpn_manager import VPN_Manager
import asyncio

vpn_manager = VPN_Manager()

asyncio.run(vpn_manager.connect())

quit()