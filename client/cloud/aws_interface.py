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


        #response = client.describe_security_groups(GroupNames=["ALLOW_VPN"])
        

        #Configure security group - input firewall
        response = client.create_security_group(
            Description='vpn security group',
            GroupName='TESTALLOWVPN',
            TagSpecifications=[{'ResourceType':'security-group','Tags':[{'Key':'cisvpn','Value':'delete'}]}],
            DryRun=False
        )
        if response == 0:
            #TODO Error handling
            pass
        sec_group_id = response["GroupId"]

        # Allow VPN and SSH traffic inbound
        response = client.authorize_security_group_ingress(
            GroupId=sec_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0'
                        },
                    ],
                    'Ipv6Ranges': [],
                    'PrefixListIds': []
                },
                {
                    'IpProtocol': 'udp',
                    'FromPort': 500,
                    'ToPort': 500,
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0'
                        },
                    ],
                    'Ipv6Ranges': [],
                    'PrefixListIds': []
                },
                {
                    'IpProtocol': 'udp',
                    'FromPort': 4500,
                    'ToPort': 4500,
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0'
                        },
                    ],
                    'Ipv6Ranges': [],
                    'PrefixListIds': []
                },
            ],
            DryRun=False
        )
        
        # Create SSH Key
        ssh_key = client.create_key_pair(
                KeyName='cisvpn',
                KeyType='ed25519',
                TagSpecifications=[
                    {
                        'ResourceType': 'key-pair',
                        'Tags': [
                            {
                                'Key': 'cisvpn',
                                'Value': 'delete'
                            }
                        ]
                    }
                ],
                KeyFormat='pem',
                DryRun=False
            )

        # Get image (AMI) id
        
        IMAGEID = None
        SSHKEY = None

        resource.create_instances(
                BlockDeviceMappings=[{
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'Iops': 3000,
                        'VolumeSize': 5,
                        'VolumeType': 'gp3',
                        'Throughput': 125,
                        'Encrypted': False
                    },
                    'DeviceName': 'xvda',
                }],
                ImageId=IMAGEID,
                InstanceType='t2.micro',
                KeyName=SSHKEY,
                MaxCount=1,
                MinCount=1,
                Monitoring={'Enabled':False},
                #Placement={},
                #RamdiskId='',
                #SecurityGroupIds=[SECGROUPID],
                #SecurityGroups=[],
                #SubnetId='',
                #UserData='',
                #ElasticGpuSpecification=[],
                #ElasticInferenceAccelerators=[],
                #TagSpecifications=['ResourceType':'instance', 'Tags':[{'Key':'cisvpn','Value':'delete'}]],
                #LaunchTemplate={},
                #InstanceMarketOptions={},
                CreditSpecification={'CpuCredits':'standard'},
                #CpuOptions={},
                CapacityReservationSpecification={'CapacityReservationPreference':'none'},
                #HibernationOptions={},
                #LicenseSpecifications={},
                #MetadataOptions={},
                #EnclaveOptions={},
                #PrivateDnsNameOptions={},
                #MaintenanceOptions={},
                DisableApiStop=False,
                EnablePrimaryIpv6=False,
                DryRun=False,
                DisableApiTermination=False,
                InstanceInitiatedShutdownBehavior='terminate',
                #PrivateIpAddress=,
                #ClientToken=,
                #AdditionalInfo=,
                NetworkInterfaces=[{
                    'AssociatePublicIpAddress': True,
                    'DeleteOnTermination':True,
                    'Description':'InterfaceDescription',
                    'DeviceIndex':0,
                    'Groups':[sec_group_id],
                    'Ipv6AddressCount':0,
                    #'NetworkInterfaceId':'',
                    'PrivateIpAddress':'10.88.88.1/24',
                    'SecondaryPrivateIpAddressCount':0,
                    #'SubnetId':SUBNETID,
                    'AssociateCarrierIpAddress':False,
                    #'InterfaceType':?,
                    'NetworkCardIndex':0,
                    }],
                #IamInstanceProfile={},
                EbsOptimized=False
            )
        

        quit()
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
