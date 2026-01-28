package com.example.s3service.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.core.ResponseBytes;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.*;

import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import java.util.Optional;

/**
 * S3 Service Implementation Class
 * 
 * @author KO
 * @since 2026-01-19
 */
@Service
public class S3Service {

    @Value("${s3.bucket}")
    private String defaultBucketName;

    private final S3Client s3Client;

    /**
     * Constructor with S3Client dependency injection
     * 
     * @param s3Client configured S3Client
     */
    public S3Service(S3Client s3Client) {
        this.s3Client = s3Client;
    }

    /**
     * Upload file to S3 bucket
     * 
     * @param file MultipartFile to upload
     * @param key  S3 object key
     * @param bucketName name of the bucket to use, if null use default bucket
     * @return uploaded file key
     * @throws IOException if file upload fails
     */
    public String uploadFile(MultipartFile file, String key, String bucketName) throws IOException {
        String bucket = bucketName != null ? bucketName : defaultBucketName;
        try (InputStream inputStream = file.getInputStream()) {
            PutObjectRequest putObjectRequest = PutObjectRequest.builder()
                    .bucket(bucket)
                    .key(key)
                    .contentType(file.getContentType())
                    .contentLength(file.getSize())
                    .build();

            s3Client.putObject(putObjectRequest, RequestBody.fromInputStream(inputStream, file.getSize()));
            return key;
        }
    }

    /**
     * Download file from S3 bucket
     * 
     * @param key S3 object key
     * @param bucketName name of the bucket to use, if null use default bucket
     * @return ResponseBytes containing file content
     */
    public ResponseBytes<GetObjectResponse> downloadFile(String key, String bucketName) {
        String bucket = bucketName != null ? bucketName : defaultBucketName;
        GetObjectRequest getObjectRequest = GetObjectRequest.builder()
                .bucket(bucket)
                .key(key)
                .build();

        return s3Client.getObjectAsBytes(getObjectRequest);
    }

    /**
     * Delete file from S3 bucket
     * 
     * @param key S3 object key
     * @param bucketName name of the bucket to use, if null use default bucket
     */
    public void deleteFile(String key, String bucketName) {
        String bucket = bucketName != null ? bucketName : defaultBucketName;
        DeleteObjectRequest deleteObjectRequest = DeleteObjectRequest.builder()
                .bucket(bucket)
                .key(key)
                .build();

        s3Client.deleteObject(deleteObjectRequest);
    }

    /**
     * Check if file exists in S3 bucket
     * 
     * @param key S3 object key
     * @param bucketName name of the bucket to use, if null use default bucket
     * @return true if file exists, false otherwise
     */
    public boolean fileExists(String key, String bucketName) {
        String bucket = bucketName != null ? bucketName : defaultBucketName;
        try {
            HeadObjectRequest headObjectRequest = HeadObjectRequest.builder()
                    .bucket(bucket)
                    .key(key)
                    .build();

            s3Client.headObject(headObjectRequest);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Get file metadata from S3 bucket
     * 
     * @param key S3 object key
     * @param bucketName name of the bucket to use, if null use default bucket
     * @return Optional containing HeadObjectResponse if file exists, empty otherwise
     */
    public Optional<HeadObjectResponse> getFileMetadata(String key, String bucketName) {
        String bucket = bucketName != null ? bucketName : defaultBucketName;
        try {
            HeadObjectRequest headObjectRequest = HeadObjectRequest.builder()
                    .bucket(bucket)
                    .key(key)
                    .build();

            HeadObjectResponse response = s3Client.headObject(headObjectRequest);
            return Optional.of(response);
        } catch (NoSuchKeyException e) {
            return Optional.empty();
        }
    }

    /**
     * List all files in S3 bucket
     * 
     * @param bucketName name of the bucket to use, if null use default bucket
     * @return List of S3 object keys
     */
    public ListObjectsV2Response listFiles(String bucketName) {
        String bucket = bucketName != null ? bucketName : defaultBucketName;
        ListObjectsV2Request listObjectsRequest = ListObjectsV2Request.builder()
                .bucket(bucket)
                .build();

        return s3Client.listObjectsV2(listObjectsRequest);
    }
    
    /**
     * List all S3 buckets
     * 
     * @return List of S3 bucket names
     */
    public List<Bucket> listBuckets() {
        ListBucketsRequest listBucketsRequest = ListBucketsRequest.builder().build();
        return s3Client.listBuckets(listBucketsRequest).buckets();
    }
    
    /**
     * Create a new S3 bucket
     * 
     * @param bucketName name of the bucket to create
     * @return true if bucket was created successfully, false if bucket already exists
     */
    public boolean createBucket(String bucketName) {
        try {
            // Check if bucket already exists
            if (doesBucketExist(bucketName)) {
                return false;
            }
            
            CreateBucketRequest createBucketRequest = CreateBucketRequest.builder()
                    .bucket(bucketName)
                    .build();
            
            s3Client.createBucket(createBucketRequest);
            return true;
        } catch (Exception e) {
            throw e;
        }
    }
    
    /**
     * Check if a bucket exists
     * 
     * @param bucketName name of the bucket to check
     * @return true if bucket exists, false otherwise
     */
    public boolean doesBucketExist(String bucketName) {
        try {
            HeadBucketRequest headBucketRequest = HeadBucketRequest.builder()
                    .bucket(bucketName)
                    .build();
            
            s3Client.headBucket(headBucketRequest);
            return true;
        } catch (NoSuchBucketException e) {
            return false;
        } catch (Exception e) {
            throw e;
        }
    }
}