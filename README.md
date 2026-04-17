# 🎬 YouTube Data Pipeline (End-to-End AWS Data Engineering Project)

This project is a complete end-to-end **data engineering pipeline** built using AWS services to ingest, process, validate, and analyze YouTube trending data across multiple regions.

The pipeline is designed using the **Medallion Architecture (Bronze → Silver → Gold)** and simulates a production-grade data platform. It integrates multiple AWS services to handle ingestion, transformation, data quality validation, orchestration, and analytics.

The goal of this project is to demonstrate how raw data from external APIs and historical datasets can be transformed into structured, analytics-ready datasets using scalable and serverless cloud architecture.

---

## 📡 Data Sources

The pipeline uses two main data sources:

### 1. YouTube Data API v3
- Primary source of live trending video data
- Provides up-to-date information across multiple regions
- Used for real-time ingestion

### 2. Kaggle YouTube Trending Dataset
- Historical dataset used for backfilling
- Helps simulate real-world large-scale data scenarios
- Useful for testing transformations and analytics

---

## 🏗️ Architecture Overview



<img width="2784" height="1536" alt="YouTube Trending Data Pipeline" src="https://github.com/user-attachments/assets/9f36b322-50ba-4a1e-bd12-0682619d2100" />


The pipeline follows a layered architecture:

- **Bronze Layer** → Raw data ingestion (JSON format)
- **Silver Layer** → Cleaned and structured data (Parquet format)
- **Gold Layer** → Aggregated analytics datasets

All components are orchestrated using **AWS Step Functions**, enabling automation, retry handling, and parallel execution.

---

## 🚀 Technology Stack

This project uses a combination of AWS services and Python-based tools:

- **AWS Lambda** → Used for ingestion and lightweight transformations  
- **AWS S3** → Central data lake storage (Bronze, Silver, Gold layers)  
- **AWS Glue** → ETL jobs, Crawlers, and Data Catalog  
- **AWS Athena** → Query engine for validation and analytics  
- **AWS Step Functions** → Workflow orchestration  
- **AWS SNS** → Alerting and notifications  
- **Python Libraries**:
  - Pandas (data manipulation)
  - PySpark (large-scale ETL)
  - AWS Wrangler (Athena + S3 integration)

---

## 📌 Pipeline Overview

The pipeline is designed to process data through multiple stages:

1. Data ingestion from external sources  
2. Storage of raw data in Bronze layer  
3. Transformation and cleaning into Silver layer  
4. Data quality validation  
5. Aggregation into Gold layer  
6. Querying and analytics  

Each stage is designed to be modular, scalable, and fault-tolerant.

---

## 🟤 Bronze Layer (Raw Data)

The Bronze layer stores raw data exactly as it is received.

### Characteristics:
- Stored in JSON format  
- No transformations applied  
- Includes:
  - API-ingested data  
  - Historical Kaggle data  

### Purpose:
- Acts as a **source of truth**  
- Enables reprocessing in case of failures  
- Preserves original data integrity  

---

## ⚪ Silver Layer (Cleaned & Structured Data)

The Silver layer contains cleaned, structured, and enriched data.

Two main datasets are created:

---

### 📊 clean_statistics

This dataset is derived from raw trending data.

#### Transformations applied:
- Data type conversions (string → integer, date parsing)  
- Column normalization  
- Removal of invalid or duplicate records  
- Derived metrics:
  - like_ratio  
  - engagement_rate  

#### Optimization:
- Stored in Parquet format  
- Partitioned by region for efficient querying  

---

### 🏷️ clean_reference_data

This dataset contains category metadata.

#### Processing steps:
- JSON data flattened  
- Converted to structured format  
- Metadata added:
  - ingestion timestamp  
  - source file  
  - region  

---

## 🟡 Gold Layer (Analytics Layer)

The Gold layer contains business-level aggregated datasets optimized for analytics.

---

### 📈 trending_analytics

- Aggregated daily metrics per region  
- Includes:
  - total views  
  - total likes  
  - total comments  
  - average engagement  

---

### 📺 channel_analytics

- Channel-level performance analysis  
- Metrics include:
  - total views  
  - average engagement  
  - ranking within region  
  - trending frequency  

---

### 🏷️ category_analytics

- Category-level trends over time  
- Includes:
  - total views per category  
  - engagement metrics  
  - percentage share of views  

---

## ⚙️ Data Processing Workflow

The pipeline processes data in multiple stages:

---

### 🔹 Ingestion Layer

A Lambda function is used to fetch trending video data from the YouTube API.

- Retrieves data for multiple regions  
- Writes raw JSON data to S3 Bronze layer  
- Ensures consistent structure for downstream processing  

---

### 🔹 Reference Data Transformation

Another Lambda function processes category/reference data.

- Reads JSON files from S3  
- Converts them into Parquet format  
- Adds metadata such as ingestion timestamp and region  
- Writes output to Silver layer  

---

### 🔹 Bronze to Silver Transformation

A Glue ETL job processes raw statistics data.

- Reads from Bronze using Glue Catalog  
- Cleans and transforms data  
- Applies schema normalization  
- Generates derived metrics  
- Writes partitioned data to Silver  

---

### 🔹 Data Quality Validation

A dedicated Lambda function performs data quality checks before data moves forward.

#### Checks performed:
- Row count validation  
- Null value thresholds  
- Schema validation  
- Value range validation (e.g., no negative views)  
- Freshness validation  

The result determines whether the pipeline proceeds to the next stage.

---

### 🔹 Silver to Gold Transformation

A Glue job aggregates Silver layer data.

- Joins statistics and reference data  
- Performs aggregations  
- Generates analytics tables  
- Writes output to Gold layer  

---

### 🔹 Orchestration

AWS Step Functions orchestrates the entire pipeline.


<img width="986" height="686" alt="Screenshot 2026-04-18 at 00 44 53" src="https://github.com/user-attachments/assets/ce5cc608-c7a9-4ed2-82a7-d323e642ab64" />


#### Responsibilities:
- Controls execution flow  
- Runs tasks in parallel  
- Implements retry logic  
- Handles failures gracefully  
- Ensures data quality checks pass before aggregation  

---

### 🔹 Alerting System

SNS is integrated to notify failures.

#### Alerts triggered for:
- Ingestion failures  
- Transformation failures  
- Data quality failures  
- Aggregation failures  

---

## 📊 Query & Analytics

- Data is queried using **AWS Athena**  
- Enables:
  - Ad-hoc queries  
  - Analytical reporting  
  - Integration with BI tools (QuickSight)  

---

## ⚙️ Key Features

- Fully serverless architecture  
- End-to-end automated pipeline  
- Parallel execution for efficiency  
- Data quality validation layer  
- Partitioned storage for performance optimization  
- Schema evolution handling  
- Fault tolerance with retry mechanisms  

---

## 📈 Use Cases

- Analyze trending videos across different regions  
- Identify top-performing channels  
- Track category-level trends over time  
- Measure engagement and audience behavior  

---

## 🧠 Learnings

- Built a real-world scalable data pipeline using AWS  
- Gained hands-on experience with Glue ETL and Crawlers  
- Learned to handle messy and inconsistent raw data  
- Implemented a custom data quality framework  
- Designed orchestration using Step Functions  
- Debugged IAM roles and permission-related issues  
- Optimized data storage using partitioning and Parquet  

---

## 🙌 Author

Aakash Patania  
Aspiring Data Engineer 🚀
