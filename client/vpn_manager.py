import platform
import paramiko
import os
import time
import logging
logger = logging.getLogger(__name__)
logging.getLogger('paramiko').setLevel(logging.ERROR)

class VPN_Manager():
    '''
        Description: Manages the connection to the VPN, allowing for connecting, disconnecting, and monitoring of the VPN.
    '''
    def __init__(self):
        self.is_ready = False
        self.is_monitored = False
        self.is_connected = False
        self.profile_name = "CIS375VPN"
        self.username = "user"
        self.password = ""
        self.pbk_path = "data/vpn.pbk"
        
        if platform.system() == "Windows":
            from vpn.windows_vpn import Windows_VPN
            self.vpn = Windows_VPN()
        else:
            logger.critical(f"ERROR: Platform {platform.system()} not supported")
            quit()

    def get_vpn_keys(self, server_ip):
        '''
        Description: gets the VPN keys from the server given a server_ip

        param server_ip: IP address of server to connect to
        return: None
        '''
        key = paramiko.RSAKey.from_private_key_file("data/sshkey.pem")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=server_ip, username="ubuntu", pkey=key)
        sftp = ssh.open_sftp()
        sftp.get("/etc/swanctl/x509/cert.pem", "data/cert.pem")
        sftp.get("/home/ubuntu/vpnkey.secret", "data/vpnkey.secret")
        sftp.close()
        ssh.close()
        logger.info("Successfully retrieved server keys")
        return

    def monitor_connection(self):
        '''
        Description: periodically monitor the connection status of the VPN

        return: None
        '''
        while True:
            time.sleep(3)
            if not self.is_ready:
                continue
            try:
                result = self.vpn.status(self.profile_name)
                if result == 0:
                    self.is_connected = True
                else:
                    self.is_connected = False
            except Exception as e:
                logger.error(f"Error monitoring vpn connection: {e}")

    def connect(self, server_address):
        '''
        Description: Connects to the VPN using the server_address

        param server_address: Address of server to connect to
        return: None
        '''
        self.get_vpn_keys(server_address)
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/cert.pem")
        self.vpn.install_cert(path)
        time.sleep(0.3)
        self.vpn.create_profile(self.profile_name, server_address, self.pbk_path)
        file = open("data/vpnkey.secret")
        password = file.readline().strip()
        self.vpn.connect(self.profile_name, self.username, password, self.pbk_path)
        self.is_ready = True
        return
    
    def disconnect(self):
        '''
        Description: Disconnects from the VPN

        return: the status of the VPN disconnection(successful or unsuccessful)
        '''
        return self.vpn.disconnect(self.profile_name)
