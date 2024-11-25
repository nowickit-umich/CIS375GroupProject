from cloud.cloud_interface import CloudInterface 
import boto3
import botocore.exceptions as be
import base64
import logging

logging.getLogger('botocore').setLevel(logging.ERROR)
logging.getLogger('boto3').setLevel(logging.ERROR)

# Constants used to identify resources
# DO NOT MODIFY ANY RESOURCES WITHOUT THESE TAGS
ID_KEY = "CIS375VPN"
ID_VALUE = "delete"

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class AwsInterface(CloudInterface):

    def __init__(self):
        # TODO the interface should not have any data members
        # return the data to the caller
        self.security_group_id = None
        self.instance_id = None
        self.ssh_key_data = None
        # map region ids to names
        self.region_names = {
            "us-east-1": "United States (Virginia)",
            "us-east-2": "United States (Ohio)",
            "us-west-1": "United States (California)",
            "us-west-2": "United States (Oregon)",
            "ca-central-1": "Canada (Central)",
            "eu-west-1": "Ireland",
            "eu-west-2": "United Kingdom (London)",
            "eu-west-3": "France (Paris)",
            "eu-central-1": "Germany (Frankfurt)",
            "eu-north-1": "Sweden (Stockholm)",
            "ap-northeast-1": "Japan (Tokyo)",
            "ap-northeast-2": "South Korea (Seoul)",
            "ap-northeast-3": "Japan (Osaka)",
            "ap-southeast-1": "Singapore",
            "ap-southeast-2": "Australia (Sydney)",
            "ap-south-1": "India (Mumbai)",
            "sa-east-1": "Brazil (São Paulo)",
            "af-south-1": "South Africa (Cape Town)",
            "me-south-1": "Bahrain",
            "me-central-1": "UAE (Dubai)"
        }

    def create_session(self, api_key, region):
        return boto3.Session(
            aws_access_key_id=api_key[0],
            aws_secret_access_key=api_key[1],
            region_name=region
        )
    
    def create_security_group(self, client, group_name, description):
        try:
            # Check for existing security group
            response = client.describe_security_groups(
                GroupNames=[group_name],
                Filters=[{
                    'Name': f'tag:{ID_KEY}',
                    'Values': [ID_VALUE]
                }]
            )
            if len(response['SecurityGroups']) == 0:
               raise
            logger.info(f"Security group {group_name} already exists.")
            return response['SecurityGroups'][0]['GroupId']
        except be.ClientError as e:
            pass
        try:

            response = client.create_security_group(
                Description=description,
                GroupName=group_name,
                TagSpecifications=[{
                    'ResourceType': 'security-group',
                    'Tags': [{'Key':ID_KEY, 'Value':ID_VALUE}]
                }]
            )
            logger.info(f"Security group {group_name} created successfully.")

            # Authorize Ingress Rules
            self.authorize_security_group_ingress(client, response['GroupId'])

            return response['GroupId']
        except be.ClientError as e:
            logger.error(f"Failed to create security group: {e.response['Error']['Message']}")
            raise

    def authorize_security_group_ingress(self, client, group_id):
        try:
            client.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    },
                    {
                        'IpProtocol': 'udp',
                        'FromPort': 500,
                        'ToPort': 500,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    },
                    {
                        'IpProtocol': 'udp',
                        'FromPort': 4500,
                        'ToPort': 4500,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )
            logger.info("Ingress rules added to the security group.")
        except be.ClientError as e:
            logger.error(f"Failed to authorize security group ingress: {e.response['Error']['Message']}")
            raise

    # Returns list containing key name followed by key data
    def create_ssh_key(self, key_name, api_key, region):
        session = self.create_session(api_key, region)
        client = session.client('ec2')
        # Delete key if it already exists
        try:
            response = client.delete_key_pair(
                KeyName=key_name,
            )
        except Exception as e:
            print(e)
            raise
            pass
        # Create the key
        try:
            response = client.create_key_pair(
                KeyName=key_name,
                KeyType='rsa',
                TagSpecifications=[{
                    'ResourceType': 'key-pair',
                    'Tags': [{'Key':ID_KEY, 'Value':ID_VALUE}]
                }],
                KeyFormat='pem'
            )
            logger.info(f"SSH key pair {key_name} created successfully.")
            return [key_name, response['KeyMaterial']]
        except be.ClientError as e:
            logger.error(f"Failed to create SSH key pair: {e.response['Error']['Message']}")
            raise

    # Returns the server data
    def create_server(self, ssh_key_name, api_key, region):
        session = self.create_session(api_key, region)
        client = session.client('ec2')
        resource = session.resource('ec2')

        # Create Security Group
        self.security_group_id = self.create_security_group(
            client,
            group_name='CIS375ALLOWVPN',
            description='CIS375 VPN App security group'
        )

        # TODO get valid ami for the selected region - search for ubuntu 24.04
        ami_id = 'ami-0ea3c35c5c3284d82' # us-east-2

        # load server install script
        try:
            with open('../server/install.sh', 'r') as file:
                script_data = file.read()
        except:
            raise

        # Launch EC2 Instance
        instance = resource.create_instances(
            BlockDeviceMappings=[{
                'DeviceName': '/dev/xvda',
                'Ebs': {'VolumeSize': 10, 'VolumeType': 'gp2'}
            }],
            ImageId=ami_id,
            InstanceType='t2.micro',
            KeyName=ssh_key_name,
            UserData=script_data,
            MaxCount=1,
            MinCount=1,
            SecurityGroupIds=[self.security_group_id],
            InstanceInitiatedShutdownBehavior='terminate',
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key':ID_KEY, 'Value':ID_VALUE}]
            }],
        )[0]

        logger.info(f"EC2 instance {instance.instance_id} created successfully.")

        # Send Configuration Info to VPN
        # TODO the functions in the interface should simply return the data, no need for this
        vpn_config = {
            'instance_id': self.instance_id,
            'public_ip': instance.public_ip_address,
            'ssh_key': self.ssh_key_data
        }
        self.send_to_vpn_interface(vpn_config)

        return {'server_id':instance.instance_id, 'server_ip':instance.public_ip_address}
    
    # TODO the functions in the interface should simply return the data, no need for this
    def send_to_vpn_interface(self, config):
        """
        Placeholder for sending configuration to VPN interface.
        Replace with actual implementation to communicate with VPN.
        """
        logger.info(f"Sending configuration to VPN interface: {config}")

    def terminate_cloud(self, api_key, region):
        session = self.create_session(api_key, region)
        client = session.client('ec2')

        # TODO we should find and delete all resources with the ID_KEY tags 

        try:
            # Terminate EC2 Instance
            if self.instance_id:
                client.terminate_instances(InstanceIds=[self.instance_id])
                logger.info(f"EC2 instance {self.instance_id} terminated successfully.")
                self.instance_id = None

            # Delete Security Group
            if self.security_group_id:
                client.delete_security_group(GroupId=self.security_group_id)
                logger.info(f"Security group {self.security_group_id} deleted successfully.")
                self.security_group_id = None

            # Delete SSH Key Pair
            if self.ssh_key_data:
                client.delete_key_pair(KeyName='CIS375VPN')
                logger.info("SSH key pair 'cisvpn' deleted successfully.")
                self.ssh_key_data = None

        except be.ClientError as e:
            logger.error(f"Error during termination: {e.response['Error']['Message']}")
            raise
    
    # TODO
    def delete_server(self):
        print("\n DELETE SERVER \n")
        pass
   
    # TODO
    def start_server(self):
        print("\n START SERVER \n")
        pass

    # TODO
    def stop_server(self):
        print("\n STOP SERVER \n")
        pass

    # TODO the 'state' of the instance is not what we need to monitor. Server is not up until 'Status' == ok  
    def get_status(self, api_key, server_id, server_location):
        session = boto3.Session(
            aws_access_key_id=api_key[0],
            aws_secret_access_key=api_key[1],
            region_name=server_location
        )
        client = session.client('ec2', region_name=server_location)
        try:
            response = client.describe_instances(
                InstanceIds=[server_id],
            )
            return {'state': response["Reservations"][0]["Instances"][0]["State"]["Name"],
                    'public_ip': response["Reservations"][0]["Instances"][0]["NetworkInterfaces"][0]["Association"]["PublicIp"],
                    'private_ip': response["Reservations"][0]["Instances"][0]["NetworkInterfaces"][0]["PrivateIpAddress"]
            }
        except be.NoRegionError as e:
            return
        except be.ClientError as e:
            print(e.response)
            raise e
        except Exception as e:
            print(e)
            raise e
        return

    # Verify the api key is valid
    def test_key(self, api_key):
        session = boto3.Session(
            aws_access_key_id=api_key[0],
            aws_secret_access_key=api_key[1],
        )
        client = session.client('ec2', region_name="us-east-1")
        try:
            client.describe_regions(AllRegions=False, DryRun=True)
        except be.ClientError as e:
            if e.response["Error"]["Code"] == "DryRunOperation":
                return 0
            else:
                print(e.response)
                raise e
        return -1

    # Return a list of valid server locations
    def get_locations(self, api_key):
        session = boto3.Session(
            aws_access_key_id=api_key[0],
            aws_secret_access_key=api_key[1],
        )
        client = session.client('ec2', region_name="us-east-1")
        try:
            res = client.describe_regions(AllRegions=False, DryRun=False)
        except be.ClientError as e:
            print(e.response)
            raise e
        return [region['RegionName'] for region in res['Regions']]