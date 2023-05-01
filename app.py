import boto3
import json
from datetime import datetime, timezone

def datetime_converter(obj):
    if isinstance(obj, datetime):
        return obj.__str__()

def get_launch_time(instance):
    return instance.launch_time

def split_and_clean(s: str):
    items = s.split(',')
    items = [item.strip() for item in items]
    return items


def print_uptime(sorted_instances):
    current_time = datetime.utcnow()
    for instance in sorted_instances:
        launch_time_naive = instance.launch_time.astimezone(timezone.utc).replace(tzinfo=None)
        time_since_launch = (current_time - launch_time_naive).total_seconds()
        print(f"Instance ID: {instance.id}, Time since launch: {time_since_launch} seconds")


def etl(endpoint: str):
    with open('regions.txt', 'r') as f:
        regions = split_and_clean(f.read())

    for region in regions:
        ec2 = boto3.resource(
            'ec2',
            region_name=region,
            endpoint_url=endpoint
        )

        instances = ec2.instances.all()

        sorted_instances = sorted(
            instances,
            key=get_launch_time
        )

        with open(f'{region}.json', 'w') as f:
            instances_data = []
            for instance in sorted_instances:
                instances_data.append({
                    'instance_id': instance.id,
                    'instance_type': instance.instance_type,
                    'launch_time': instance.launch_time,
                    'state': instance.state['Name'],
                    'public_ip_address': instance.public_ip_address,
                    'private_ip_address': instance.private_ip_address,
                    'tags': instance.tags
                })
            json.dump(instances_data, f, default=datetime_converter, indent=4)

            # Bonus Print instance ID and upTime
            print_uptime(sorted_instances)


def get_instances_from_file(region):
    file_name = f'{region}.json'
    try:
        with open(file_name, 'r') as f:
            instances_data = json.load(f)

        instance_ids = [instance['instance_id'] for instance in instances_data]
        return instance_ids
    except FileNotFoundError:
        print(f'File not found: {file_name}')
        return []

if __name__ == "__main__":
    etl(endpoint='http://0.0.0.0:4000')
    region = 'us-east-1'
    print(get_instances_from_file(region))
