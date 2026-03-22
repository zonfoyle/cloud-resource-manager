from utils import (
    load_config,
    get_ec2_client,
    create_vpc,
    create_subnet,
    create_internet_gateway,
    create_route_table,
    create_internet_route,
    associate_route_table_with_subnet,
    create_security_group,
    launch_ec2_instance,
    get_instance_public_ip,
)


def main():
    # Load config
    config = load_config()

    print("Loaded configuration:\n")
    print(config)

    # Get AWS client
    region = config["aws_region"]
    ec2_client = get_ec2_client(region)

    # Create VPC
    vpc_id = create_vpc(
        ec2_client=ec2_client,
        cidr_block=config["vpc"]["cidr_block"],
        name=config["vpc"]["name"]
    )
    print(f"\nVPC created successfully: {vpc_id}")

    # Create Subnet
    subnet_id = create_subnet(
        ec2_client=ec2_client,
        vpc_id=vpc_id,
        cidr_block=config["subnet"]["cidr_block"],
        name=config["subnet"]["name"]
    )
    print(f"Subnet created successfully: {subnet_id}")

    # Create and attach Internet Gateway
    igw_id = create_internet_gateway(
        ec2_client=ec2_client,
        vpc_id=vpc_id,
        name=config["internet_gateway"]["name"]
    )
    print(f"Internet Gateway created and attached successfully: {igw_id}")

    # Create Route Table
    route_table_id = create_route_table(
        ec2_client=ec2_client,
        vpc_id=vpc_id,
        name=config["route_table"]["name"]
    )
    print(f"Route Table created successfully: {route_table_id}")

    # Create default internet route
    create_internet_route(
        ec2_client=ec2_client,
        route_table_id=route_table_id,
        igw_id=igw_id
    )
    print("Internet route created successfully.")

    # Associate route table with subnet
    associate_route_table_with_subnet(
        ec2_client=ec2_client,
        route_table_id=route_table_id,
        subnet_id=subnet_id
    )
    print("Route Table associated with subnet successfully.")

    # Create Security Group
    sg_id = create_security_group(
        ec2_client=ec2_client,
        vpc_id=vpc_id,
        name="cloud-resource-manager-sg"
    )
    print(f"Security Group ready: {sg_id}")

    # Launch EC2 instance
    instance_id = launch_ec2_instance(
        ec2_client=ec2_client,
        subnet_id=subnet_id,
        ami_id=config["ec2"]["ami_id"],
        instance_type=config["ec2"]["instance_type"],
        key_name=config["ec2"]["key_name"],
        name=config["ec2"]["name"],
        security_group_id=sg_id
    )
    print(f"EC2 instance ready: {instance_id}")

    public_ip = get_instance_public_ip(ec2_client, instance_id)
    print(f"EC2 public IP: {public_ip}")


if __name__ == "__main__":
    main()