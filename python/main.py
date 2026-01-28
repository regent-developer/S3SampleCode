"""
S3服务API主文件，使用FastAPI框架实现S3操作的RESTful接口

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
- 健康检查
- 根路径重定向到静态文件
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import StreamingResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from s3_service import S3Service
import mimetypes

# 创建FastAPI应用实例
app = FastAPI(title="S3 Service API", description="FastAPI implementation of S3 operations")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置静态文件服务
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# 创建S3服务实例
s3_service = S3Service()

@app.post("/api/s3/upload")
async def upload_file(
    file: UploadFile = File(...),
    key: str = Query(None, description="Optional S3 object key, if not provided, use original filename"),
    bucket: str = Query(None, description="Optional bucket name, if not provided, use default bucket")
):
    """
    上传文件到S3存储桶
    
    参数：
    - file: UploadFile对象，要上传的文件
    - key: str，可选，S3对象键，默认为原始文件名
    - bucket: str，可选，存储桶名称，默认为默认存储桶
    
    返回值：
    - dict: 包含上传成功消息和对象键的响应
    
    异常：
    - HTTPException: 上传失败时抛出，状态码500
    """
    try:
        # 如果没有提供key，使用原始文件名
        object_key = key or file.filename
        s3_service.upload_file(file, object_key, bucket)
        return {"message": f"File uploaded successfully with key: {object_key}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/s3/download/{key}")
async def download_file(
    key: str,
    bucket: str = Query(None, description="Optional bucket name, if not provided, use default bucket")
):
    """
    从S3存储桶下载文件
    
    参数：
    - key: str，S3对象键
    - bucket: str，可选，存储桶名称，默认为默认存储桶
    
    返回值：
    - StreamingResponse: 包含文件内容的流式响应
    
    异常：
    - HTTPException: 下载失败时抛出，状态码500
    """
    try:
        response = s3_service.download_file(key, bucket)
        content_type = response.get("ContentType", "application/octet-stream")
        
        # 返回流式响应
        return StreamingResponse(
            response["Body"],
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={key}",
                "Content-Length": str(response["ContentLength"])
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/s3/delete/{key}")
async def delete_file(
    key: str,
    bucket: str = Query(None, description="Optional bucket name, if not provided, use default bucket")
):
    """
    从S3存储桶删除文件
    
    参数：
    - key: str，S3对象键
    - bucket: str，可选，存储桶名称，默认为默认存储桶
    
    返回值：
    - dict: 包含删除成功消息的响应
    
    异常：
    - HTTPException: 删除失败时抛出，状态码500
    """
    try:
        s3_service.delete_file(key, bucket)
        return {"message": f"File deleted successfully: {key}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/s3/exists/{key}")
async def check_file_exists(
    key: str,
    bucket: str = Query(None, description="Optional bucket name, if not provided, use default bucket")
):
    """
    检查文件是否存在于S3存储桶
    
    参数：
    - key: str，S3对象键
    - bucket: str，可选，存储桶名称，默认为默认存储桶
    
    返回值：
    - bool: 文件是否存在
    
    异常：
    - HTTPException: 检查失败时抛出，状态码500
    """
    try:
        exists = s3_service.file_exists(key, bucket)
        return exists
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/s3/health")
async def health_check():
    """
    健康检查端点
    
    返回值：
    - PlainTextResponse: 包含服务运行状态的响应
    """
    return PlainTextResponse("S3 Service is running")

@app.get("/api/s3/list")
async def list_files(
    bucket: str = Query(None, description="Optional bucket name, if not provided, use default bucket")
):
    """
    列出S3存储桶中的所有文件
    
    参数：
    - bucket: str，可选，存储桶名称，默认为默认存储桶
    
    返回值：
    - list: 文件列表，每个文件包含key、size和lastModified属性
    
    异常：
    - HTTPException: 列出失败时抛出，状态码500
    """
    try:
        files = s3_service.list_files(bucket)
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/s3/buckets")
async def list_buckets():
    """
    列出所有S3存储桶
    
    返回值：
    - list: 存储桶列表，每个存储桶包含name和creationDate属性
    
    异常：
    - HTTPException: 列出失败时抛出，状态码500
    """
    try:
        buckets = s3_service.list_buckets()
        return buckets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/s3/bucket")
async def create_bucket(
    bucketName: str = Query(..., description="Name of the bucket to create")
):
    """
    创建新的S3存储桶
    
    参数：
    - bucketName: str，要创建的存储桶名称
    
    返回值：
    - dict: 包含创建成功消息的响应
    
    异常：
    - HTTPException: 存储桶已存在时抛出，状态码409
    - HTTPException: 创建失败时抛出，状态码500
    """
    try:
        created = s3_service.create_bucket(bucketName)
        if created:
            return {"message": f"Bucket created successfully: {bucketName}"}
        else:
            raise HTTPException(status_code=409, detail=f"Bucket already exists: {bucketName}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """
    根路径重定向到index.html
    
    返回值：
    - RedirectResponse: 重定向到静态文件index.html
    """
    return RedirectResponse(url="/static/index.html")