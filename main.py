from EC2_instance_creator import EC2Creator
from remote_client import RemoteClient
from config_builder import ConfigBuilder
from logger import logger
from utils import setup_node
import constant
import os
import threading

# Remove all pem files generated previously
os.system('chmod 777 *.pem | rm *.pem')

ec2_creator = EC2Creator()
private_keyfile = ec2_creator.keypair['KeyName']+ ".pem"

#################### FIRST PART ####################
logger.info("##################### FIRST PART ####################")

# Create ec2 instance for mysql standalone server
logger.info('Creating instance for MySQL standalone server...')
instance_id = ec2_creator.create_instance(availability_zone=constant.US_EAST_1A,instance_type=constant.T2_MICRO)
public_dns, private_dns = ec2_creator.get_instance_dns(instance_id)
logger.info(f"MySQL Standalone server public DNS: {public_dns} and private DNS: {private_dns}")

# Create ec2 instance for MySQL cluster manager
logger.info('Creating instance for MySQL cluster manager...')
manager_instance_id = ec2_creator.create_instance(availability_zone=constant.US_EAST_1A, instance_type=constant.T2_MICRO)
manager_public_dns, manager_private_dns = ec2_creator.get_instance_dns(manager_instance_id)
logger.info(f"MySQL cluster manager public DNS: {manager_public_dns} and private DNS: {manager_private_dns}")

# Create ec2 instance for MySQL cluster data node 1
logger.info('Creating instance for MySQL data node 1...')
node1_instance_id = ec2_creator.create_instance(availability_zone=constant.US_EAST_1A, instance_type=constant.T2_MICRO)
node1_public_dns, node1_private_dns = ec2_creator.get_instance_dns(node1_instance_id)
logger.info(f"MySQL data node 1 public DNS: {node1_public_dns} and private DNS: {node1_private_dns}")

# Create ec2 instance for MySQL cluster data node 2
logger.info('Creating instance for MySQL data node 2...')
node2_instance_id = ec2_creator.create_instance(availability_zone=constant.US_EAST_1A, instance_type=constant.T2_MICRO)
node2_public_dns, node2_private_dns = ec2_creator.get_instance_dns(node2_instance_id)
logger.info(f"MySQL data node 2 public DNS: {node2_public_dns} and private DNS: {node2_private_dns}")

# Create ec2 instance for MySQL cluster data node 3
logger.info('Creating instance for MySQL data node 3...')
node3_instance_id = ec2_creator.create_instance(availability_zone=constant.US_EAST_1A, instance_type=constant.T2_MICRO)
node3_public_dns, node3_private_dns = ec2_creator.get_instance_dns(node3_instance_id)
logger.info(f"MySQL data node 3 public DNS: {node3_public_dns} and private DNS: {node3_private_dns}")

#Create ec2 instance for proxy
logger.info('Creating instance for Proxy...')
proxy_instance_id = ec2_creator.create_instance(availability_zone=constant.US_EAST_1A, instance_type=constant.T2_LARGE)
proxy_public_dns, proxy_private_dns = ec2_creator.get_instance_dns(proxy_instance_id)
logger.info(f"Proxy public DNS: {proxy_public_dns} and private DNS: {proxy_private_dns}")


logger.info(f"Setting up MySQL Standalone server...")
standalone_remote_client = RemoteClient(hostname=public_dns, username=constant.USERNAME, private_keyfile=private_keyfile)
standalone_remote_client.upload_file(local_filepath='setups/setup_standalone_mysql.sh', remote_filepath='/home/ubuntu/setup_standalone_mysql.sh')
standalone_remote_client.upload_file(local_filepath='setups/setup_benchmark.sh', remote_filepath='/home/ubuntu/setup_benchmark.sh')
standalone_remote_client.execute_command("sh setup_standalone_mysql.sh")

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

logger.info("Setting up cluster manager...")

