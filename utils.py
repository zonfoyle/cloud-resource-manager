import boto3
import yaml


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def get_ec2_client(region_name: str):
    return boto3.client("ec2", region_name=region_name)


def get_iam_client():
    return boto3.client("iam")


def create_vpc(ec2_client, cidr_block: str, name: str):
    existing_vpcs = ec2_client.describe_vpcs(
        Filters=[{"Name": "tag:Name", "Values": [name]}]
    )["Vpcs"]

    if existing_vpcs:
        vpc_id = existing_vpcs[0]["VpcId"]
        print(f"Using existing VPC: {vpc_id}")
        return vpc_id

    response = ec2_client.create_vpc(CidrBlock=cidr_block)
    vpc_id = response["Vpc"]["VpcId"]

    ec2_client.create_tags(
        Resources=[vpc_id],
        Tags=[{"Key": "Name", "Value": name}]
    )

    return vpc_id


def create_subnet(ec2_client, vpc_id: str, cidr_block: str, name: str):
    existing_subnets = ec2_client.describe_subnets(
        Filters=[
            {"Name": "vpc-id", "Values": [vpc_id]},
            {"Name": "tag:Name", "Values": [name]}
        ]
    )["Subnets"]

    if existing_subnets:
        subnet_id = existing_subnets[0]["SubnetId"]
        print(f"Using existing Subnet: {subnet_id}")
        return subnet_id

    response = ec2_client.create_subnet(
        VpcId=vpc_id,
        CidrBlock=cidr_block
    )

    subnet_id = response["Subnet"]["SubnetId"]

    ec2_client.create_tags(
        Resources=[subnet_id],
        Tags=[{"Key": "Name", "Value": name}]
    )

    return subnet_id


def create_internet_gateway(ec2_client, vpc_id: str, name: str):
    existing_igws = ec2_client.describe_internet_gateways(
        Filters=[{"Name": "tag:Name", "Values": [name]}]
    )["InternetGateways"]

    if existing_igws:
        igw_id = existing_igws[0]["InternetGatewayId"]
        print(f"Using existing Internet Gateway: {igw_id}")
        return igw_id

    response = ec2_client.create_internet_gateway()
    igw_id = response["InternetGateway"]["InternetGatewayId"]

    ec2_client.create_tags(
        Resources=[igw_id],
        Tags=[{"Key": "Name", "Value": name}]
    )

    ec2_client.attach_internet_gateway(
        InternetGatewayId=igw_id,
        VpcId=vpc_id
    )

    return igw_id


def create_route_table(ec2_client, vpc_id: str, name: str):
    existing_route_tables = ec2_client.describe_route_tables(
        Filters=[
            {"Name": "vpc-id", "Values": [vpc_id]},
            {"Name": "tag:Name", "Values": [name]}
        ]
    )["RouteTables"]

    if existing_route_tables:
        route_table_id = existing_route_tables[0]["RouteTableId"]
        print(f"Using existing Route Table: {route_table_id}")
        return route_table_id

    response = ec2_client.create_route_table(VpcId=vpc_id)
    route_table_id = response["RouteTable"]["RouteTableId"]

    ec2_client.create_tags(
        Resources=[route_table_id],
        Tags=[{"Key": "Name", "Value": name}]
    )

    return route_table_id


def create_internet_route(ec2_client, route_table_id: str, igw_id: str):
    route_tables = ec2_client.describe_route_tables(
        RouteTableIds=[route_table_id]
    )["RouteTables"]

    routes = route_tables[0].get("Routes", [])
    for route in routes:
        if route.get("DestinationCidrBlock") == "0.0.0.0/0":
            print("Default internet route already exists.")
            return

    ec2_client.create_route(
        RouteTableId=route_table_id,
        DestinationCidrBlock="0.0.0.0/0",
        GatewayId=igw_id
    )

    print("Created default internet route.")


def associate_route_table_with_subnet(ec2_client, route_table_id: str, subnet_id: str):
    route_tables = ec2_client.describe_route_tables(
        RouteTableIds=[route_table_id]
    )["RouteTables"]

    associations = route_tables[0].get("Associations", [])
    for assoc in associations:
        if assoc.get("SubnetId") == subnet_id:
            print("Route Table is already associated with this subnet.")
            return

    ec2_client.associate_route_table(
        RouteTableId=route_table_id,
        SubnetId=subnet_id
    )

    print("Associated Route Table with Subnet.")


def create_security_group(ec2_client, vpc_id: str, name: str):
    existing_sgs = ec2_client.describe_security_groups(
        Filters=[
            {"Name": "group-name", "Values": [name]},
            {"Name": "vpc-id", "Values": [vpc_id]}
        ]
    )["SecurityGroups"]

    if existing_sgs:
        sg_id = existing_sgs[0]["GroupId"]
        print(f"Using existing Security Group: {sg_id}")
        return sg_id

    response = ec2_client.create_security_group(
        GroupName=name,
        Description="Security group for cloud resource manager",
        VpcId=vpc_id
    )

    sg_id = response["GroupId"]

    ec2_client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
            }
        ]
    )

    ec2_client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 80,
                "ToPort": 80,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
            }
        ]
    )

    return sg_id


def launch_ec2_instance(
    ec2_client,
    subnet_id: str,
    ami_id: str,
    instance_type: str,
    key_name: str,
    name: str,
    security_group_id: str
):
    reservations = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [name]},
            {"Name": "instance-state-name", "Values": ["pending", "running", "stopped"]}
        ]
    )["Reservations"]

    if reservations:
        instance = reservations[0]["Instances"][0]
        instance_id = instance["InstanceId"]
        print(f"Using existing EC2 instance: {instance_id}")
        return instance_id

    user_data_script = """#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd

echo "<h1>Hello Zonique 🚀</h1>" > /var/www/html/index.html
echo "<p>This server was deployed using Python + AWS automation.</p>" >> /var/www/html/index.html
echo "<p>Auto-deployed with User Data 💪</p>" >> /var/www/html/index.html
"""

    response = ec2_client.run_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        KeyName=key_name,
        MinCount=1,
        MaxCount=1,
        NetworkInterfaces=[
            {
                "DeviceIndex": 0,
                "SubnetId": subnet_id,
                "Groups": [security_group_id],
                "AssociatePublicIpAddress": True
            }
        ],
        UserData=user_data_script,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": name}
                ]
            }
        ]
    )

    instance_id = response["Instances"][0]["InstanceId"]
    return instance_id


def get_instance_public_ip(ec2_client, instance_id: str):
    import time
    from botocore.exceptions import ClientError

    for _ in range(10):
        try:
            response = ec2_client.describe_instances(InstanceIds=[instance_id])

            reservations = response["Reservations"]
            if not reservations:
                time.sleep(5)
                continue

            instances = reservations[0]["Instances"]
            if not instances:
                time.sleep(5)
                continue

            public_ip = instances[0].get("PublicIpAddress")
            if public_ip:
                return public_ip

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "InvalidInstanceID.NotFound":
                time.sleep(5)
                continue
            raise

        time.sleep(5)

    return None