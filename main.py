from EC2_instance_creator import EC2Creator
from remote_client import RemoteClient
import constant
import os

# Remove locally all previously generated pem files
os.system('chmod 777 *.pem | rm *.pem')

ec2_creator = EC2Creator()
private_keyfile = ec2_creator.keypair['KeyName']+ ".pem"

#Create ec2 instance for mysql standalone server
print('Creating instance for MySQL standalone server...')
instance_id = ec2_creator.create_instance(
    availability_zone=constant.US_EAST_1A,
    instance_type=constant.T2_MICRO)
print(f'Instance {instance_id} created!')

public_dns, private_dns = ec2_creator.get_instance_dns(instance_id)
print(public_dns, private_dns)

standalone_remote_client = RemoteClient(
    hostname=public_dns, 
    username=constant.USERNAME, 
    private_keyfile=private_keyfile
    )

print("uploading mysql standalone setup to remote server...")
standalone_remote_client.upload_file(
    local_filepath='setups/setup_standalone_mysql.sh', 
    remote_filepath='/home/ubuntu/setup_standalone_mysql.sh'
    )

print("uploading benchmark script to remote server..")
standalone_remote_client.upload_file(
    local_filepath='setups/setup_benchmark.sh', 
    remote_filepath='/home/ubuntu/setup_benchmark.sh'
    )

print("executing mysql standalone setup remotely...")
standalone_remote_client.execute_command("sh setup_standalone_mysql.sh")


print("Executing benchmark script remotely...")
standalone_remote_client.execute_command("sh setup_benchmark.sh")

print("getting back mysql standalone benchmark result from remote server...")
standalone_remote_client.get_file(
    remote_filepath='benchmark_results.txt',
    local_filepath='results/standalone_benchmark_results.txt', 
    )