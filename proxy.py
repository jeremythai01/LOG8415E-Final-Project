from database_connector import DBConnector
from sshtunnel import SSHTunnelForwarder
from pythonping import ping
import random

class Proxy:

    def __init__(self, manager_pdns, node1_pdns, node2_pdns, node3_pdns, pkey):
        self.manager_pdns = manager_pdns
        self.node1_pdns = node1_pdns
        self.node2_pdns = node2_pdns
        self.node3_pdns = node3_pdns
        self.pkey = pkey


    def forward_request(self, target_host, query):
        with SSHTunnelForwarder(target_host, ssh_username='ubuntu', ssh_pkey=self.pkey, remote_bind_address=(self.manager_pdns, 3306)) as tunnel:
            DBConnector(self.manager_pdns).execute_query(query)     

        
    def direct_hit(self, query):
        self.forward_request(self.manager_pdns, query)


    # Random: randomly choose a slave node 
    def random(self, query):

        # Choose randomly a slave node
        target_host = random.choice([self.node1_pdns, self.node2_pdns, self.node3_pdns])

        self.forward_request(target_host, query)


    def ping_host(self, host):
        return ping(target=host, count=1, timeout=2).rtt_avg_ms
        

    # Customize: Measure ping for all server and choose the one with the smallest response time
    def customize(self, query):

        nodes = [self.node1_pdns, self.node2_pdns, self.node3_pdns]
        avg_latencies = [self.ping_host(host) for host in nodes]
        fastest_node = nodes[avg_latencies.index(min(avg_latencies))]
        self.forward_request(fastest_node, query)