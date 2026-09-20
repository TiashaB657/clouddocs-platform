resource "aws_s3_bucket" "clouddocs" {
  bucket = "clouddocs-platform-tiasha-mumbai"

  tags = {
    Name = "${var.project_name}-S3"
  }
}

resource "aws_s3_bucket_public_access_block" "clouddocs" {
  bucket = aws_s3_bucket.clouddocs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}