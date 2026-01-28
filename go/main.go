// Package main 是S3服务的主入口
// 作者: KO
// 创建时间: 2026-01-27
// 修改时间: 2026-01-27
package main

import (
	"fmt"

	"github.com/example/s3service/config"
	"github.com/example/s3service/controllers"
	"github.com/example/s3service/s3"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

// main 函数是S3服务的主入口
func main() {
	// 加载配置
	cfg, err := config.LoadConfig()
	if err != nil {
		fmt.Printf("Failed to load config: %v\n", err)
		return
	}

	// 初始化S3服务
	service, err := s3.NewService(cfg)
	if err != nil {
		fmt.Printf("Failed to initialize S3 service: %v\n", err)
		return
	}

	// 创建Echo实例
	e := echo.New()

	// 配置CORS
	e.Use(middleware.CORSWithConfig(middleware.CORSConfig{
		AllowOrigins: []string{"*"},
		AllowMethods: []string{echo.GET, echo.POST, echo.PUT, echo.DELETE, echo.OPTIONS},
		AllowHeaders: []string{echo.HeaderOrigin, echo.HeaderContentType, echo.HeaderAccept},
	}))

	// 创建S3控制器
	controller := controllers.NewS3Controller(service)

	// 配置API路由
	api := e.Group("/api/s3")
	{
		// 健康检查
		api.GET("/health", controller.HealthCheck)

		// 文件上传
		api.POST("/upload", controller.UploadFile)

		// 文件下载
		api.GET("/download/:key", controller.DownloadFile)

		// 文件删除
		api.DELETE("/delete/:key", controller.DeleteFile)

		// 检查文件是否存在
		api.GET("/exists/:key", controller.CheckFileExists)

		// 列出文件
		api.GET("/list", controller.ListFiles)

		// 列出存储桶
		api.GET("/buckets", controller.ListBuckets)

		// 创建存储桶
		api.POST("/bucket", controller.CreateBucket)
	}

	// 配置静态文件服务
	e.Static("/", "./static")

	// 根路径重定向到index.html
	e.GET("/", func(c echo.Context) error {
		return c.File("./static/index.html")
	})

	// 启动服务器
	port := "8080"
	fmt.Printf("S3 Service is running on http://localhost:%s\n", port)
	if err := e.Start(fmt.Sprintf(":%s", port)); err != nil {
		fmt.Printf("Failed to start server: %v\n", err)
	}
}