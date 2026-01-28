"""
S3服务单元测试文件

作者：KO
创建时间：2026-01-28
修改时间：2026-01-28

功能：
- 测试S3Service类的所有方法
- 使用mock模拟boto3客户端，避免实际连接到S3服务
- 测试正常情况和异常情况
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from s3_service import S3Service

class TestS3Service(unittest.TestCase):
    """
    S3Service类的单元测试
    """
    
    def setUp(self):
        """
        测试前的设置
        """
        # 补丁boto3.client，返回一个mock对象
        self.boto3_client_patcher = patch('s3_service.boto3.client')
        self.mock_boto3_client = self.boto3_client_patcher.start()
        
        # 创建mock s3客户端
        self.mock_s3_client = Mock()
        self.mock_boto3_client.return_value = self.mock_s3_client
        
        # 创建S3Service实例
        self.s3_service = S3Service()
    
    def tearDown(self):
        """
        测试后的清理
        """
        # 停止补丁
        self.boto3_client_patcher.stop()
    
    def test_upload_file_success(self):
        """
        测试上传文件成功的情况
        """
        # 创建mock文件对象
        mock_file = Mock()
        mock_file.file = Mock()
        
        # 设置mock s3客户端的upload_fileobj方法
        self.mock_s3_client.upload_fileobj.return_value = None
        
        # 调用upload_file方法
        result = self.s3_service.upload_file(mock_file, "test-key")
        
        # 验证结果
        self.assertEqual(result, "test-key")
        # 验证upload_fileobj方法被调用
        self.mock_s3_client.upload_fileobj.assert_called_once_with(
            mock_file.file, self.s3_service.default_bucket, "test-key"
        )
    
    def test_upload_file_with_custom_bucket(self):
        """
        测试使用自定义存储桶上传文件的情况
        """
        # 创建mock文件对象
        mock_file = Mock()
        mock_file.file = Mock()
        
        # 设置mock s3客户端的upload_fileobj方法
        self.mock_s3_client.upload_fileobj.return_value = None
        
        # 调用upload_file方法，指定自定义存储桶
        custom_bucket = "custom-bucket"
        result = self.s3_service.upload_file(mock_file, "test-key", custom_bucket)
        
        # 验证结果
        self.assertEqual(result, "test-key")
        # 验证upload_fileobj方法被调用，使用了自定义存储桶
        self.mock_s3_client.upload_fileobj.assert_called_once_with(
            mock_file.file, custom_bucket, "test-key"
        )
    
    def test_upload_file_failure(self):
        """
        测试上传文件失败的情况
        """
        # 创建mock文件对象
        mock_file = Mock()
        mock_file.file = Mock()
        
        # 导入ClientError
        from botocore.exceptions import ClientError
        
        # 设置mock s3客户端的upload_fileobj方法，抛出ClientError异常
        error_response = {'Error': {'Code': '500', 'Message': 'Internal Server Error'}}
        self.mock_s3_client.upload_fileobj.side_effect = ClientError(
            error_response, 'UploadFileObj'
        )
        
        # 验证调用upload_file方法会抛出异常
        with self.assertRaises(Exception) as context:
            self.s3_service.upload_file(mock_file, "test-key")
        
        # 验证异常消息包含预期内容
        self.assertIn("Failed to upload file", str(context.exception))
    
    def test_download_file_success(self):
        """
        测试下载文件成功的情况
        """
        # 设置mock响应
        mock_response = {"Body": Mock(), "ContentLength": 100}
        self.mock_s3_client.get_object.return_value = mock_response
        
        # 调用download_file方法
        result = self.s3_service.download_file("test-key")
        
        # 验证结果
        self.assertEqual(result, mock_response)
        # 验证get_object方法被调用
        self.mock_s3_client.get_object.assert_called_once_with(
            Bucket=self.s3_service.default_bucket, Key="test-key"
        )
    
    def test_download_file_with_custom_bucket(self):
        """
        测试使用自定义存储桶下载文件的情况
        """
        # 设置mock响应
        mock_response = {"Body": Mock(), "ContentLength": 100}
        self.mock_s3_client.get_object.return_value = mock_response
        
        # 调用download_file方法，指定自定义存储桶
        custom_bucket = "custom-bucket"
        result = self.s3_service.download_file("test-key", custom_bucket)
        
        # 验证结果
        self.assertEqual(result, mock_response)
        # 验证get_object方法被调用，使用了自定义存储桶
        self.mock_s3_client.get_object.assert_called_once_with(
            Bucket=custom_bucket, Key="test-key"
        )
    
    def test_download_file_failure(self):
        """
        测试下载文件失败的情况
        """
        # 导入ClientError
        from botocore.exceptions import ClientError
        
        # 设置mock s3客户端的get_object方法，抛出ClientError异常
        error_response = {'Error': {'Code': '500', 'Message': 'Internal Server Error'}}
        self.mock_s3_client.get_object.side_effect = ClientError(
            error_response, 'GetObject'
        )
        
        # 验证调用download_file方法会抛出异常
        with self.assertRaises(Exception) as context:
            self.s3_service.download_file("test-key")
        
        # 验证异常消息包含预期内容
        self.assertIn("Failed to download file", str(context.exception))
    
    def test_delete_file_success(self):
        """
        测试删除文件成功的情况
        """
        # 设置mock s3客户端的delete_object方法
        self.mock_s3_client.delete_object.return_value = None
        
        # 调用delete_file方法
        self.s3_service.delete_file("test-key")
        
        # 验证delete_object方法被调用
        self.mock_s3_client.delete_object.assert_called_once_with(
            Bucket=self.s3_service.default_bucket, Key="test-key"
        )
    
    def test_delete_file_with_custom_bucket(self):
        """
        测试使用自定义存储桶删除文件的情况
        """
        # 设置mock s3客户端的delete_object方法
        self.mock_s3_client.delete_object.return_value = None
        
        # 调用delete_file方法，指定自定义存储桶
        custom_bucket = "custom-bucket"
        self.s3_service.delete_file("test-key", custom_bucket)
        
        # 验证delete_object方法被调用，使用了自定义存储桶
        self.mock_s3_client.delete_object.assert_called_once_with(
            Bucket=custom_bucket, Key="test-key"
        )
    
    def test_delete_file_failure(self):
        """
        测试删除文件失败的情况
        """
        # 导入ClientError
        from botocore.exceptions import ClientError
        
        # 设置mock s3客户端的delete_object方法，抛出ClientError异常
        error_response = {'Error': {'Code': '500', 'Message': 'Internal Server Error'}}
        self.mock_s3_client.delete_object.side_effect = ClientError(
            error_response, 'DeleteObject'
        )
        
        # 验证调用delete_file方法会抛出异常
        with self.assertRaises(Exception) as context:
            self.s3_service.delete_file("test-key")
        
        # 验证异常消息包含预期内容
        self.assertIn("Failed to delete file", str(context.exception))
    
    def test_file_exists_true(self):
        """
        测试文件存在的情况
        """
        # 设置mock s3客户端的head_object方法
        self.mock_s3_client.head_object.return_value = None
        
        # 调用file_exists方法
        result = self.s3_service.file_exists("test-key")
        
        # 验证结果
        self.assertTrue(result)
        # 验证head_object方法被调用
        self.mock_s3_client.head_object.assert_called_once_with(
            Bucket=self.s3_service.default_bucket, Key="test-key"
        )
    
    def test_file_exists_false(self):
        """
        测试文件不存在的情况
        """
        # 导入ClientError
        from botocore.exceptions import ClientError
        
        # 设置mock s3客户端的head_object方法，抛出404错误
        error_response = {'Error': {'Code': '404', 'Message': 'Not Found'}}
        self.mock_s3_client.head_object.side_effect = ClientError(
            error_response, 'HeadObject'
        )
        
        # 调用file_exists方法
        result = self.s3_service.file_exists("test-key")
        
        # 验证结果
        self.assertFalse(result)
    
    def test_file_exists_error(self):
        """
        测试检查文件存在时发生错误的情况
        """
        # 导入ClientError
        from botocore.exceptions import ClientError
        
        # 设置mock s3客户端的head_object方法，抛出非404错误
        error_response = {'Error': {'Code': '500', 'Message': 'Internal Server Error'}}
        self.mock_s3_client.head_object.side_effect = ClientError(
            error_response, 'HeadObject'
        )
        
        # 验证调用file_exists方法会抛出异常
        with self.assertRaises(Exception) as context:
            self.s3_service.file_exists("test-key")
        
        # 验证异常消息包含预期内容
        self.assertIn("Failed to check file existence", str(context.exception))
    
    def test_list_files_empty(self):
        """
        测试列出空存储桶中的文件
        """
        # 设置mock s3客户端的list_objects_v2方法，返回空内容
        self.mock_s3_client.list_objects_v2.return_value = {}
        
        # 调用list_files方法
        result = self.s3_service.list_files()
        
        # 验证结果
        self.assertEqual(result, [])
        # 验证list_objects_v2方法被调用
        self.mock_s3_client.list_objects_v2.assert_called_once_with(
            Bucket=self.s3_service.default_bucket
        )
    
    def test_list_files_with_contents(self):
        """
        测试列出非空存储桶中的文件
        """
        # 设置mock s3客户端的list_objects_v2方法，返回包含文件的响应
        mock_response = {
            'Contents': [
                {'Key': 'file1.txt', 'Size': 100, 'LastModified': Mock()},
                {'Key': 'file2.txt', 'Size': 200, 'LastModified': Mock()}
            ]
        }
        self.mock_s3_client.list_objects_v2.return_value = mock_response
        
        # 调用list_files方法
        result = self.s3_service.list_files()
        
        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['key'], 'file1.txt')
        self.assertEqual(result[0]['size'], 100)
        self.assertEqual(result[1]['key'], 'file2.txt')
        self.assertEqual(result[1]['size'], 200)
    
    def test_list_files_failure(self):
        """
        测试列出文件失败的情况
        """
        # 导入ClientError
        from botocore.exceptions import ClientError
        
        # 设置mock s3客户端的list_objects_v2方法，抛出ClientError异常
        error_response = {'Error': {'Code': '500', 'Message': 'Internal Server Error'}}
        self.mock_s3_client.list_objects_v2.side_effect = ClientError(
            error_response, 'ListObjectsV2'
        )
        
        # 验证调用list_files方法会抛出异常
        with self.assertRaises(Exception) as context:
            self.s3_service.list_files()
        
        # 验证异常消息包含预期内容
        self.assertIn("Failed to list files", str(context.exception))
    
    def test_list_buckets(self):
        """
        测试列出所有存储桶
        """
        # 设置mock s3客户端的list_buckets方法，返回包含存储桶的响应
        mock_response = {
            'Buckets': [
                {'Name': 'bucket1', 'CreationDate': Mock()},
                {'Name': 'bucket2', 'CreationDate': Mock()}
            ]
        }
        self.mock_s3_client.list_buckets.return_value = mock_response
        
        # 调用list_buckets方法
        result = self.s3_service.list_buckets()
        
        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'bucket1')
        self.assertEqual(result[1]['name'], 'bucket2')
    
    def test_list_buckets_failure(self):
        """
        测试列出存储桶失败的情况
        """
        # 导入ClientError
        from botocore.exceptions import ClientError
        
        # 设置mock s3客户端的list_buckets方法，抛出ClientError异常
        error_response = {'Error': {'Code': '500', 'Message': 'Internal Server Error'}}
        self.mock_s3_client.list_buckets.side_effect = ClientError(
            error_response, 'ListBuckets'
        )
        
        # 验证调用list_buckets方法会抛出异常
        with self.assertRaises(Exception) as context:
            self.s3_service.list_buckets()
        
        # 验证异常消息包含预期内容
        self.assertIn("Failed to list buckets", str(context.exception))
    
    def test_create_bucket_success(self):
        """
        测试创建存储桶成功的情况
        """
        # 补丁_bucket_exists方法，返回False
        with patch.object(self.s3_service, '_bucket_exists', return_value=False):
            # 设置mock s3客户端的create_bucket方法
            self.mock_s3_client.create_bucket.return_value = None
            
            # 调用create_bucket方法
            result = self.s3_service.create_bucket("new-bucket")
            
            # 验证结果
            self.assertTrue(result)
            # 验证create_bucket方法被调用
            self.mock_s3_client.create_bucket.assert_called_once()
    
    def test_create_bucket_already_exists(self):
        """
        测试创建已存在的存储桶
        """
        # 补丁_bucket_exists方法，返回True
        with patch.object(self.s3_service, '_bucket_exists', return_value=True):
            # 调用create_bucket方法
            result = self.s3_service.create_bucket("existing-bucket")
            
            # 验证结果
            self.assertFalse(result)
            # 验证create_bucket方法没有被调用
            self.mock_s3_client.create_bucket.assert_not_called()
    
    def test_create_bucket_failure(self):
        """
        测试创建存储桶失败的情况
        """
        # 补丁_bucket_exists方法，返回False
        with patch.object(self.s3_service, '_bucket_exists', return_value=False):
            # 导入ClientError
            from botocore.exceptions import ClientError
            
            # 设置mock s3客户端的create_bucket方法，抛出ClientError异常
            error_response = {'Error': {'Code': '500', 'Message': 'Internal Server Error'}}
            self.mock_s3_client.create_bucket.side_effect = ClientError(
                error_response, 'CreateBucket'
            )
            
            # 验证调用create_bucket方法会抛出异常
            with self.assertRaises(Exception) as context:
                self.s3_service.create_bucket("new-bucket")
            
            # 验证异常消息包含预期内容
            self.assertIn("Failed to create bucket", str(context.exception))
    
    def test_bucket_exists_true(self):
        """
        测试存储桶存在的情况
        """
        # 设置mock s3客户端的head_bucket方法
        self.mock_s3_client.head_bucket.return_value = None
        
        # 通过访问私有方法来测试
        result = self.s3_service._bucket_exists("existing-bucket")
        
        # 验证结果
        self.assertTrue(result)
        # 验证head_bucket方法被调用
        self.mock_s3_client.head_bucket.assert_called_once_with(
            Bucket="existing-bucket"
        )
    
    def test_bucket_exists_false(self):
        """
        测试存储桶不存在的情况
        """
        # 导入ClientError
        from botocore.exceptions import ClientError
        
        # 设置mock s3客户端的head_bucket方法，抛出404错误
        error_response = {'Error': {'Code': '404', 'Message': 'Not Found'}}
        self.mock_s3_client.head_bucket.side_effect = ClientError(
            error_response, 'HeadBucket'
        )
        
        # 通过访问私有方法来测试
        result = self.s3_service._bucket_exists("non-existent-bucket")
        
        # 验证结果
        self.assertFalse(result)
    
    def test_bucket_exists_error(self):
        """
        测试检查存储桶存在时发生错误的情况
        """
        # 导入ClientError
        from botocore.exceptions import ClientError
        
        # 设置mock s3客户端的head_bucket方法，抛出非404错误
        error_response = {'Error': {'Code': '500', 'Message': 'Internal Server Error'}}
        self.mock_s3_client.head_bucket.side_effect = ClientError(
            error_response, 'HeadBucket'
        )
        
        # 验证调用_bucket_exists方法会抛出异常
        with self.assertRaises(Exception) as context:
            self.s3_service._bucket_exists("test-bucket")
        
        # 验证异常消息包含预期内容
        self.assertIn("Failed to check bucket existence", str(context.exception))

if __name__ == '__main__':
    unittest.main()