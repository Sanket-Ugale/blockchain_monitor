import boto3
import paramiko
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
EMAIL = os.getenv('EMAIL')  # For SNS alerts

# AWS Configuration
REGION = 'us-east-1'
INSTANCE_TYPE = 't2.micro'
AMI_ID = 'ami-0c55b159cbfafe1f0'  # Ubuntu 22.04 LTS
KEY_PAIR = 'blockchain-node'
SECURITY_GROUP_ID = 'sg-xxxxxxxx'  # Allow SSH + blockchain ports

# Blockchain Configuration
BLOCKCHAIN = 'ethereum'  # Options: 'ethereum', 'polkadot'

def create_ec2_instance():
    """Provision an EC2 instance using Boto3."""
    ec2 = boto3.client(
        'ec2',
        region_name=REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    
    instance = ec2.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_PAIR,
        SecurityGroupIds=[SECURITY_GROUP_ID],
        MinCount=1,
        MaxCount=1
    )
    instance_id = instance['Instances'][0]['InstanceId']
    print(f"Instance {instance_id} launching...")
    
    # Wait for instance to be running
    ec2.get_waiter('instance_running').wait(InstanceIds=[instance_id])
    instance = ec2.describe_instances(InstanceIds=[instance_id])
    public_ip = instance['Reservations'][0]['Instances'][0]['PublicIpAddress']
    return public_ip

def install_blockchain(public_ip):
    """Install blockchain dependencies via SSH."""
    key = paramiko.RSAKey.from_private_key_file(f"{KEY_PAIR}.pem")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(public_ip, username='ubuntu', pkey=key)
        
        # Install Ethereum Node (Geth)
        if BLOCKCHAIN == 'ethereum':
            commands = [
                'sudo apt-get update',
                'sudo apt-get install -y software-properties-common',
                'sudo add-apt-repository -y ppa:ethereum/ethereum',
                'sudo apt-get update',
                'sudo apt-get install -y ethereum',
                'sudo systemctl start geth'
            ]
        
        # Install Polkadot Node
        elif BLOCKCHAIN == 'polkadot':
            commands = [
                'sudo apt-get update',
                'sudo apt-get install -y curl',
                'curl https://getsubstrate.io -sSf | bash -s -- --fast',
                'source ~/.cargo/env',
                'cargo install --git https://github.com/paritytech/polkadot'
            ]
        
        # Execute commands
        for cmd in commands:
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode())
        
        print("Blockchain node setup complete!")
    
    finally:
        client.close()

def monitor_node(public_ip):
    """Check node status and send alerts via AWS SNS."""
    sns = boto3.client(
        'sns',
        region_name=REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    topic_arn = sns.create_topic(Name='NodeDownAlerts')['TopicArn']
    sns.subscribe(TopicArn=topic_arn, Protocol='email', Endpoint=EMAIL)
    
    key = paramiko.RSAKey.from_private_key_file(f"{KEY_PAIR}.pem")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    while True:
        try:
            client.connect(public_ip, username='ubuntu', pkey=key)
            # Check if Geth is running (for Ethereum)
            _, stdout, _ = client.exec_command('systemctl is-active geth')
            status = stdout.read().decode().strip()
            
            if status != 'active':
                sns.publish(
                    TopicArn=topic_arn,
                    Message=f"Blockchain node at {public_ip} is down!"
                )
                print("Alert sent!")
        except Exception as e:
            print(f"Connection failed: {e}")
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    public_ip = create_ec2_instance()
    install_blockchain(public_ip)
    monitor_node(public_ip)