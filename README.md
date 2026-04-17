# 🎬 YouTube Data Pipeline (AWS End-to-End Project)

An end-to-end data engineering pipeline built on AWS that ingests, processes, validates, and transforms YouTube trending data into analytics-ready datasets.

This project follows a Medallion Architecture (Bronze → Silver → Gold) and demonstrates real-world concepts like ETL pipelines, orchestration, and data quality validation.

---

## 🏗️ Architecture

### 📊 Overall Architecture

<img width="2784" height="1536" alt="YouTube Trending Data Pipeline" src="https://github.com/user-attachments/assets/d741fe5c-2c7b-46ba-a68f-c253eaa010bd" />


---

### 🔄 Step Functions Workflow
> ⬇️ Replace this with your step function graph image
Step Function Graph

---

## 🚀 Tech Stack

- AWS Lambda  
- AWS S3  
- AWS Glue  
- AWS Athena  
- AWS Step Functions  
- AWS SNS  
- Python (Pandas, PySpark, AWS Wrangler)

---

## 📊 Pipeline Flow

### 1️⃣ Data Ingestion (Lambda)
- Fetches YouTube trending data (JSON)
- Stores raw data in S3 Bronze layer

---

### 2️⃣ Reference Data Processing (Lambda)
- Converts JSON → Parquet
- Stores structured data in Silver layer

---

### 3️⃣ Bronze → Silver (Glue Job)
- Cleans and transforms raw data
- Writes partitioned Parquet data
- Updates Glue Data Catalog

---

### 4️⃣ Data Quality Checks (Lambda)
- Row count validation  
- Null checks  
- Schema validation  
- Value range checks  
- Freshness checks  

---

### 5️⃣ Silver → Gold (Glue Job)
Creates analytics tables:
- trending_analytics  
- channel_analytics  
- category_analytics  

---

### 6️⃣ Orchestration (Step Functions)
- Runs entire pipeline  
- Executes tasks in parallel  
- Handles retries & failures  

---

### 7️⃣ Alerts (SNS)
- Sends notifications on failures  

---

## 🗂️ Data Layers

### 🟤 Bronze Layer
- Raw JSON data from API  

### ⚪ Silver Layer
- Cleaned and structured data  
- Partitioned by region  

Tables:
- clean_statistics  
- clean_reference_data  

### 🟡 Gold Layer
- Aggregated analytics datasets  

Tables:
- trending_analytics  
- channel_analytics  
- category_analytics  

---

## ⚙️ Key Features

- Fully serverless pipeline  
- Automated orchestration  
- Data quality validation layer  
- Partitioned data for performance  
- Retry & failure handling  

---

## 📈 Use Cases

- Analyze trending videos by region  
- Identify top channels  
- Track category trends  
- Measure engagement metrics  

---

## 🧠 Learnings

- Built scalable AWS data pipeline  
- Worked with Glue Data Catalog  
- Implemented data quality checks  
- Designed orchestration using Step Functions  
- Managed IAM roles & permissions  

---

## 🙌 Author

Aakash Patania  
