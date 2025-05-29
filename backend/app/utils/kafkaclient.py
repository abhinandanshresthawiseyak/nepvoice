from confluent_kafka import Producer, Consumer
import json, socket, time
from confluent_kafka.admin import AdminClient, NewTopic

class KafkaClient:
    def __init__(self, bootstrap_servers: str, timeout: int = 5):
        self.bootstrap_servers = bootstrap_servers
        self.timeout = timeout  # Timeout in seconds
    
    def initialize_producer(self):
        try:
            self.producer_conf = {
                'bootstrap.servers': self.bootstrap_servers,
                'retries': 5,
                'retry.backoff.ms': 500,
                'socket.timeout.ms': self.timeout * 1000,  # Convert to milliseconds
                'api.version.request.timeout.ms': self.timeout * 1000,
                "message.max.bytes": 10485760,
                "max.partition.fetch.bytes": 10485760   # Max per-partition bytes
            }
            self.producer = Producer(self.producer_conf)
            self.check_kafka_connection()
            print("✅ Producer initialized successfully")
        except Exception as e:
            raise Exception(f"Failed to initialize producer: {e}")
        
    def initialize_consumer(self, group_id: str = 'default-group', auto_offset_reset: str = 'earliest'):
        try:
            """Initialize Kafka consumer with configuration"""
            self.consumer_conf = {
                'bootstrap.servers': self.bootstrap_servers,
                'group.id': group_id,
                'auto.offset.reset': auto_offset_reset,
                "fetch.max.bytes": 10485760
            }
            self.consumer = Consumer(self.consumer_conf)
            self.check_kafka_connection()
            print("✅ Consumer initialized successfully")
        except Exception as e:
            raise Exception(f"Failed to initialize consumer: {e}")
        
    def initialize_admin_client(self):
        try:
            self.admin_client = AdminClient({
                "bootstrap.servers": self.bootstrap_servers,
            })
            self.check_kafka_connection()
            print("✅ Admin Client initialized successfully")
        except Exception as e:
            raise Exception(f"Failed to initialize producer: {e}")
    
    def create_topic(self, topic_name: str, num_partitions: int = 1, replication_factor: int = 1, config: dict = None):
        topic_name = topic_name.strip()
        num_partitions = num_partitions if num_partitions > 0 else 1
        replication_factor = replication_factor if replication_factor > 0 else 1

        # Check existing topics
        metadata = self.admin_client.list_topics(timeout=10)
        existing_topics = metadata.topics.keys()

        if topic_name not in existing_topics:
            new_topic = NewTopic(topic=topic_name,
                                num_partitions=num_partitions,
                                replication_factor=replication_factor, config=config)
            fs = self.admin_client.create_topics([new_topic])
            for topic, f in fs.items():
                try:
                    f.result()
                    print(f"Topic {topic} created successfully.")
                except Exception as e:
                    print(f"Failed to create topic {topic}: {e}")
        else:
            print(f"Topic {topic_name} already exists. Skipping creation.")
    
    def delivery_report(self, err, msg):
        if err is not None:
            print(f"Delivery failed: {err}")
        else:
            print(f"Delivered message to {msg.topic()} [{msg.partition()}]")
    
    def check_kafka_connection(self) -> bool:
        """Check if any Kafka server is reachable"""
        servers = [server.strip() for server in self.bootstrap_servers.split(',')]
        connection_errors = []
        
        for server in servers:
            try:
                # Parse host and port
                host, port = server.split(':')
                port = int(port)
                
                # Test socket connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    print(f"✅ Successfully connected to {server}")
                    return True  # Return True if any server is reachable
                else:
                    error_msg = f"Connection refused to {server}"
                    print(f"❌ {error_msg}")
                    connection_errors.append(error_msg)
                    
            except Exception as e:
                error_msg = f"Connection check failed for {server}: {e}"
                print(f"❌ {error_msg}")
                connection_errors.append(error_msg)
                
        raise Exception(f"All Kafka servers are unreachable. Errors: {'; '.join(connection_errors)}")