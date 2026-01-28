/**
 * S3服务主入口文件
 * 作者: KO
 * 创建时间: 2026-01-27
 * 修改时间: 2026-01-27
 * 描述: 启动Express服务器，配置API端点，处理S3相关的HTTP请求
 */
require('dotenv').config();
const express = require('express');
const multer = require('multer');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const s3Service = require('./s3Service');

/**
 * Express应用实例
 */
const app = express();

/**
 * 服务器端口，从环境变量获取或使用默认值8080
 */
const port = process.env.PORT || 8080;

/**
 * 默认存储桶名称，从环境变量获取
 */
const defaultBucket = process.env.S3_BUCKET;

// 配置CORS
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Origin', 'Content-Type', 'Accept']
}));

// 配置multer，用于处理文件上传
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB
  }
});

/**
 * 健康检查端点
 * @param {object} req - Express请求对象
 * @param {object} res - Express响应对象
 */
app.get('/api/s3/health', (req, res) => {
  res.send('S3 Service is running');
});

/**
 * 文件上传端点
 * @param {object} req - Express请求对象
 * @param {object} res - Express响应对象
 */
app.post('/api/s3/upload', upload.single('file'), async (req, res) => {
  try {
    const file = req.file;
    const key = req.body.key || file.originalname;
    const bucket = req.body.bucket || defaultBucket;
    
    // 保存临时文件
    const tempFilePath = path.join(__dirname, '..', 'temp', file.originalname);
    fs.writeFileSync(tempFilePath, file.buffer);
    
    // 上传到S3
    await s3Service.uploadFile(bucket, key, tempFilePath);
    
    // 删除临时文件
    fs.unlinkSync(tempFilePath);
    
    res.status(200).send(`File uploaded successfully with key: ${key}`);
  } catch (error) {
    console.error('Failed to upload file:', error);
    res.status(500).send(`Failed to upload file: ${error.message}`);
  }
});

/**
 * 文件下载端点
 * @param {object} req - Express请求对象
 * @param {object} res - Express响应对象
 */
app.get('/api/s3/download/:key', async (req, res) => {
  try {
    const key = req.params.key;
    const bucket = req.query.bucket || defaultBucket;
    
    // 创建临时文件路径
    const tempFilePath = path.join(__dirname, '..', 'temp', path.basename(key));
    
    // 从S3下载文件
    await s3Service.downloadFile(bucket, key, tempFilePath);
    
    // 发送文件给客户端
    res.download(tempFilePath, path.basename(key), (err) => {
      // 删除临时文件
      fs.unlinkSync(tempFilePath);
      
      if (err) {
        console.error('Failed to send file:', err);
        res.status(500).send(`Failed to download file: ${err.message}`);
      }
    });
  } catch (error) {
    console.error('Failed to download file:', error);
    res.status(500).send(`Failed to download file: ${error.message}`);
  }
});

/**
 * 文件删除端点
 * @param {object} req - Express请求对象
 * @param {object} res - Express响应对象
 */
app.delete('/api/s3/delete/:key', async (req, res) => {
  try {
    const key = req.params.key;
    const bucket = req.query.bucket || defaultBucket;
    
    await s3Service.deleteFile(bucket, key);
    res.status(200).send(`File deleted successfully: ${key}`);
  } catch (error) {
    console.error('Failed to delete file:', error);
    res.status(500).send(`Failed to delete file: ${error.message}`);
  }
});

/**
 * 检查文件是否存在端点
 * @param {object} req - Express请求对象
 * @param {object} res - Express响应对象
 */
app.get('/api/s3/exists/:key', async (req, res) => {
  try {
    const key = req.params.key;
    const bucket = req.query.bucket || defaultBucket;
    
    const exists = await s3Service.fileExists(bucket, key);
    res.status(200).json(exists);
  } catch (error) {
    console.error('Failed to check file existence:', error);
    res.status(500).json(false);
  }
});

/**
 * 列出文件端点
 * @param {object} req - Express请求对象
 * @param {object} res - Express响应对象
 */
app.get('/api/s3/list', async (req, res) => {
  try {
    const bucket = req.query.bucket || defaultBucket;
    
    const files = await s3Service.listFiles(bucket);
    
    // 转换为前端可以处理的简单数据结构
    const fileInfoList = files.map(file => ({
      key: file.Key,
      size: file.Size,
      lastModified: file.LastModified
    }));
    
    res.status(200).json(fileInfoList);
  } catch (error) {
    console.error('Failed to list files:', error);
    res.status(500).send(`Failed to list files: ${error.message}`);
  }
});

/**
 * 列出存储桶端点
 * @param {object} req - Express请求对象
 * @param {object} res - Express响应对象
 */
app.get('/api/s3/buckets', async (req, res) => {
  try {
    const buckets = await s3Service.listBuckets();
    
    // 转换为前端可以处理的简单数据结构
    const bucketInfoList = buckets.map(bucket => ({
      name: bucket.Name,
      creationDate: bucket.CreationDate
    }));
    
    res.status(200).json(bucketInfoList);
  } catch (error) {
    console.error('Failed to list buckets:', error);
    res.status(500).send(`Failed to list buckets: ${error.message}`);
  }
});

/**
 * 创建存储桶端点
 * @param {object} req - Express请求对象
 * @param {object} res - Express响应对象
 */
app.post('/api/s3/bucket', async (req, res) => {
  try {
    const bucketName = req.body.bucketName || req.query.bucketName;
    
    if (!bucketName) {
      res.status(400).send('Bucket name is required');
      return;
    }
    
    // 检查存储桶是否已存在
    const exists = await s3Service.doesBucketExist(bucketName);
    if (exists) {
      res.status(409).send(`Bucket already exists: ${bucketName}`);
      return;
    }
    
    await s3Service.createBucket(bucketName);
    res.status(200).send(`Bucket created successfully: ${bucketName}`);
  } catch (error) {
    console.error('Failed to create bucket:', error);
    res.status(500).send(`Failed to create bucket: ${error.message}`);
  }
});

// 配置静态文件服务
app.use(express.static(path.join(__dirname, '..', 'static')));

/**
 * 根路径重定向到index.html
 * @param {object} req - Express请求对象
 * @param {object} res - Express响应对象
 */
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'static', 'index.html'));
});

// 确保temp目录存在
const tempDir = path.join(__dirname, '..', 'temp');
if (!fs.existsSync(tempDir)) {
  fs.mkdirSync(tempDir, { recursive: true });
}

/**
 * 启动服务器
 */
app.listen(port, () => {
  console.log(`S3 Service is running on http://localhost:${port}`);
  console.log(`API endpoints available at http://localhost:${port}/api/s3`);
  console.log(`Frontend available at http://localhost:${port}`);
});