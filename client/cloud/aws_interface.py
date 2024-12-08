from cloud.cloud_interface import CloudInterface
import boto3
import botocore.exceptions as be
import logging

logger = logging.getLogger(__name__)
logging.getLogger('botocore').setLevel(logging.ERROR)
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

ID_KEY = "CIS375VPN"
ID_VALUE = "delete"
DEFAULT_REGION = "us-east-2"

class AwsInterface(CloudInterface):
    def create_session(self, api_key, region):
        return boto3.Session(
            aws_access_key_id=api_key[0],
            aws_secret_access_key=api_key[1],
            region_name=region
        )

    def create_security_group(self, client, group_name, description):
        try:
            response = client.describe_security_groups(
                Filters=[{'Name': f'tag:{ID_KEY}', 'Values': [ID_VALUE]}]
            )
            for group in response.get('SecurityGroups', []):
                if group['GroupName'] == group_name:
                    logger.info(f"Security group {group_name} already exists.")
                    return group['GroupId']
        except be.ClientError:
            logger.debug("No existing security group found, proceeding with creation.")

        try:
            response = client.create_security_group(
                Description=description,
                GroupName=group_name,
                TagSpecifications=[{
                    'ResourceType': 'security-group',
                    'Tags': [{'Key': ID_KEY, 'Value': ID_VALUE}]
                }]
            )
            group_id = response['GroupId']
            logger.info(f"Security group {group_name} created successfully.")
            self.authorize_security_group_ingress(client, group_id)
            return group_id
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
            logger.info(f"Ingress rules added to security group {group_id}.")
        except be.ClientError as e:
            logger.error(f"Failed to authorize ingress for group {group_id}: {e.response['Error']['Message']}")
            raise

    def create_ssh_key(self, key_name, api_key, region):
        session = self.create_session(api_key, region)
        client = session.client('ec2')
        try:
            client.delete_key_pair(KeyName=key_name)
            logger.info(f"Deleted existing key pair {key_name}.")
        except be.ClientError:
            logger.debug(f"No existing key pair {key_name} found.")

        try:
            response = client.create_key_pair(
                KeyName=key_name,
                KeyType='rsa',
                TagSpecifications=[{
                    'ResourceType': 'key-pair',
                    'Tags': [{'Key': ID_KEY, 'Value': ID_VALUE}]
                }],
                KeyFormat='pem'
            )
            logger.info(f"SSH key pair {key_name} created successfully.")
            return response['KeyMaterial']
        except be.ClientError as e:
            logger.error(f"Failed to create SSH key pair: {e.response['Error']['Message']}")
            raise

    def find_ami(self, client, name_filter, version_filter):
        try:
            response = client.describe_images(
                Filters=[
                    {'Name': 'name', 'Values': [f"ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server*"]},
                    {'Name':'owner-alias', 'Values':["amazon"]},
                    {'Name':'virtualization-type', 'Values':["hvm"]}   
                ]
            )
            if not response['Images']:
                raise ValueError("No matching AMI found.")
            return sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)[0]['ImageId']
        except be.ClientError as e:
            logger.error(f"Failed to find AMI: {e.response['Error']['Message']}")
            raise

    def create_server(self, ssh_key_name, api_key, region):
        session = self.create_session(api_key, region)
        client = session.client('ec2')
        resource = session.resource('ec2')

        security_group_id = self.create_security_group(
            client, group_name='CIS375ALLOWVPN', description='CIS375 VPN App security group'
        )

        try:
            ami_id = self.find_ami(client, "ubuntu", "24.04")
            logger.debug(f"Using AMI: {ami_id}")
        except ValueError as e:
            logger.error(e)
            raise

        try:
            with open('../server/install.sh', 'r') as file:
                user_data = file.read()
        except FileNotFoundError:
            logger.error("Install script not found.")
            raise

        try:
            instance = resource.create_instances(
                BlockDeviceMappings=[{
                    'DeviceName': '/dev/xvda',
                    'Ebs': {'VolumeSize': 10, 'VolumeType': 'gp3'}
                }],
                ImageId=ami_id,
                InstanceType='t3.nano',
                KeyName=ssh_key_name,
                UserData=user_data,
                MaxCount=1,
                MinCount=1,
                InstanceInitiatedShutdownBehavior='terminate',
                SecurityGroupIds=[security_group_id],
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': [{'Key': ID_KEY, 'Value': ID_VALUE}]
                }],
            )[0]
            logger.info(f"Instance {instance.id} created.")
            instance.wait_until_running()
            instance.reload()
            return {'InstanceId': instance.id, 'PublicIp': instance.public_ip_address, 'PrivateIp': instance.private_ip_address}
        except be.ClientError as e:
            logger.error(f"Failed to create EC2 instance: {e.response['Error']['Message']}")
            raise

    def delete_server(self, api_key, region, instance_id):
        session = self.create_session(api_key, region)
        client = session.client('ec2')
        try:
            client.terminate_instances(InstanceIds=[instance_id])
            logger.info(f"EC2 instance {instance_id} deleted successfully.")
        except be.ClientError as e:
            logger.error(f"Error deleting EC2 instance {instance_id}: {e.response['Error']['Message']}")
            raise

    def start_server(self, api_key, region, instance_id):
        session = self.create_session(api_key, region)
        client = session.client('ec2')
        try:
            client.start_instances(InstanceIds=[instance_id])
            logger.info(f"EC2 instance {instance_id} started successfully.")
        except be.ClientError as e:
            logger.error(f"Error starting EC2 instance {instance_id}: {e.response['Error']['Message']}")
            raise

    def stop_server(self, api_key, region, instance_id):
        session = self.create_session(api_key, region)
        client = session.client('ec2')
        try:
            client.stop_instances(InstanceIds=[instance_id])
            logger.info(f"EC2 instance {instance_id} stopped successfully.")
        except be.ClientError as e:
            logger.error(f"Error stopping EC2 instance {instance_id}: {e.response['Error']['Message']}")
            raise

    def terminate_cloud():
        pass

    def get_status(self, api_key, server_id, server_location):
        if server_id == "" or server_location is None:
            return 'Offline'
        try:
            session = self.create_session(api_key, server_location)
            client = session.client('ec2', region_name=server_location)
            response = client.describe_instance_status(
                InstanceIds=[server_id],
                IncludeAllInstances=True
            )
            if not response["InstanceStatuses"]:
                logger.info(
                    f"No status found for instance ID: {server_id}")
                return "Instance not found or terminated."
            status = response["InstanceStatuses"][0]["InstanceStatus"]["Status"]
            logger.info(f"Instance {server_id} status: {status}.")
            status_map = {'not-applicable':'Offline', 'ok':'Running', 'initializing':'Starting', 'impaired':'Unknown', 'insufficient-data':'Unknown'}
            return status_map[status]
        except be.ClientError as e:
            error_message = e.response['Error']['Message']
            logger.error(f"ClientError while retrieving status for instance {server_id}: {error_message}")
            return f"Error: {error_message}"
        except Exception as e:
            logger.error(f"Unexpected error while retrieving status for instance {server_id}: {str(e)}")
            return f"Error: {str(e)}"

    def test_key(self, api_key):
        '''
        Description: Verifies that the given API key is valid.

        param api_key: list containing the access key string followed by the secret key string.
        return: Return true if the api key is valid, else return false.
        '''
        if len(api_key) != 2:
            logger.error("Invalid API key provided.")
            return False
        if not isinstance(api_key[0], str) or not isinstance(api_key[1], str):
            logger.error("Invalid API key provided.")
            return False
        session = boto3.Session(
            aws_access_key_id=api_key[0],
            aws_secret_access_key=api_key[1],
        )
        client = session.client('ec2', region_name="us-east-1")
        try:
            client.describe_regions(AllRegions=False, DryRun=False)
            logger.info("API key is valid.")
            return True
        except be.ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ["AuthFailure", "InvalidClientTokenId"]:
                logger.error("Invalid API key provided.")
                return False
            else:
                logger.error(f"Unexpected error occurred: {e.response['Error']['Message']}")
                raise e

    def get_locations(self, api_key):
        '''
        Description: retrieves a list of available server locations. 

        param api_key: list containing the access key string followed by the secret key string.
        return: list of valid location strings.
        '''
        if len(api_key) != 2:
            logger.error("Invalid API key provided.")
            raise ValueError("Invalid API key")
        if not isinstance(api_key[0], str) or not isinstance(api_key[1], str):
            logger.error("Invalid API key provided.")
            raise ValueError("Invalid API key")
        session = boto3.Session(
            aws_access_key_id=api_key[0],
            aws_secret_access_key=api_key[1],
        )
        client = session.client('ec2', region_name=DEFAULT_REGION)
        try:
            response = client.describe_regions(AllRegions=False, DryRun=False)
            locations = [region["RegionName"] for region in response["Regions"]]
            logger.info(f"Available regions: {locations}")
            return locations
        except be.ClientError as e:
            logger.error(f"Error while fetching regions: {e.response['Error']['Message']}")
            raise
