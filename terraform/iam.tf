# 1. Dedicated IAM User for GitHub Actions CI/CD
resource "aws_iam_user" "github_actions_user" {
  name = "github-actions-frontdeskai"
}

# 2. Access Keys for this user
resource "aws_iam_access_key" "github_actions_key" {
  user = aws_iam_user.github_actions_user.name
}

# 3. Policy granting push permissions to the ECR repository
resource "aws_iam_user_policy" "ecr_push_policy" {
  name = "FrontDeskAI-ECR-Push-Policy"
  user = aws_iam_user.github_actions_user.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ecr:GetAuthorizationToken"
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = aws_ecr_repository.app_ecr.arn
      }
    ]
  })
}
