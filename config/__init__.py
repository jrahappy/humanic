import boto3

# Initialize AWS SDK
boto3.setup_default_session(
    aws_access_key_id="your_aws_access_key_id",  # Replace with your AWS Access Key ID
    aws_secret_access_key="your_aws_secret_access_key",  # Replace with your AWS Secret Access Key
    region_name="your_aws_region",  # Replace with your AWS region
)
