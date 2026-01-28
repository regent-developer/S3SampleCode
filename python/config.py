"""
S3配置文件，用于存储S3服务的配置参数

作者：KO
创建时间：2024-01-01
修改时间：2026-01-27

功能：
- 从环境变量加载S3配置参数
- 提供默认配置值
- 定义S3客户端配置
"""
import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# S3配置参数
S3_CONFIG = {
    "endpoint_url": os.getenv("S3_ENDPOINT", "http://localhost:9000/"),  # S3服务端点URL
    "bucket": os.getenv("S3_BUCKET", "test-bucket"),  # 默认存储桶名称
    "region_name": os.getenv("S3_REGION", "us-east-1"),  # S3服务区域
    "aws_access_key_id": os.getenv("S3_ACCESS_KEY", "minioadmin"),  # S3访问密钥
    "aws_secret_access_key": os.getenv("S3_SECRET_KEY", "minioadmin"),  # S3密钥
    "config": {
        "s3": {
            "use_accelerate_endpoint": False,  # 是否使用加速端点
            "addressing_style": "path"  # 寻址样式，使用path模式
        }
    }
}