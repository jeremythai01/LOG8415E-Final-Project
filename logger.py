import logging

# Instanciate a logger to be used in other files
logger = logging

logger.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S")

# Allow only INFO-level logs
logger.getLogger('botocore').setLevel(logging.INFO)
logger.getLogger('boto3').setLevel(logging.INFO)
logger.getLogger('paramiko').setLevel(logging.INFO)
logger.getLogger('sshtunnel').setLevel(logging.INFO)