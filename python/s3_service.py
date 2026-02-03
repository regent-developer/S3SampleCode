"""
S3服务类，提供S3存储操作的核心功能

作者：KO
创建时间：2024-01-01
修改时间：2026-01-30

功能：
- 文件上传到S3存储桶
- 从S3存储桶下载文件
- 从S3存储桶删除文件
- 检查文件是否存在于S3存储桶
- 列出S3存储桶中的所有文件
- 列出所有S3存储桶
- 创建新的S3存储桶
- 检查存储桶是否存在
- 监听S3存储桶变化事件
"""
import boto3
from botocore.exceptions import ClientError
from config import S3_CONFIG
import time
import threading
from enum import Enum
from typing import Dict, List, Optional, Callable, Any

# 事件类型枚举
class EventType(Enum):
    OBJECT_CREATED = "ObjectCreated"
    OBJECT_DELETED = "ObjectDeleted"
    OBJECT_MODIFIED = "ObjectModified"

# S3事件类
class S3Event:
    def __init__(self, event_type: EventType, bucket: str, key: str, size: int, last_modified: Any, e_tag: str):
        self.event_type = event_type
        self.bucket = bucket
        self.key = key
        self.size = size
        self.last_modified = last_modified
        self.e_tag = e_tag

    def __str__(self):
        return f"S3Event(type={self.event_type.value}, bucket={self.bucket}, key={self.key}, size={self.size}, last_modified={self.last_modified})"

# 存储桶监听器配置类
class BucketListenerConfig:
    def __init__(self):
        self.bucket: Optional[str] = None
        self.poll_interval: int = 5  # 默认5秒
        self.error_handler: Optional[Callable[[Exception], None]] = None
        self.event_handler: Optional[Callable[[S3Event], None]] = None
        self.max_retries: int = 3  # 默认3次
        self.retry_interval: int = 2  # 默认2秒

