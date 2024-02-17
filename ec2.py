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

#define a empty list to store running instances
InstanceIds=[]
#function to create instance 
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
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        instance_id = response['Instances'][0]['InstanceId']
        ec2.get_waiter('instance_running').wait(
                InstanceIds.append(instance_id)
            )
        print(f"EC2 instance with ID {instance_id} launched successfully.")
    else:
        print('error occurs while creating instance please try again')
    #Define a waiter to wait for the instance to reach the "running" state
    instance_running_waiter = ec2.get_waiter('instance_running')
    # Set a longer wait time (e.g., 300 seconds)
    wait_time_seconds = 500
    # Print public IP of the instance
    response = ec2.describe_instances(InstanceIds=[instance_id])
    public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
    print(f"Public IP address of the EC2 instance: {public_ip}")


# function call to launch instance 
#create_EC2_instance()
# Define a waiter to wait for the instance to reach the "running" state
#time.sleep(100)


#Load balancing part 
    
# defining empty list to store the target arn's
target_group_arns = []
def create_alb():
    client = boto3.client('elbv2', region_name=region_name)
    
    # Define ALB parameters
    alb_params = {
        'Name': 'my-alb',  # Replace with your ALB name
        'Subnets': ['subnet-0e79495817e1b9130', 'subnet-0698d439e10bd8b1c' , 'subnet-01059ecc73324ffd1'],  # Replace with your subnet IDs
        'SecurityGroups': ['sg-078ec58c53614eba1'],  # Replace with your security group IDs
        'Scheme': 'internet-facing',  # Replace with 'internal' for internal ALB
        'IpAddressType': 'ipv4',  # Replace with 'dualstack' for IPv6 support
        'Tags': [{'Key': 'Name', 'Value': 'my-alb'}]  # Replace with additional tags as needed
    }
    
    # Create ALB
    alb_response = client.create_load_balancer(**alb_params)
    alb_arn = alb_response['LoadBalancers'][0]['LoadBalancerArn']
    print("ALB created successfully:", alb_arn)
    
    # Define target group parameters
    target_group_params = {
        'Name': 'my-target-group',  # Replace with your target group name
        'Protocol': 'HTTP',  # Replace with your desired protocol
        'Port': 80,  # Replace with your desired port
        'VpcId': 'vpc-06b1320d527910a58',  # Replace with your VPC ID
        'HealthCheckProtocol': 'HTTP',  # Replace with your desired health check protocol
        'HealthCheckPort': str(80),  # Replace with your desired health check port
        'HealthCheckPath': '/',  # Replace with your desired health check path
        #'TargetType': 'instance',  # Replace with 'ip' or 'lambda' if needed
        
    }
    
    # Create target group
    target_group_response = client.create_target_group(**target_group_params)
    target_group_arn = target_group_response['TargetGroups'][0]['TargetGroupArn']
    target_group_arns.append(target_group_arn)
    print("Target group created successfully:", target_group_arns)
    
    

    # Register ec2 instance with the target

    instance_ids = ['i-00a4d65741d135b58']  # Replace with your EC2 instance IDs
    target_group_attachment_params = {
        'TargetGroupArn': target_group_arn,
        'Targets': [{'Id': instance_id} for instance_id in instance_ids]
    }
    client.register_targets(**target_group_attachment_params)
    print("EC2 instances registered with target group successfully")
    
    # Define listener parameters
    listener_params = {
        'LoadBalancerArn': alb_arn,
        'Protocol': 'HTTP',  # Replace with your desired protocol
        'Port': 80,  # Replace with your desired port
        'DefaultActions': [
            {
                'Type': 'forward',
                'TargetGroupArn': target_group_arn
            },
        ]
    }
    
    # Create listener
    client.create_listener(**listener_params)
    print("Listener created successfully")

#Function call to create ALB
#print(create_alb())


