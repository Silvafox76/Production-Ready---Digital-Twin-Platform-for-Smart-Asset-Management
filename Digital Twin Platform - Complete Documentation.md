# Digital Twin Platform - Complete Documentation

**Author:** Manus AI  
**Version:** 1.0.0  
**Date:** July 13, 2025

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Installation and Setup](#installation-and-setup)
5. [API Documentation](#api-documentation)
6. [Frontend Components](#frontend-components)
7. [Machine Learning Models](#machine-learning-models)
8. [Database Schema](#database-schema)
9. [Deployment Guide](#deployment-guide)
10. [Monitoring and Observability](#monitoring-and-observability)
11. [Security Considerations](#security-considerations)
12. [Performance Optimization](#performance-optimization)
13. [Testing Strategy](#testing-strategy)
14. [Maintenance and Operations](#maintenance-and-operations)
15. [Troubleshooting Guide](#troubleshooting-guide)
16. [Future Enhancements](#future-enhancements)

## Executive Summary

The Digital Twin Platform represents a comprehensive, production-ready solution for smart asset management, specifically designed for industries managing physical infrastructure such as HVAC systems, utilities, and public works. This platform leverages cutting-edge technologies including Internet of Things (IoT) sensors, machine learning algorithms, 3D visualization capabilities, and modern DevOps practices to deliver real-time monitoring, predictive maintenance, and AI-driven optimization recommendations.

The platform addresses critical challenges in asset management by providing organizations with the ability to predict equipment failures before they occur, visualize sensor data through interactive 3D building models, receive intelligent recommendations for energy savings, and enable both edge computing and offline inference capabilities. The system is built with scalability, reliability, and security as core principles, ensuring it can grow with organizational needs while maintaining high availability and protecting sensitive operational data.

At its core, the Digital Twin Platform serves three primary user personas: technicians who need to fix problems based on predictive alerts, operations managers who plan maintenance schedules and reduce operational costs, and engineers who update machine learning models and monitor data pipelines. Each persona benefits from tailored interfaces and functionality that streamline their specific workflows and decision-making processes.

The platform's architecture follows modern microservices principles, with containerized components that can be deployed across various environments from development to production. The system includes comprehensive monitoring, logging, and alerting capabilities that provide deep insights into both the managed assets and the platform's own operational health. This documentation serves as a complete guide for understanding, deploying, and maintaining the Digital Twin Platform in production environments.




## System Architecture

The Digital Twin Platform employs a sophisticated multi-layered architecture designed to handle real-time data processing, machine learning inference, and interactive visualization at scale. The architecture follows microservices principles with clear separation of concerns, enabling independent scaling and maintenance of different system components.

### High-Level Architecture Overview

The system architecture can be conceptualized as a data flow pipeline that begins with edge devices and sensors, progresses through various processing and storage layers, and culminates in user-facing interfaces and visualization components. This design ensures that data flows efficiently from physical assets to actionable insights while maintaining high availability and fault tolerance.

```
[Edge Devices/Sensors] --> [MQTT Broker / AWS IoT] --> [Data Pipeline (Kafka/Flink)]
                                                              ↓
[Edge Inference] <-- [Cloud ML Model Inference] <-- [Digital Twin Engine]
                                                              ↓
[3D Visualization (WebGL)] <-- [API Gateway / GraphQL / REST] --> [User Portal]
                                                              ↓
                                                        [Asset Database]
```

### Core Components

#### Edge Layer
The edge layer consists of physical sensors and IoT devices deployed on assets such as HVAC units, pumps, and motors. These devices collect telemetry data including temperature, humidity, pressure, vibration, and power consumption metrics. The edge devices communicate using MQTT protocol, which provides lightweight, reliable messaging suitable for IoT environments with potentially unstable network connections.

Edge devices are configured to publish data to specific MQTT topics following a hierarchical naming convention that enables efficient routing and filtering. For example, telemetry data from HVAC Unit 1 would be published to the topic `assets/telemetry/hvac_unit_1`. This structure allows for granular subscription patterns and efficient data distribution to interested consumers.

#### Message Broker Layer
The MQTT broker serves as the central communication hub for all IoT device communications. The platform supports both Eclipse Mosquitto for on-premises deployments and AWS IoT Core for cloud-based implementations. The broker handles message routing, quality of service guarantees, and connection management for potentially thousands of concurrent device connections.

The broker is configured with appropriate security measures including TLS encryption, client certificate authentication, and access control lists that restrict device access to specific topics based on device identity and authorization levels. This ensures that devices can only publish data to their designated topics and cannot access data from other assets.

#### Data Processing Pipeline
The data processing pipeline is responsible for ingesting, transforming, and routing telemetry data from the MQTT broker to various downstream consumers. The pipeline is built using Apache Kafka for high-throughput message streaming and Apache Flink for real-time stream processing, though the current implementation includes a simplified version using FastAPI and WebSocket connections for real-time data distribution.

The pipeline performs several critical functions including data validation, format normalization, timestamp synchronization, and routing to appropriate storage and processing systems. It also implements backpressure handling to manage situations where downstream systems cannot keep pace with incoming data volumes.

#### Machine Learning Engine
The ML engine consists of multiple components working together to provide predictive analytics and anomaly detection capabilities. The engine includes model training pipelines, inference services, and model management systems that ensure models remain accurate and up-to-date as system conditions change.

The platform implements several types of machine learning models including time series forecasting for predictive maintenance, anomaly detection for identifying unusual operating conditions, and optimization models for energy efficiency recommendations. Models are trained using historical telemetry data and continuously updated as new data becomes available.

#### Database Layer
The database layer utilizes PostgreSQL with the TimescaleDB extension to provide efficient storage and querying of time-series telemetry data. This combination offers the reliability and ACID properties of PostgreSQL while providing specialized time-series capabilities such as automatic partitioning, data retention policies, and optimized queries for temporal data.

The database schema is designed to support both real-time queries for dashboard displays and analytical queries for machine learning model training. Continuous aggregates are used to pre-compute common metrics at various time intervals, significantly improving query performance for dashboard and reporting use cases.

#### API Gateway
The API gateway provides a unified interface for all client applications to interact with the platform's services. Built using FastAPI, the gateway offers both REST and WebSocket endpoints, comprehensive request validation, authentication and authorization, rate limiting, and detailed logging of all API interactions.

The gateway implements a microservices architecture pattern where different functional areas are organized into logical service boundaries. This design enables independent development, testing, and deployment of different platform capabilities while maintaining a consistent external interface.

#### Frontend Layer
The frontend layer consists of a React-based single-page application that provides interactive dashboards, 3D visualizations, and administrative interfaces. The frontend communicates with the backend through both REST API calls for standard operations and WebSocket connections for real-time data updates.

The 3D visualization component uses Three.js to render interactive building models with real-time sensor data overlays. This provides users with an intuitive spatial understanding of asset locations and current operating conditions, making it easier to identify patterns and respond to alerts.

### Data Flow Architecture

The platform's data flow follows a clear path from data generation to user consumption, with multiple processing stages that add value and ensure data quality. Understanding this flow is crucial for troubleshooting, optimization, and extending the platform's capabilities.

#### Ingestion Phase
Data ingestion begins when IoT sensors collect measurements from physical assets and publish them to the MQTT broker. The platform supports various sensor types and communication protocols, with MQTT serving as the primary integration point. Sensors are configured to publish data at regular intervals, typically every 30 seconds to 5 minutes depending on the asset type and monitoring requirements.

The MQTT client within the platform subscribes to relevant topics and receives telemetry data as it becomes available. Each message is validated for proper format, completeness, and authenticity before being accepted into the system. Invalid or suspicious messages are logged and discarded to prevent data corruption or security issues.

#### Processing Phase
Once telemetry data is ingested, it enters the processing phase where multiple operations occur in parallel. The data is first stored in the time-series database for historical analysis and reporting. Simultaneously, it is forwarded to the machine learning engine for real-time inference and anomaly detection.

The processing phase also includes data enrichment activities such as adding asset metadata, calculating derived metrics, and applying business rules for alert generation. For example, if a temperature reading exceeds predefined thresholds, the system automatically generates an alert and notifies relevant personnel.

#### Distribution Phase
The final phase involves distributing processed data and insights to end users through various channels. Real-time data is pushed to connected dashboard clients via WebSocket connections, ensuring that users see current conditions without needing to refresh their browsers. Historical data and analytics are made available through REST API endpoints that support various query patterns and filtering options.

Alerts and notifications are distributed through multiple channels including in-application notifications, email alerts, and integration with external systems such as maintenance management platforms or enterprise resource planning systems.

### Scalability Considerations

The platform architecture is designed to scale horizontally across multiple dimensions to accommodate growing numbers of assets, users, and data volumes. Key scalability features include stateless service design, database partitioning, caching strategies, and load balancing capabilities.

The microservices architecture enables independent scaling of different platform components based on their specific resource requirements and usage patterns. For example, the machine learning inference service can be scaled separately from the web API service, allowing for optimal resource allocation based on actual demand patterns.

Database scalability is achieved through TimescaleDB's automatic partitioning capabilities, which distribute data across multiple chunks based on time intervals. This approach ensures that query performance remains consistent even as data volumes grow to terabytes or petabytes of historical telemetry data.

### Security Architecture

Security is implemented as a multi-layered approach that protects data at rest, in transit, and during processing. The architecture includes network security, application security, data security, and operational security measures that work together to provide comprehensive protection against various threat vectors.

Network security is implemented through virtual private clouds, firewalls, and network segmentation that isolate different system components and limit potential attack surfaces. All communications between components use encrypted channels with mutual authentication to prevent eavesdropping and man-in-the-middle attacks.

Application security includes input validation, output encoding, authentication and authorization controls, and secure coding practices that prevent common vulnerabilities such as SQL injection, cross-site scripting, and privilege escalation attacks.


## Technology Stack

The Digital Twin Platform leverages a carefully selected technology stack that balances performance, scalability, maintainability, and developer productivity. Each technology choice has been made based on specific requirements and proven track records in production environments.

### Backend Technologies

#### FastAPI Framework
FastAPI serves as the primary web framework for the platform's backend services. This modern Python framework was chosen for its exceptional performance characteristics, automatic API documentation generation, built-in data validation using Pydantic models, and native support for asynchronous programming patterns that are essential for real-time applications.

FastAPI's automatic OpenAPI schema generation ensures that API documentation remains synchronized with the actual implementation, reducing maintenance overhead and improving developer experience. The framework's dependency injection system enables clean separation of concerns and facilitates comprehensive testing strategies.

The framework's performance characteristics are particularly important for the Digital Twin Platform, as it needs to handle high-frequency telemetry data ingestion while simultaneously serving dashboard requests and running machine learning inference. FastAPI's async/await support allows the platform to handle thousands of concurrent connections efficiently without blocking operations.

#### PostgreSQL with TimescaleDB
The database layer combines PostgreSQL's reliability and feature richness with TimescaleDB's specialized time-series capabilities. PostgreSQL provides ACID compliance, advanced indexing options, full-text search, and a rich ecosystem of extensions that support the platform's diverse data storage requirements.

TimescaleDB extends PostgreSQL with automatic partitioning for time-series data, continuous aggregates for pre-computed analytics, data retention policies for managing storage costs, and optimized query performance for temporal queries. This combination enables the platform to efficiently store and query billions of telemetry data points while maintaining sub-second response times for dashboard queries.

The database schema utilizes PostgreSQL's advanced features including JSONB columns for flexible metadata storage, foreign key constraints for data integrity, and partial indexes for optimized query performance. TimescaleDB's continuous aggregates are used to pre-compute hourly and daily statistics, significantly improving dashboard loading times.

#### Redis Cache
Redis serves as the platform's primary caching layer and session store, providing sub-millisecond response times for frequently accessed data. The cache is used to store user sessions, API response caches, real-time asset status information, and temporary data structures used by the machine learning pipeline.

Redis's data structure support enables sophisticated caching strategies including sorted sets for time-ordered data, hash maps for structured data, and pub/sub channels for real-time notifications. The platform leverages Redis's atomic operations to implement distributed locks and counters that coordinate activities across multiple service instances.

#### MQTT with Eclipse Mosquitto
MQTT (Message Queuing Telemetry Transport) provides the communication backbone for IoT device integration. Eclipse Mosquitto serves as the MQTT broker, handling message routing, quality of service guarantees, and connection management for potentially thousands of concurrent device connections.

The MQTT implementation includes comprehensive security features such as TLS encryption, client certificate authentication, and topic-based access control lists. The broker is configured with appropriate quality of service levels to balance reliability with performance based on message criticality.

### Frontend Technologies

#### React with TypeScript
The frontend application is built using React 18 with TypeScript, providing a modern, component-based architecture that enables rapid development and maintenance of complex user interfaces. React's virtual DOM and efficient reconciliation algorithms ensure smooth performance even when displaying real-time data updates from hundreds of assets.

TypeScript adds static type checking that catches errors at compile time, improves code maintainability, and enhances developer productivity through better IDE support and refactoring capabilities. The type system is particularly valuable for the Digital Twin Platform given its complex data structures and real-time data flows.

The React application uses modern hooks-based patterns for state management, effect handling, and component lifecycle management. Custom hooks encapsulate complex logic for WebSocket connections, data fetching, and real-time updates, promoting code reuse and testability.

#### Three.js for 3D Visualization
Three.js provides the 3D rendering capabilities that enable interactive building visualizations with real-time sensor data overlays. The library's WebGL-based rendering engine delivers high-performance 3D graphics that run smoothly in web browsers without requiring additional plugins or installations.

The 3D visualization system includes features such as interactive camera controls, dynamic object highlighting based on asset status, real-time data overlays, and smooth animations for state transitions. The implementation uses Three.js's scene graph architecture to efficiently manage complex 3D models with hundreds of interactive elements.

Performance optimization techniques include level-of-detail rendering, frustum culling, and texture atlasing to ensure smooth frame rates even on lower-end devices. The 3D models are optimized for web delivery using compressed formats and progressive loading strategies.

#### TailwindCSS for Styling
TailwindCSS provides a utility-first CSS framework that enables rapid UI development while maintaining design consistency across the application. The framework's approach of composing designs from small, reusable utility classes reduces CSS bundle sizes and eliminates many common styling issues.

The platform's design system is built on top of TailwindCSS's configuration system, defining custom color palettes, spacing scales, and component variants that reflect the platform's visual identity. This approach ensures consistent styling while allowing for easy customization and theming.

### Machine Learning Technologies

#### Scikit-learn
Scikit-learn serves as the primary machine learning library for the platform's predictive analytics capabilities. The library provides a comprehensive set of algorithms for classification, regression, clustering, and dimensionality reduction, along with utilities for model evaluation, cross-validation, and hyperparameter tuning.

The platform implements several types of models using scikit-learn including Random Forest classifiers for failure prediction, Support Vector Machines for anomaly detection, and Linear Regression models for energy consumption forecasting. The library's consistent API design enables easy experimentation with different algorithms and model architectures.

#### NumPy and Pandas
NumPy provides the foundational array computing capabilities that underpin all numerical operations in the platform. Its efficient array operations and mathematical functions enable fast processing of large telemetry datasets during both training and inference phases.

Pandas builds on NumPy to provide high-level data manipulation and analysis capabilities. The platform uses Pandas for data preprocessing, feature engineering, time series analysis, and result aggregation. Pandas' DataFrame abstraction provides an intuitive interface for working with structured telemetry data while maintaining high performance for large datasets.

### DevOps and Infrastructure Technologies

#### Docker and Docker Compose
Docker containerization ensures consistent deployment environments across development, testing, and production systems. Each platform component is packaged as a Docker container with all necessary dependencies, eliminating "works on my machine" issues and simplifying deployment processes.

Docker Compose orchestrates multi-container deployments for development and testing environments, defining service dependencies, network configurations, and volume mounts in declarative YAML files. This approach enables developers to spin up complete platform environments with a single command.

The containerization strategy includes multi-stage builds for optimized image sizes, non-root user configurations for security, health checks for monitoring container status, and proper signal handling for graceful shutdowns.

#### Prometheus and Grafana
Prometheus provides comprehensive metrics collection and alerting capabilities for the platform's monitoring infrastructure. The system collects metrics from all platform components including application performance metrics, system resource utilization, and business metrics such as asset health scores and energy consumption.

Grafana complements Prometheus by providing rich visualization capabilities for metrics data. The platform includes pre-configured dashboards for system monitoring, asset performance tracking, and operational analytics. Grafana's alerting capabilities enable proactive notification of system issues and asset anomalies.

The monitoring stack includes custom metrics that provide insights into platform-specific operations such as MQTT message processing rates, machine learning inference latency, and WebSocket connection counts. These metrics enable data-driven optimization and capacity planning decisions.

### Development and Testing Technologies

#### Pytest
Pytest serves as the primary testing framework for the platform's Python components. The framework's fixture system enables efficient test setup and teardown, while its plugin ecosystem provides specialized testing capabilities for async code, database interactions, and API testing.

The testing strategy includes unit tests for individual functions and classes, integration tests for component interactions, and end-to-end tests for complete user workflows. Test coverage metrics ensure that critical code paths are thoroughly tested, while property-based testing validates edge cases and error conditions.

#### GitHub Actions
GitHub Actions provides continuous integration and deployment capabilities that automate testing, building, and deployment processes. The CI/CD pipeline includes automated testing on multiple Python versions, security scanning, code quality checks, and automated deployment to staging environments.

The deployment pipeline implements blue-green deployment strategies that minimize downtime during updates, while automated rollback capabilities ensure rapid recovery from deployment issues. Integration with monitoring systems enables automatic detection of deployment-related issues.

### Security Technologies

#### TLS/SSL Encryption
All network communications are protected using TLS encryption with modern cipher suites and perfect forward secrecy. The platform implements certificate-based authentication for service-to-service communications and supports both self-signed certificates for development and CA-signed certificates for production deployments.

#### JWT Authentication
JSON Web Tokens provide stateless authentication for API access, enabling horizontal scaling without session affinity requirements. The JWT implementation includes appropriate expiration times, refresh token mechanisms, and secure signing algorithms that prevent token tampering.

#### Environment-based Configuration
Sensitive configuration data such as database passwords, API keys, and encryption keys are managed through environment variables and secrets management systems. This approach prevents accidental exposure of sensitive data in source code repositories while enabling different configurations for different deployment environments.

The configuration system includes validation logic that ensures all required settings are present and properly formatted before application startup, preventing runtime failures due to configuration errors. Default values are provided for non-sensitive settings to simplify deployment processes.


## Installation and Setup

This section provides comprehensive instructions for setting up the Digital Twin Platform in various environments, from local development to production deployment. The platform supports multiple deployment scenarios to accommodate different organizational needs and infrastructure constraints.

### Prerequisites

Before installing the Digital Twin Platform, ensure that your system meets the following requirements:

**Hardware Requirements:**
- Minimum 8GB RAM (16GB recommended for production)
- 4 CPU cores (8 cores recommended for production)
- 100GB available disk space (500GB recommended for production)
- Network connectivity for external dependencies

**Software Requirements:**
- Docker 20.10 or later
- Docker Compose 2.0 or later
- Git for source code management
- Make utility for build automation (optional but recommended)

**Network Requirements:**
- Outbound internet access for downloading dependencies
- Inbound access on configured ports (default: 80, 8000, 1883, 5432, 6379)
- MQTT broker accessibility for IoT device connections

### Quick Start Guide

The fastest way to get the Digital Twin Platform running is using the provided Docker Compose configuration. This approach sets up all necessary services with sensible defaults for evaluation and development purposes.

1. **Clone the Repository**
```bash
git clone https://github.com/your-org/digital-twin-platform.git
cd digital-twin-platform
```

2. **Configure Environment Variables**
```bash
cp .env.example .env
# Edit .env file with your specific configuration
```

3. **Start the Platform**
```bash
make dev
# Or alternatively: docker-compose -f infra/docker/docker-compose.dev.yml up -d
```

4. **Verify Installation**
```bash
# Check service status
docker-compose ps

# View logs
make dev-logs

# Access the platform
open http://localhost:3000
```

The quick start configuration includes all necessary services running in Docker containers with persistent data storage and automatic service discovery. This setup is ideal for development, testing, and evaluation purposes.

### Development Environment Setup

For developers who need to modify the platform code, a development environment provides additional tools and configurations that facilitate debugging, testing, and iterative development.

#### Backend Development Setup

1. **Install Python Dependencies**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Development Database**
```bash
# Start only the database services
docker-compose -f infra/docker/docker-compose.dev.yml up -d postgres redis mosquitto

# Run database migrations
python db/migrations.py
```

3. **Start Development Server**
```bash
# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/digital_twin_dev"
export REDIS_URL="redis://localhost:6379/0"
export MQTT_BROKER_HOST="localhost"

# Start the FastAPI development server
uvicorn app_enhanced:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development Setup

1. **Install Node.js Dependencies**
```bash
cd frontend
npm install
# Or using pnpm: pnpm install
```

2. **Configure Environment Variables**
```bash
# Create .env.local file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
echo "VITE_WS_URL=ws://localhost:8000" >> .env.local
```

3. **Start Development Server**
```bash
npm run dev
# Or using pnpm: pnpm dev
```

The development servers include hot reloading capabilities that automatically restart when code changes are detected, significantly speeding up the development cycle.

### Production Environment Setup

Production deployments require additional considerations for security, performance, monitoring, and reliability. The platform provides production-ready configurations that implement best practices for enterprise environments.

#### Infrastructure Preparation

1. **Server Provisioning**
   - Provision servers or cloud instances meeting hardware requirements
   - Configure operating system with latest security updates
   - Install Docker and Docker Compose
   - Configure firewall rules for required ports
   - Set up SSL certificates for HTTPS access

2. **Network Configuration**
   - Configure load balancers for high availability
   - Set up DNS records for platform domains
   - Configure network security groups or firewalls
   - Establish VPN or private network connectivity if required

3. **Storage Configuration**
   - Configure persistent storage volumes for database data
   - Set up backup storage for disaster recovery
   - Configure log aggregation and retention policies
   - Implement monitoring for disk space and performance

#### Production Deployment

1. **Environment Configuration**
```bash
# Copy and customize production environment file
cp .env.example .env.production

# Configure production-specific settings
# - Strong passwords and secrets
# - Production database URLs
# - SSL certificate paths
# - Monitoring endpoints
# - Email/SMS notification settings
```

2. **Deploy Platform Services**
```bash
# Build production images
make build

# Deploy to production
docker-compose -f infra/docker/docker-compose.prod.yml up -d

# Verify deployment
make prod-logs
```

3. **Initialize Database**
```bash
# Run database migrations
docker-compose -f infra/docker/docker-compose.prod.yml exec backend python db/migrations.py

# Load initial data (optional)
docker-compose -f infra/docker/docker-compose.prod.yml exec backend python scripts/load_sample_data.py
```

#### Security Hardening

Production deployments should implement additional security measures:

1. **Network Security**
   - Enable firewall with minimal required ports
   - Use TLS encryption for all communications
   - Implement network segmentation between services
   - Configure intrusion detection systems

2. **Application Security**
   - Change all default passwords and secrets
   - Enable authentication for all services
   - Configure rate limiting and DDoS protection
   - Implement security headers and CORS policies

3. **Data Security**
   - Enable database encryption at rest
   - Configure automated backups with encryption
   - Implement access logging and audit trails
   - Set up data retention and deletion policies

### Configuration Management

The platform uses environment variables for configuration management, enabling different settings for different deployment environments without code changes.

#### Core Configuration Options

**Database Configuration:**
- `DATABASE_URL`: PostgreSQL connection string
- `DATABASE_POOL_SIZE`: Connection pool size (default: 10)
- `DATABASE_POOL_TIMEOUT`: Connection timeout in seconds (default: 30)

**Redis Configuration:**
- `REDIS_URL`: Redis connection string
- `REDIS_MAX_CONNECTIONS`: Maximum connection pool size (default: 10)
- `REDIS_SOCKET_TIMEOUT`: Socket timeout in seconds (default: 5)

**MQTT Configuration:**
- `MQTT_BROKER_HOST`: MQTT broker hostname (default: localhost)
- `MQTT_BROKER_PORT`: MQTT broker port (default: 1883)
- `MQTT_USERNAME`: MQTT authentication username
- `MQTT_PASSWORD`: MQTT authentication password

**Application Configuration:**
- `SECRET_KEY`: Application secret key for session management
- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)
- `HOST`: Server bind address (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

#### Environment-Specific Configurations

**Development Environment:**
```bash
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/digital_twin_dev
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Production Environment:**
```bash
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://username:password@db-server:5432/digital_twin_prod
REDIS_URL=redis://redis-server:6379/0
SECRET_KEY=your-very-secure-secret-key
CORS_ORIGINS=https://yourdomain.com
```

### Verification and Testing

After installation, verify that all platform components are functioning correctly:

1. **Service Health Checks**
```bash
# Check all services are running
docker-compose ps

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/assets

# Test WebSocket connections
# Use browser developer tools or WebSocket testing tools
```

2. **Database Connectivity**
```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d digital_twin

# Verify tables exist
\dt

# Check sample data
SELECT COUNT(*) FROM assets;
```

3. **MQTT Connectivity**
```bash
# Test MQTT broker
mosquitto_pub -h localhost -t test/topic -m "test message"
mosquitto_sub -h localhost -t test/topic
```

4. **Frontend Accessibility**
   - Open web browser to platform URL
   - Verify login functionality
   - Test dashboard displays
   - Confirm 3D visualization loads correctly

### Troubleshooting Common Issues

**Service Startup Failures:**
- Check Docker logs: `docker-compose logs [service-name]`
- Verify environment variables are set correctly
- Ensure required ports are not in use by other applications
- Check disk space and memory availability

**Database Connection Issues:**
- Verify database service is running and accessible
- Check database credentials and connection string
- Ensure database exists and migrations have been run
- Review firewall and network connectivity

**MQTT Connection Problems:**
- Verify MQTT broker is running and accessible
- Check MQTT credentials and topic permissions
- Test connectivity using MQTT client tools
- Review broker logs for authentication or authorization errors

**Performance Issues:**
- Monitor resource utilization (CPU, memory, disk, network)
- Check database query performance and indexing
- Review application logs for errors or warnings
- Consider scaling individual services based on bottlenecks

