from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'buhinalba',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)

}

def greet(ti):
    name = ti.xcom_pull(task_ids='get_name')
    print(f'hello {name}')

def get_name(ti):
    ti.xcom_push(key='name', value='Berry')
    

with DAG(
    default_args=default_args,
    dag_id= 'dag_with_python4',
    description='first_python_dag',
    start_date=datetime(2023,3,29),
    schedule_interval='@daily'

) as dag:
    task1 = PythonOperator(
        task_id = 'greet_with_kwargs',
        python_callable = greet,
    )
    
    task2 = PythonOperator(
        task_id = 'get_name',
        python_callable = get_name # when done the returned value will be visible in Admin -> xcoms 
    )

    task2 >> task1