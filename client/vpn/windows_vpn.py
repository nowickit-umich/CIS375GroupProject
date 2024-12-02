from vpn.vpn_interface import VPN_Interface
import subprocess
import ctypes
import os
import logging
logger = logging.getLogger(__name__)

# Windows VPN DLL
current_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(current_dir, 'windows/windows_vpn.dll')
try:
    lib = ctypes.WinDLL(dll_path)
except Exception as e:
    print(e)
    raise

# Define C++ function parameters and return types
# TODO this should probably be moved into init
lib.create_profile.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
lib.create_profile.restype = ctypes.c_int
lib.connect_vpn.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
lib.connect_vpn.restype = ctypes.c_int
lib.disconnect_vpn.argtypes = [ctypes.c_char_p]
lib.disconnect_vpn.restype = ctypes.c_int
lib.status.argtypes = [ctypes.c_char_p]
lib.status.restype = ctypes.c_int

# Windows VPN Implementation
class Windows_VPN(VPN_Interface):
    def init(self):
        pass

    # Install certificate to the root store
    def install_cert(self, path):
        try:
            cmd = f'\'-Command Import-Certificate -FilePath \"{path}\" -CertStoreLocation Cert:\LocalMachine\Root\''
            admin_cmd = f'Powershell -Command Start-Process -Verb RunAs -WindowStyle Hidden -FilePath \"PowerShell.exe\" -ArgumentList {cmd}'
            subprocess.run(admin_cmd, creationflags=subprocess.CREATE_NO_WINDOW, shell=True)
            logger.info("Installed certificate")

        except Exception as e:
            logger.error(f"Error installing certificate: {e}")
            raise

    # Create VPN profile 
    def create_profile(self, profile_name, server_address, pbk_path):
            try:
                ret = lib.create_profile(
                    profile_name.encode('utf-8'),
                    server_address.encode('utf-8'),
                    pbk_path.encode('utf-8')
                )

                if ret != 0:
                    logger.error("VPN Profile Creation Failed")
                    return -1
                logger.info("VPN Profile created successfully")
                return ret
            
            except Exception as e:
                logger.error(f"VPN Profile Creation Error: {e}")
                return -1

    def connect(self, profile_name, username, password, pbk_path):
        try:
            ret = lib.connect_vpn(
                profile_name.encode('utf-8'),
                username.encode('utf-8'),
                password.encode('utf-8'),
                pbk_path.encode('utf-8')
            )

            if ret != 0:
                logger.error("VPN Connection Failed")
                return -1
            logger.info("VPN Profile Connected")
            return ret
        
        except Exception as e:
            logger.error(f"VPN Connection Error: {e}")
            return -1

    # Return 0 on successful disconnect
    def disconnect(self, profile_name):
        try:
            ret = lib.disconnect_vpn(profile_name.encode('utf-8'))

            if ret != 0:
                logger.error("VPN Disconnection Failed")
                return -1
            
            logger.info("VPN Profile Disconnected")
            return ret
        
        except Exception as e:
            logger.error(f"VPN Disconnect Error: {e}")
            return -1

    def status(self, profile_name): # Get status of profile using profile name
        try:
            ret = lib.status(profile_name.encode('utf-8'))

            if ret < 0:
                logger.error("Failed to Retrieve VPN Status")
                return -1
            
            logger.info(f"VPN Status Retrieved: {ret}")
            return ret
        
        except Exception as e:
            logger.error(f"VPN Status Error: {e}")
            return -1
        
