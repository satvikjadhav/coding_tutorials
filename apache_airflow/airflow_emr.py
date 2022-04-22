# import modules/libraries
from airflow import DAG
from airflow.contrib.operators.emr_add_steps_operator import EmrAddStepsOperator
from airflow.contrib.sensors.emr_step_sensor import EmrStepSensor
from airflow.utils.dates import days_ago
from airflow.models import Variable
from datetime import timedelta
import os

"""
This is a simple DAG that could be used to run submit spark jobs to an already existing Amazon EMR cluster running
There are only two stes;
    1. submit the spark job
    2. watch/keep track of the job using EMR step sensor operator to know when the job finishes, so the DAG can be marked as completed or failed
"""

# setting up default args
DEFAULT_ARGS = {
    'owner': 'satvikjadhav',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
}

# add & edit the args as per your requirement. Change the pyspark file name.
SPARK_TASK = [
    {
        'Name': 'spark_app',
        'ActionOnFailure': 'CONTINUE',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': ["spark-submit", "--deploy-mode", "cluster", "s3/path/to/the/pyspark/script.py"],
        },
    }
]

# set the variables.
cluster_id  = Variable.get("CLUSTER_ID")


with DAG(
    dag_id='airflow_emr',
    default_args=DEFAULT_ARGS,
    dagrun_timeout=timedelta(hours=2),
    start_date=days_ago(1),
    schedule_interval=None,
    tags=['pyspark'],
) as dag:

    # first step to register EMR step
    step_first = EmrAddStepsOperator(
        task_id='add_emr_step',
        job_flow_id=cluster_id,
        aws_conn_id='aws_default',
        steps=SPARK_TASK,
    )

    # second step to keep track of previous step.
    step_second = EmrStepSensor(
        task_id='watch_emr_step',
        job_flow_id=cluster_id,
        step_id="{{ task_instance.xcom_pull(task_ids='add_emr_step', key='return_value')[0] }}",
        aws_conn_id='aws_default',
    )

    # call the EMR steps.
    step_first >> step_second 