#ASG configuration 
#function to create auto scalling group
asg_grp_arn=[]    
def create_asg():
    # Initialize AWS clients
    ec2_client = boto3.client('ec2')
    asg_client = boto3.client('autoscaling',region_name=region_name)
    instance_ids = ['i-00a4d65741d135b58'] 
    target_group_arns=['arn:aws:elasticloadbalancing:us-east-1:471112994703:targetgroup/my-target-group/e2866d138ec362bc']
    

    # Define auto scaling group parameters
    asg_params = {
        'AutoScalingGroupName': 'my-asg',  # Replace with your ASG name
        #'LaunchConfigurationName': 'my-launch-config',  # Replace with your launch configuration name
        'MinSize': 1,  # Replace with your minimum instance count
        'MaxSize': 5,  # Replace with your maximum instance count
        'DesiredCapacity': 2,  # Replace with your desired instance count
        #'AvailabilityZones': ['us-west-1a', 'us-west-1b'],  # Replace with your availability zones
        'InstanceId': instance_ids[0],
        'TargetGroupARNs': target_group_arns
        # Add additional parameters as needed
    }

    # Create auto scaling group
    asg_response= asg_client.create_auto_scaling_group(**asg_params)
    asg_arn = asg_response['AutoScalingGroups'][0]['AutoScalingGroupARN']
    asg_grp_arn.append(asg_arn)
    print("Auto Scaling Group created successfully ",asg_grp_arn)

    # Define scaling policies
    scaling_policy_params = {
        'AutoScalingGroupName': 'my-asg',  # Replace with your ASG name
        'PolicyName': 'my-scaling-policy',  # Replace with your scaling policy name
        'ScalingAdjustment': 1,  # Replace with your scaling adjustment (e.g., 1 for scale out, -1 for scale in)
        'Cooldown': 300,  # Replace with your cooldown period in seconds
        'InstanceId': instance_ids[0],
        'DesiredCapacity': 2,
        'AdjustmentType': 'ChangeInCapacity',  # Replace with 'PercentChangeInCapacity' for percentage-based adjustment
        # Add additional parameters as needed
    }

    # Create scale out policy
    asg_client.put_scaling_policy(
        **scaling_policy_params,
        PolicyType='SimpleScaling',
        AdjustmentType='ChangeInCapacity',
        Cooldown=300,
        ScalingAdjustment=1
    )
    print("Scale out policy created successfully")

    # Create scale in policy
    asg_client.put_scaling_policy(
        **scaling_policy_params,
        PolicyName='my-scaling-policy-scale-in',  # Replace with your scale in policy name
        ScalingAdjustment=-1  # Replace with your scaling adjustment for scale in
    )
    print("Scale in policy created successfully")

#function call for asg config
#print(create_asg())


#Loggs and monitors 

s3_bucket_name = 'first-bucket-poo-web'
elb_client = boto3.client('elbv2', region_name=region_name)    
alb_arn = []
alb_name='my-alb'

response_describe_arn = elb_client.describe_load_balancers(
    Names=[alb_name],
)

alb_arn.append(response_describe_arn['LoadBalancers'][0]['LoadBalancerArn'])


def configure_alb_access_logs(alb_arn, s3_bucket_name):
    # Initialize boto3 client
    elbv2_client = boto3.client('elbv2')

    # Configure ALB access logs
    response = elbv2_client.modify_load_balancer_attributes(
        LoadBalancerArn=alb_arn,
        Attributes=[
            {
                'Key': 'access_logs.s3.enabled',
                'Value': 'true'
            },
            {
                'Key': 'access_logs.s3.bucket',
                'Value': s3_bucket_name
            }
        ]
    )

    print('ALB access logs configured successfully.')


# Configure ALB access logs function call
configure_alb_access_logs(alb_arn, s3_bucket_name)

bucket_name = 'log-bucket11'
#function call to create a bucket 
buc=create_s3_bucket(bucket_name)
print(buc)

