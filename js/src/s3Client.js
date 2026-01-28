/**
 * S3客户端配置
 * 作者: KO
 * 创建时间: 2026-01-27
 * 修改时间: 2026-01-27
 * 描述: 创建并配置S3客户端实例，用于与S3兼容的存储服务进行交互
 */
const { S3Client } = require('@aws-sdk/client-s3');
require('dotenv').config();

/**
 * S3客户端实例
 * 配置包括：
 * - 端点：从环境变量S3_ENDPOINT获取
 * - 凭证：从环境变量S3_ACCESS_KEY和S3_SECRET_KEY获取
 * - 区域：从环境变量S3_REGION获取
 * - 强制路径风格：启用，以兼容Minio等存储服务
 */
const s3Client = new S3Client({
  endpoint: process.env.S3_ENDPOINT,
  credentials: {
    accessKeyId: process.env.S3_ACCESS_KEY,
    secretAccessKey: process.env.S3_SECRET_KEY,
  },
  region: process.env.S3_REGION,
  forcePathStyle: true, // 必须启用，兼容Minio
});

module.exports = s3Client;