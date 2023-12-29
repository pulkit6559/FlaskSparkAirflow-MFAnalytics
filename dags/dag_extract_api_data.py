import airflow
from datetime import timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator 
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.utils.dates import days_ago
import os


default_args = {
    'owner': 'airflow',    
    'retry_delay': timedelta(minutes=5),
}

spark_dag = DAG(
        dag_id = "spark_api_data_to_s3",
        default_args=default_args,
        schedule_interval=None,	
        dagrun_timeout=timedelta(minutes=60),
        description='use case of SparkSubmitOperator in airflow',
        start_date = airflow.utils.dates.days_ago(1)
)

Extract = SparkSubmitOperator(
		application ='/opt/airflow/spark_scripts/mfi_to_s3.py',
		conn_id= 'spark_default', 
		task_id='spark_submit_task',
        conf = {
            'spark.executorEnv.AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID'),
            'spark.executorEnv.AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY'),
            'spark.executorEnv.AWS_DEFAULT_REGION': os.environ.get('AWS_DEFAULT_REGION'),
        },
		dag=spark_dag,
        application_args=['{{ dag_run.conf["mf_id"]}}']
		)

Extract