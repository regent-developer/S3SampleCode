package com.example.s3service.controller;

import com.example.s3service.service.S3Service;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.core.ResponseBytes;
import software.amazon.awssdk.services.s3.model.GetObjectResponse;

/**
 * S3 REST Controller
 * 
 * @author KO
 * @since 2026-01-19
 */
@RestController
@RequestMapping("/api/s3")
public class S3Controller {

    private final S3Service s3Service;

    /**
     * Constructor with S3Service dependency injection
     * 
     * @param s3Service S3Service instance
     */
    public S3Controller(S3Service s3Service) {
        this.s3Service = s3Service;
    }

    /**
     * Upload file to S3 bucket
     * 
     * @param file MultipartFile to upload
     * @param key  optional S3 object key, if not provided, use original filename
     * @param bucket optional bucket name, if not provided, use default bucket
     * @return ResponseEntity with upload result
     */
    @PostMapping("/upload")
    public ResponseEntity<String> uploadFile(@RequestParam("file") MultipartFile file, 
                                             @RequestParam(value = "key", required = false) String key, 
                                             @RequestParam(value = "bucket", required = false) String bucket) {
        try {
            String objectKey = key != null && !key.isEmpty() ? key : file.getOriginalFilename();
            s3Service.uploadFile(file, objectKey, bucket);
            return ResponseEntity.ok("File uploaded successfully with key: " + objectKey);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to upload file: " + e.getMessage());
        }
    }

    /**
     * Download file from S3 bucket
     * 
     * @param key S3 object key
     * @param bucket optional bucket name, if not provided, use default bucket
     * @return ResponseEntity with file content
     */
    @GetMapping("/download/{key}")
    public ResponseEntity<ByteArrayResource> downloadFile(@PathVariable String key, 
                                                          @RequestParam(value = "bucket", required = false) String bucket) {
        try {
            ResponseBytes<GetObjectResponse> responseBytes = s3Service.downloadFile(key, bucket);
            byte[] data = responseBytes.asByteArray();
            GetObjectResponse response = responseBytes.response();

            ByteArrayResource resource = new ByteArrayResource(data);

            return ResponseEntity.ok()
                    .contentType(MediaType.parseMediaType(response.contentType()))
                    .contentLength(data.length)
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + key + "\"")
                    .body(resource);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(null);
        }
    }

    /**
     * Delete file from S3 bucket
     * 
     * @param key S3 object key
     * @param bucket optional bucket name, if not provided, use default bucket
     * @return ResponseEntity with delete result
     */
    @DeleteMapping("/delete/{key}")
    public ResponseEntity<String> deleteFile(@PathVariable String key, 
                                             @RequestParam(value = "bucket", required = false) String bucket) {
        try {
            s3Service.deleteFile(key, bucket);
            return ResponseEntity.ok("File deleted successfully: " + key);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to delete file: " + e.getMessage());
        }
    }

    /**
     * Check if file exists in S3 bucket
     * 
     * @param key S3 object key
     * @param bucket optional bucket name, if not provided, use default bucket
     * @return ResponseEntity with exists status
     */
    @GetMapping("/exists/{key}")
    public ResponseEntity<Boolean> checkFileExists(@PathVariable String key, 
                                                  @RequestParam(value = "bucket", required = false) String bucket) {
        try {
            boolean exists = s3Service.fileExists(key, bucket);
            return ResponseEntity.ok(exists);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(false);
        }
    }

    /**
     * Health check endpoint
     * 
     * @return ResponseEntity with health status
     */
    @GetMapping("/health")
    public ResponseEntity<String> healthCheck() {
        return ResponseEntity.ok("S3 Service is running");
    }

    /**
     * List all files in S3 bucket
     * 
     * @param bucket optional bucket name, if not provided, use default bucket
     * @return ResponseEntity with list of files
     */
    @GetMapping("/list")
    public ResponseEntity<?> listFiles(@RequestParam(value = "bucket", required = false) String bucket) {
        try {
            var response = s3Service.listFiles(bucket);
            // 转换为前端可以处理的简单数据结构
            var files = response.contents().stream()
                    .map(file -> {
                        // 创建包含必要信息的简单对象
                        var fileInfo = new java.util.HashMap<String, Object>();
                        fileInfo.put("key", file.key());
                        fileInfo.put("size", file.size());
                        fileInfo.put("lastModified", file.lastModified());
                        return fileInfo;
                    })
                    .collect(java.util.stream.Collectors.toList());
            return ResponseEntity.ok(files);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to list files: " + e.getMessage());
        }
    }
    
    /**
     * List all S3 buckets
     * 
     * @return ResponseEntity with list of buckets
     */
    @GetMapping("/buckets")
    public ResponseEntity<?> listBuckets() {
        try {
            var buckets = s3Service.listBuckets();
            // 转换为前端可以处理的简单数据结构
            var bucketInfo = buckets.stream()
                    .map(bucket -> {
                        // 创建包含必要信息的简单对象
                        var info = new java.util.HashMap<String, Object>();
                        info.put("name", bucket.name());
                        info.put("creationDate", bucket.creationDate());
                        return info;
                    })
                    .collect(java.util.stream.Collectors.toList());
            return ResponseEntity.ok(bucketInfo);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to list buckets: " + e.getMessage());
        }
    }
    
    /**
     * Create a new S3 bucket
     * 
     * @param bucketName name of the bucket to create
     * @return ResponseEntity with creation result
     */
    @PostMapping("/bucket")
    public ResponseEntity<String> createBucket(@RequestParam("bucketName") String bucketName) {
        try {
            boolean created = s3Service.createBucket(bucketName);
            if (created) {
                return ResponseEntity.ok("Bucket created successfully: " + bucketName);
            } else {
                return ResponseEntity.status(HttpStatus.CONFLICT)
                        .body("Bucket already exists: " + bucketName);
            }
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to create bucket: " + e.getMessage());
        }
    }
}