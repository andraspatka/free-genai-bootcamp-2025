resource "aws_s3_bucket" "data_bucket" {
  bucket = "${local.environment}-${local.project}-data"

  tags = merge(
    local.common_tags,
    {
      Name = "${local.environment}-${local.project}-data"
    }
  )
}

resource "aws_s3_bucket_ownership_controls" "data_bucket_ownership" {
  bucket = aws_s3_bucket.data_bucket.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "data_bucket_acl" {
  depends_on = [aws_s3_bucket_ownership_controls.data_bucket_ownership]

  bucket = aws_s3_bucket.data_bucket.id
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "data_bucket_public_access_block" {
  bucket = aws_s3_bucket.data_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "data_bucket_versioning" {
  bucket = aws_s3_bucket.data_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_bucket_encryption" {
  bucket = aws_s3_bucket.data_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
