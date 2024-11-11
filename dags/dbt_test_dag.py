from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.empty import EmptyOperator

default_args = {
    'owner': 'Admin',
    'depends_on_past': False,
    'retries': 1,
}

with DAG(
    'dbt_test_dag',
    default_args=default_args,
    description='Run dbt test container after extraction DAG',
    schedule_interval='@weekly',
    start_date=days_ago(1),
    catchup=False,
) as dag:

    start_task = EmptyOperator(task_id='start')

    # DockerOperator to run the dbt-test container
    run_dbt_test = DockerOperator(
    task_id='run_dbt_test',
    image='europe-west1-docker.pkg.dev/eltl-pipeline-project/dbt-test-europe/dbt-test:latest',
    api_version='auto',
    auto_remove=True,
    docker_url="unix://var/run/docker.sock",
    network_mode="bridge",
    command="poetry run dbt run"
    )


    start_task >> run_dbt_test
