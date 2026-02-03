/**
 * S3服务模块
 * 作者: KO
 * 创建时间: 2026-01-27
 * 修改时间: 2026-01-30
 * 描述: 提供S3相关的操作函数，包括文件上传、下载、删除、检查存在性、列出文件和存储桶等
 */
const { PutObjectCommand, GetObjectCommand, DeleteObjectCommand, HeadObjectCommand, CreateBucketCommand, ListObjectsV2Command, ListBucketsCommand } = require('@aws-sdk/client-s3');
const { createReadStream, createWriteStream } = require('fs');
const s3Client = require('./s3Client');

// 事件类型常量
const EventType = {
  OBJECT_CREATED: 'ObjectCreated',
  OBJECT_DELETED: 'ObjectDeleted',
  OBJECT_MODIFIED: 'ObjectModified'
};

// BucketListener 存储桶监听器类
class BucketListener {
  constructor(service, config) {
    this.service = service;
    this.config = config;
    this.running = false;
    this.intervalId = null;
    this.lastObjects = new Map();
  }

  // 启动监听器
  start() {
    if (this.running) {
      return;
    }

    this.running = true;
    const bucket = this.config.bucket || this.service.defaultBucket;

    // 初始化对象列表
    this.service.listObjects(bucket)
      .then(objects => {
        objects.forEach(obj => {
          this.lastObjects.set(obj.Key, obj);
        });

        // 开始轮询
        this.intervalId = setInterval(() => {
          this.checkForChanges(bucket).catch(err => {
            if (this.config.errorHandler) {
              this.config.errorHandler(err);
            } else {
              console.error('S3 listener error:', err);
            }
          });
        }, this.config.pollInterval);

        console.log('S3 Bucket listener started successfully');
      })
      .catch(err => {
        if (this.config.errorHandler) {
          this.config.errorHandler(err);
        } else {
          console.error('Failed to initialize object list:', err);
        }
        this.stop();
      });
  }

  // 停止监听器
  stop() {
    if (!this.running) {
      return;
    }

    this.running = false;
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    console.log('S3 Bucket listener stopped');
  }

  // 检查存储桶变化
  async checkForChanges(bucket) {
    let retries = 0;
    let currentObjects;

    // 重试逻辑
    while (retries <= this.config.maxRetries) {
      try {
        currentObjects = await this.service.listObjects(bucket);
        break;
      } catch (err) {
        retries++;
        if (retries > this.config.maxRetries) {
          throw err;
        }
        await new Promise(resolve => setTimeout(resolve, this.config.retryInterval));
      }
    }

    // 创建当前对象映射
    const currentMap = new Map();
    currentObjects.forEach(obj => {
      currentMap.set(obj.Key, obj);
    });

    // 检查删除的对象
    for (const [key, oldObj] of this.lastObjects.entries()) {
      if (!currentMap.has(key)) {
        // 对象被删除
        const event = {
          eventType: EventType.OBJECT_DELETED,
          bucket: bucket,
          key: key,
          size: oldObj.Size,
          lastModified: oldObj.LastModified,
          eTag: oldObj.ETag
        };
        this.config.eventHandler(event);
      }
    }

    // 检查创建和修改的对象
    for (const [key, currentObj] of currentMap.entries()) {
      if (!this.lastObjects.has(key)) {
        // 对象被创建
        const event = {
          eventType: EventType.OBJECT_CREATED,
          bucket: bucket,
          key: key,
          size: currentObj.Size,
          lastModified: currentObj.LastModified,
          eTag: currentObj.ETag
        };
        this.config.eventHandler(event);
      } else {
        // 检查对象是否被修改
        const oldObj = this.lastObjects.get(key);
        if (currentObj.ETag !== oldObj.ETag || 
            currentObj.LastModified > oldObj.LastModified) {
          // 对象被修改
          const event = {
            eventType: EventType.OBJECT_MODIFIED,
            bucket: bucket,
            key: key,
            size: currentObj.Size,
            lastModified: currentObj.LastModified,
            eTag: currentObj.ETag
          };
          this.config.eventHandler(event);
        }
      }
    }

    // 更新对象列表
    this.lastObjects = currentMap;
  }
}


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

// 列出存储桶中的所有对象（用于监听器）
const listObjects = async (bucket) => {
  const command = new ListObjectsV2Command({
    Bucket: bucket,
  });
  
  const response = await s3Client.send(command);
  return response.Contents || [];
};

// 默认存储桶（从环境变量或配置中获取）
let defaultBucket = process.env.S3_BUCKET;

// 事件历史记录
const eventHistory = [];
const MAX_EVENT_HISTORY = 100;

// 记录事件到历史记录
const recordEvent = (event) => {
  // 添加事件到历史记录的开头
  eventHistory.unshift(event);
  // 限制历史记录的长度
  if (eventHistory.length > MAX_EVENT_HISTORY) {
    eventHistory.pop();
  }
};

// 获取事件历史记录
const getEventHistory = () => {
  return eventHistory;
};

// 清空事件历史记录
const clearEventHistory = () => {
  eventHistory.length = 0;
};

// 启动存储桶监听器
const startBucketListener = (config) => {
  // 验证配置
  if (!config.eventHandler) {
    throw new Error('Event handler is required');
  }

  // 设置默认值
  const bucket = config.bucket || defaultBucket;
  if (!bucket) {
    throw new Error('Bucket is required');
  }

  // 包装事件处理函数，添加事件记录功能
  const originalEventHandler = config.eventHandler;
  const wrappedEventHandler = (event) => {
    // 记录事件
    recordEvent(event);
    // 调用原始事件处理函数
    originalEventHandler(event);
  };

  const listenerConfig = {
    bucket: bucket,
    pollInterval: config.pollInterval || 5000, // 默认5秒
    maxRetries: config.maxRetries || 3, // 默认3次
    retryInterval: config.retryInterval || 2000, // 默认2秒
    errorHandler: config.errorHandler || ((err) => console.error('S3 listener error:', err)),
    eventHandler: wrappedEventHandler
  };

  // 创建并启动监听器
  const listener = new BucketListener({
    listObjects,
    defaultBucket: bucket
  }, listenerConfig);

  listener.start();
  return listener;
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
  startBucketListener,
  getEventHistory,
  clearEventHistory,
  EventType
};