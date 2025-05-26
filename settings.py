import os

# AWS Valkey Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")  # Replace with your AWS Access Key ID
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")  # Replace with your AWS Secret Access Key
AWS_REGION = os.getenv("AWS_REGION")  # Replace with your AWS region (e.g., 'us-east-1')

# Optional: S3 Bucket Configuration (if using S3)
AWS_STORAGE_BUCKET_NAME = "your_s3_bucket_name"  # Replace with your S3 bucket name
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False

# Static and Media Files (if using S3 for storage)
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"


DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"