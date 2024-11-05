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

def load_data_to_staging(source_file, staging_table_id):
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        max_bad_records=100000,  # Lenient max errors to capture as many rows as possible
        ignore_unknown_values=True,
        autodetect=True,
        encoding="UTF-8",
    )

    uri = f"gs://eltl-project-raw-data/{source_file}"
    load_job = client.load_table_from_uri(uri, staging_table_id, job_config=job_config)
    load_job.result()
    print(f"Loaded all rows from {source_file} into staging table {staging_table_id}")

def compare_staging_and_cleaned(staging_table_id, cleaned_table_id, error_table_id):
    client = bigquery.Client()

    try:
        client.get_table(error_table_id)
    except exceptions.NotFound:
        schema = [
            bigquery.SchemaField("row_data", "STRING"),
            bigquery.SchemaField("error_description", "STRING"),
        ]
        table = bigquery.Table(error_table_id, schema=schema)
        client.create_table(table)
        print(f"Created table {error_table_id} for storing data quality errors.")

    query = f"""
        SELECT 
            TO_JSON_STRING(s) AS row_data,
            "Row did not load into cleaned table" AS error_description
        FROM `{staging_table_id}` s
        LEFT JOIN `{cleaned_table_id}` c
        ON s.primary_key = c.primary_key  -- Adjust this join key based on the unique identifier in your data
        WHERE c.primary_key IS NULL
    """

    job_config = bigquery.QueryJobConfig(
        destination=error_table_id,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    query_job = client.query(query, job_config=job_config)
    query_job.result()
    print(f"Data quality check completed. Unprocessed rows stored in {error_table_id}")

with DAG(
    dag_id='gcs_to_bq_with_staging_and_quality_checks',
    default_args=default_args,
    description='Load CSV files from GCS to BigQuery with data quality checks by comparing staging and cleaned tables',
    schedule_interval='@weekly',
    start_date=days_ago(1),
    catchup=False,
) as dag:

    load_vbak_to_staging = PythonOperator(
        task_id='load_vbak_to_staging',
        python_callable=load_data_to_staging,
        op_kwargs={
            'source_file': 'vbak.csv',
            'staging_table_id': 'eltl-pipeline-project.staging.VBAK_staging',
        },
    )

    compare_vbak_staging_and_cleaned = PythonOperator(
        task_id='compare_vbak_staging_and_cleaned',
        python_callable=compare_staging_and_cleaned,
        op_kwargs={
            'staging_table_id': 'eltl-pipeline-project.staging.VBAK_staging',
            'cleaned_table_id': 'eltl-pipeline-project.staging.VBAK',
            'error_table_id': 'eltl-pipeline-project.staging.data_quality_errors',
        },
    )

    load_vbak_to_staging >> compare_vbak_staging_and_cleaned
