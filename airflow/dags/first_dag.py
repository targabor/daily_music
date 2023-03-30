from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'buhinalba',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)

}

with DAG(
    dag_id = 'our_first_dag_v4',
    default_args=default_args,
    description = 'Test dag to see how this works',
    start_date = datetime(2023, 3, 28), # schedule starts from this date midnight
    schedule_interval = '@daily'

) as dag:
    task1 = BashOperator(
        task_id='first_task',
        bash_command='echo hello world'
    )

    task2 = BashOperator(
        task_id= 'second_task',
        bash_command='echo hello world 2'
    )

    task3 = BashOperator(
        task_id= 'third_task',
        bash_command='echo hello world 3'
    )

    # task1.set_downstream(task2)
    # task1.set_downstream(task3)

    task1 >> task2
    task1 >> task3