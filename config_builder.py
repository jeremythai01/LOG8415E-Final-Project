class ConfigBuilder:

    def __init__(self, manager_pdns, node1_pdns, node2_pdns, node3_pdns):
        self.manager_pdns = manager_pdns
        self.node1_pdns = node1_pdns
        self.node2_pdns = node2_pdns
        self.node3_pdns = node3_pdns


    def build_manager_config(self):

        content = f"""[ndbd default]
# Options affecting ndbd processes on all data nodes:
NoOfReplicas=3	# Number of replicas

[ndb_mgmd]
# Management process options:
hostname={self.manager_pdns} # Hostname of the manager
datadir=/var/lib/mysql-cluster 	# Directory for the log files

[ndbd]
hostname={self.node1_pdns} # private Hostname/IP of the first data node
NodeId=2			# Node ID for this data node
datadir=/usr/local/mysql/data	# Remote directory for the data files

[ndbd]
hostname={self.node2_pdns} # private Hostname/IP of the first data node
NodeId=3			# Node ID for this data node
datadir=/usr/local/mysql/data	# Remote directory for the data files

[ndbd]
hostname={self.node3_pdns} # private Hostname/IP of the first data node
NodeId=4			# Node ID for this data node
datadir=/usr/local/mysql/data	# Remote directory for the data files

[mysqld]
# SQL node options:
hostname={self.manager_pdns} # In our case the MySQL server/client is on the same instance as the cluster manager"""

        with open('configs/config.ini', 'w') as f:
            f.write(content)

    

    def build_node_config(self):
        
        content = f"""[mysql_cluster]
# Options for NDB Cluster processes:
ndb-connectstring={self.manager_pdns}  # location of cluster manager"""


        with open('configs/my.cnf', 'w') as f:
            f.write(content)


    
    def build_mysql_config(self):

        content = f"""# as published by the Free Software Foundation.
#
# This program is also distributed with certain software (including
# but not limited to OpenSSL) that is licensed under separate terms,
# as designated in a particular file or component or in included license
# documentation.  The authors of MySQL hereby grant you an additional
# permission to link the program and your derivative works with the
# separately licensed software that they have included with MySQL.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License, version 2.0, for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA

#
# The MySQL  Server configuration file.
#
# For explanations see
# http://dev.mysql.com/doc/mysql/en/server-system-variables.html

# * IMPORTANT: Additional settings that can override those from this file!
#   The files must end with '.cnf', otherwise they'll be ignored.
#
!includedir /etc/mysql/conf.d/
!includedir /etc/mysql/mysql.conf.d/

[mysqld]
# Options for mysqld process:
ndbcluster                      # run NDB storage engine
bind-address=0.0.0.0

[mysql_cluster]
# Options for NDB Cluster processes:
ndb-connectstring={self.manager_pdns}  # location of management server"""

        with open('configs/mysql.cnf', 'w') as f:
            f.write(content)