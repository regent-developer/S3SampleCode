// Package controllers 处理HTTP请求
// 作者: KO
// 创建时间: 2026-01-27
// 修改时间: 2026-01-27
package controllers

import (
	"bytes"
	"fmt"
	"net/http"

	"github.com/example/s3service/s3"
	"github.com/labstack/echo/v4"
)

// S3Controller 处理S3相关的HTTP请求
type S3Controller struct {
	service *s3.Service // S3服务实例
}

// NewS3Controller 创建新的S3控制器实例
// 参数:
//
//	service: S3服务实例
//
// 返回值:
//
//	*S3Controller: S3控制器实例
func NewS3Controller(service *s3.Service) *S3Controller {
	return &S3Controller{
		service: service,
	}
}

// UploadFile 上传文件到S3存储桶
// 参数:
//
//	ctx: Echo上下文
//
// 返回值:
//
//	error: 错误信息
func (c *S3Controller) UploadFile(ctx echo.Context) error {
	file, err := ctx.FormFile("file")
	if err != nil {
		return ctx.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid file",
		})
	}

	// 打开上传的文件
	src, err := file.Open()
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Failed to open file",
		})
	}
	defer src.Close()

	// 读取文件内容
	content := bytes.Buffer{}
	if _, err := content.ReadFrom(src); err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Failed to read file",
		})
	}

	// 获取对象键
	key := ctx.FormValue("key")
	if key == "" {
		key = file.Filename
	}

	// 获取存储桶名称
	bucket := ctx.FormValue("bucket")

	// 上传文件
	if err := c.service.UploadFile(ctx.Request().Context(), bucket, key, content.Bytes()); err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Failed to upload file: " + err.Error(),
		})
	}

	return ctx.JSON(http.StatusOK, map[string]string{
		"message": "File uploaded successfully with key: " + key,
	})
}

// DownloadFile 从S3存储桶下载文件
// 参数:
//
//	ctx: Echo上下文
//
// 返回值:
//
//	error: 错误信息
func (c *S3Controller) DownloadFile(ctx echo.Context) error {
	key := ctx.Param("key")
	bucket := ctx.QueryParam("bucket")

	content, err := c.service.DownloadFile(ctx.Request().Context(), bucket, key)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Failed to download file: " + err.Error(),
		})
	}

	// 设置响应头
	ctx.Response().Header().Set("Content-Disposition", "attachment; filename="+key)
	ctx.Response().Header().Set("Content-Length", fmt.Sprintf("%d", len(content)))

	return ctx.Blob(http.StatusOK, "application/octet-stream", content)
}

// DeleteFile 从S3存储桶删除文件
// 参数:
//
//	ctx: Echo上下文
//
// 返回值:
//
//	error: 错误信息
func (c *S3Controller) DeleteFile(ctx echo.Context) error {
	key := ctx.Param("key")
	bucket := ctx.QueryParam("bucket")

	if err := c.service.DeleteFile(ctx.Request().Context(), bucket, key); err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Failed to delete file: " + err.Error(),
		})
	}

	return ctx.JSON(http.StatusOK, map[string]string{
		"message": "File deleted successfully: " + key,
	})
}

// CheckFileExists 检查文件是否存在于S3存储桶
// 参数:
//
//	ctx: Echo上下文
//
// 返回值:
//
//	error: 错误信息
func (c *S3Controller) CheckFileExists(ctx echo.Context) error {
	key := ctx.Param("key")
	bucket := ctx.QueryParam("bucket")

	exists := c.service.FileExists(ctx.Request().Context(), bucket, key)

	return ctx.JSON(http.StatusOK, exists)
}

// HealthCheck 健康检查端点
// 参数:
//
//	ctx: Echo上下文
//
// 返回值:
//
//	error: 错误信息
func (c *S3Controller) HealthCheck(ctx echo.Context) error {
	return ctx.String(http.StatusOK, "S3 Service is running")
}

// ListFiles 列出S3存储桶中的所有文件
// 参数:
//
//	ctx: Echo上下文
//
// 返回值:
//
//	error: 错误信息
func (c *S3Controller) ListFiles(ctx echo.Context) error {
	bucket := ctx.QueryParam("bucket")

	files, err := c.service.ListFiles(ctx.Request().Context(), bucket)
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Failed to list files: " + err.Error(),
		})
	}

	return ctx.JSON(http.StatusOK, files)
}

// ListBuckets 列出所有S3存储桶
// 参数:
//
//	ctx: Echo上下文
//
// 返回值:
//
//	error: 错误信息
func (c *S3Controller) ListBuckets(ctx echo.Context) error {
	buckets, err := c.service.ListBuckets(ctx.Request().Context())
	if err != nil {
		return ctx.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Failed to list buckets: " + err.Error(),
		})
	}

	return ctx.JSON(http.StatusOK, buckets)
}

// CreateBucket 创建新的S3存储桶
// 参数:
//
//	ctx: Echo上下文
//
// 返回值:
//
//	error: 错误信息
func (c *S3Controller) CreateBucket(ctx echo.Context) error {
	bucketName := ctx.QueryParam("bucketName")
	if bucketName == "" {
		return ctx.JSON(http.StatusBadRequest, map[string]string{
			"error": "Bucket name is required",
		})
	}

	if err := c.service.CreateBucket(ctx.Request().Context(), bucketName); err != nil {
		if err.Error() == "bucket already exists" {
			return ctx.JSON(http.StatusConflict, map[string]string{
				"error": "Bucket already exists: " + bucketName,
			})
		}
		return ctx.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Failed to create bucket: " + err.Error(),
		})
	}

	return ctx.JSON(http.StatusOK, map[string]string{
		"message": "Bucket created successfully: " + bucketName,
	})
}