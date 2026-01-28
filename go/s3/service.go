// Package s3 提供S3服务相关功能
// 作者: KO
// 创建时间: 2026-01-27
// 修改时间: 2026-01-27
package s3

import (
	"bytes"
	"context"
	"errors"
	"io"
	"strings"

	"github.com/aws/aws-sdk-go-v2/aws"
	awsconfig "github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/credentials"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/aws/aws-sdk-go-v2/service/s3/types"
	"github.com/example/s3service/config"
)

// Service S3服务实现
type Service struct {
	client        *s3.Client // S3客户端
	defaultBucket string     // 默认存储桶
}

// NewService 创建新的S3服务实例
// 参数:
//
//	cfg: S3配置信息
//
// 返回值:
//
//	*Service: S3服务实例
//	error: 错误信息
func NewService(cfg *config.S3Config) (*Service, error) {
	// 创建自定义AWS配置
	awsCfg, err := awsconfig.LoadDefaultConfig(context.Background(),
		awsconfig.WithRegion(cfg.Region),
		awsconfig.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(
			cfg.AccessKeyID,
			cfg.SecretAccessKey,
			"",
		)),
	)
	if err != nil {
		return nil, err
	}

	// 创建S3客户端
	client := s3.NewFromConfig(awsCfg, func(o *s3.Options) {
		o.BaseEndpoint = aws.String(cfg.Endpoint)
		o.UsePathStyle = cfg.UsePathStyle
	})

	return &Service{
		client:        client,
		defaultBucket: cfg.Bucket,
	}, nil
}

// UploadFile 上传文件到S3存储桶
// 参数:
//
//	ctx: 上下文
//	bucket: 存储桶名称（为空时使用默认存储桶）
//	key: 文件键
//	content: 文件内容
//
// 返回值:
//
//	error: 错误信息
func (s *Service) UploadFile(ctx context.Context, bucket, key string, content []byte) error {
	if bucket == "" {
		bucket = s.defaultBucket
	}

	_, err := s.client.PutObject(ctx, &s3.PutObjectInput{
		Bucket:        aws.String(bucket),
		Key:           aws.String(key),
		Body:          bytes.NewReader(content),
		ContentLength: aws.Int64(int64(len(content))),
	})

	return err
}

// DownloadFile 从S3存储桶下载文件
// 参数:
//
//	ctx: 上下文
//	bucket: 存储桶名称（为空时使用默认存储桶）
//	key: 文件键
//
// 返回值:
//
//	[]byte: 文件内容
//	error: 错误信息
func (s *Service) DownloadFile(ctx context.Context, bucket, key string) ([]byte, error) {
	if bucket == "" {
		bucket = s.defaultBucket
	}

	output, err := s.client.GetObject(ctx, &s3.GetObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	})
	if err != nil {
		return nil, err
	}
	defer output.Body.Close()

	return io.ReadAll(output.Body)
}

// DeleteFile 从S3存储桶删除文件
// 参数:
//
//	ctx: 上下文
//	bucket: 存储桶名称（为空时使用默认存储桶）
//	key: 文件键
//
// 返回值:
//
//	error: 错误信息
func (s *Service) DeleteFile(ctx context.Context, bucket, key string) error {
	if bucket == "" {
		bucket = s.defaultBucket
	}

	_, err := s.client.DeleteObject(ctx, &s3.DeleteObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	})

	return err
}

// FileExists 检查文件是否存在于S3存储桶
// 参数:
//
//	ctx: 上下文
//	bucket: 存储桶名称（为空时使用默认存储桶）
//	key: 文件键
//
// 返回值:
//
//	bool: 文件是否存在
func (s *Service) FileExists(ctx context.Context, bucket, key string) bool {
	if bucket == "" {
		bucket = s.defaultBucket
	}

	_, err := s.client.HeadObject(ctx, &s3.HeadObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
	})

	return err == nil
}

// ListFiles 列出S3存储桶中的所有文件
// 参数:
//
//	ctx: 上下文
//	bucket: 存储桶名称（为空时使用默认存储桶）
//
// 返回值:
//
//	[]map[string]interface{}: 文件列表
//	error: 错误信息
func (s *Service) ListFiles(ctx context.Context, bucket string) ([]map[string]interface{}, error) {
	if bucket == "" {
		bucket = s.defaultBucket
	}

	output, err := s.client.ListObjectsV2(ctx, &s3.ListObjectsV2Input{
		Bucket: aws.String(bucket),
	})
	if err != nil {
		return nil, err
	}

	files := make([]map[string]interface{}, 0, len(output.Contents))
	for _, obj := range output.Contents {
		files = append(files, map[string]interface{}{
			"key":          *obj.Key,
			"size":         obj.Size,
			"lastModified": obj.LastModified,
		})
	}

	return files, nil
}

// ListBuckets 列出所有S3存储桶
// 参数:
//
//	ctx: 上下文
//
// 返回值:
//
//	[]map[string]interface{}: 存储桶列表
//	error: 错误信息
func (s *Service) ListBuckets(ctx context.Context) ([]map[string]interface{}, error) {
	output, err := s.client.ListBuckets(ctx, &s3.ListBucketsInput{})
	if err != nil {
		return nil, err
	}

	buckets := make([]map[string]interface{}, 0, len(output.Buckets))
	for _, bucket := range output.Buckets {
		buckets = append(buckets, map[string]interface{}{
			"name":         *bucket.Name,
			"creationDate": bucket.CreationDate,
		})
	}

	return buckets, nil
}

// CreateBucket 创建新的S3存储桶
// 参数:
//
//	ctx: 上下文
//	bucket: 存储桶名称
//
// 返回值:
//
//	error: 错误信息
func (s *Service) CreateBucket(ctx context.Context, bucket string) error {
	// 检查存储桶是否已存在
	_, err := s.client.HeadBucket(ctx, &s3.HeadBucketInput{
		Bucket: aws.String(bucket),
	})
	if err == nil {
		// 存储桶已存在
		return errors.New("bucket already exists")
	}

	// 检查是否是NoSuchBucket错误或404错误
	var apiErr *types.NoSuchBucket
	if errors.As(err, &apiErr) {
		// 确实是NoSuchBucket错误，可以继续创建
	} else {
		// 对于MinIO，HeadBucket返回404时，可能不会返回NoSuchBucket类型的错误
		// 而是返回一个包含"NotFound"或"StatusCode: 404"的错误消息
		// 所以我们需要检查错误信息是否包含"NotFound"或"StatusCode: 404"
		errMsg := err.Error()
		if errMsg == "" {
			return err
		}
		// 检查错误消息中是否包含"NotFound"或"StatusCode: 404"
		if !strings.Contains(errMsg, "NotFound") && !strings.Contains(errMsg, "StatusCode: 404") {
			// 其他错误，比如权限问题、网络问题等
			return err
		}
	}

	// 创建存储桶
	_, err = s.client.CreateBucket(ctx, &s3.CreateBucketInput{
		Bucket: aws.String(bucket),
	})

	return err
}