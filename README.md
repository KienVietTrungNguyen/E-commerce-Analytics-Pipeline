# 🛒 E-commerce Analytics Pipeline (End-to-End)

> End-to-end data engineering project: từ raw JSON/GCS → BigQuery Data Warehouse → Power BI Dashboards

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Data Sources](#-data-sources)
- [BigQuery Schema](#-bigquery-schema)
- [ETL Pipeline](#-etl-pipeline)
- [Power BI Dashboards](#-power-bi-dashboards)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Data Quality Checks](#-data-quality-checks)
- [Sample Queries](#-sample-queries)
- [Deliverables](#-deliverables)

---

## 🎯 Overview

Pipeline xử lý và phân tích dữ liệu toàn diện cho hệ thống bán lẻ công nghệ **TechStore Vietnam**, tích hợp dữ liệu từ nhiều kênh bán hàng (online/offline) và cổng thanh toán.

### Mục tiêu

| # | Mục tiêu |
|---|---|
| 1 | Tích hợp dữ liệu từ nhiều nguồn: Shopify, Sapo POS, PayPal, MoMo, ZaloPay, Mercury Bank |
| 2 | Phân tích customer journey xuyên suốt các kênh bán hàng |
| 3 | Theo dõi cashflow và tình trạng thanh toán real-time |
| 4 | Xây dựng 3 Power BI dashboards với DAX measures đầy đủ |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     STORAGE LAYER                               │
│              Google Cloud Storage (GCS)                         │
│   gs://minpy/shopify/  │  gs://minpy/sapo/  │  gs://minpy/...  │
└──────────────────────────┬──────────────────────────────────────┘
                           │  Python ETL Pipeline
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATA WAREHOUSE LAYER                          │
│                BigQuery — Star Schema                           │
│                                                                 │
│   ┌─────────┐   ┌─────────┐   ┌──────────┐   ┌─────────────┐  │
│   │dim_cust │   │dim_prod │   │ dim_date │   │dim_location │  │
│   └────┬────┘   └────┬────┘   └────┬─────┘   └──────┬──────┘  │
│        │             │             │                  │         │
│   ┌────▼─────────────▼─────────────▼──────────────────▼──────┐ │
│   │                    fact_orders (center)                   │ │
│   └──────┬──────────────────────┬────────────────────────────┘ │
│          │                      │                               │
│   ┌──────▼──────┐    ┌──────────▼──────┐   ┌────────────────┐  │
│   │fact_payment │    │fact_order_items │   │fact_cart_events│  │
│   └──────┬──────┘    └─────────────────┘   └────────────────┘  │
│          │                                                      │
│   ┌──────▼────────────┐                                        │
│   │fact_bank_transact │                                        │
│   └───────────────────┘                                        │
│                                                                 │
│   Views: vw_customer_journey │ vw_cashflow_daily │ vw_payment  │
└──────────────────────────┬──────────────────────────────────────┘
                           │  Power BI Connector
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SERVING LAYER                                │
│  Dashboard 1: Customer Journey  │  7 tables loaded to Power BI  │
│  Dashboard 2: Cashflow          │  6 Import + 1 DirectQuery     │
│  Dashboard 3: Payment Risk      │  Published to Power BI Service│
└─────────────────────────────────────────────────────────────────┘
```

---

### Pipeline Flow

```
Step 1: Extract
  └── BaseExtractor.list_files(bucket, prefix)
  └── BaseExtractor.extract_json_gz(file_path)
  └── Decompress + parse JSON → DataFrame

Step 2: Transform
  ├── DimensionTransformer
  │   ├── Standardize column names & data types
  │   ├── Generate surrogate keys (customer_id, product_id...)
  │   ├── Deduplicate records
  │   └── Handle missing values
  └── FactTransformer
      ├── Generate order_key, payment_key, event_key (UUID/hash)
      ├── Map transaction_id across sources
      ├── Unify payment status codes (resultCode=0 → success)
      └── Calculate derived fields (line_total = qty × unit_price)

Step 3: Load
  └── BigQueryLoader.create_dataset_if_not_exists()
  └── BigQueryLoader.load_dataframe(df, table, write_disposition)
      ├── Dims: WRITE_TRUNCATE
      └── Facts: WRITE_APPEND (incremental)

Step 4: Orchestrate
  └── PipelineOrchestrator
      ├── 1. Load all dimension tables
      ├── 2. Load all fact tables
      ├── 3. Update dim_customer aggregates (LTV, total_orders)
      ├── 4. Create/refresh analysis views
      └── 5. Log pipeline run metadata
```

## ⚙️ ETL Pipeline

### Project Structure

```
etl_pipeline/
├── config/
│   ├── gcs_config.yaml          # GCS bucket paths & credentials
│   └── bigquery_schema.yaml     # Table schemas & partition config
├── extractors/
│   ├── __init__.py
│   ├── base_extractor.py        # BaseExtractor: extract_json_gz(), list_files()
│   ├── shopify_extractor.py     # Shopify orders, customers, products
│   ├── sapo_extractor.py        # Sapo POS orders, locations
│   ├── payment_extractor.py     # PayPal, MoMo, ZaloPay, Mercury
│   └── tracking_extractor.py   # Cart events
├── transformers/
│   ├── __init__.py
│   ├── base_transformer.py      # Standardize columns, data types, keys
│   ├── dimension_transformer.py # dim_customer, dim_product, dim_date...
│   └── fact_transformer.py      # fact_orders, fact_payment, fact_cart_events...
├── loaders/
│   ├── __init__.py
│   └── bigquery_loader.py       # create_dataset(), load_dataframe(), execute_query()
├── utils/
│   ├── __init__.py
│   ├── gcs_helper.py            # GCS read/write helpers
│   └── logger.py                # Logging config
├── orchestration/
│   ├── __init__.py
│   └── pipeline_orchestrator.py # Load dims first → facts → views → aggregates
├── tests/
│   └── test_pipeline.py         # Unit tests (coverage > 80%)
├── main.py                      # Entry point
└── requirements.txt
```


## 📊 Data Sources

### 1. E-commerce Platforms

| Source | Location | Volume | Key Data |
|--------|----------|--------|----------|
| **Shopify** | `gs://minpy/shopify/` | 200K orders, 2M customers | orders, products, customers, staff |
| **Sapo POS** | `gs://minpy/sapo/` | 1M orders, 50 stores | offline transactions, locations |
| **Online Orders** | `gs://minpy/online_orders/` | 50K orders | multi-channel: website, mobile, marketplace |

### 2. Payment Gateways

| Gateway | Location | Volume | Notes |
|---------|----------|--------|-------|
| **PayPal** | `gs://minpy/paypal/` | 300 transactions | USD, international |
| **Mercury Bank** | `gs://minpy/mercury/` | 500 transactions, 3 accounts | bank statements |
| **MoMo** | `gs://minpy/momo/` | 500 transactions | resultCode = 0 → success |
| **ZaloPay** | `gs://minpy/zalopay/` | 500 transactions | return_code = 1 → success |

### 3. Tracking & Analytics

| Source | Location | Volume | Key Data |
|--------|----------|--------|----------|
| **Cart Events** | `gs://minpy/cart_tracking/` | 10K+ events | view_item, add_to_cart, purchase, utm tracking |

---

## 🗄 BigQuery Schema

**Dataset:** `lithe-willow-411604.end_to_end_project`

### Dimension Tables

```
dim_customer     → customer_id (PK), email, full_name, customer_segment,
                   lifetime_value_vnd, total_orders, first/last_order_date
                   [PARTITION: created_at]

dim_product      → product_id (PK), product_name, sku, category, brand,
                   price_vnd, price_usd, stock_quantity, is_active

dim_location     → location_id (PK), location_code, location_name,
                   location_type, city, address, is_active

dim_staff        → staff_id (PK), staff_code, full_name, position,
                   location_id (FK), hire_date, is_active

dim_date         → date_key (PK), date, year, quarter, month, week,
                   day_of_week, is_weekend, is_holiday, fiscal_year
```

### Fact Tables

```
fact_orders          → order_key (PK), order_id, transaction_id, customer_id (FK),
                       order_date_key (FK), channel, status, payment_status,
                       total_vnd, total_usd
                       [PARTITION: order_date_key | CLUSTER: customer_id, channel]

fact_order_items     → order_item_key (PK), order_key (FK), product_id (FK),
                       quantity, unit_price_vnd, line_total_vnd
                       [PARTITION: order_date_key | CLUSTER: product_id]

fact_payment         → payment_key (PK), transaction_id (FK), customer_id (FK),
                       payment_gateway, payment_method, amount_vnd, payment_status
                       [PARTITION: payment_date_key | CLUSTER: customer_id, gateway]

fact_cart_events     → event_key (PK), session_id, customer_id (FK),
                       event_type, event_timestamp, product_id (FK),
                       source, device, utm_source, utm_campaign
                       [PARTITION: event_date_key | CLUSTER: customer_id, event_type]

fact_bank_transactions → transaction_key (PK), account_id, transaction_type,
                         amount_vnd, status, transaction_date
                         [PARTITION: transaction_date_key]
```

### Analysis Views

#### `vw_customer_journey`
```sql
-- Mục đích: Customer journey từ first touch → purchase
-- Kết hợp: fact_cart_events + fact_orders + dim_customer
-- Key fields: touchpoint_sequence, is_first_touch, is_last_touch,
--             next_traffic_source, days_to_first_purchase, recency_days,
--             hour_of_day, day_of_week
```

#### `vw_cashflow_daily`
```sql
-- Mục đích: Cashflow tổng hợp theo ngày
-- Kết hợp: fact_orders + fact_payment + fact_bank_transactions (FULL OUTER JOIN)
-- Key fields: sales_revenue_vnd, payments_received_vnd,
--             bank_inflow_vnd, bank_outflow_vnd, net_cashflow_vnd
```

#### `vw_payment_status`
```sql
-- Mục đích: Phân loại trạng thái thanh toán + risk scoring
-- Kết hợp: fact_orders + fact_payment + dim_customer
-- Key fields: payment_status_category (Paid/Pending/Overdue/Failed),
--             days_overdue, outstanding_amount_vnd,
--             payment_delay_hours, risk_score
```

---


### Installation

```bash
# Clone repo
git clone https://github.com/your-username/techstore-analytics-pipeline.git
cd techstore-analytics-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Requirements

```
google-cloud-storage==2.10.0
google-cloud-bigquery==3.11.0
pandas==2.0.3
pyarrow==12.0.1
pyyaml==6.0
python-dotenv==1.0.0
pytest==7.4.0
pytest-cov==4.1.0
```

### Configuration

```bash
# .env file
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GCS_BUCKET=minpy
BIGQUERY_PROJECT=your-project-id
BIGQUERY_DATASET=techstore_analytics
```

### Run Pipeline

```bash
# Full pipeline
python main.py --mode full

# Specific source only
python main.py --mode incremental --source shopify

# Run tests
pytest tests/ --cov=. --cov-report=html
```

---

## 📊 Power BI Dashboards

### Tables loaded to Power BI (7/13 total)

| Table | Mode | Used for |
|-------|------|----------|
| `vw_customer_journey` | Import | Dashboard 1 |
| `vw_cashflow_daily` | Import | Dashboard 2 |
| `vw_payment_status` | **DirectQuery** | Dashboard 3 (real-time) |
| `dim_customer` | Import | Slicers, tooltips |
| `dim_date` | Import | Time intelligence DAX |
| `dim_product` | Import | Product slicers |
| `dim_location` | Import | Geographic map |

> **Why not load all tables?** Raw fact tables are already denormalized into views. Loading duplicates would cause ambiguous filter context in DAX and waste memory.

---

### Dashboard 1 — Customer Journey Analytics

```
<img width="1266" height="711" alt="image" src="https://github.com/user-attachments/assets/0561a168-b6df-420b-88b9-7ced65b9cbee" />

### Insights
- Conversion rate ~100% → indicates data quality issue (likely duplicate or incorrect joins)
- Cart abandonment extremely low (~1%) → unrealistic → tracking issue
- Channel distribution is evenly split (~20% each) → attribution model may be inaccurate
- Time to purchase decreased significantly → faster conversion or compressed data
- Customer segmentation shows many low-frequency users
### Recommendations
- Fix event tracking & deduplication logic
- Implement session-based funnel tracking
- Use multi-touch attribution instead of linear
- Launch retention & loyalty campaigns

---

### Dashboard 2 — Cashflow & Financial Analytics

```
<img width="1257" height="708" alt="image" src="https://github.com/user-attachments/assets/ca6b072e-5ec4-4d65-9556-a07c1dd97e8b" />

### Insights
- Revenue generated but no payment collected
- Extremely high receivables → serious financial risk
- Cashflow fluctuates heavily
- Business heavily depends on Shopify (~84%)
- Bank balance unstable → liquidity risk
### Recommendations
- Implement payment reconciliation system
- Monitor receivables & payment delays
- Diversify sales channels
- Set alerts for low cash balance
---


---

## 📚 Resources

- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)
- [BigQuery Partitioning & Clustering](https://cloud.google.com/bigquery/docs/partitioned-tables)
- [Power BI DAX Reference](https://docs.microsoft.com/en-us/dax/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [google-cloud-python](https://googleapis.dev/python/google-api-core/latest/index.html)

---

*Good luck! 🎉*
