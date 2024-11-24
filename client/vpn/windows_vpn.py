from vpn.vpn_interface import VPN_Interface

import ctypes
lib = ctypes.WinDLL("vpn/windows_vpn.dll")
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

    def delete_profile():
        print("Not implemented")
        pass

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