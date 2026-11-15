terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# The AWS provider uses standard AWS credential discovery.
# To point to local MiniStack/LocalStack, simply set AWS_ENDPOINT_URL="http://localhost:4566" in your environment.
provider "aws" {
  region = var.aws_region
}

# 1. Private ECR Repository
resource "aws_ecr_repository" "app_ecr" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project   = "FrontDeskAI"
    ManagedBy = "Terraform"
  }
}

# 2. Lifecycle Policy (Keep last 10 images to save storage costs)
resource "aws_ecr_lifecycle_policy" "cleanup_policy" {
  repository = aws_ecr_repository.app_ecr.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images, expire older ones"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
