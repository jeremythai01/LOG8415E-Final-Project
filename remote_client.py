import paramiko
import time

class RemoteClient:
    """Client used to create and handle connection to EC2 instances."""
    def __init__(self, hostname, username, private_keyfile):
        """Constructor
        
        Parameters
        ----------
        hostname :          string
                            Name of server to connect to
        username :          string
                            Username used to authenticate
        private_keyfile :   string
                            Filename of private key used to authenticate
        """
        private_key = paramiko.RSAKey.from_private_key_file(private_keyfile)
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Set timeout and retry connecting to the instance until it is successful
        while True:
            try:
                self.ssh_client.connect(hostname=hostname, username=username, pkey=private_key)
            except paramiko.ssh_exception.NoValidConnectionsError as e:
                time.sleep(5)
            else:
                break

        # Open SFTP 
        self.ftp_client=self.ssh_client.open_sftp()

    
    def execute_command(self, command):
        """Execute command on the SSH server.
        
        Parameters
        ----------
        command :   string
                    Command to execute
        """
        stdin, stdout, stderr = self.ssh_client.exec_command(command)

        exit_status = stdout.channel.recv_exit_status()  # Blocking call
        if exit_status != 0:
            print("Error", exit_status)
            

    def close_connection(self):
        """Close SSH connection"""
        self.ssh_client.close()


    def get_file(self, remote_filepath, local_filepath):
        """Retrieve remote file from the SFTP server into local path.
        
        Parameters
        ----------
        remote_path :       string
                            Remote path of file to copy
        local_filepath :    string
                            Destination path of file
        """
        self.ftp_client.get(remote_filepath, local_filepath)


    def upload_file(self, local_filepath, remote_filepath):
        """Upload local file from local path into the SFTP server.
        
        Parameters
        ----------
        local_filepath :    string
                            Local path of file to copy
        remote_filepath :   string
                            Destination path of file
        """
        self.ftp_client.put(local_filepath, remote_filepath)