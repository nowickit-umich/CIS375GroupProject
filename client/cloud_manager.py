import time
import logging
from observer import Observer, Subject

logger = logging.getLogger(__name__)

class Cloud_Manager(Subject):
    '''
    Description: Manages the cloud including the interface of choice,  the server creation and deletion, and periodic status monitoring.
    '''
    def __init__(self):
        super().__init__([])
        self.locations = ["None"]
        self.api_key = []
        self.is_ready = False
        self.server_id = None
        self.server_ip = None
        self.server_private_ip = None
        self.server_location = None
        self.server_status = "Offline"
        self.server_key_name = "CIS375VPNKEY"
        self.cloud = None
        return

    # setup cloud interface and validate credentials
    def setup(self, credentials):
        '''
        Description: Given credentials(cloud interface name, and API keys), sets up the cloud interface of choice, logs the user in using the API keys, and gets the server locations.

        param credentials: list containing cloud interface name, and API keys
        return: Boolean indicating successful or unsuccessful login
        '''
        cloud_name = credentials[0]
        api_key = [credentials[1], credentials[2]]
        #Select Cloud_Interface implementation based on API selection
        if cloud_name == "AWS":
            from cloud.aws_interface import AwsInterface
            self.cloud = AwsInterface()
        else:
            logger.error("Invalid Cloud Platform")
            return False
        # Test given api key
        self.api_key = api_key
        if not self.cloud.test_key(self.api_key):
            # Invalid key
            logger.info("Invalid API key")
            return False
        # Get valid server locations
        try:
            self.get_locations()
        except Exception as e:
            logger.error(f"Unable to get locations: {e}")
            raise Exception("Unable to get locations")
        # Cloud manager is now ready
        logger.debug("Cloud Manager Setup Complete")
        self.is_ready = True
        return True

    # Server status: initializing -> ok 
    def monitor_server(self):
        '''
        Description: periodically monitors the status of the server, updating server_status

        return: None
        '''
        while True:
            time.sleep(3)
            if not self.is_ready or self.server_id is None:
                continue
            try:
                self.server_status = self.cloud.get_status(self.api_key, self.server_id, self.server_location)
                self.notify(self, None)
            except Exception as e:
                logger.error(f"Server Monitoring Error: {e}")

    def create_server(self):
        '''
        Description: Creates an ssh key and server instance using the name, API key, and location.

        return: None
        '''
        key = self.cloud.create_ssh_key(self.server_key_name, self.api_key, self.server_location)
        # Save the private key to a file
        with open("data/sshkey.pem", 'w') as file:
            file.write(key)
        instance = self.cloud.create_server(self.server_key_name, self.api_key, self.server_location)
        self.server_id = instance["InstanceId"]
        self.server_ip = instance["PublicIp"]
        self.server_private_ip = instance["PrivateIp"]
        return

    def delete_server(self):
        '''
        Description: deletes the server and resets all attributes

        return: None
        '''
        self.cloud.delete_server(self.api_key, self.server_location, self.server_id)
        self.server_id = None
        self.server_ip = None
        self.server_location = None
        self.server_status = "Offline"
        return

    #return list of locations (strings)  
    def get_locations(self):
        '''
        Description: Gets the locations of the server given the API key, and updates the server_location attribute

        return: None
        '''
        self.locations = self.cloud.get_locations(self.api_key)
        self.server_location = self.locations[0]
