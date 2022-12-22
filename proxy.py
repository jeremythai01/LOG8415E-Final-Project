from database_connector import DBConnector
from sshtunnel import SSHTunnelForwarder
from pythonping import ping
import constant
import random
import os
import sys

class Proxy:
    def __init__(self, pkey, manager_pdns, node1_pdns, node2_pdns, node3_pdns):
        self.pkey = pkey
        self.manager_pdns = manager_pdns
        self.node1_pdns = node1_pdns
        self.node2_pdns = node2_pdns
        self.node3_pdns = node3_pdns


    def forward_request(self, target_host, query):
        with SSHTunnelForwarder(target_host, ssh_username=constant.USERNAME, ssh_pkey=self.pkey, remote_bind_address=(self.manager_pdns, constant.MYSQL_PORT)) as tunnel:
            DBConnector(self.manager_pdns).execute_query(query)     

        
    def direct_hit(self, query):
        print(f"Chosen node: {self.manager_pdns}")
        self.forward_request(self.manager_pdns, query)

    
    def random_hit(self, query):
        # Choose randomly a data node
        target_host = random.choice([self.node1_pdns, self.node2_pdns, self.node3_pdns])
        print(f"Chosen node: {target_host}")
        self.forward_request(target_host, query)


    def ping_server(self, server_pdns):
        return ping(target=server_pdns, count=1, timeout=2).rtt_avg_ms
        

   
    def custom_hit(self, query):
        nodes = [self.node1_pdns, self.node2_pdns, self.node3_pdns]
        avg_latencies = [self.ping_server(host) for host in nodes]

        # Custom: Measure ping for all server and choose the one with the lowest response time
        fastest_node = nodes[avg_latencies.index(min(avg_latencies))]
        print(f"Chosen node: {fastest_node}")
        self.forward_request(fastest_node, query)


if __name__ == "__main__":

    # Get env variables
    pkey = os.getenv('KEYPAIR')
    manager_pdns = os.getenv('MANAGER_PRIVATE_DNS')
    node1_pdns = os.getenv('NODE1_PRIVATE_DNS')
    node2_pdns = os.getenv('NODE2_PRIVATE_DNS')
    node3_pdns = os.getenv('NODE3_PRIVATE_DNS')

    # Get passed request
    request = sys.argv[1]

    proxy = Proxy(pkey, manager_pdns, node1_pdns, node2_pdns, node3_pdns)

    print("DIRECT HIT:")
    proxy.direct_hit(request)

    print("RANDOM:")
    proxy.random_hit(request)

    print("LOWEST RESPONSE TIME:")
    proxy.custom_hit(request)