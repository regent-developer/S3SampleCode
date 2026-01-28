package com.example.s3service.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.S3ClientBuilder;
import software.amazon.awssdk.utils.AttributeMap;

import java.net.URI;

/**
 * S3 Client Configuration Class
 * 
 * @author KO
 * @since 2026-01-19
 */
@Configuration
public class S3Config {

    @Value("${s3.endpoint}")
    private String endpoint;

    @Value("${s3.region}")
    private String region;

    @Value("${s3.access-key}")
    private String accessKey;

    @Value("${s3.secret-key}")
    private String secretKey;

    @Value("${s3.path-style-access-enabled}")
    private boolean pathStyleAccessEnabled;

    /**
     * Create and configure S3Client Bean
     * 
     * @return configured S3Client
     */
    @Bean
    public S3Client s3Client() {
        AwsBasicCredentials awsCredentials = AwsBasicCredentials.create(accessKey, secretKey);
        StaticCredentialsProvider credentialsProvider = StaticCredentialsProvider.create(awsCredentials);

        S3ClientBuilder builder = S3Client.builder()
                .credentialsProvider(credentialsProvider)
                .region(Region.of(region))
                .endpointOverride(URI.create(endpoint));

        if (pathStyleAccessEnabled) {
            builder.forcePathStyle(true);
        }

        return builder.build();
    }
}