import json
import boto3

def lambda_handler(event, context):
    region = 'us-east-1'

    # Create ELB client
    elbv2 = boto3.client('elbv2', region_name=region)

    """# Describe all load balancers
    response = elbv2.describe_load_balancers()

    # Extract load balancer information
    load_balancers = response['LoadBalancers']
    for lb in load_balancers:
        print(f"Load Balancer Name: {lb['LoadBalancerName']}")
        print(f"Load Balancer ARN: {lb['LoadBalancerArn']}")
        print(f"Load Balancer DNS Name: {lb['DNSName']}")
        print(f"Load Balancer Scheme: {lb['Scheme']}")
        print(f"Load Balancer VPC ID: {lb['VpcId']}")
        print("\n")"""
    #load_balancer_arn = 'arn:aws:elasticloadbalancing:us-east-1:295397358094:targetgroup/poovatarget/5c5d18dd6c89082d'
    load_balancer_arn = 'arn:aws:elasticloadbalancing:us-east-1:295397358094:targetgroup/ASGpoo-1/0736934b5d40817f'
    sns_topic_arn = 'arn:aws:sns:us-east-1:295397358094:sns-poo'

    # Describe instances registered with the Load Balancer
    instances = elbv2.describe_target_health(TargetGroupArn=load_balancer_arn)

    # Check the health status of each instance
    for instance in instances['TargetHealthDescriptions']:
        instance_id = instance['Target']['Id']
        health_status = instance['TargetHealth']['State']

        print(f"Instance ID: {instance_id}, Health Status: {health_status}")
        
    unhealthy_instances = []
    for instance in instances['TargetHealthDescriptions']:
        instance_id = instance['Target']['Id']
        health_status = instance['TargetHealth']['State']

        if health_status != ('healthy' or 'unused'):
            unhealthy_instances.append(instance_id)
    if unhealthy_instances:
        sns = boto3.client('sns')
        message = f"Health Status: {health_status}"
        subject = 'Unhealthy Instances Alert'
        print(message)
        print(subject)
        print(sns_topic_arn)

        # Publish message to SNS topic
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject=subject
        )
    return {
        'statusCode': 200,
        'body': 'Load Balancer health check completed.'
    }
