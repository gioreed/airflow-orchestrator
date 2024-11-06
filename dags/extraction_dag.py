from airflow import DAG
from airflow.operators.python import PythonOperator
from google.cloud import bigquery
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
        max_bad_records=100000,  # Adjusted for broken records
        ignore_unknown_values=True,
        autodetect=True,
        encoding="UTF-8", 
    )
    
    uri = f"gs://eltl-project-raw-data/{source_file}"
    
    # Load the data from GCS to BigQuery
    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()  # Wait for the job to complete
    print(f"Loaded data from {source_file} into {table_id}")

# Define DAG
with DAG(
    dag_id='gcs_to_bq_custom_operator_dag',
    default_args=default_args,
    description='Load CSV files from GCS to BigQuery with custom operator',
    schedule_interval='@weekly',
    start_date=days_ago(1),
    catchup=False,
) as dag:

# Tasks to load each CSV to BigQuery
    load_vbak_task = PythonOperator(
        task_id='load_vbak_to_bq',
        python_callable=load_data_to_bq,
        op_kwargs={
            'source_file': 'vbak.csv',
            'table_id': 'eltl-pipeline-project.staging.VBAK',
        },
    )

    load_vbap_task = PythonOperator(
        task_id='load_vbap_to_bq',
        python_callable=load_data_to_bq,
        op_kwargs={
            'source_file': 'vbap.csv',
            'table_id': 'eltl-pipeline-project.staging.VBAP',
        },
    )

    load_vbrk_task = PythonOperator(
        task_id='load_vbrk_to_bq',
        python_callable=load_data_to_bq,
        op_kwargs={
            'source_file': 'vbrk.csv',
            'table_id': 'eltl-pipeline-project.staging.VBRK',
        },
    )

    load_vbrp_task = PythonOperator(
        task_id='load_vbrp_to_bq',
        python_callable=load_data_to_bq,
        op_kwargs={
            'source_file': 'vbrp.csv',
            'table_id': 'eltl-pipeline-project.staging.VBRP',
        },
    )

    load_lips_task = PythonOperator(
        task_id='load_lips_to_bq',
        python_callable=load_data_to_bq,
        op_kwargs={
            'source_file': 'lips.csv',
            'table_id': 'eltl-pipeline-project.staging.LIPS',
        },
    )

    load_ekpo_task = PythonOperator(
        task_id='load_ekpo_to_bq',
        python_callable=load_data_to_bq,
        op_kwargs={
            'source_file': 'ekpo.csv',
            'table_id': 'eltl-pipeline-project.staging.EKPO',
        },
    )

    load_kna1_task = PythonOperator(
        task_id='load_kna1_to_bq',
        python_callable=load_data_to_bq,
        op_kwargs={
            'source_file': 'kna1.csv',
            'table_id': 'eltl-pipeline-project.staging.KNA1',
        },
    )

    load_mara_task = PythonOperator(
        task_id='load_mara_to_bq',
        python_callable=load_data_to_bq,
        op_kwargs={
            'source_file': 'mara.csv',
            'table_id': 'eltl-pipeline-project.staging.MARA',
        },
    )

    load_makt_task = PythonOperator(
        task_id='load_makt_to_bq',
        python_callable=load_data_to_bq,
        op_kwargs={
            'source_file': 'makt.csv',
            'table_id': 'eltl-pipeline-project.staging.MAKT',
        },
    )

    load_mard_task = PythonOperator(
        task_id='load_mard_to_bq',
        python_callable=load_data_to_bq,
        op_kwargs={
            'source_file': 'mard.csv',
            'table_id': 'eltl-pipeline-project.staging.MARD',
        },
    )

    load_t001w_task = PythonOperator(
        task_id='load_t001w_to_bq',
        python_callable=load_data_to_bq,
        op_kwargs={
            'source_file': 't001w.csv',
            'table_id': 'eltl-pipeline-project.staging.T001W',
        },
    )

    load_konv_task = PythonOperator(
        task_id='load_konv_to_bq',
        python_callable=load_data_to_bq,
        op_kwargs={
            'source_file': 'konv.csv',
            'table_id': 'eltl-pipeline-project.staging.KONV',
        },
    )
  
    # Define task dependencies to run sequentially
    (
        load_vbak_task >> load_vbap_task >> load_vbrk_task >> load_vbrp_task >>
        load_lips_task >> load_ekpo_task >> load_kna1_task >> load_mara_task >>
        load_makt_task >> load_mard_task >> load_t001w_task >> load_konv_task
    )
