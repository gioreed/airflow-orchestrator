from airflow import DAG
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from datetime import datetime
from pytz import timezone

default_args = {
    'owner': 'Admin',  # Airflow user
    'depends_on_past': False,
    'retries': 1,
}

with DAG(
    dag_id='airbyte_sync_dag_full',
    default_args=default_args,
    description='Triggers multiple Airbyte syncs to transfer data from GCS to BigQuery',
    schedule_interval='@weekly',  # Runs every hour
    start_date=datetime(2024, 10, 28, tzinfo=timezone('Europe/Rome')),
    catchup=False,
) as dag:

    # Define each Airbyte sync task with a unique task_id and connection_id
    trigger_airbyte_sync_vbak = AirbyteTriggerSyncOperator(
        task_id='trigger_airbyte_sync_vbak',
        airbyte_conn_id='airbyte_conn',
        connection_id='0e1f6143-f01a-45b7-aba2-569a32e74413',  # Replace with the UUID (url -> connection/uuid/...)
        asynchronous=True,
        timeout=7200
    )

    trigger_airbyte_sync_vbap = AirbyteTriggerSyncOperator(
        task_id='trigger_airbyte_sync_vbap',
        airbyte_conn_id='airbyte_conn',
        connection_id='dee89720-aa11-4eae-8da5-6539ccfc117e',
        asynchronous=True,
        timeout=7200    )

    trigger_airbyte_sync_vbrk = AirbyteTriggerSyncOperator(
        task_id='trigger_airbyte_sync_vbrk',
        airbyte_conn_id='airbyte_conn',
        connection_id='40560f55-5075-48ef-b997-35364efca6bb',
        asynchronous=True,
        timeout=7200    )
    
    trigger_airbyte_sync_vbrp = AirbyteTriggerSyncOperator(
        task_id='trigger_airbyte_sync_vbrp',
        airbyte_conn_id='airbyte_conn',
        connection_id='5b73d4f9-4266-42c3-aa15-e5d377fd97ec',
        asynchronous=True,
        timeout=7200,
    )

    trigger_airbyte_sync_lips = AirbyteTriggerSyncOperator(
        task_id='trigger_airbyte_sync_lips',
        airbyte_conn_id='airbyte_conn',
        connection_id='1e69a233-25df-44b8-9336-a95f2ee83ac3',
        asynchronous=True,
        timeout=7200,
    )

    trigger_airbyte_sync_ekpo = AirbyteTriggerSyncOperator(
        task_id='trigger_airbyte_sync_ekpo',
        airbyte_conn_id='airbyte_conn',
        connection_id='887d4b34-171f-4fe2-8da0-e16274a5a91c',
        asynchronous=True,
        timeout=7200,
    )

    trigger_airbyte_sync_kna1 = AirbyteTriggerSyncOperator(
        task_id='trigger_airbyte_sync_kna1',
        airbyte_conn_id='airbyte_conn',
        connection_id='fb46b2d2-205c-499f-b9c6-086c15f8f53b',
        asynchronous=True,
        timeout=7200,
    )

    trigger_airbyte_sync_mara = AirbyteTriggerSyncOperator(
        task_id='trigger_airbyte_sync_mara',
        airbyte_conn_id='airbyte_conn',
        connection_id='fda82d28-ca68-472b-b341-17cbb4eea42e',
        asynchronous=True,
        timeout=7200,
    )

    trigger_airbyte_sync_makt = AirbyteTriggerSyncOperator(
        task_id='trigger_airbyte_sync_makt',
        airbyte_conn_id='airbyte_conn',
        connection_id='1540cf29-f5d3-4a0e-969c-74ef76df1bc4',
        asynchronous=True,
        timeout=7200,
    )

    trigger_airbyte_sync_mard = AirbyteTriggerSyncOperator(
        task_id='trigger_airbyte_sync_mard',
        airbyte_conn_id='airbyte_conn',
        connection_id='a5ef754e-0116-4b98-80ea-dd6bd5f26285',
        asynchronous=True,
        timeout=7200,
    )

    trigger_airbyte_sync_t001w = AirbyteTriggerSyncOperator(
        task_id='trigger_airbyte_sync_t001w',
        airbyte_conn_id='airbyte_conn',
        connection_id='9b88b086-1aab-4884-b167-6cd66c32f087',
        asynchronous=True,
        timeout=7200,
    )
    # Set dependencies so each sync runs sequentially
    (
     trigger_airbyte_sync_vbak >>
     trigger_airbyte_sync_vbap >>
     trigger_airbyte_sync_vbrk >>
     trigger_airbyte_sync_vbrp >>
     trigger_airbyte_sync_lips >>
     trigger_airbyte_sync_ekpo >>
     trigger_airbyte_sync_kna1 >>
     trigger_airbyte_sync_mara >>
     trigger_airbyte_sync_makt >>
     trigger_airbyte_sync_mard >>
     trigger_airbyte_sync_t001w
     )
