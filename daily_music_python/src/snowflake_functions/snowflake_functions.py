import snowflake.connector
from src.snowflake_functions.SnowflakeCredentials import SnowflakeCredentials


def __connect_to_snowflake(credentials: SnowflakeCredentials) -> snowflake.connector.SnowflakeConnection:
    """Creates snowflake connection

    Args:
        user (str): Snowflake username inside account
        password (str): Password for account
        account (str): Snowflake account without ".snowflakecomputing.com"
        warehouse (str): Warehouse name
        database (str): Database name
        schema (str): Schema name

    Returns:
        snowflake.connector.SnowflakeConnection: Instance of connection to Snowflake
    """
    conn = snowflake.connector.connect(
        user=credentials.user,
        password=credentials.password,
        account=credentials.account,
        warehouse=credentials.warehouse,
        database=credentials.database,
        schema=credentials.schema,
    )
    return conn


def load_raw_messages_into_snowflake(messages):
    """It loads raw Slack responds into Snowflake

    Args:
        messages (slack.app.conversation_history response): Filtered Slack response messages
    """
    with __connect_to_snowflake(SnowflakeCredentials.get_credentialsFor('EXTRACTED')) as connection:
        insert_query = '''INSERT INTO EXTRACTED_MESSAGES (CLIENT_MSG_ID,SLACK_ID,MESSAGE_TIME,SERVICE_NAME,ORIGINAL_URL,ARTIST,TITLE,SPOTIFY_ID,REACTION_COUNT,PROCESSING_STATUS)
                            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,'')'''
        connection.cursor().executemany(insert_query, messages)
        connection.commit()
