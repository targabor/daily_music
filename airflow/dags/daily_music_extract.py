from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests

default_args = {
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# def get_slack_extract_url():
#    return "http://127.0.0.1:5000/extract_data"


def call_slack_api():
    response = requests.get("http://127.0.0.1:5000/extract_data")
    print(response)


def call_spotify_api():
    # response = requests.get("spoty_bot_url")
    # print(response)
    pass



with DAG(
    default_args = default_args,
    dag_id = 'daily_music_extract_v02',
    description = 'extract and load daily_music from slack',
    start_date = datetime(2023, 4, 2),
    schedule_interval = '@daily'
) as dag:
    extract_daily_music = PythonOperator(
        task_id = 'extract_daily_music_slack',
        python_callable = call_slack_api
    )

    extract_spotify_data = PythonOperator(
        task_id = 'extract_spotify_data',
        python_callable = call_spotify_api
    )


    extract_daily_music >> extract_spotify_data
