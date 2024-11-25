import platform
import paramiko

class VPN_Manager():
    def __init__(self):
        self.is_ready = False
        self.is_connected = False
        self.profile_name = "CIS375VPN"
        self.username = "user"
        self.password = ""
        self.pbk_path = "data/vpn.pbk"
        
        if platform.system() == "Windows":
            from vpn.windows_vpn import Windows_VPN
            self.vpn = Windows_VPN()
        else:
            print("ERROR: Platform ", platform.system(), " not supported")
            quit()
        pass

    def get_vpn_keys(self, server_ip):
        key = paramiko.RSAKey.from_private_key_file("data/sshkey.pem")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=server_ip, username="ubuntu", pkey=key)
        sftp = ssh.open_sftp()
        sftp.get("/etc/swanctl/x509/cert.pem", "data/cert.pem")
        sftp.get("/home/ubuntu/vpn.secret", "data/vpnkey.secret")
        sftp.close()
        ssh.close()
        return

    async def update(self):
        if not self.is_ready:
            return
        self.is_ready = False
        await self.status()
        self.is_ready = True
        return

    def connect(self, server_address):
        self.get_vpn_keys(server_address)
        self.vpn.create_profile(self.profile_name, server_address, self.pbk_path)
        self.vpn.connect(self.profile_name, self.username, self.password, self.pbk_path)
        return
    
    async def disconnect(self):
        await self.vpn.disconnect(self.profile_name)
        return
    
    # sets connection status of the vpn
    async def status(self):
        self.is_conneted = await self.vpn.status()
        return