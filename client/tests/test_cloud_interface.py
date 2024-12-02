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
api_key = [access, secret]

cloud = AwsInterface()

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
try:
    ret = cloud.get_locations([])
except ValueError as e:
    assert(e == "Invalid API key")

print('----- TESTING: create_ssh_key() -----')
# create_ssh_key()

print('----- TESTING: create_server() -----')
# create_server()

print('----- TESTING: get_status() -----')
# get_status()
#valid api key
ret = cloud.get_status()

print('----- TESTING: delete_server() -----')
# delete_server()


