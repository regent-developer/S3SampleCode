"""
S3服务类，提供S3存储操作的核心功能

作者：KO
创建时间：2024-01-01
修改时间：2026-01-27

功能：
- 文件上传到S3存储桶
- 从S3存储桶下载文件
- 从S3存储桶删除文件
- 检查文件是否存在于S3存储桶
- 列出S3存储桶中的所有文件
- 列出所有S3存储桶
- 创建新的S3存储桶
- 检查存储桶是否存在
"""
import boto3
from botocore.exceptions import ClientError
from config import S3_CONFIG

class S3Service:
    """
    S3服务类，用于处理与S3存储相关的所有操作
    
    属性：
    - s3_client: boto3 S3客户端实例
    - default_bucket: 默认存储桶名称
    """
    def __init__(self):
        """
        初始化S3服务实例
        
        从配置中获取S3连接参数，创建S3客户端实例
        """
        # 创建S3客户端
        self.s3_client = boto3.client(
            's3',
            endpoint_url=S3_CONFIG["endpoint_url"],
            region_name=S3_CONFIG["region_name"],
            aws_access_key_id=S3_CONFIG["aws_access_key_id"],
            aws_secret_access_key=S3_CONFIG["aws_secret_access_key"],
            config=boto3.session.Config(**S3_CONFIG["config"])
        )
        self.default_bucket = S3_CONFIG["bucket"]
    
    def upload_file(self, file, key, bucket=None):
        """
        上传文件到S3存储桶
        
        参数：
        - file: UploadFile对象，包含要上传的文件
        - key: str，S3对象键
        - bucket: str，可选，存储桶名称，默认为默认存储桶
        
        返回值：
        - str: 上传成功的对象键
        
        异常：
        - Exception: 上传失败时抛出
        """
        bucket_name = bucket or self.default_bucket
        try:
            self.s3_client.upload_fileobj(file.file, bucket_name, key)
            return key
        except ClientError as e:
            raise Exception(f"Failed to upload file: {e}")
    
    def download_file(self, key, bucket=None):
        """
        从S3存储桶下载文件
        
        参数：
        - key: str，S3对象键
        - bucket: str，可选，存储桶名称，默认为默认存储桶
        
        返回值：
        - dict: 包含文件内容的响应对象
        
        异常：
        - Exception: 下载失败时抛出
        """
        bucket_name = bucket or self.default_bucket
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=key)
            return response
        except ClientError as e:
            raise Exception(f"Failed to download file: {e}")
    
    def delete_file(self, key, bucket=None):
        """
        从S3存储桶删除文件
        
        参数：
        - key: str，S3对象键
        - bucket: str，可选，存储桶名称，默认为默认存储桶
        
        异常：
        - Exception: 删除失败时抛出
        """
        bucket_name = bucket or self.default_bucket
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=key)
        except ClientError as e:
            raise Exception(f"Failed to delete file: {e}")
    
    def file_exists(self, key, bucket=None):
        """
        检查文件是否存在于S3存储桶
        
        参数：
        - key: str，S3对象键
        - bucket: str，可选，存储桶名称，默认为默认存储桶
        
        返回值：
        - bool: 文件是否存在
        
        异常：
        - Exception: 检查失败时抛出
        """
        bucket_name = bucket or self.default_bucket
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise Exception(f"Failed to check file existence: {e}")
    
    def list_files(self, bucket=None):
        """
        列出S3存储桶中的所有文件
        
        参数：
        - bucket: str，可选，存储桶名称，默认为默认存储桶
        
        返回值：
        - list: 文件列表，每个文件包含key、size和lastModified属性
        
        异常：
        - Exception: 列出失败时抛出
        """
        bucket_name = bucket or self.default_bucket
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket_name)
            files = []
            if 'Contents' in response:
                for file in response['Contents']:
                    files.append({
                        'key': file['Key'],
                        'size': file['Size'],
                        'lastModified': file['LastModified']
                    })
            return files
        except ClientError as e:
            raise Exception(f"Failed to list files: {e}")
    
    def list_buckets(self):
        """
        列出所有S3存储桶
        
        返回值：
        - list: 存储桶列表，每个存储桶包含name和creationDate属性
        
        异常：
        - Exception: 列出失败时抛出
        """
        try:
            response = self.s3_client.list_buckets()
            buckets = []
            for bucket in response['Buckets']:
                buckets.append({
                    'name': bucket['Name'],
                    'creationDate': bucket['CreationDate']
                })
            return buckets
        except ClientError as e:
            raise Exception(f"Failed to list buckets: {e}")
    
    def create_bucket(self, bucket_name):
        """
        创建新的S3存储桶
        
        参数：
        - bucket_name: str，要创建的存储桶名称
        
        返回值：
        - bool: 是否创建成功
        
        异常：
        - Exception: 创建失败时抛出
        """
        try:
            # 检查存储桶是否已存在
            if self._bucket_exists(bucket_name):
                return False
            
            # 创建存储桶
            self.s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': S3_CONFIG["region_name"]}
            )
            return True
        except ClientError as e:
            raise Exception(f"Failed to create bucket: {e}")
    
    def _bucket_exists(self, bucket_name):
        """
        检查存储桶是否存在
        
        参数：
        - bucket_name: str，要检查的存储桶名称
        
        返回值：
        - bool: 存储桶是否存在
        
        异常：
        - Exception: 检查失败时抛出
        """
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise Exception(f"Failed to check bucket existence: {e}")