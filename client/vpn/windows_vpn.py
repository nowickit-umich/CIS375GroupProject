from vpn.vpn_interface import VPN_Interface
import subprocess
import ctypes
import os

# Windows VPN DLL
current_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(current_dir, 'windows/windows_vpn.dll')
try:
    lib = ctypes.WinDLL(dll_path)
except Exception as e:
    print(e)
    raise

# Define C++ function parameters and return types
lib.create_profile.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
lib.create_profile.restype = ctypes.c_int
lib.connect_vpn.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
lib.connect_vpn.restype = ctypes.c_int
lib.disconnect_vpn.argtypes = [ctypes.c_char_p]
lib.disconnect_vpn.restype = ctypes.c_int
lib.status.argtypes = [ctypes.c_char_p]
lib.status.restype = ctypes.c_int
lib.debug.argtypes = [ctypes.c_int, ctypes.c_char_p]
lib.debug.restype = ctypes.c_int

# Windows VPN Implementation
class Windows_VPN(VPN_Interface):
    def init(self):
        self.debug(1, "VPN Interface Initialized") # Successful Initalization(1 = success, 0 = fail)

    def install_cert(self, path): # Install certificate given path
        try:
            cmd = f'-Command Import-Certificate -FilePath "{path}" -CertStoreLocation Cert:\LocalMachine\Root'
            admin_cmd = f'Powershell -Command Start-Process -Verb RunAs -WindowStyle Hidden -FilePath "PowerShell.exe" -ArgumentList "{cmd}"'
            subprocess.run(admin_cmd, creationflags=subprocess.CREATE_NO_WINDOW, shell=True, check=True)
            self.debug(1, "Certificate Installed Successfully")

        except Exception as e:
            self.debug(0, f"Error: {e}")
            raise

    def create_profile(self, profile_name, server_address, pbk_path): # Create profile given name, server address, and pbk path
            try:
                ret = lib.create_profile(
                    profile_name.encode('utf-8'),
                    server_address.encode('utf-8'),
                    pbk_path.encode('utf-8')
                )

                if ret != 0:
                    self.debug(0, "Profile Creation Failed")
                    return -1
                self.debug(1, "Profile created successfully")
                return ret
            
            except Exception as e:
                self.debug(0, f"Error: {e}")
                return -1
            
    def debug(self, x, s): # Debug function printing out the string and error code
        return lib.debug(x, ctypes.c_char_p(s))

    def connect(self, profile_name, username, password, pbk_path): # Connect VPN profile using name of profile, username, password, and pbk path
        try:
            ret = lib.connect_vpn(
                profile_name.encode('utf-8'),
                username.encode('utf-8'),
                password.encode('utf-8'),
                pbk_path.encode('utf-8')
            )

            if ret != 0:
                self.debug(0, "VPN Connection Failed")
                return -1
            self.debug(1, "VPN Profile Connected")
            return ret
        
        except Exception as e:
            self.debug(0, f"Error: {e}")
            return -1

    def disconnect(self, profile_name): # Disconnect VPN profile using name of profile
        try:
            ret = lib.disconnect_vpn(profile_name.encode('utf-8'))

            if ret != 0:
                self.debug(0, "VPN Disconnection Failed")
                return -1
            
            self.debug(1, "VPN Profile Disconnected")
            return ret
        
        except Exception as e:
            self.debug(0, f"Error: {e}")
            return -1
        
    def status(self, profile_name): # Get status of profile using profile name
        try:
            ret = lib.status(profile_name.encode('utf-8'))

            if ret < 0:
                self.debug(0, "Failed to Retrieve Status")
                return -1
            
            self.debug(1, "Status Retrieved Successfully")
            return ret
        
        except Exception as e:
            self.debug(0, f"Error: {e}")
            return -1
        