package com.example.s3test;

import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.*;

import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.UUID;

/**
 * S3 Test Application
 * 
 * 作者：KO
 * 创建时间：2026-01-20
 * 修改时间：2026-01-27
 * 
 * 功能：
 * 1. 上传测试文件到S3存储桶
 * 2. 检查文件是否存在于S3存储桶
 * 3. 从S3存储桶删除文件
 * 4. 检查文件是否不再存在于S3存储桶
 * 
 * 命令行用法：
 * - java -jar <jar-file> upload <filename> <content> - 上传文件
 * - java -jar <jar-file> delete <filename> - 删除文件
 * - java -jar <jar-file> exists <filename> - 检查文件是否存在
 */
public class S3TestApplication {

    // S3 Configuration
    private static final String ENDPOINT = "http://localhost:9000/";
    private static final String BUCKET = "test-bucket";
    private static final String REGION = "us-east-1";
    private static final String ACCESS_KEY = "minioadmin";
    private static final String SECRET_KEY = "minioadmin";

    public static void main(String[] args) {
        // Create S3 client
        S3Client s3Client = createS3Client();

        try {
            // Check if command line arguments are provided
            if (args.length < 1) {
                System.out.println("=== S3 Test Application ===");
                System.out.println("Testing S3 delete and file existence check functionality");
                System.out.println();
                runTestFlow(s3Client);
                return;
            }

            // Parse command line arguments
            String command = args[0];
            
            switch (command) {
                case "upload":
                    if (args.length < 3) {
                        System.out.println("Usage: java -jar <jar-file> upload <filename> <content>");
                        break;
                    }
                    String uploadFileName = args[1];
                    String uploadContent = args[2];
                    uploadFile(s3Client, uploadFileName, uploadContent);
                    System.out.println("✓ File uploaded successfully: " + uploadFileName);
                    break;
                
                case "delete":
                    if (args.length < 2) {
                        System.out.println("Usage: java -jar <jar-file> delete <filename>");
                        break;
                    }
                    String deleteFileName = args[1];
                    deleteFile(s3Client, deleteFileName);
                    System.out.println("✓ File deleted successfully: " + deleteFileName);
                    break;
                
                case "exists":
                    if (args.length < 2) {
                        System.out.println("Usage: java -jar <jar-file> exists <filename>");
                        break;
                    }
                    String existsFileName = args[1];
                    boolean exists = existsFile(s3Client, existsFileName);
                    System.out.println("File '" + existsFileName + "' " + (exists ? "exists" : "does not exist"));
                    break;
                
                default:
                    System.out.println("Unknown command: " + command);
                    System.out.println("Available commands: upload, delete, exists");
                    break;
            }
        } catch (Exception e) {
            System.err.println("✗ An error occurred: " + e.getMessage());
        } finally {
            // Close the S3 client
            if (s3Client != null) {
                s3Client.close();
            }
            System.out.println();
            System.out.println("=== Application Complete ===");
        }
    }

    /**
     * Run the original test flow
     * 
     * @param s3Client configured S3Client
     */
    private static void runTestFlow(S3Client s3Client) {
        try {
            // Use a fixed test file name instead of random generated name
            String testFileName = "test1.csv";
            String testContent = "This is a test file for S3 delete and existence check functionality.";

            System.out.println("1. Uploading test file: " + testFileName);
            uploadFile(s3Client, testFileName, testContent);
            System.out.println("   ✓ Test file uploaded successfully");
            System.out.println();

            System.out.println("2. Checking if file exists: " + testFileName);
            boolean existsBeforeDelete = existsFile(s3Client, testFileName);
            System.out.println("   ✓ File existence check completed");
            System.out.println("   - Result: " + (existsBeforeDelete ? "File exists" : "File does not exist"));
            System.out.println();

            System.out.println("3. Deleting test file: " + testFileName);
            deleteFile(s3Client, testFileName);
            System.out.println("   ✓ Test file deleted successfully");
            System.out.println();

            System.out.println("4. Checking if file exists after deletion: " + testFileName);
            boolean existsAfterDelete = existsFile(s3Client, testFileName);
            System.out.println("   ✓ File existence check completed");
            System.out.println("   - Result: " + (existsAfterDelete ? "File exists" : "File does not exist"));
            System.out.println();

            // Verify results
            System.out.println("=== Test Results ===");
            if (existsBeforeDelete && !existsAfterDelete) {
                System.out.println("✓ ALL TESTS PASSED!");
                System.out.println("   - File was successfully uploaded");
                System.out.println("   - File existence check worked correctly before deletion");
                System.out.println("   - File was successfully deleted");
                System.out.println("   - File existence check worked correctly after deletion");
            } else {
                System.out.println("✗ TESTS FAILED!");
                System.out.println("   - Expected: File should exist before deletion and not exist after deletion");
                System.out.println("   - Actual: Before deletion: " + (existsBeforeDelete ? "exists" : "does not exist"));
                System.out.println("   - Actual: After deletion: " + (existsAfterDelete ? "exists" : "does not exist"));
            }
        } catch (Exception e) {
            System.err.println("✗ An error occurred during testing: ");
            e.printStackTrace();
        }
    }

    /**
     * Create and configure S3 client
     * 
     * @return configured S3Client
     */
    private static S3Client createS3Client() {
        System.out.println("Initializing S3 client...");
        System.out.println("   Endpoint: " + ENDPOINT);
        System.out.println("   Bucket: " + BUCKET);
        System.out.println("   Region: " + REGION);

        AwsBasicCredentials credentials = AwsBasicCredentials.create(ACCESS_KEY, SECRET_KEY);
        StaticCredentialsProvider credentialsProvider = StaticCredentialsProvider.create(credentials);

        return S3Client.builder()
                .credentialsProvider(credentialsProvider)
                .region(Region.of(REGION))
                .endpointOverride(URI.create(ENDPOINT))
                .forcePathStyle(true)
                .build();
    }

    /**
     * Upload a file to S3 bucket
     * 
     * @param s3Client     configured S3Client
     * @param fileName     name of the file to upload
     * @param fileContent  content of the file
     */
    private static void uploadFile(S3Client s3Client, String fileName, String fileContent) {
        PutObjectRequest putObjectRequest = PutObjectRequest.builder()
                .bucket(BUCKET)
                .key(fileName)
                .contentType("text/plain")
                .contentLength((long) fileContent.getBytes(StandardCharsets.UTF_8).length)
                .build();

        s3Client.putObject(putObjectRequest, RequestBody.fromString(fileContent));
    }

    /**
     * Check if a file exists in S3 bucket
     * 
     * @param s3Client  configured S3Client
     * @param fileName  name of the file to check
     * @return true if file exists, false otherwise
     */
    private static boolean existsFile(S3Client s3Client, String fileName) {
        try {
            HeadObjectRequest headObjectRequest = HeadObjectRequest.builder()
                    .bucket(BUCKET)
                    .key(fileName)
                    .build();

            s3Client.headObject(headObjectRequest);
            return true;
        } catch (NoSuchKeyException e) {
            return false;
        } catch (Exception e) {
            System.err.println("   ✗ Error checking file existence: " + e.getMessage());
            return false;
        }
    }

    /**
     * Delete a file from S3 bucket
     * 
     * @param s3Client  configured S3Client
     * @param fileName  name of the file to delete
     */
    private static void deleteFile(S3Client s3Client, String fileName) {
        DeleteObjectRequest deleteObjectRequest = DeleteObjectRequest.builder()
                .bucket(BUCKET)
                .key(fileName)
                .build();

        s3Client.deleteObject(deleteObjectRequest);
    }
}