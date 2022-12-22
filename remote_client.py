import paramiko
import time

class RemoteClient:
    def __init__(self, hostname, username, private_keyfile):
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
        stdin, stdout, stderr = self.ssh_client.exec_command(command)

        exit_status = stdout.channel.recv_exit_status()  # Blocking call
        if exit_status != 0:
            print("Error", exit_status)
            

    def close_connection(self):
        self.ssh_client.close()


    def get_file(self, remote_filepath, local_filepath):
        self.ftp_client.get(remote_filepath, local_filepath)


    def upload_file(self, local_filepath, remote_filepath):
        self.ftp_client.put(local_filepath, remote_filepath)