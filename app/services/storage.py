from __future__ import annotations
import boto3
from botocore.client import Config
from app.core.settings import settings

def _s3():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
        config=Config(signature_version="s3v4"),
    )

def presign_put(key: str, content_type: str = "application/pdf", expires: int = 900) -> str:
    return _s3().generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": key, "ContentType": content_type},
        ExpiresIn=expires,
    )

def presign_get(key: str, expires: int = 900) -> str:
    return _s3().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": key},
        ExpiresIn=expires,
    )

def head_bucket() -> bool:
    try:
        _s3().head_bucket(Bucket=settings.S3_BUCKET)
        return True
    except Exception:
        return False
