from cloud.cloud_interface import CloudInterface 
import boto3


class AwsInterface(CloudInterface):
    def __init__(self):
        try:
            keyfile = open("./cloud/aws.secret")
        except:
            raise Exception("Failed to open AWS key file.")
        self.session = boto3.Session(
            aws_access_key_id=keyfile.readline().strip(),
            aws_secret_access_key=keyfile.readline().strip(),
        )


    def create_server(self, region):
        resource = self.session.resource('ec2', region_name=region)
        client = self.session.client('ec2', region_name=region)

        #Configure security group - input firewall
        response = client.create_security_group(
                Description='vpn security group',
                GroupName='TESTALLOWVPN',
                TagSpecifications=[{'ResourceType':'security-group','Tags':[{'Key':'cisvpn','Value':'delete'}]}],
                DryRun=True
            )
        if response == 0:
            #TODO Error handling
            pass
        sec_group_id = response["GroupId"]

        #TODO - Not done - specify all rules in a single API call
        response = client.authorize_security_group_ingress(
                GroupId=sec_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'udp',
                        'FromPort': -1,
                        'ToPort': 500,
                        'IpRanges': [
                            {
                                'Description': 'VPN500',
                                'CidrIp': 'string'
                            },
                        ],
                        'Ipv6Ranges': [
                            {
                                'Description': 'string',
                                'CidrIpv6': 'string'
                            },
                        ],
                        'PrefixListIds': [
                            {
                                'Description': 'string',
                                'PrefixListId': 'string'
                            },
                        ]
                    },
                ],
                IpProtocol='string',
                SourceSecurityGroupName='string',
                SourceSecurityGroupOwnerId='string',
                ToPort=123,
                TagSpecifications=[
                    {
                        'ResourceType': 'capacity-reservation'|'client-vpn-endpoint'|'customer-gateway'|'carrier-gateway'|'coip-pool'|'dedicated-host'|'dhcp-options'|'egress-only-internet-gateway'|'elastic-ip'|'elastic-gpu'|'export-image-task'|'export-instance-task'|'fleet'|'fpga-image'|'host-reservation'|'image'|'import-image-task'|'import-snapshot-task'|'instance'|'instance-event-window'|'internet-gateway'|'ipam'|'ipam-pool'|'ipam-scope'|'ipv4pool-ec2'|'ipv6pool-ec2'|'key-pair'|'launch-template'|'local-gateway'|'local-gateway-route-table'|'local-gateway-virtual-interface'|'local-gateway-virtual-interface-group'|'local-gateway-route-table-vpc-association'|'local-gateway-route-table-virtual-interface-group-association'|'natgateway'|'network-acl'|'network-interface'|'network-insights-analysis'|'network-insights-path'|'network-insights-access-scope'|'network-insights-access-scope-analysis'|'placement-group'|'prefix-list'|'replace-root-volume-task'|'reserved-instances'|'route-table'|'security-group'|'security-group-rule'|'snapshot'|'spot-fleet-request'|'spot-instances-request'|'subnet'|'subnet-cidr-reservation'|'traffic-mirror-filter'|'traffic-mirror-session'|'traffic-mirror-target'|'transit-gateway'|'transit-gateway-attachment'|'transit-gateway-connect-peer'|'transit-gateway-multicast-domain'|'transit-gateway-policy-table'|'transit-gateway-route-table'|'transit-gateway-route-table-announcement'|'volume'|'vpc'|'vpc-endpoint'|'vpc-endpoint-connection'|'vpc-endpoint-service'|'vpc-endpoint-service-permission'|'vpc-peering-connection'|'vpn-connection'|'vpn-gateway'|'vpc-flow-log'|'capacity-reservation-fleet'|'traffic-mirror-filter-rule'|'vpc-endpoint-connection-device-type'|'verified-access-instance'|'verified-access-group'|'verified-access-endpoint'|'verified-access-policy'|'verified-access-trust-provider'|'vpn-connection-device-type'|'vpc-block-public-access-exclusion'|'ipam-resource-discovery'|'ipam-resource-discovery-association'|'instance-connect-endpoint'|'ipam-external-resource-verification-token',
                        'Tags': [
                            {
                                'Key': 'string',
                                'Value': 'string'
                            },
                        ]
                    },
                ],
                DryRun=True
            )
        


        pass
    
    def delete_server(self):
        print("\n DELETE SERVER \n")
        pass
   
    def start_server(self):
        print("\n START SERVER \n")
        pass

    def stop_server(self):
        print("\n STOP SERVER \n")
        pass

    # return -1 on error
    def init_cloud(self):
        pass

    def terminate_cloud(self):
        pass