# 存储桶监听器类
class BucketListener:
    def __init__(self, service, config: BucketListenerConfig):
        self.service = service
        self.config = config
        self.running = False
        self.thread = None
        self.last_objects: Dict[str, Dict[str, Any]] = {}

    def start(self):
        if self.running:
            return

        self.running = True
        bucket = self.config.bucket or self.service.default_bucket

        # 初始化对象列表
        try:
            objects = self.service._list_objects(bucket)
            for obj in objects:
                self.last_objects[obj['Key']] = obj
        except Exception as e:
            if self.config.error_handler:
                self.config.error_handler(e)
            else:
                print(f"Failed to initialize object list: {e}")
            self.stop()
            return

        # 启动监听线程
        self.thread = threading.Thread(target=self._run, args=(bucket,))
        self.thread.daemon = True
        self.thread.start()
        print("S3 Bucket listener started successfully")

    def stop(self):
        if not self.running:
            return

        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("S3 Bucket listener stopped")

    def _run(self, bucket: str):
        while self.running:
            try:
                self._check_for_changes(bucket)
            except Exception as e:
                retries = 0
                while retries < self.config.max_retries and self.running:
                    try:
                        time.sleep(self.config.retry_interval)
                        self._check_for_changes(bucket)
                        break
                    except Exception as ex:
                        retries += 1
                        if retries >= self.config.max_retries:
                            if self.config.error_handler:
                                self.config.error_handler(ex)
                            else:
                                print(f"S3 listener error: {ex}")
            
            # 等待下一次轮询
            for _ in range(self.config.poll_interval):
                if not self.running:
                    break
                time.sleep(1)

    def _check_for_changes(self, bucket: str):
        current_objects = self.service._list_objects(bucket)
        current_map = {obj['Key']: obj for obj in current_objects}

        # 检查删除的对象
        for key, old_obj in list(self.last_objects.items()):
            if key not in current_map:
                # 对象被删除
                event = S3Event(
                    event_type=EventType.OBJECT_DELETED,
                    bucket=bucket,
                    key=key,
                    size=old_obj['Size'],
                    last_modified=old_obj['LastModified'],
                    e_tag=old_obj['ETag']
                )
                if self.config.event_handler:
                    self.config.event_handler(event)

        # 检查创建和修改的对象
        for key, current_obj in current_map.items():
            if key not in self.last_objects:
                # 对象被创建
                event = S3Event(
                    event_type=EventType.OBJECT_CREATED,
                    bucket=bucket,
                    key=key,
                    size=current_obj['Size'],
                    last_modified=current_obj['LastModified'],
                    e_tag=current_obj['ETag']
                )
                if self.config.event_handler:
                    self.config.event_handler(event)
            else:
                # 检查对象是否被修改
                old_obj = self.last_objects[key]
                if current_obj['ETag'] != old_obj['ETag'] or current_obj['LastModified'] > old_obj['LastModified']:
                    # 对象被修改
                    event = S3Event(
                        event_type=EventType.OBJECT_MODIFIED,
                        bucket=bucket,
                        key=key,
                        size=current_obj['Size'],
                        last_modified=current_obj['LastModified'],
                        e_tag=current_obj['ETag']
                    )
                    if self.config.event_handler:
                        self.config.event_handler(event)

        # 更新对象列表
        self.last_objects = current_map

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
        self.listeners = []
        self.event_history = []
        self.MAX_EVENT_HISTORY = 100
    
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

    def _list_objects(self, bucket):
        """
        列出存储桶中的所有对象
        
        参数：
        - bucket: str，存储桶名称
        
        返回值：
        - List[Dict[str, Any]]: 对象列表
        
        异常：
        - Exception: 列出失败时抛出
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket)
            return response.get('Contents', [])
        except ClientError as e:
            raise Exception(f"Failed to list objects: {e}")

    def start_bucket_listener(self, config: BucketListenerConfig):
        """
        启动存储桶监听器
        
        参数：
        - config: BucketListenerConfig，监听器配置
        
        返回值：
        - BucketListener: 监听器实例
        
        异常：
        - Exception: 监听器启动失败时抛出
        """
        # 验证配置
        if not config.event_handler:
            raise ValueError("Event handler is required")

        # 设置默认值
        bucket = config.bucket or self.default_bucket
        if not bucket:
            raise ValueError("Bucket is required")

        # 创建并启动监听器
        listener = BucketListener(self, config)
        listener.start()

        # 添加到监听器列表
        self.listeners.append(listener)

        return listener

    def stop_all_listeners(self):
        """
        停止所有存储桶监听器
        """
        for listener in self.listeners:
            listener.stop()
        self.listeners.clear()
    
    def record_event(self, event):
        """
        记录事件到历史记录
        
        参数：
        - event: S3Event对象，要记录的事件
        """
        # 添加事件到历史记录的开头
        self.event_history.insert(0, event)
        # 限制历史记录的长度
        if len(self.event_history) > self.MAX_EVENT_HISTORY:
            self.event_history.pop()
    
    def get_event_history(self):
        """
        获取事件历史记录
        
        返回值：
        - list: 事件历史记录列表，每个事件包含event_type、bucket、key、size、last_modified和e_tag属性
        """
        # 转换为前端可以处理的格式
        events = []
        for event in self.event_history:
            events.append({
                "eventType": event.event_type.value,
                "bucket": event.bucket,
                "key": event.key,
                "size": event.size,
                "lastModified": event.last_modified,
                "eTag": event.e_tag
            })
        return events
    
    def clear_event_history(self):
        """
        清空事件历史记录
        """
        self.event_history.clear()
    
    def start_bucket_listener_for_bucket(self, bucket):
        """
        启动针对特定存储桶的监听器
        
        参数：
        - bucket: str，存储桶名称
        
        返回值：
        - BucketListener: 监听器实例
        
        异常：
        - Exception: 监听器启动失败时抛出
        """
        from s3_service import BucketListenerConfig, EventType
        
        # 停止所有现有监听器
        self.stop_all_listeners()
        
        # 配置监听器
        config = BucketListenerConfig()
        config.bucket = bucket
        config.poll_interval = 5  # 5秒轮询一次
        config.event_handler = lambda event: (
            print(f"S3 Event: {event.event_type.value} - Bucket: {event.bucket}, Key: {event.key}, Size: {event.size}, LastModified: {event.last_modified}"),
            self.record_event(event)
        )
        config.error_handler = lambda error: (
            print(f"S3 Listener Error: {error}")
        )

        # 启动监听器
        listener = self.start_bucket_listener(config)
        print(f"S3 Bucket listener started successfully for bucket: {bucket}")
        
        return listener
