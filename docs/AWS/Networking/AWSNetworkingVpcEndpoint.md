---
tags:
  - VPC
---

# VPC Endpoint Services

## Types of VPC Endpoints
- **Gateway**
- **Interface**
- **Gateway Load Balancer**

## VPC Endpoint Details

### Interface Endpoints
An **interface endpoint** is an elastic network interface with a private IP address from the IP address range of your subnet. It acts as an entry point for traffic destined to a service owned by AWS or by an AWS customer/partner.

For [[../AWS|AWS]] services that integrate with AWS PrivateLink, see [AWS services that integrate with AWS PrivateLink](https://docs.aws.amazon.com/vpc/latest/privatelink/integrated-services-vpce.html).

### Gateway Endpoints
**Gateway Endpoints** are primarily used for S3 or DynamoDB. They are usually set up by making an entry in route tables.

### Gateway Load Balancer Endpoints
A **Gateway Load Balancer endpoint** is an elastic network interface with a private IP address from the IP address range of your subnet. It is used as an entry point to intercept traffic and route it to a network or security service configured using a Gateway Load Balancer.

Gateway Load Balancers enable the deployment, scaling, and management of virtual appliances like firewalls, intrusion detection, and prevention systems. They operate at the third layer of the OSI model (the network layer), listening for all IP packets across all ports and forwarding traffic to the target group specified in the listener rule.

Gateway Load Balancer endpoints are supported only for endpoint services configured using a Gateway Load Balancer.

## Example Scenario: Redis Access Across AWS Accounts

To access Redis from one AWS account to another:

1. **Create a VPC Endpoint:**
   - Type: Network Load Balancer.
   - Load Balancer: Select the one with endpoint IPs of Redis in the target group.
   - Enable "Acceptance Required" and private DNS if needed.

2. **Allow Principal:**
   - Add the account ARN under "Allow Principal."

3. **Endpoint Configuration in Another Account:**
   - Go to the other account.
   - Navigate to "Endpoints."
   - Find "Service by Name."
   - Enter the Endpoint Service ARN.
   - Select VPC, Subnet, and Security Group.
   - Save the configuration.

4. **Connection Acceptance:**
   - Go back to the first account.
   - Under "Endpoint Connections" of the VPC Endpoint Service, accept the connection.

## S3 Endpoint Options

### Gateway Endpoints for Amazon S3
- Traffic remains on the AWS network.
- **Use Case:**
  - Uses Amazon S3 public IP addresses.
  - Does not allow access from on-premises.
  - Does not allow access from another AWS Region.
  - Not billed.

### Interface Endpoints for Amazon S3
- Traffic uses private IP addresses from your VPC to access Amazon S3.
- **Use Case:**
  - Allows access from on-premises.
  - Allows access from a VPC in another AWS Region using VPC peering or AWS Transit Gateway.
  - Billed.

## Lambda Function with VPC Endpoints

Even if you are triggering Lambda from anywhere inside your VPC, you need a VPC endpoint of the interface type.


{% if pdf == "true" %}
??? note "Checkout the PDF"

      ![PDF](pdf/Comparison_of_Web_Development_Stacks.pdf){ type=application/pdf style="min-height:100vh;width:100%" }
{% endif %}

