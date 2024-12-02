import time
import logging

logger = logging.getLogger(__name__)

class Cloud_Manager():
    def __init__(self):
        self.locations = ["None"]
        self.api_key = []
        self.is_ready = False
        self.is_monitored = False
        self.server_id = None
        self.server_ip = None
        self.server_location = None
        self.server_status = "Offline"
        self.server_key_name = "CIS375VPNKEY"
        self.cloud = None
        return

    # setup cloud interface and validate credentials
    def setup(self, credentials):
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
        while True:
            time.sleep(3)
            if not self.is_ready or self.server_id is None:
                continue
            logger.debug("CLOUD MONITOR LOOP")
            try:
                self.server_status = self.cloud.get_status(self.api_key, self.server_id, self.server_location)
            except Exception as e:
                logger.error(f"Server Monitoring Error: {e}")

    def create_server(self):
        key = self.cloud.create_ssh_key(self.server_key_name, self.api_key, self.server_location)
        # Save the private key to a file
        with open("data/sshkey.pem", 'w') as file:
            file.write(key)
        instance = self.cloud.create_server(self.server_key_name, self.api_key, self.server_location)
        self.server_id = instance["InstanceId"]
        self.server_ip = instance["PublicIp"]
        return

    def delete_server(self):
        self.cloud.delete_server()
        return

    #return list of locations (strings)  
    def get_locations(self):
        self.locations = self.cloud.get_locations(self.api_key)
        self.server_location = self.locations[0]
