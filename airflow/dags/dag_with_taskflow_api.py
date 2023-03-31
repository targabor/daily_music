from datetime import datetime, timedelta
from airflow.decorators import dag, task


default_args = {
    'owner': 'buhinalba',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}


@dag(dag_id='dag_with_taskflow',
    default_args=default_args,
    start_date=datetime(2023,3,29),
    schedule_interval='@daily')
def hello_world_etl():

    @task()
    def get_first_name():
        return "Jerry"

    @task()
    def get_last_name():
        return "Smith"

    @task()
    def greet(first_name, last_name):
        print(f"Hello {first_name} {last_name}")

    first_name = get_first_name()
    last_name = get_last_name()
    greet(first_name, last_name)


hello_world_etl()