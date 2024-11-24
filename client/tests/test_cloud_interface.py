# This file tests each function of the cloud interface
import sys
sys.path.append('..')
from cloud.aws_interface import AwsInterface
import os
import time

# Read credentials from file
try:
    file = open("../data/credentials.secret", "r")
except:
    print("Unable to read cloud credential file.")
    quit()
cloud_type = file.readline().strip()
access = file.readline().strip()
secret = file.readline().strip()
if not cloud_type or not access or not secret:
    os.remove("data/credentials.secret")
    print("Invalid Credentials.")
    quit()

cloud = AwsInterface()

region = 'us-east-2'
ssh = cloud.create_ssh_key("TESTKEY", [access, secret], region)
server = cloud.create_server("TESTKEY", [access, secret], region)
print(f"Created server {server}")
time.sleep(10)
res = cloud.get_status([access, secret], server["server_id"], region)
print(res)

'''{'InstanceStatuses': [{'AvailabilityZone': 'us-east-2b', 'InstanceId': 'i-0d38d7e7798d79306', 'InstanceState': {'Code': 16, 'Name': 'running'}, 'InstanceStatus': {'Details': [{'Name': 'reachability', 'Status': 'initializing'}], 'Status': 'initializing'}, 'SystemStatus': {'Details': [{'Name': 'reachability', 'Status': 'initializing'}], 'Status': 'initializing'}}], 'ResponseMetadata': {'RequestId': '4d4c2e32-3b9b-45f0-bd84-0ac6402656fe', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '4d4c2e32-3b9b-45f0-bd84-0ac6402656fe', 'cache-control': 'no-cache, no-store', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'content-type': 'text/xml;charset=UTF-8', 'content-length': '758', 'date': 'Sun, 24 Nov 2024 10:50:01 GMT', 'server': 'AmazonEC2'}, 'RetryAttempts': 0}}'''

