from vpn.vpn_interface import VPN_Interface
import subprocess
import ctypes
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
lib = ctypes.WinDLL(os.path.join(current_dir, 'windows/windows_vpn.dll'))
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

class Windows_VPN(VPN_Interface):
    def __init__(self):
        pass

    def install_cert(self, path):
        cmd = f'\'-Command Import-Certificate -FilePath \"{path}\" -CertStoreLocation Cert:\LocalMachine\Root\''
        admin_cmd = f'Powershell -Command Start-Process -Verb RunAs -WindowStyle Hidden -FilePath \"PowerShell.exe\" -ArgumentList {cmd}'
        subprocess.run(admin_cmd, creationflags=subprocess.CREATE_NO_WINDOW, shell=True)

    def create_profile(self, profile_name, server_address, pbk_path):
        ret = lib.create_profile(ctypes.c_char_p(profile_name.encode('utf-8')), 
                                ctypes.c_char_p(server_address.encode('utf-8')),
                                ctypes.c_char_p(pbk_path.encode('utf-8'))
                            )
        if ret != 0:
            print("Create Profile Error")
            return -1
        return 0

    def debug(self, x, s):
        return lib.debug(x, ctypes.c_char_p(s))

    # Not needed for this implementation
    def delete_profile(self):
        return

    def connect(self, profile_name, username, password, pbk_path):
        ret = lib.connect_vpn(ctypes.c_char_p(profile_name.encode('utf-8')), 
                              ctypes.c_char_p(username.encode('utf-8')), 
                              ctypes.c_char_p(password.encode('utf-8')), 
                              ctypes.c_char_p(pbk_path.encode('utf-8'))
                            )
        if ret != 0:
            print("Connect Error")
            return -1
        return 0

    def disconnect(self, profile_name):
        ret = lib.disconnect_vpn(ctypes.c_char_p(profile_name.encode('utf-8')))
        if ret != 0:
            print("Disconnect Error")
            return -1
        return 0

    def status(self, profile_name):
        ret = lib.status(ctypes.c_char_p(profile_name.encode('utf-8')))
        if ret < 0:
            print("Status Error")
            return -1
        return ret