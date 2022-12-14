from EC2_instance_creator import EC2Creator
from remote_client import RemoteClient
from config_builder import ConfigBuilder
import utils
import constant
import os
import threading

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


manager_client = RemoteClient(
    hostname=manager_public_dns, 
    username=constant.USERNAME, 
    private_keyfile=private_keyfile
    )

# Instanciate ConfigBuilder object to build required config files
config_builder = ConfigBuilder(
    manager_pdns=manager_private_dns,
    node1_pdns=node1_private_dns,
    node2_pdns=node2_private_dns,
    node3_pdns=node3_private_dns
)

# Build config files
config_builder.build_manager_config()
config_builder.build_mysql_config()
config_builder.build_node_config()

# Upload all required files for manager instance
manager_client.upload_file(
    local_filepath='setups/setup_cluster_manager.sh', 
    remote_filepath='/home/ubuntu/setup_cluster_manager.sh'
    )

manager_client.upload_file(
    local_filepath='setups/setup_cluster_mysql.sh', 
    remote_filepath='/home/ubuntu/setup_cluster_mysql.sh'
    )

manager_client.upload_file(
    local_filepath='setups/setup_benchmark.sh', 
    remote_filepath='/home/ubuntu/setup_benchmark.sh'
    )

manager_client.upload_file(
    local_filepath='configs/config.ini', 
    remote_filepath='/home/ubuntu/config.ini'
    )

manager_client.upload_file(
    local_filepath='configs/mysql.cnf', 
    remote_filepath='/home/ubuntu/mysql.cnf'
    )

print("Executing cluster manager setup script remotely...")
manager_client.execute_command("sh setup_cluster_manager.sh")


print("Executing 3 threads to setup nodes...")
thread_1 = threading.Thread(target=utils.setup_node, args=(private_keyfile, node1_public_dns))
thread_2 = threading.Thread(target=utils.setup_node, args=(private_keyfile, node2_public_dns))
thread_3 = threading.Thread(target=utils.setup_node, args=(private_keyfile, node3_public_dns))

# Start threads
thread_1.start()
thread_2.start()
thread_3.start()

# Wait for threads to terminate
thread_1.join()
thread_2.join()
thread_3.join()

# EXECUTE CLUSTER MANAGER SCRIPT MANUALLY
print(f"""Run manually the setup_cluster_mysql.sh script in the manager server:\n\
STEP 1: Open a new terminal in project file directory and run: \
'ssh -i {private_keyfile} {constant.USERNAME}@{manager_public_dns}'\n\
STEP 2: Once connected, run 'sh setup_cluster_mysql.sh' """)
input("Once the script is successfully executed, press enter to continue: ")

## BENCHMARK

print("Executing benchmark script remotely...")
manager_client.execute_command("sh setup_benchmark.sh")

print("Getting back cluster benchmark result from manager remote server...")
manager_client.get_file(
    remote_filepath='benchmark_results.txt',
    local_filepath='results/cluster_benchmark_results.txt', 
)


print("Executing benchmark script remotely...")
standalone_remote_client.execute_command("sh setup_benchmark.sh")

print("getting back mysql standalone benchmark result from remote server...")
standalone_remote_client.get_file(
    remote_filepath='benchmark_results.txt',
    local_filepath='results/standalone_benchmark_results.txt', 
)

print('Creating instance for Proxy...')
proxy_instance_id = ec2_creator.create_instance(
    availability_zone=constant.US_EAST_1A,
    instance_type='t2.large')
print(f'Instance {proxy_instance_id} is running!')

proxy_public_dns, proxy_private_dns = ec2_creator.get_instance_dns(proxy_instance_id)
print(proxy_public_dns, proxy_private_dns)

proxy_client = RemoteClient(
    hostname=proxy_public_dns, 
    username=constant.USERNAME, 
    private_keyfile=private_keyfile
)

proxy_client.upload_file(local_filepath='setups/setup_proxy.sh', remote_filepath='/home/ubuntu/setup_proxy.sh')
proxy_client.upload_file(local_filepath=private_keyfile, remote_filepath=f'/home/ubuntu/{private_keyfile}')
proxy_client.upload_file(local_filepath='database_connector.py', remote_filepath='/home/ubuntu/database_connector.py')
proxy_client.upload_file(local_filepath='proxy.py', remote_filepath='/home/ubuntu/proxy.py')

print(f"""Run manually proxy script in the proxy server:\n\
STEP 1: Open a new terminal in project file directory and run: \
'ssh -i {private_keyfile} {constant.USERNAME}@{proxy_public_dns}'\n\
STEP 2: Once connected, run 'sh setup_proxy.sh && sudo python3 proxy.py {private_keyfile} {manager_private_dns} {node1_private_dns} {node2_private_dns} {node3_private_dns}'""")