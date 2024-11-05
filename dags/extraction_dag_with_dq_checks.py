from airflow import DAG
from airflow.operators.python import PythonOperator
from google.cloud import bigquery
from google.api_core import exceptions
from datetime import datetime
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'Admin',
    'depends_on_past': False,
    'retries': 1,
}

# Custom BigQuery load function
def load_data_to_bq(source_file, table_id):
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        max_bad_records=100000,
        ignore_unknown_values=True,
        autodetect=True,
        encoding="UTF-8",
    )
    
    uri = f"gs://eltl-project-raw-data/{source_file}"
    
    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()  # Wait for the job to complete
    print(f"Loaded data from {source_file} into {table_id}")

# Data quality validation function that logs row-level errors
def validate_data_quality(source_table_id, error_table_id, source_file):
    client = bigquery.Client()
    
    # Check if data_quality_errors table exists, if not, create it with schema
    try:
        client.get_table(error_table_id)
    except exceptions.NotFound:
        schema = [
            bigquery.SchemaField("table_name", "STRING"),
            bigquery.SchemaField("row_number", "INTEGER"),
            bigquery.SchemaField("error_description", "STRING"),
        ]
        table = bigquery.Table(error_table_id, schema=schema)
        client.create_table(table)
        print(f"Created table {error_table_id} for storing data quality errors.")
    
    # Dummy query to simulate logging row-based errors
    query = f"""
        SELECT
            "{source_table_id.split('.')[-1]}" AS table_name,
            ROW_NUMBER() OVER() AS row_number,
            "Generic data quality issue detected" AS error_description
        FROM `{source_table_id}`
        WHERE FALSE  -- Replace this with actual conditions to identify bad rows
    """
    
    job_config = bigquery.QueryJobConfig(destination=error_table_id, write_disposition="WRITE_APPEND")
    query_job = client.query(query, job_config=job_config)
    query_job.result()
    print(f"Data quality check completed for {source_table_id}")

# Define DAG
with DAG(
    dag_id='gcs_to_bq_with_quality_checks',
    default_args=default_args,
    description='Load CSV files from GCS to BigQuery with data quality checks',
    schedule_interval='@weekly',
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # Task to load VBAK.csv to BigQuery
    load_vbak_task = PythonOperator(
        task_id='load_vbak_to_bq',
        python_callable=load_data_to_bq,
        op_kwargs={
            'source_file': 'vbak.csv',
            'table_id': 'eltl-pipeline-project.staging.VBAK',
        },
    )

    # Task to run data quality check on VBAK table
    check_vbak_quality = PythonOperator(
        task_id='check_vbak_quality',
        python_callable=validate_data_quality,
        op_kwargs={
            'source_table_id': 'eltl-pipeline-project.staging.VBAK',
            'error_table_id': 'eltl-pipeline-project.staging.data_quality_errors',
            'source_file': 'vbak.csv'
        },
    )

    # Define dependencies
    load_vbak_task >> check_vbak_quality
