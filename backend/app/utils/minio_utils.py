import boto3, io, os
from botocore.exceptions import BotoCoreError, ClientError
from botocore.client import Config

# Configuration (you can externalize this)
MINIO_ENDPOINT = "http://192.168.88.40:7814"  # or "http://minio:9000" inside Docker network
MINIO_ACCESS_KEY = "nepvoice"
MINIO_SECRET_KEY = "nepvoice"
MINIO_REGION = "us-east-1"

def upload_audio_to_minio(
    audio_bytes: bytes,
    bucket_name: str,
    object_name: str,
    content_type: str = "audio/wav"
):
    """
    Uploads a file to a MinIO (S3-compatible) bucket.

    Args:
        file_path (str): Local path to the file.
        bucket_name (str): Name of the bucket.
        object_name (str, optional): Target object key in the bucket. Defaults to filename.
        content_type (str, optional): MIME type of the object. Defaults to binary.
        make_public (bool, optional): If True, sets the object ACL to public-read.

    Returns:
        str: The object URL or key if upload succeeds.
    """
    try:
        s3_client = boto3.client(
            "s3",
            endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            region_name=MINIO_REGION,
            config=Config(signature_version="s3v4")
        )

        # Ensure bucket exists (you can comment this out if already created)
        try:
            s3_client.head_bucket(Bucket=bucket_name)
        except ClientError:
            s3_client.create_bucket(Bucket=bucket_name)

        # Upload file
        s3_client.upload_fileobj(
            Fileobj=io.BytesIO(audio_bytes),
            Bucket=bucket_name,
            Key=object_name,
            ExtraArgs={"ContentType": content_type}
        )

        return object_name

    except (BotoCoreError, ClientError) as e:
        print(f"❌ MinIO upload error: {e}")
        return None

def read_object_from_minio(bucket_name: str, object_name: str):
    """
    Downloads an object from a MinIO bucket and returns it as bytes.

    Args:
        bucket_name (str): Name of the bucket.
        object_name (str): Key of the object in the bucket.

    Returns:
        bytes or None: The object content as bytes if successful, None otherwise.
    """
    try:
        s3_client = boto3.client(
            "s3",
            endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            region_name=MINIO_REGION,
            config=Config(signature_version="s3v4")
        )

        response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        data = response['Body'].read()
        return data

    except (BotoCoreError, ClientError) as e:
        print(f"❌ MinIO download error: {e}")
        return None