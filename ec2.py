import boto3
import paramiko
import time
from botocore.exceptions import WaiterError

# Specify your AWS credentials and region
aws_access_key_id = '#############' #replace withg your access_key
aws_secret_access_key = '########'  #replace withg your secret_access_key
region_name = 'us-east-1'  # e.g., 'us-east-1'

# Create an S3 client
s3_client = boto3.client('s3')

def create_s3_bucket(bucket_name):
    # Attempt to create the bucket
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"S3 bucket '{bucket_name}' created successfully.")
        return bucket_name
    except Exception as e:
        print(f"Error creating S3 bucket '{bucket_name}': {e}")
        return None
    
bucket_name = 'first-bucket-poo-web'
#function call to create bucket 
#create_s3_bucket(bucket_name)

# upload file in the bucket
file_path= 'C:\\Users\\Asus\\OneDrive\\Desktop\\web application boto3 automation\\boto3_automation_web_application-\\index.html'
def upload_to_s3_bucket(bucket_name):
    try:
        # Upload the file to the specified bucket and object key
        s3_client.upload_file(file_path, bucket_name, 'index.html')
        print(f"File uploaded successfully to bucket '{bucket_name}'")
        return True
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return False
#function call to upload static file in the bucket     
#upload_to_s3_bucket(bucket_name)


# function to create ec2 instance 
    
#userdata='C:\\Users\\Asus\\OneDrive\\Desktop\\web application boto3 automation\\userdata.sh'
user_data='''#!/bin/bash
sudo apt update 
sudo apt-get install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
sudo apt install awscli -y
sudo rm -rf /var/www/html/*
sudo aws s3 cp s3://first-bucket-poo-web/index.html /var/www/html/index.html
sudo systemctl restart nginx
'''
ec2 = boto3.client('ec2')

def create_EC2_instance():
    # Create an EC2 client
    ec2 = boto3.client('ec2', region_name=region_name)
    security_group_id='sg-078ec58c53614eba1'
    Role='poo-ec2'
    
    # Specify the parameters for launching the EC2 instance
    response = ec2.run_instances(
        ImageId= 'ami-0c7217cdde317cfec',  # Replace with the desired AMI ID
        InstanceType = 't2.micro',           # Replace with the desired instance type
        KeyName= 'poova',     # Replace with your key pair name
        IamInstanceProfile={
                'Name': Role
            },
        UserData=user_data,
        MinCount= 1,
        MaxCount= 1,
        
        SecurityGroupIds= [security_group_id],
        TagSpecifications= [
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': 'Myinstance'}
                ]
            }
        ]
     )

    # Launch the EC2 instance
   # instance_response = ec2.run_instances(**instance_params)
    instance_id = response['Instances'][0]['InstanceId']
    print(f"EC2 instance with ID {instance_id} launched successfully.")
    #Define a waiter to wait for the instance to reach the "running" state
    instance_running_waiter = ec2.get_waiter('instance_running')
    # Set a longer wait time (e.g., 300 seconds)
    wait_time_seconds = 500
    # Print public IP of the instance
    response = ec2.describe_instances(InstanceIds=[instance_id])
    public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
    print(f"Public IP address of the EC2 instance: {public_ip}")


# function call to launch instance 
create_EC2_instance()
# Define a waiter to wait for the instance to reach the "running" state
#instance_running_waiter = ec2.get_waiter('instance_running')



