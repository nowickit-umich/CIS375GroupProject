from vpn.vpn_interface import VPN_Interface
import subprocess
import ctypes
import os
import logging
logger = logging.getLogger(__name__)

# Windows VPN Implementation
class Windows_VPN(VPN_Interface):
    '''
    Description: Implementation of a VPN using the Windows API with the capabilities to create a profile, connect, disconnect, and get the current status.
    '''
    def __init__(self):
        # Windows VPN DLL
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dll_path = os.path.join(current_dir, 'windows/windows_vpn.dll')
        self.lib = None
        try:
            self.lib = ctypes.WinDLL(dll_path)
        except Exception as e:
            logger.critical(f"Error Loading DLL: {e}")
            quit()

        # Define C++ function parameters and return types
        self.lib.create_profile.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        self.lib.create_profile.restype = ctypes.c_int
        self.lib.connect_vpn.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        self.lib.connect_vpn.restype = ctypes.c_int
        self.lib.disconnect_vpn.argtypes = [ctypes.c_char_p]
        self.lib.disconnect_vpn.restype = ctypes.c_int
        self.lib.status.argtypes = [ctypes.c_char_p]
        self.lib.status.restype = ctypes.c_int

    # Install certificate to the root store
    def install_cert(self, path):
        '''
        Description: installs the certificate found in the given path

        param path: path to the certificate file
        return: None
        '''
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
            '''
            Description: creates a VPN profile using the parameters given including the profile name, server address, and the pbk_path
        
            param profile_name: name of the VPN profile
            param server_address: address of the VPN server
            param pbk_path: path to the PBK file
            return: status of profile creation, successful = 0 or unsuccessful = -1
            '''
            try:
                ret = self.lib.create_profile(
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
        '''
        Description: connects a given profile to the VPN given credentials(username and password)
    
        param profile_name: name of the VPN profile
        param username: username used for connecting to the VPN
        param password: password used for connecting to the VPN
        param pbk_path: path to the PBK file
        return: status of VPN connection, successful = 0 or unsuccessful = -1
        '''
        try:
            ret = self.lib.connect_vpn(
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
        '''
        Description: disconnects a given profile from the VPN 
    
        param profile_name: name of the VPN profile
        return: status of VPN disconnection, successful = 0 or unsuccessful = -1
        '''
        try:
            ret = self.lib.disconnect_vpn(profile_name.encode('utf-8'))

            if ret != 0:
                logger.error("VPN Disconnection Failed")
                return -1
            
            logger.info("VPN Profile Disconnected")
            return ret
        
        except Exception as e:
            logger.error(f"VPN Disconnect Error: {e}")
            return -1

    def status(self, profile_name): # Get status of profile using profile name
        '''
        Description: gets the connection status of a given profile 
    
        param profile_name: name of the VPN profile
        return: status of VPN profile, connected = 0 or disconnected = -1
        '''
        try:
            ret = self.lib.status(profile_name.encode('utf-8'))

            if ret < 0:
                logger.error("Failed to Retrieve VPN Status")
                return -1
            
            logger.info(f"VPN Status Retrieved: {ret}")
            return ret
        
        except Exception as e:
            logger.error(f"VPN Status Error: {e}")
            return -1
        
    def delete_profile(self, profile_name):
        '''
        Description: Not required for the windows implementation. Profile is stored locally
        '''
        return