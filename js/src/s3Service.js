/**
 * S3服务模块
 * 作者: KO
 * 创建时间: 2026-01-27
 * 修改时间: 2026-01-27
 * 描述: 提供S3相关的操作函数，包括文件上传、下载、删除、检查存在性、列出文件和存储桶等
 */
const { PutObjectCommand, GetObjectCommand, DeleteObjectCommand, HeadObjectCommand, CreateBucketCommand, ListObjectsV2Command, ListBucketsCommand } = require('@aws-sdk/client-s3');
const { createReadStream, createWriteStream } = require('fs');
const s3Client = require('./s3Client');

/**
 * 文件上传到S3
 * @param {string} bucket - 存储桶名称
 * @param {string} key - 文件在S3中的键
 * @param {string} filePath - 本地文件路径
 * @param {object} metadata - 自定义元数据
 * @returns {Promise} - 上传结果
 */
const uploadFile = async (bucket, key, filePath, metadata = {}) => {
  const fileStream = createReadStream(filePath);
  
  const command = new PutObjectCommand({
    Bucket: bucket,
    Key: key,
    Body: fileStream,
    Metadata: metadata,
  });
  
  return s3Client.send(command);
};

/**
 * 从S3下载文件
 * @param {string} bucket - 存储桶名称
 * @param {string} key - 文件在S3中的键
 * @param {string} downloadPath - 本地下载路径
 * @returns {Promise} - 下载结果
 */
const downloadFile = async (bucket, key, downloadPath) => {
  const command = new GetObjectCommand({
    Bucket: bucket,
    Key: key,
  });
  
  const response = await s3Client.send(command);
  const writeStream = createWriteStream(downloadPath);
  
  return new Promise((resolve, reject) => {
    response.Body.pipe(writeStream);
    writeStream.on('finish', resolve);
    writeStream.on('error', reject);
  });
};

/**
 * 从S3删除文件
 * @param {string} bucket - 存储桶名称
 * @param {string} key - 文件在S3中的键
 * @returns {Promise} - 删除结果
 */
const deleteFile = async (bucket, key) => {
  const command = new DeleteObjectCommand({
    Bucket: bucket,
    Key: key,
  });
  
  return s3Client.send(command);
};

/**
 * 检查S3中文件是否存在
 * @param {string} bucket - 存储桶名称
 * @param {string} key - 文件在S3中的键
 * @returns {Promise<boolean>} - 文件是否存在
 */
const fileExists = async (bucket, key) => {
  try {
    const command = new HeadObjectCommand({
      Bucket: bucket,
      Key: key,
    });
    
    await s3Client.send(command);
    return true;
  } catch (error) {
    if (error.name === 'NotFound') {
      return false;
    }
    throw error;
  }
};

/**
 * 创建S3存储桶
 * @param {string} bucket - 存储桶名称
 * @returns {Promise} - 创建结果
 */
const createBucket = async (bucket) => {
  const command = new CreateBucketCommand({
    Bucket: bucket,
  });
  
  return s3Client.send(command);
};

/**
 * 获取S3文件元数据
 * @param {string} bucket - 存储桶名称
 * @param {string} key - 文件在S3中的键
 * @returns {Promise<object|null>} - 文件元数据，如果文件不存在则返回null
 */
const getFileMetadata = async (bucket, key) => {
  try {
    const command = new HeadObjectCommand({
      Bucket: bucket,
      Key: key,
    });
    
    const response = await s3Client.send(command);
    return response;
  } catch (error) {
    if (error.name === 'NotFound') {
      return null;
    }
    throw error;
  }
};

/**
 * 列出S3存储桶中的所有文件
 * @param {string} bucket - 存储桶名称
 * @returns {Promise<Array>} - 文件列表
 */
const listFiles = async (bucket) => {
  const command = new ListObjectsV2Command({
    Bucket: bucket,
  });
  
  const response = await s3Client.send(command);
  return response.Contents || [];
};

/**
 * 列出所有S3存储桶
 * @returns {Promise<Array>} - 存储桶列表
 */
const listBuckets = async () => {
  const command = new ListBucketsCommand({});
  
  const response = await s3Client.send(command);
  return response.Buckets || [];
};

/**
 * 检查S3存储桶是否存在
 * @param {string} bucket - 存储桶名称
 * @returns {Promise<boolean>} - 存储桶是否存在
 */
const doesBucketExist = async (bucket) => {
  try {
    // 使用HeadBucketCommand检查存储桶是否存在
    // 注意：HeadBucketCommand在@aws-sdk/client-s3中可用，需要添加到导入
    const { HeadBucketCommand } = require('@aws-sdk/client-s3');
    const command = new HeadBucketCommand({
      Bucket: bucket,
    });
    
    await s3Client.send(command);
    return true;
  } catch (error) {
    if (error.name === 'NotFound' || error.name === 'NoSuchBucket') {
      return false;
    }
    throw error;
  }
};

module.exports = {
  uploadFile,
  downloadFile,
  deleteFile,
  fileExists,
  createBucket,
  getFileMetadata,
  listFiles,
  listBuckets,
  doesBucketExist,
};