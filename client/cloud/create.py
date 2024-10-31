# THIS IS JUST A TEST
# REMOVE FROM FINAL 
# TODO

import boto3

IMAGEID=''
SSHKEY=''
SECGROUPID=''
SUBNETID=''
region = 'us-east-1'

resource = boto3.resource('ec2', region_name=region)
client = boto3.client('ec2', region_name=region)

#VPC, Internet gateway, IPv6, AutoShutdown

#Create VPN
vpc = client.create_vpc(
        CidrBlock='',
        Ipv6Pool='',
        Ipv6CidrBlock='',
        Ipv4IpamPoolId='',
        Ipv4NetmaskLength='',
        Ipv6IpamPoolId='',
        Ipv6NetmaskLength='',
        Ipv6CidrBlockNetworkBorderGroup='',
        TagSpecifications=[],
        DryRun=False,
        InstanceTenancy='',
        AmazonProvidedIpv6CidrBlock=''
    )



#Configure security group - input firewall
SECGROUP = client.create_security_group(
        Description='',
        GroupName='',
        VpcId='',
        TagSpecifications=[],
        DryRun=False
    )

client.authorize_security_group_ingress(
        CidrIp='',
        FromPort='',
        GroupId='',
        GroupName='',
        IpPermissions=[],
        IpProtocol='',
        SourceSecurityGroupName='',
        SourceSecurityGroupOwnerId='',
        ToPort='',
        TagSpecifications=[],
        DryRun=False
    )


#Create Instance
instance = resource.create_instances(
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
        TagSpecifications=['ResourceType':'instance', 'Tags':[{'Key':'info','Value':'EasyVPN'}]],
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
        DryRun=True,
        DisableApiTermination=False,
        InstanceInitiatedShutdownBehavior='stop',
        #PrivateIpAddress=,
        #ClientToken=,
        #AdditionalInfo=,
        NetworkInterfaces=[{
            'AssociatePublicIpAddress': True,
            'DeleteOnTermination':True,
            'Description':'InterfaceDescription',
            'DeviceIndex':0,
            'Groups':[SECGROUPID],
            'Ipv6AddressCount':0,
            #'NetworkInterfaceId':'',
            'PrivateIpAddress':'10.88.88.1/24',
            'SecondaryPrivateIpAddressCount':0,
            'SubnetId':SUBNETID,
            'AssociateCarrierIpAddress':False,
            #'InterfaceType':?,
            'NetworkCardIndex':0,

            }],
        #IamInstanceProfile={},
        EbsOptimized=False
        )




