from database_connector import DBConnector
from sshtunnel import SSHTunnelForwarder

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