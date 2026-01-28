# Solo S3 项目概要

## 1. 项目概述

Solo S3 是一个基于多种编程语言实现的 S3 服务客户端和 API 服务，提供了与 Amazon S3 兼容的存储服务接口。项目支持多种编程语言实现，包括 Java、Python、Go 和 JavaScript，方便不同技术栈的开发者使用。

## 2. 目录结构

```
d:\project\Trae\solo_s3\
├── doc/              # 项目文档
├── go/              # Go 语言实现
├── java/            # Java 语言实现
├── javaapplication/ # Java 应用示例
├── js/              # JavaScript 语言实现
├── python/          # Python 语言实现
├── .env             # 环境变量配置
├── .env.example     # 环境变量示例
├── docker-compose.yml     # Docker Compose 配置
└── README.md              # 项目说明文档
```

## 3. 各语言版本实现

### 3.1 Java 版本

**技术栈**：
- Spring Boot 框架
- AWS SDK for Java v2
- Maven 构建工具

**主要功能**：
- REST API 实现
- 文件上传、下载、删除
- 检查文件存在性
- 列出文件和存储桶
- 创建存储桶
- 前端页面

**目录结构**：
```
java/
├── src/
│   ├── main/
│   │   ├── java/com/example/s3service/  # Java 源代码
│   │   └── resources/                   # 配置文件和静态资源
│   └── test/                            # 单元测试
└── target/                              # 构建输出
```

### 3.2 Java 应用示例

**描述**：
- 简单的 Java 应用示例，演示如何使用 AWS SDK for Java v2 与 S3 服务交互
- 适合作为入门示例

**目录结构**：
```
javaapplication/
├── src/
│   └── main/
│       └── java/com/example/s3test/     # Java 应用源代码
└── target/                              # 构建输出
```

### 3.3 Python 版本

**技术栈**：
- FastAPI 框架
- boto3 库
- uvicorn 服务器

**主要功能**：
- REST API 实现
- 文件上传、下载、删除
- 检查文件存在性
- 列出文件和存储桶
- 创建存储桶
- 前端页面

**目录结构**：
```
python/
├── static/           # 静态资源
├── config.py         # 配置文件
├── main.py           # 主应用程序
├── requirements.txt  # 依赖列表
└── s3_service.py     # S3 服务实现
```

### 3.4 Go 版本

**技术栈**：
- Echo 框架
- AWS SDK for Go v2
- Go Modules 依赖管理

**主要功能**：
- REST API 实现
- 文件上传、下载、删除
- 检查文件存在性
- 列出文件和存储桶
- 创建存储桶
- 前端页面

**目录结构**：
```
go/
├── config/          # 配置包
├── controllers/     # 控制器包
├── s3/              # S3 服务包
├── static/          # 静态资源
├── config.yaml      # 配置文件
├── go.mod           # Go 模块配置
├── go.sum           # 依赖校验文件
└── main.go          # 主应用程序
```

### 3.5 JavaScript 版本

**技术栈**：
- Node.js 运行时
- Express 框架
- AWS SDK for JavaScript v3
- Multer 文件上传处理

**主要功能**：
- REST API 实现
- 文件上传、下载、删除
- 检查文件存在性
- 列出文件和存储桶
- 创建存储桶
- 前端页面

**目录结构**：
```
js/
├── node_modules/     # npm 依赖
├── src/             # 源代码
├── static/          # 静态资源
├── tests/           # 测试代码
├── temp/            # 临时文件目录
├── .env             # 环境变量配置
├── package.json     # npm 项目配置
└── package-lock.json # 依赖锁定文件
```

## 4. 功能特性

### 4.1 核心功能

| 功能 | 描述 |
|------|------|
| 文件上传 | 将本地文件上传到 S3 存储桶 |
| 文件下载 | 从 S3 存储桶下载文件到本地 |
| 文件删除 | 从 S3 存储桶删除文件 |
| 检查文件存在 | 检查指定文件是否存在于 S3 存储桶中 |
| 列出文件 | 列出 S3 存储桶中的所有文件 |
| 列出存储桶 | 列出所有 S3 存储桶 |
| 创建存储桶 | 创建新的 S3 存储桶 |

