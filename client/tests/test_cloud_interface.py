# This file tests each function of the cloud interface
import sys
sys.path.append('..')

from cloud.aws_interface import AwsInterface
import os
import time

# Read credentials from file
try:
    file = open("client/data/credentials.secret", "r")
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
api_key = [access, secret]

cloud = AwsInterface()
DEFAULT_REGION = "us-east-2"

print('----- TESTING: test_key() -----')
# test_key()
#valid api key
ret = cloud.test_key(api_key)
assert(ret == True)
#invalid api key
# Empty key
ret = cloud.test_key([])
assert(ret == False)
#invalid Type
ret = cloud.test_key([1, 2])
assert(ret == False)
#invalid length
ret = cloud.test_key(['abc', 'xyz', '123'])
assert(ret == False)
#invalid key
ret = cloud.test_key(['abc', 'xyz'])
assert(ret == False)

print('----- TESTING: get_locations() -----')
# get_locations()
#valid key
ret = cloud.get_locations(api_key)
assert(isinstance(ret, list))
print("Retrieved Locations:", ret)
#empty key
#try:
#    ret = cloud.get_locations([])
#except ValueError as e:
#    assert(e == "Invalid API key")

print('----- TESTING: create_ssh_key() -----')
ssh_key_name = "testkey123" 
private_key = cloud.create_ssh_key(ssh_key_name, api_key, DEFAULT_REGION)
assert private_key is not None
print(f"SSH Key {ssh_key_name} created successfully")

#invalid_key_name = ""
#try:
#    ret = cloud.create_ssh_key(invalid_key_name, api_key, DEFAULT_REGION)
#except ValueError as e:
#    print(f"Error: {e}")

print('----- TESTING: create_server() -----')
server_info = cloud.create_server(ssh_key_name, api_key, DEFAULT_REGION)
assert 'InstanceId' in server_info
assert 'PublicIp' in server_info
assert 'PrivateIp' in server_info

instance_id = server_info['InstanceId']
print(f"Server created with Instance ID: {server_info['InstanceId']}")
print(f"Public IP: {server_info['PublicIp']}")
print(f"Private IP: {server_info['PrivateIp']}")
time.sleep(30)

#invalid_region = "invalid-region"

#try:
#    ret = cloud.create_server(ssh_key_name, api_key, invalid_region)
#except ValueError as e:
#        print(f"Error: {e}")


print('----- TESTING: get_status() -----')
status = cloud.get_status(api_key, instance_id, DEFAULT_REGION)
assert status in ["Running", "Starting", "Offline"]
print(f"Server status: {status}")

#invalid_id = "invalid-id"
#try:
#    ret = cloud.get_status(api_key, invalid_id, DEFAULT_REGION)
#except ValueError as e:
#        print(f"Error: {e}")

print('----- TESTING: start_server() -----')

cloud.stop_server(api_key, DEFAULT_REGION, instance_id)
time.sleep(300) 

cloud.start_server(api_key, DEFAULT_REGION, instance_id)
time.sleep(300) 

status = cloud.get_status(api_key, instance_id, DEFAULT_REGION)
assert status == "Running"
print("Server started successfully")

#try:
#    ret = cloud.start_server(api_key, DEFAULT_REGION, invalid_id)
#except ValueError as e:
#    print(f"Error: {e}")


print('----- TESTING: stop_server() -----')
cloud.stop_server(api_key, DEFAULT_REGION, instance_id)
time.sleep(20)  

status = cloud.get_status(api_key, instance_id, DEFAULT_REGION)
assert status in ["Offline"]
print("Server stopped successfully")


#try:
#    ret = cloud.stop_server(api_key, DEFAULT_REGION, invalid_id)
#except ValueError as e:
#   print(f"Error: {e}")

print('----- TESTING: delete_server() -----')
cloud.delete_server(api_key, DEFAULT_REGION, instance_id)
time.sleep(30)  

status = cloud.get_status(api_key, instance_id, DEFAULT_REGION)
print(f"Server status after deletion: {status}")

#try:
#    ret = cloud.delete_server(api_key, DEFAULT_REGION, invalid_id)
#except ValueError as e:
#    print(f"Error: {e}")

