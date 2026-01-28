"""
S3服务API测试脚本

作者：KO
创建时间：2026-01-27
修改时间：2026-01-27

功能：
- 测试S3服务的/api/s3/buckets端点
- 打印响应状态码、头部和内容
- 尝试将响应解析为JSON并打印
"""
import requests

# 测试API端点URL
url = 'http://127.0.0.1:8000/api/s3/buckets'

try:
    # 发送GET请求到API端点
    response = requests.get(url)
    
    # 打印响应状态码
    print(f"Status Code: {response.status_code}")
    
    # 打印响应头部
    print(f"Response Headers: {response.headers}")
    
    # 打印响应内容
    print(f"Response Content: {response.text}")
    
    # 尝试解析为JSON
    if response.headers.get('content-type') and 'application/json' in response.headers.get('content-type'):
        try:
            json_data = response.json()
            print(f"JSON Data: {json_data}")
            print(f"Type of Data: {type(json_data)}")
        except ValueError:
            print("Failed to parse JSON")
except Exception as e:
    # 打印异常信息
    print(f"Error: {e}")