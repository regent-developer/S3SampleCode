# 本地S3测试环境与多语言文件管理系统

## 项目概述

Solo S3 是一个基于多种编程语言实现的 S3 服务客户端和 API 服务，提供了与 Amazon S3 兼容的存储服务接口。项目支持多种编程语言实现，包括 Java、Python、Go 和 JavaScript，方便不同技术栈的开发者使用。

## 支持的语言实现

- **Java**: Spring Boot 框架，提供完整的 REST API 和前端页面
- **Java 应用示例**: 简单的 Java 应用示例，适合入门学习
- **Python**: FastAPI 框架，轻量级高性能的 API 服务
- **Go**: Echo 框架，高性能的 API 服务
- **JavaScript**: Express 框架，全栈 JavaScript 实现

## 目录结构

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

## 1. 快速搭建Minio S3服务

### 步骤1：启动Minio服务

在项目根目录执行以下命令：

```bash
docker-compose up -d
```

### 步骤2：访问Minio管理界面

打开浏览器访问：http://localhost:9001
- 用户名：minioadmin
- 密码：minioadmin

### 步骤3：创建测试Bucket

1. 登录管理界面
2. 点击"Create Bucket"按钮
3. 输入Bucket名称（例如："test-bucket"）
4. 点击"Create Bucket"完成创建

## 2. 各语言版本使用指南

### 2.1 Java 版本

**技术栈**：
- Spring Boot 框架
- AWS SDK for Java v2
- Maven 构建工具

**使用步骤**：

1. 进入Java项目目录：
   ```bash
   cd java
   ```

2. 运行应用：
   ```bash
   mvn spring-boot:run
   ```

3. 访问前端页面：
   ```
   http://localhost:8080
   ```

4. 运行测试：
   ```bash
   mvn test
   ```

### 2.2 Java 应用示例

**描述**：
- 简单的 Java 应用示例，演示如何使用 AWS SDK for Java v2 与 S3 服务交互
- 适合作为入门示例

**使用步骤**：

1. 进入Java应用示例目录：
   ```bash
   cd javaapplication
   ```

2. 构建并运行：
   ```bash
   mvn package
   java -jar target/s3-test-application-1.0-SNAPSHOT-jar-with-dependencies.jar
   ```

### 2.3 Python 版本

**技术栈**：
- FastAPI 框架
- boto3 库
- uvicorn 服务器

**使用步骤**：

1. 进入Python项目目录：
   ```bash
   cd python
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 运行应用：
   ```bash
   uvicorn main:app --reload
   ```

4. 访问前端页面：
   ```
   http://localhost:8080
   ```

5. 运行测试：
   ```bash
   pytest
   ```

### 2.4 Go 版本

**技术栈**：
- Echo 框架
- AWS SDK for Go v2
- Go Modules 依赖管理

**使用步骤**：

1. 进入Go项目目录：
   ```bash
   cd go
   ```

2. 下载依赖：
   ```bash
   go mod tidy
   ```

3. 运行应用：
   ```bash
   go run main.go
   ```

4. 访问前端页面：
   ```
   http://localhost:8080
   ```

5. 运行测试：
   ```bash
   go test ./...
   ```

### 2.5 JavaScript 版本

**技术栈**：
- Node.js 运行时
- Express 框架
- AWS SDK for JavaScript v3

**使用步骤**：

1. 进入JavaScript项目目录：
   ```bash
   cd js
   ```

2. 安装依赖：
   ```bash
   npm install
   ```

3. 运行应用：
   ```bash
   npm start
   ```

4. 访问前端页面：
   ```
   http://localhost:8080
   ```

5. 运行测试：
   ```bash
   npm test
   ```

## 3. 核心功能

所有语言版本均实现了以下核心功能：

- ✅ 文件上传到 S3 存储桶
- ✅ 从 S3 存储桶下载文件
- ✅ 从 S3 存储桶删除文件
- ✅ 检查文件是否存在于 S3 存储桶
- ✅ 列出 S3 存储桶中的所有文件
- ✅ 列出所有 S3 存储桶
- ✅ 创建新的 S3 存储桶
- ✅ 提供 REST API 接口
- ✅ 提供前端页面（除 Java 应用示例外）

## 4. API 端点

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

## 5. 环境变量配置

所有语言版本均支持通过 `.env` 文件进行配置，主要配置项包括：

```env
# S3配置
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_REGION=us-east-1
S3_BUCKET=test-bucket
```

## 6. 常见问题

### Q: 为什么连接失败？
A: 请检查：
1. Minio服务是否正在运行（`docker ps`）
2. 环境变量配置是否正确
3. `forcePathStyle: true`是否已启用（针对SDK配置）

### Q: 如何修改存储路径？
A: 修改docker-compose.yml中的volumes配置

### Q: 如何添加更多桶？
A: 通过Minio管理界面或使用各语言版本提供的API

### Q: 如何访问前端页面？
A: 所有语言版本的前端页面均可通过 http://localhost:8080 访问

## 7. 技术栈

| 语言 | 框架 | S3 SDK | 其他主要依赖 |
|------|------|--------|--------------|
| Java | Spring Boot | AWS SDK for Java v2 | Maven, Thymeleaf |
| Python | FastAPI | boto3 | uvicorn, python-multipart |
| Go | Echo | AWS SDK for Go v2 | Viper 配置管理 |
| JavaScript | Express | AWS SDK for JavaScript v3 | Multer, CORS |

## 8. 前后端架构

### 8.1 后端架构

所有语言版本的后端架构遵循 REST API 设计原则，提供了统一的 API 接口。后端服务负责处理客户端请求，与 S3 存储服务进行交互，并返回响应结果。

### 8.2 前端架构

前端页面是一个单页面应用，使用 HTML、CSS 和 JavaScript 实现，提供了直观的用户界面来操作 S3 存储服务。前端通过 AJAX 请求与后端 API 进行通信，实现了文件上传、下载、删除、存在性检查、文件列表显示和存储桶管理等功能。

## 9. 兼容性

项目兼容以下 S3 兼容存储服务：

- Amazon S3
- MinIO
- Ceph
- Wasabi

## 10. 安全考虑

- 使用 HTTPS 协议保护数据传输（生产环境）
- 访问密钥和秘密密钥的安全存储
- 合理设置存储桶权限
- 输入验证和文件大小限制

## 11. 优势

1. **多语言支持**：支持 Java、Python、Go 和 JavaScript
2. **最简配置**：仅需一个docker-compose.yml文件启动S3服务
3. **快速启动**：Docker Compose一键部署
4. **完整功能**：支持所有S3核心功能
5. **可视化管理**：提供Web管理界面
6. **成本为零**：无需AWS账号和费用
7. **易于扩展**：支持多桶、多用户配置
8. **REST API**：提供统一的REST API接口
9. **前端页面**：提供直观的Web操作界面

## 12. 结论

Solo S3 项目提供了一个完整的本地 S3 测试环境和多语言文件管理系统，适合开发人员在本地进行 S3 相关功能的开发和测试，无需依赖 AWS S3 服务。项目支持多种编程语言实现，提供了统一的 REST API 接口和直观的前端页面，便于不同技术栈的开发者使用和学习。

## 13. 文档

详细的项目文档请查看 `doc/project_overview.md` 文件。