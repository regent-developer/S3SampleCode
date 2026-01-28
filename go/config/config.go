// Package config 提供配置相关功能
// 作者: KO
// 创建时间: 2026-01-27
// 修改时间: 2026-01-27
package config

import (
	"github.com/spf13/viper"
)

// S3Config 存储S3客户端配置
type S3Config struct {
	Endpoint        string `mapstructure:"endpoint"`          // S3服务端点
	Region          string `mapstructure:"region"`            // 区域
	Bucket          string `mapstructure:"bucket"`            // 默认存储桶
	AccessKeyID     string `mapstructure:"access_key_id"`     // 访问密钥ID
	SecretAccessKey string `mapstructure:"secret_access_key"` // 秘密访问密钥
	UsePathStyle    bool   `mapstructure:"use_path_style"`    // 是否使用路径风格访问
}

// LoadConfig 从配置文件加载S3配置
// 返回值:
//
//	*S3Config: S3配置信息
//	error: 错误信息
func LoadConfig() (*S3Config, error) {
	viper.SetConfigFile("./config.yaml")
	viper.SetConfigType("yaml")

	// 设置默认值
	viper.SetDefault("endpoint", "http://localhost:9000")
	viper.SetDefault("region", "us-east-1")
	viper.SetDefault("bucket", "test")
	viper.SetDefault("use_path_style", true)

	if err := viper.ReadInConfig(); err != nil {
		return nil, err
	}

	var config S3Config
	if err := viper.Unmarshal(&config); err != nil {
		return nil, err
	}

	return &config, nil
}