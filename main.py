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


#Create ec2 instance for MySQL cluster manager
print('Creating instance for MySQL cluster manager...')
manager_instance_id = ec2_creator.create_instance(
    availability_zone=constant.US_EAST_1A,
    instance_type=constant.T2_MICRO)
print(f'Instance {manager_instance_id} is running!')

# Create ec2 instance for MySQL cluster data node
print('Creating instance for MySQL data node 1...')
node1_instance_id = ec2_creator.create_instance(
    availability_zone=constant.US_EAST_1A,
    instance_type=constant.T2_MICRO)
print(f'Instance {node1_instance_id} created!')

# Create ec2 instance for MySQL cluster data node
print('Creating instance for MySQL data node 2...')
node2_instance_id = ec2_creator.create_instance(
    availability_zone=constant.US_EAST_1A,
    instance_type=constant.T2_MICRO)
print(f'Instance {node2_instance_id} created!')


# Create ec2 instance for MySQL cluster data node
print('Creating instance for MySQL data node 3...')
node3_instance_id = ec2_creator.create_instance(
    availability_zone=constant.US_EAST_1A,
    instance_type=constant.T2_MICRO)
print(f'Instance {node3_instance_id} created!')


manager_public_dns, manager_private_dns = ec2_creator.get_instance_dns(manager_instance_id)
print(manager_public_dns, manager_private_dns)

node1_public_dns, node1_private_dns = ec2_creator.get_instance_dns(node1_instance_id)
print(node1_public_dns, node1_private_dns)

node2_public_dns, node2_private_dns = ec2_creator.get_instance_dns(node2_instance_id)
print(node2_public_dns, node2_private_dns)

node3_public_dns, node3_private_dns = ec2_creator.get_instance_dns(node3_instance_id)
print(node3_public_dns, node3_private_dns)