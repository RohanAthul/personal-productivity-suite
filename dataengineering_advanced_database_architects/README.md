# MeetingBank Data Engineering Project

This project implements an end-to-end data engineering pipeline using the MeetingBank dataset. It demonstrates data ingestion from JSON, intermediate processing using Parquet, a hybrid storage architecture (MySQL hosted on Aiven + MongoDB), and query optimization across both SQL and NoSQL environments.

## Project Structure

```
MeetingBank_Project/
├── Data/                          # Raw JSON source files
├── Processed_Data/                # Intermediate Parquet files and cleaned data
├── power_bi_dashboard             # Sample powerbi dashboard created using final output
│
├── .env.example                   # Template for required database credentials
├── database_schema.jpeg           # Visual ERD/Schema layout for the hybrid setup
├── README.md                      # Project documentation
├── report.pdf                     # project report
├── requirements.txt               # Python dependencies
│
├── exploratory.py                 # Initial data exploration
├── main.py                        # Primary orchestrator to run the full pipeline
│
├── step1_process_metadata.py      # Clean metadata, add PKs/indexes, export Parquet
├── step2_process_transcripts.py   # Extract text, word/speaker counts, export Parquet
├── step3_database_loading.py      # Connection logic for Aiven MySQL & MongoDB
│
├── step4_sql_optimization.ipynb   # SQLAlchemy benchmarking (Notebook version)
├── step4_sql_optimization.py      # SQL optimization logic (Script version)
│
├── step5_mql_queries.js           # MongoDB Query Language (MQL) scripts
│
├── step6_sql_nosql_merge_and_visualization_jupyternotebook.ipynb     # Merge SQL and NoSQL data and analysis (Notebook version)
└── step6_sql_nosql_merge_and_visualization.py                        # Merge SQL and NoSQL data and analysis (Script version)
```
## Execution guide: MeetingBank Project

Please visit the below link and download the MeetingBank.json file and save it in this repository before you run the program [Data set].
   Zenodo. https://doi.org/10.5281/zenodo.7989108
1. **Environment Setup**
Before running any scripts, ensure all dependencies are installed and your database connections (Aiven MySQL & MongoDB) are configured
  - **Install dependencies:** pip install -r requirements.txt
  - **Check connections:** Ensure your credentials (check .env.example and save your credentials as .env) are set up for step3_database_loading.py
2. **Data Cleaning & Preparation**
- These steps transform the raw JSON into optimized Parquet files for faster processing
   - Step 1: Run python step1_process_metadata.py to clean metadata and generate primary keys
   - Step 2: Run python step2_process_transcripts.py to process text and speaker metrics
3. **Database Ingestion**
- Load the processed data into your hybrid database environment
   - Step 3: Run python step3_database_loading.py to push data to Aiven MySQL and MongoDB
4. **Optimization & Querying**
- Perform performance benchmarking and NoSQL data retrieval
   - SQL Optimization: Run python step4_sql_optimization.py (or use the .ipynb version) to benchmark SQLAlchemy performance
   - NoSQL Analysis: Execute step5_mql_queries.js within your MongoDB shell or Compass to run MQL scripts
5. **Final Integration & Visualization**
- The final step merges the structured SQL data with the unstructured NoSQL data for total analysis
   - Step 6: Run python step6_sql_nosql_merge_and_visualization.py to generate the final insights and plots
   - Step 7: Load file from power_bi_dashboard folder on to powerbi for interactive visualization

#### One-command run
- If you want to run the entire Python pipeline automatically, you can simply execute the orchestrator:
- python main.py

Note: The .ipynb files are provided for interactive exploration and visualization, while the .py scripts are intended for automated production runs.


## Pipeline Summary
- Exploration & Processing: Analyze raw JSON, extract metadata, and engineer features (e.g., primary keys, transcript word counts, and speaker counts).

- Intermediate Storage: Processed data is saved into the Processed_Data/ directory as .parquet files for high-efficiency.

- Hybrid Database Loading:

  - MySQL (Aiven): Stores structured summary data across three relational tables (cities, meetings, meeting_metrics).

  - MongoDB: Stores unstructured full-length transcripts and associated flexible metadata.

- Query Optimization: Using step4_sql_optimization, the project benchmarks query execution times and demonstrates performance gains through indexing and SQLAlchemy optimization.

- NoSQL Interaction: step5_mql_queries.js contains native MongoDB queries to interact with the document store.

- Data Integration: The final step merges data from both MySQL and MongoDB into a unified DataFrame for comprehensive analytical visualizations.

## Technologies Used
- Python: ETL, feature engineering (Pandas/PyArrow).

- MySQL (Aiven): Cloud-hosted relational data storage.

- MongoDB: Document-oriented database for transcripts.

- SQLAlchemy: Programmatic database interaction and benchmarking.

- JavaScript: Native MQL query scripting.

- Jupyter Notebooks: Data storytelling and performance visualization.

## Key Focus
- Hybrid Architecture: Seamlessly handles both structured relational data and unstructured text.

- Orchestration: Includes a main.py to streamline the execution of the ETL pipeline.

- Schema Design: Includes a database_schema.jpeg for clear architectural transparency.

- Dual-Format Delivery: Provides both .py scripts for production-style execution and .ipynb for interactive analysis.

- Subset from dataset chosen: **Longbeach** & **Seattle**

## Resources
#### Dataset
- Yebowen Hu, Tim Ganter, Hanieh Deilamsalehy, Franck Dernoncourt, Hassan Foroosh, & Fei Liu. (2023). MeetingBank: A Benchmark Dataset for Meeting Summarization (Version v2) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.7989108
#### Infrastructure
- Aiven for MySQL: Cloud-hosted database service used for structured data storage
* MongoDB Atlas: Used for document-based transcript storage
#### Development Support
* Gemini 3 Flash: Utilized as a technical collaborator for syntax optimization, debugging Python/SQL integration, and refining documentation structure.
* SQLAlchemy & Pandas: Core libraries used for the ETL and benchmarking logic.

## Advanced Database Architects - Group Members
- Athul Rohan Anil Kumar Rajitha
- Zaw Win Htet Naing
- Srushti Deepak Borkar
- Lakshmi Sahiti Varada

## Status
- ✔ Meets all course project requirements
- ✔ Demonstrates both SQL and NoSQL (MQL) query capabilities
- ✔ Includes end-to-end integration from raw JSON to final merged visualizations
