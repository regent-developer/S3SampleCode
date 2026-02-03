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
import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

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
    private final List<BucketListener> listeners = new ArrayList<>();
    private final List<S3Event> eventHistory = new CopyOnWriteArrayList<>();
    private static final int MAX_EVENT_HISTORY = 100;

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

    // EventType enum
    public enum EventType {
        OBJECT_CREATED, OBJECT_DELETED, OBJECT_MODIFIED
    }

    // S3Event class
    public static class S3Event {
        private final EventType eventType;
        private final String bucket;
        private final String key;
        private final long size;
        private final Instant lastModified;
        private final String eTag;

        public S3Event(EventType eventType, String bucket, String key, long size, Instant lastModified, String eTag) {
            this.eventType = eventType;
            this.bucket = bucket;
            this.key = key;
            this.size = size;
            this.lastModified = lastModified;
            this.eTag = eTag;
        }

        public EventType getEventType() {
            return eventType;
        }

        public String getBucket() {
            return bucket;
        }

        public String getKey() {
            return key;
        }

        public long getSize() {
            return size;
        }

        public Instant getLastModified() {
            return lastModified;
        }

        public String getETag() {
            return eTag;
        }
    }

    // EventHandler functional interface
    @FunctionalInterface
    public interface EventHandler {
        void handle(S3Event event);
    }

    // ErrorHandler functional interface
    @FunctionalInterface
    public interface ErrorHandler {
        void handle(Throwable error);
    }

    // BucketListenerConfig class
    public static class BucketListenerConfig {
        private String bucket;
        private Duration pollInterval = Duration.ofSeconds(5);
        private ErrorHandler errorHandler;
        private EventHandler eventHandler;
        private int maxRetries = 3;
        private Duration retryInterval = Duration.ofSeconds(2);

        public BucketListenerConfig() {
        }

        public String getBucket() {
            return bucket;
        }

        public BucketListenerConfig setBucket(String bucket) {
            this.bucket = bucket;
            return this;
        }

        public Duration getPollInterval() {
            return pollInterval;
        }

        public BucketListenerConfig setPollInterval(Duration pollInterval) {
            this.pollInterval = pollInterval;
            return this;
        }

        public ErrorHandler getErrorHandler() {
            return errorHandler;
        }

        public BucketListenerConfig setErrorHandler(ErrorHandler errorHandler) {
            this.errorHandler = errorHandler;
            return this;
        }

        public EventHandler getEventHandler() {
            return eventHandler;
        }

        public BucketListenerConfig setEventHandler(EventHandler eventHandler) {
            this.eventHandler = eventHandler;
            return this;
        }

        public int getMaxRetries() {
            return maxRetries;
        }

        public BucketListenerConfig setMaxRetries(int maxRetries) {
            this.maxRetries = maxRetries;
            return this;
        }

        public Duration getRetryInterval() {
            return retryInterval;
        }

        public BucketListenerConfig setRetryInterval(Duration retryInterval) {
            this.retryInterval = retryInterval;
            return this;
        }
    }

    // BucketListener class
    public class BucketListener {
        private final S3Service service;
        private final BucketListenerConfig config;
        private final ExecutorService executorService = Executors.newSingleThreadExecutor();
        private final AtomicBoolean running = new AtomicBoolean(true);
        private final Map<String, S3ObjectInfo> lastObjects = new HashMap<>();

        public BucketListener(S3Service service, BucketListenerConfig config) {
            this.service = service;
            this.config = config;
        }

        public void start() {
            executorService.submit(() -> {
                try {
                    run();
                } catch (Exception e) {
                    if (config.getErrorHandler() != null) {
                        config.getErrorHandler().handle(e);
                    } else {
                        e.printStackTrace();
                    }
                }
            });
        }

        public void stop() {
            running.set(false);
            executorService.shutdown();
            try {
                executorService.awaitTermination(5, TimeUnit.SECONDS);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }

        private void run() {
            String bucket = config.getBucket() != null ? config.getBucket() : service.defaultBucketName;

            // Initialize object list
            try {
                List<S3ObjectInfo> initialObjects = listObjects(bucket);
                for (S3ObjectInfo obj : initialObjects) {
                    lastObjects.put(obj.getKey(), obj);
                }
            } catch (Exception e) {
                if (config.getErrorHandler() != null) {
                    config.getErrorHandler().handle(e);
                } else {
                    e.printStackTrace();
                }
            }

            while (running.get()) {
                try {
                    checkForChanges(bucket);
                } catch (Exception e) {
                    int retries = 0;
                    while (retries < config.getMaxRetries() && running.get()) {
                        try {
                            Thread.sleep(config.getRetryInterval().toMillis());
                            checkForChanges(bucket);
                            break;
                        } catch (Exception ex) {
                            retries++;
                            if (retries >= config.getMaxRetries()) {
                                if (config.getErrorHandler() != null) {
                                    config.getErrorHandler().handle(ex);
                                } else {
                                    ex.printStackTrace();
                                }
                            }
                        }
                    }
                }

                try {
                    Thread.sleep(config.getPollInterval().toMillis());
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        }

        private void checkForChanges(String bucket) throws Exception {
            List<S3ObjectInfo> currentObjects = listObjects(bucket);
            Map<String, S3ObjectInfo> currentMap = new HashMap<>();
            for (S3ObjectInfo obj : currentObjects) {
                currentMap.put(obj.getKey(), obj);
            }

            // Check for deleted objects
            for (Map.Entry<String, S3ObjectInfo> entry : lastObjects.entrySet()) {
                String key = entry.getKey();
                if (!currentMap.containsKey(key)) {
                    S3ObjectInfo oldObj = entry.getValue();
                    S3Event event = new S3Event(
                            EventType.OBJECT_DELETED,
                            bucket,
                            key,
                            oldObj.getSize(),
                            oldObj.getLastModified(),
                            oldObj.getETag()
                    );
                    config.getEventHandler().handle(event);
                }
            }

            // Check for created or modified objects
            for (Map.Entry<String, S3ObjectInfo> entry : currentMap.entrySet()) {
                String key = entry.getKey();
                S3ObjectInfo currentObj = entry.getValue();
                if (!lastObjects.containsKey(key)) {
                    // Object created
                    S3Event event = new S3Event(
                            EventType.OBJECT_CREATED,
                            bucket,
                            key,
                            currentObj.getSize(),
                            currentObj.getLastModified(),
                            currentObj.getETag()
                    );
                    config.getEventHandler().handle(event);
                } else {
                    // Check if object was modified
                    S3ObjectInfo oldObj = lastObjects.get(key);
                    if (!oldObj.getETag().equals(currentObj.getETag()) || 
                            oldObj.getLastModified().isBefore(currentObj.getLastModified())) {
                        // Object modified
                        S3Event event = new S3Event(
                                EventType.OBJECT_MODIFIED,
                                bucket,
                                key,
                                currentObj.getSize(),
                                currentObj.getLastModified(),
                                currentObj.getETag()
                        );
                        config.getEventHandler().handle(event);
                    }
                }
            }

            // Update last objects
            lastObjects.clear();
            lastObjects.putAll(currentMap);
        }

        private List<S3ObjectInfo> listObjects(String bucket) throws Exception {
            ListObjectsV2Request request = ListObjectsV2Request.builder()
                    .bucket(bucket)
                    .build();
            ListObjectsV2Response response = service.s3Client.listObjectsV2(request);
            List<S3ObjectInfo> objects = new ArrayList<>();
            for (S3Object object : response.contents()) {
                objects.add(new S3ObjectInfo(
                        object.key(),
                        object.size(),
                        object.lastModified(),
                        object.eTag()
                ));
            }
            return objects;
        }

        private class S3ObjectInfo {
            private final String key;
            private final long size;
            private final Instant lastModified;
            private final String eTag;

            public S3ObjectInfo(String key, long size, Instant lastModified, String eTag) {
                this.key = key;
                this.size = size;
                this.lastModified = lastModified;
                this.eTag = eTag;
            }

            public String getKey() {
                return key;
            }

            public long getSize() {
                return size;
            }

            public Instant getLastModified() {
                return lastModified;
            }

            public String getETag() {
                return eTag;
            }
        }
    }

    /**
     * Start bucket listener
     * 
     * @param config listener configuration
     * @return BucketListener instance
     * @throws Exception if listener fails to start
     */
    public BucketListener startBucketListener(BucketListenerConfig config) throws Exception {
        // Validate configuration
        if (config.getEventHandler() == null) {
            throw new IllegalArgumentException("Event handler is required");
        }

        // Set default error handler if not provided
        if (config.getErrorHandler() == null) {
            config.setErrorHandler(Throwable::printStackTrace);
        }

        // Create and start listener
        BucketListener listener = new BucketListener(this, config);
        listener.start();

        // Add to listeners list
        synchronized (listeners) {
            listeners.add(listener);
        }

        return listener;
    }

    /**
     * Stop all bucket listeners
     */
    public void stopAllListeners() {
        synchronized (listeners) {
            for (BucketListener listener : listeners) {
                listener.stop();
            }
            listeners.clear();
        }
    }

    /**
     * Start a new bucket listener with specified bucket
     * 
     * @param bucket bucket name to listen to
     * @return BucketListener instance
     * @throws Exception if listener fails to start
     */
    public BucketListener startBucketListenerForBucket(String bucket) throws Exception {
        // Create a new listener config
        BucketListenerConfig config = new BucketListenerConfig()
                .setBucket(bucket)
                .setPollInterval(Duration.ofSeconds(5))
                .setEventHandler(event -> {
                    System.out.printf("S3 Event: %s - Bucket: %s, Key: %s, Size: %d, LastModified: %s\n",
                            event.getEventType(), event.getBucket(), event.getKey(), event.getSize(), event.getLastModified());
                    // Record event to history
                    recordEvent(event);
                })
                .setErrorHandler(error -> {
                    System.err.printf("S3 Listener Error: %s\n", error.getMessage());
                    error.printStackTrace();
                });

        // Stop all existing listeners
        stopAllListeners();

        // Start new listener
        return startBucketListener(config);
    }

    /**
     * Record event to history
     * 
     * @param event S3 event to record
     */
    public void recordEvent(S3Event event) {
        eventHistory.add(0, event); // Add to beginning of list
        if (eventHistory.size() > MAX_EVENT_HISTORY) {
            eventHistory.remove(eventHistory.size() - 1); // Remove oldest event
        }
    }

    /**
     * Get event history
     * 
     * @return list of recent S3 events
     */
    public List<S3Event> getEventHistory() {
        return eventHistory;
    }

    /**
     * Clear event history
     */
    public void clearEventHistory() {
        eventHistory.clear();
    }
}