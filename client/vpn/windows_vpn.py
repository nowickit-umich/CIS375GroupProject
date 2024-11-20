import asyncio
import subprocess
import inspect

from winrt.windows.networking.vpn import (
    VpnManagementAgent,
    VpnNativeProfile,
    VpnNativeProtocolType,
    VpnAuthenticationMethod,
    VpnRoutingPolicyType,
    IVpnProfile,
    VpnManagementErrorStatus
)
from vpn.vpn_interface import VPN_Interface

class Windows_VPN(VPN_Interface):
    def __init__(self):
        self.channel = None
        self.server_uri = None
        self.credentials = None

    def install_cert(self, path):
        cmd = f'\'-Command Import-Certificate -FilePath \"{path}\" -CertStoreLocation Cert:\LocalMachine\Root\''
        admin_cmd = f'Powershell -Command Start-Process -Verb RunAs -WindowStyle Hidden -FilePath \"PowerShell.exe\" -ArgumentList {cmd}'
        subprocess.run(admin_cmd, creationflags=subprocess.CREATE_NO_WINDOW, shell=True)

    async def create_profile(self, server_uri="test", username="user", password="pass"):
        # Working cert install function
        # try:
        #     self.install_cert("data/cert.pem")
        # except Exception as e:
        #     print(e)
        #     raise e

        # Need to delete the profile if it already exists
        agent = VpnManagementAgent()
        p = await agent.get_profiles_async()
        for x in range(p.size):
            if p.get_at(x).profile_name == "passwordTest":
                for m in dir(p.get_at(x)):
                    print(m)
                print("TTT:",p.get_at(x).__class__)
                print("TYPE:", type(p.get_at(x)))
                if isinstance(p.get_at(x), IVpnProfile):
                    print("Valid IVpnProfile object.")
                res = await agent.delete_profile_async(p.get_at(x))
                print("RES:",res)

        #print([x.profile_name for x in list(p)])

        # for x in dir(VpnManagementErrorStatus):
        #     value = getattr(VpnManagementErrorStatus, x)
        #     print(f"{x} = {value}")

        quit()

        # create profile
        profile = VpnNativeProfile()
        profile.profile_name = "CIS375VPN"
        profile.servers.append(server_uri)
        profile.native_protocol_type = VpnNativeProtocolType.IPSEC_IKEV2
        profile.user_authentication_method = VpnAuthenticationMethod.EAP
        #profile.tunnel_authentication_method = VpnAuthenticationMethod.PRESHARED_KEY
        profile.routing_policy_type = VpnRoutingPolicyType.FORCE_ALL_TRAFFIC_OVER_VPN
        #profile.remember_credentials = True
        #profile.always_on = True
        profile.require_vpn_client_app_u_i = False

        # test
        #profile.eap_configuration = '''<EapHostConfig xmlns="http://www.microsoft.com/provisioning/EapHostConfig"><EapMethod><Type xmlns="http://www.microsoft.com/provisioning/EapCommon">25</Type><VendorId xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorId><VendorType xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorType><AuthorId xmlns="http://www.microsoft.com/provisioning/EapCommon">0</AuthorId></EapMethod><Config xmlns="http://www.microsoft.com/provisioning/EapHostConfig"><Eap xmlns="http://www.microsoft.com/provisioning/BaseEapConnectionPropertiesV1"><Type>25</Type><EapType xmlns="http://www.microsoft.com/provisioning/MsPeapConnectionPropertiesV1"><ServerValidation><DisableUserPromptForServerValidation>false</DisableUserPromptForServerValidation><ServerNames>vpn.c2secure.link</ServerNames><TrustedRootCA>e2 92 5f 12 c1 40 0d d3 a6 15 b1 e0 05 54 63 7e 26 44 a2 e3 </TrustedRootCA></ServerValidation><FastReconnect>true</FastReconnect><InnerEapOptional>false</InnerEapOptional><Eap xmlns="http://www.microsoft.com/provisioning/BaseEapConnectionPropertiesV1"><Type>26</Type><EapType xmlns="http://www.microsoft.com/provisioning/MsChapV2ConnectionPropertiesV1"><UseWinLogonCredentials>false</UseWinLogonCredentials></EapType></Eap><EnableQuarantineChecks>false</EnableQuarantineChecks><RequireCryptoBinding>false</RequireCryptoBinding><PeapExtensions><PerformServerValidation xmlns="http://www.microsoft.com/provisioning/MsPeapConnectionPropertiesV2">true</PerformServerValidation><AcceptServerName xmlns="http://www.microsoft.com/provisioning/MsPeapConnectionPropertiesV2">true</AcceptServerName><PeapExtensionsV2 xmlns="http://www.microsoft.com/provisioning/MsPeapConnectionPropertiesV2"><AllowPromptingWhenServerCANotFound xmlns="http://www.microsoft.com/provisioning/MsPeapConnectionPropertiesV3">true</AllowPromptingWhenServerCANotFound></PeapExtensionsV2></PeapExtensions></EapType></Eap></Config></EapHostConfig>'''
        # EAP-MSCHAPV2
        #profile.eap_configuration = '''<EapHostConfig xmlns="http://www.microsoft.com/provisioning/EapHostConfig"><EapMethod><Type xmlns="http://www.microsoft.com/provisioning/EapCommon">26</Type><VendorId xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorId><VendorType xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorType><AuthorId xmlns="http://www.microsoft.com/provisioning/EapCommon">0</AuthorId></EapMethod><Config xmlns="http://www.microsoft.com/provisioning/EapHostConfig"><Eap xmlns="http://www.microsoft.com/provisioning/BaseEapConnectionPropertiesV1"><Type>26</Type><EapType xmlns="http://www.microsoft.com/provisioning/MsChapV2ConnectionPropertiesV1"><UseWinLogonCredentials>false</UseWinLogonCredentials></EapType></Eap></Config></EapHostConfig>'''
        # Certificate
        profile.eap_configuration = '''<EapHostConfig xmlns="http://www.microsoft.com/provisioning/EapHostConfig"><EapMethod><Type xmlns="http://www.microsoft.com/provisioning/EapCommon">13</Type><VendorId xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorId><VendorType xmlns="http://www.microsoft.com/provisioning/EapCommon">0</VendorType><AuthorId xmlns="http://www.microsoft.com/provisioning/EapCommon">0</AuthorId></EapMethod><Config xmlns="http://www.microsoft.com/provisioning/EapHostConfig"><Eap xmlns="http://www.microsoft.com/provisioning/BaseEapConnectionPropertiesV1"><Type>13</Type><EapType xmlns="http://www.microsoft.com/provisioning/EapTlsConnectionPropertiesV1"><CredentialsSource><CertificateStore><SimpleCertSelection>true</SimpleCertSelection></CertificateStore></CredentialsSource><ServerValidation><DisableUserPromptForServerValidation>false</DisableUserPromptForServerValidation><ServerNames></ServerNames><TrustedRootCA>83 4a 3c 37 d8 10 97 e1 9a 87 e9 cc 76 da 3e 66 4a 49 36 14 </TrustedRootCA></ServerValidation><DifferentUsername>false</DifferentUsername><PerformServerValidation xmlns="http://www.microsoft.com/provisioning/EapTlsConnectionPropertiesV2">true</PerformServerValidation><AcceptServerName xmlns="http://www.microsoft.com/provisioning/EapTlsConnectionPropertiesV2">true</AcceptServerName></EapType></Eap></Config></EapHostConfig>'''

        print(profile.servers)

        # adds profile
        res = await agent.add_profile_from_object_async(profile)
        print("ADD PROFILE RESULT:", res)

        #await self.agent.connect_profile_async(self.profile)
        print(profile.connection_status)

        self.server_uri = server_uri

    async def delete_profile(self):
        # deletes profile
        await self.agent.delete_profile_async(self.profile_name)
    
    async def connect(self):
        await self.agent.connect_profile_async(self.profile)

    async def disconnect(self):
        await self.agent.disconnect_profile_async(self.profile)

    async def status(self):
        return await self.profile.connection_status