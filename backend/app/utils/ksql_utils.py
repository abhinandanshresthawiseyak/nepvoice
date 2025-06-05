import requests
from app.utils.kafkaclient import KafkaClient

KSQLDB_URL = "http://192.168.88.40:7816"  # replace with your ksqlDB server URL

# {'request_id':data['request_id'],
# 'bucket_name':'tts-audios' ,
# 'object_name':object_name, '
# text':data['text'], 
# 'language':data['lang'], 
# 'size':len(audio_bytes), 
# 'created_at': str(datetime.now())}

CREATE_STREAM = """
CREATE STREAM tts_response_queue_stream (
    request_id VARCHAR,
    bucket_name VARCHAR,
    object_name VARCHAR,
    text VARCHAR,
    language VARCHAR,
    audio_size BIGINT,
    created_at timestamp
) WITH (
    KAFKA_TOPIC='tts_response_queue_topic',
    VALUE_FORMAT='JSON'
);
"""

CREATE_TABLE = """
CREATE TABLE tts_response_table AS
SELECT
    request_id,
    LATEST_BY_OFFSET(bucket_name) AS bucket_name,
    LATEST_BY_OFFSET(object_name) AS object_name,
    LATEST_BY_OFFSET(text) AS text,
    LATEST_BY_OFFSET(language) AS language,
    LATEST_BY_OFFSET(audio_size) AS audio_size,
    LATEST_BY_OFFSET(created_at) AS created_at
FROM tts_response_queue_stream
GROUP BY request_id
EMIT CHANGES;

"""

def run_ksql_statement(statement: str):
    """Run KSQL statement using the /ksql endpoint."""
    payload = {
        "ksql": statement,
        "streamsProperties": {}
    }
    resp = requests.post(f"{KSQLDB_URL}/ksql", json=payload)
    resp.raise_for_status()
    return resp.json()

def run_pull_query(sql: str):
    url = f"{KSQLDB_URL}/query"

    payload = {
        "ksql": sql,  # Changed from "sql" to "ksql"
        "properties": {}
    }

    headers = {
        "Content-Type": "application/vnd.ksql.v1+json; charset=utf-8",
        "Accept": "application/vnd.ksql.v1+json"
    }

    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()  # raise error if status != 2xx
    return resp.json()


def create_stream_and_table_in_kafka_ksql_db():
    # Initialize Kafka client
    kafkaClient = KafkaClient(bootstrap_servers='192.168.88.40:19092, 192.168.88.40:19093')
    kafkaClient.initialize_admin_client()
    kafkaClient.create_topic(topic_name='tts_request_queue_topic', num_partitions=3, replication_factor=1, config={"max.message.bytes": 10485760})
    kafkaClient.create_topic(topic_name='tts_response_queue_topic', num_partitions=3, replication_factor=1, config={"max.message.bytes": 10485760})
    # query = "SELECT * FROM tts_response_table limit 1;"
    print("Executing query to check if tts_response_table exists")
    try:
        # result = run_pull_query(query)
        result = run_ksql_statement("DESCRIBE tts_response_table;")
        print("tts_response_table already exists:", result)
        print("Skipping creation of stream and table.")
    except requests.HTTPError as e:
        print(f"Query failed: {e.response.status_code}")
        print(e.response.text)
        try:
            run_ksql_statement(CREATE_STREAM)
            print("stream created successfully.")
        except requests.HTTPError as e:
            print(f"Failed to create stream: {e.response.status_code}")
            print(e.response.text)
            
        try:   
            run_ksql_statement(CREATE_TABLE)
            print("table created successfully.")
        except requests.HTTPError as e:
            print(f"Failed to create table: {e.response.status_code}")
            print(e.response.text)
            