# Upload all required files for manager instance
manager_client = RemoteClient(hostname=manager_public_dns, username=constant.USERNAME, private_keyfile=private_keyfile)
manager_client.upload_file(local_filepath='setups/setup_cluster_manager.sh', remote_filepath='/home/ubuntu/setup_cluster_manager.sh')
manager_client.upload_file(local_filepath='setups/setup_cluster_mysql.sh', remote_filepath='/home/ubuntu/setup_cluster_mysql.sh')
manager_client.upload_file(local_filepath='setups/setup_benchmark.sh', remote_filepath='/home/ubuntu/setup_benchmark.sh')
manager_client.upload_file(local_filepath='configs/config.ini', remote_filepath='/home/ubuntu/config.ini')
manager_client.upload_file(local_filepath='configs/mysql.cnf', remote_filepath='/home/ubuntu/mysql.cnf')
manager_client.execute_command("sh setup_cluster_manager.sh")


logger.info("Starting 3 threads to setup nodes...")
thread_1 = threading.Thread(target=setup_node, args=(private_keyfile, node1_public_dns, 1))
thread_2 = threading.Thread(target=setup_node, args=(private_keyfile, node2_public_dns, 2))
thread_3 = threading.Thread(target=setup_node, args=(private_keyfile, node3_public_dns, 3))

# Start threads
thread_1.start()
thread_2.start()
thread_3.start()

# Wait for threads to terminate
thread_1.join()
thread_2.join()
thread_3.join()

# Execute cluster mysql server manually
logger.info(f"""FOLLOW THESE STEPS TO SETUP THE CLUSTER MYSQL SERVER:\n\
STEP 1: Open a new terminal in the project folder location and run:\
' ssh -i {private_keyfile} {constant.USERNAME}@{manager_public_dns} '\n\
STEP 2: Once connected, run ' sh setup_cluster_mysql.sh ' """)
input("Once it is successfully done, press enter to continue: ")

# Benchmark both standalone and cluster databases
logger.info("Executing benchmark for standalone and cluster (using 100 000 records)...")
manager_client.execute_command("sh setup_benchmark.sh")
manager_client.get_file(remote_filepath='benchmark_results.txt', local_filepath='results/cluster_benchmark_results.txt')
standalone_remote_client.execute_command("sh setup_benchmark.sh")
standalone_remote_client.get_file(remote_filepath='benchmark_results.txt',local_filepath='results/standalone_benchmark_results.txt')
logger.info("DONE. Benchmark results can be found in the folder \'results\'...")


##################### SECOND PART ####################

logger.info("##################### SECOND PART ####################")

logger.info(f"""FOLLOW THESE STEPS TO CREATE A SQL USER FOR THE PROXY IN THE CLUSTER MYSQL:\n\
STEP 1: Run ' sudo mysql -e "CREATE USER '{constant.MYSQL_USERNAME}'@'{proxy_private_dns}' IDENTIFIED BY '{constant.MYSQL_PASSWORD}';" '\n\
STEP 2: Run ' sudo mysql -e "GRANT ALL PRIVILEGES ON *.* TO '{constant.MYSQL_USERNAME}'@'{proxy_private_dns}';" ' """)
input("Once it is successfully done, press enter to continue: ")

proxy_client = RemoteClient(hostname=proxy_public_dns, username=constant.USERNAME, private_keyfile=private_keyfile)

# Upload proxy files
proxy_client.upload_file(local_filepath='setups/setup_proxy.sh', remote_filepath='/home/ubuntu/setup_proxy.sh')
proxy_client.upload_file(local_filepath=private_keyfile, remote_filepath=f'/home/ubuntu/{private_keyfile}')
proxy_client.upload_file(local_filepath='constant.py', remote_filepath='/home/ubuntu/constant.py')
proxy_client.upload_file(local_filepath='database_connector.py', remote_filepath='/home/ubuntu/database_connector.py')
proxy_client.upload_file(local_filepath='proxy.py', remote_filepath='/home/ubuntu/proxy.py')

logger.info(f"""FOLLOW THESE STEPS TO SETUP THE PROXY:\n\
STEP 1: Open a new terminal in the project folder location and run: \
' ssh -i {private_keyfile} {constant.USERNAME}@{proxy_public_dns} '\n\
STEP 2: Once connected, run ' sh setup_proxy.sh {private_keyfile} {manager_private_dns} {node1_private_dns} {node2_private_dns} {node3_private_dns} '\n\
STEP 3: Start proxy by running ' sudo python3 proxy.py "SELECT COUNT(*) FROM actor;" '""")