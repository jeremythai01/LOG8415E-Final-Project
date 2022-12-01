from EC2_instance_creator import EC2Creator
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