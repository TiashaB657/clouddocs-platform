resource "aws_lambda_function" "clouddocs" {
  function_name = "${var.project_name}-Lambda"

  filename         = "${path.module}/lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda.zip")

  handler = "lambda_function.lambda_handler"
  runtime = "python3.12"

  role = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.metadata.name
      S3_BUCKET      = aws_s3_bucket.clouddocs.bucket
    }
  }

  tags = {
    Name = "${var.project_name}-Lambda"
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy.lambda_cloud_docs_access
  ]
}
resource "aws_apigatewayv2_api" "clouddocs" {
  name          = "${var.project_name}-API"
  protocol_type = "HTTP"

  tags = {
    Name = "${var.project_name}-API"
  }
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id = aws_apigatewayv2_api.clouddocs.id

  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.clouddocs.invoke_arn
  integration_method = "POST"

  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "lambda" {
  api_id = aws_apigatewayv2_api.clouddocs.id

  route_key = "GET /documents"

  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id = aws_apigatewayv2_api.clouddocs.id

  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id = "AllowAPIGatewayInvoke"

  action = "lambda:InvokeFunction"

  function_name = aws_lambda_function.clouddocs.function_name

  principal = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.clouddocs.execution_arn}/*/*"
}
output "api_gateway_url" {
  value = aws_apigatewayv2_api.clouddocs.api_endpoint
}