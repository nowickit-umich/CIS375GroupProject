import asyncio
from winrt.windows.networking.vpn import (
    VpnManagementAgent,
    VpnNativeProfile,
    VpnChannelConfiguration,
    VpnCredential,
    VpnChannel,
    VpnNativeProtocolType,
)
from vpn.vpn_interface import VPN_Interface

class Windows_VPN(VPN_Interface):
    def __init__(self):
        self.agent = VpnManagementAgent()
        self.channel = None
        self.profile_name = "WindowsVPNProfile"
        self.server_uri = None
        self.credentials = None
        
    async def create_profile(self, server_uri, username, password):

        # creates profile with the parameters
        profile = VpnNativeProfile()
        profile.ProfileName = self.profile_name
        profile.ServerUris.Add(server_uri)
        profile.NativeProtocolType = VpnNativeProtocolType.IkeV2
        
        # credentials(optional, potentially remove)
        self.credentials = VpnCredential()
        self.credentials.UserName = username
        self.credentials.Password = password
        
        # adds profile
        await self.agent.AddProfileFromObjectAsync(profile)
        self.server_uri = server_uri       

    
    async def delete_profile(self):
        # deletes profile
        await self.agent.DeleteProfileAsync(self.profile_name)
    
    async def connect(self):
        print("\n VPN CONNECT \n")
        # sets the configuration, could use a custom config
        config = VpnChannelConfiguration()
        config.ServerServiceName = self.server_uri
        
        # sets channel
        self.channel = await VpnChannel.CreateAsync()
        await self.channel.StartWithMainTransport(config, self.credentials)
            
    
    async def disconnect(self):
        # disconnects vpn
        print("\n VPN DISCONNECT \n")
        await self.channel.Stop()
        self.channel = None
