output "ecr_repository_url" {
  description = "The URL of the created ECR Repository"
  value       = aws_ecr_repository.app_ecr.repository_url
}

output "aws_region" {
  description = "The AWS Region to configure in GitHub Secrets"
  value       = var.aws_region
}

output "github_actions_access_key_id" {
  description = "Access Key ID for GitHub Actions"
  value       = aws_iam_access_key.github_actions_key.id
}

output "github_actions_secret_access_key" {
  description = "Secret Access Key for GitHub Actions"
  value       = aws_iam_access_key.github_actions_key.secret
  sensitive   = true
}
