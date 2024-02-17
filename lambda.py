import json
import boto3

def lambda_handler(event, context):
    region = 'us-east-1'

    # Create ELB client
    elbv2 = boto3.client('elbv2', region_name=region)
    ec2 = boto3.client('ec2', region_name=region)
    sns = boto3.client('sns', region_name=region)
    asg = boto3.client('autoscaling', region_name=region)

    
    #load_balancer_arn = 'arn:aws:elasticloadbalancing:us-east-1:295397358094:targetgroup/poovatarget/5c5d18dd6c89082d'
    alb_name = 'my-alb'
    asg_name = 'my-asg'
    #load_balancer_arn = 'arn:aws:elasticloadbalancing:us-east-1:295397358094:targetgroup/ASGpoo-1/0736934b5d40817f'
    sns_topic_arn = 'arn:aws:sns:us-east-1:471112994703:poo_sns'


    alb_describe = elbv2.describe_load_balancers(Names=[alb_name])

    alb_arns = alb_describe['LoadBalancers'][0]['LoadBalancerArn']

    # Get the target group attached to the ALB
    target_groups = elbv2.describe_target_groups(LoadBalancerArn=alb_arns)
    target_group_arn = target_groups['TargetGroups'][0]['TargetGroupArn']

    print(target_group_arn)

    # Describe instances registered with the Load Balancer
    instances = elbv2.describe_target_health(TargetGroupArn=target_group_arn)

    # Check the health status of each instance
    for instance in instances['TargetHealthDescriptions']:
        instance_id = instance['Target']['Id']
        health_status = instance['TargetHealth']['State']

        print(f"Instance ID: {instance_id}, Health Status: {health_status}")
        
    unhealthy_instances = []
    for instance in instances['TargetHealthDescriptions']:
        instance_id = instance['Target']['Id']
        health_status = instance['TargetHealth']['State']

        if health_status != ('healthy'):
            unhealthy_instances.append(instance_id)

            # snapshot 
            snapshot_id = create_snapshot(ec2, instance_id)

             # Terminate the instance
            terminate_instance(ec2, asg, asg_name, instance_id)
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


def create_snapshot(ec2, instance_id):
    response = ec2.create_snapshot(
        Description=f"Snapshot for debugging instance {instance_id}",
        VolumeId=instance_id
    )
    return response['SnapshotId']


def terminate_instance(ec2, asg, asg_name, instance_id):
    
    asg.detach_instances(InstanceIds=[instance_id], AutoScalingGroupName=asg_name, ShouldDecrementDesiredCapacity=True)

    # Terminate the instance
    ec2.terminate_instances(InstanceIds=[instance_id])