### 4.2 API 端点

所有语言版本实现了相同的 REST API 端点：

| 端点 | 方法 | 描述 |
|------|------|------|
| /api/s3/health | GET | 健康检查 |
| /api/s3/upload | POST | 文件上传 |
| /api/s3/download/:key | GET | 文件下载 |
| /api/s3/delete/:key | DELETE | 文件删除 |
| /api/s3/exists/:key | GET | 检查文件存在 |
| /api/s3/list | GET | 列出文件 |
| /api/s3/buckets | GET | 列出存储桶 |
| /api/s3/bucket | POST | 创建存储桶 |

## 5. 技术栈

| 语言 | 框架 | S3 SDK | 其他主要依赖 |
|------|------|--------|--------------|
| Java | Spring Boot | AWS SDK for Java v2 | Maven, Thymeleaf |
| Python | FastAPI | boto3 | uvicorn, python-multipart |
| Go | Echo | AWS SDK for Go v2 | Viper 配置管理 |
| JavaScript | Express | AWS SDK for JavaScript v3 | Multer, CORS |

## 6. 前后端架构

### 6.1 后端架构

所有语言版本的后端架构遵循 REST API 设计原则，提供了统一的 API 接口。后端服务负责处理客户端请求，与 S3 存储服务进行交互，并返回响应结果。

### 6.2 前端架构

前端页面是一个单页面应用，使用 HTML、CSS 和 JavaScript 实现，提供了直观的用户界面来操作 S3 存储服务。前端通过 AJAX 请求与后端 API 进行通信，实现了以下功能：

- 服务端 URL 配置
- 存储桶选择和管理
- 文件上传、下载、删除
- 文件存在性检查
- 文件列表显示
- 存储桶创建

## 7. 如何运行

### 7.1 启动 S3 服务

使用 Docker Compose 启动 MinIO 服务：
```bash
docker-compose up -d
```

### 7.2 运行后端服务

#### Java 版本
```bash
cd java
mvn spring-boot:run
```

#### Python 版本
```bash
cd python
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Go 版本
```bash
cd go
go mod tidy
go run main.go
```

#### JavaScript 版本
```bash
cd js
npm install
npm start
```

### 7.3 访问前端页面

所有版本的前端页面均可通过 http://localhost:8080 访问。

## 8. 测试

### 8.1 Java 版本
```bash
cd java
mvn test
```

### 8.2 Python 版本
```bash
cd python
pytest
```

### 8.3 Go 版本
```bash
cd go
go test ./...
```

### 8.4 JavaScript 版本
```bash
cd js
npm test
```

## 9. 配置管理

所有语言版本均支持通过配置文件或环境变量进行配置，主要配置项包括：

- S3 服务端点
- 访问密钥和秘密密钥
- 默认存储桶
- 区域
- 端口号

## 10. 兼容性

项目兼容以下 S3 兼容存储服务：
- Amazon S3
- MinIO
- Ceph
- Wasabi

## 11. 安全考虑

- 使用 HTTPS 协议保护数据传输（生产环境）
- 访问密钥和秘密密钥的安全存储
- 合理设置存储桶权限
- 输入验证和文件大小限制

## 12. 未来计划

- 支持更多 S3 功能（如对象版本控制、生命周期管理）
- 增加更多语言实现
- 完善测试用例
- 增加监控和日志功能
- 支持更多 S3 兼容存储服务

## 13. 贡献指南

欢迎通过以下方式贡献代码：

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送分支
5. 创建 Pull Request

## 14. 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 15. 联系方式

如有问题或建议，请通过 GitHub Issues 提交。

---

**作者**：KO  
**创建时间**：2026-01-25  
**版本**：1.0  