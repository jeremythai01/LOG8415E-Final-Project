from remote_client import RemoteClient
import constant


def setup_node(private_keyfile, node_public_dns):

    node_client = RemoteClient(
        hostname=node_public_dns, 
        username=constant.USERNAME, 
        private_keyfile=private_keyfile
    )

    node_client.upload_file(
    local_filepath='setups/setup_cluster_node.sh', 
    remote_filepath='/home/ubuntu/setup_cluster_node.sh'
    )

    node_client.upload_file(
    local_filepath='configs/my.cnf', 
    remote_filepath='/home/ubuntu/my.cnf'
    )

    node_client.execute_command("sh setup_cluster_node.sh")

    node_client.close_connection()