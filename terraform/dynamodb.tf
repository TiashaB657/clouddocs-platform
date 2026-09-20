resource "aws_dynamodb_table" "metadata" {
  name         = "CloudDocsMetadata"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "file_name"

  attribute {
    name = "file_name"
    type = "S"
  }

  tags = {
    Name = "${var.project_name}-DynamoDB"
  }
}