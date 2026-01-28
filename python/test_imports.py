"""
测试基本导入是否正常
"""
print("Testing imports...")
try:
    import unittest
    print("✓ unittest imported successfully")
except Exception as e:
    print(f"✗ unittest import failed: {e}")

try:
    from unittest.mock import Mock, patch
    print("✓ unittest.mock imported successfully")
except Exception as e:
    print(f"✗ unittest.mock import failed: {e}")

try:
    import boto3
    print("✓ boto3 imported successfully")
except Exception as e:
    print(f"✗ boto3 import failed: {e}")

try:
    from botocore.exceptions import ClientError
    print("✓ ClientError imported successfully")
except Exception as e:
    print(f"✗ ClientError import failed: {e}")

try:
    from config import S3_CONFIG
    print("✓ config imported successfully")
except Exception as e:
    print(f"✗ config import failed: {e}")

try:
    from s3_service import S3Service
    print("✓ S3Service imported successfully")
except Exception as e:
    print(f"✗ S3Service import failed: {e}")

print("Import test completed.")