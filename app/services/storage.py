from __future__ import annotations
import boto3
from botocore.client import Config
from app.core.settings import settings
from urllib.parse import urlparse, urlunparse

def _s3():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )

def _rewrite_public(url: str) -> str:
    pe = settings.S3_PUBLIC_ENDPOINT
    if not pe:
        return url
    pub, u = urlparse(pe), urlparse(url)
    return urlunparse(u._replace(scheme=pub.scheme, netloc=pub.netloc))

def presign_put(key: str, content_type: str = "application/pdf", expires: int = 900) -> str:
    # ВАЖНО: НЕ переписываем на S3_PUBLIC_ENDPOINT!
    url = _s3().generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": key, "ContentType": content_type},
        ExpiresIn=expires,
    )
    return url  # <-- без _rewrite_public

def presign_get(key: str, *, filename: str | None = None, expires: int = 900) -> str:
    disp = f'inline; filename="{filename or key.split("/")[-1]}"'
    url = _s3().generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.S3_BUCKET,
            "Key": key,
            "ResponseContentType": "application/pdf",
            "ResponseContentDisposition": disp,
            "ResponseCacheControl": "private, max-age=300",
        },
        ExpiresIn=expires,
    )
    return _rewrite_public(url)  # <-- переписываем только GET

def head_bucket() -> bool:
    try:
        _s3().head_bucket(Bucket=settings.S3_BUCKET)
        return True
    except Exception:
        return False
