terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = "us-east-2"
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "image_bucket" {
  bucket = "labels-generator-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "LabelsGeneratorImages"
    Environment = "Dev"
    Project     = "LabelsGenerator"
  }
}

resource "aws_s3_bucket_public_access_block" "image_bucket" {
  bucket = aws_s3_bucket.image_bucket.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "animal_image" {
  bucket       = aws_s3_bucket.image_bucket.id
  key          = "images/wild-animals.jpeg"
  source       = "${path.module}/wild-animals.jpeg"
  source_hash  = filemd5("${path.module}/wild-animals.jpeg")
  content_type = "image/jpeg"
}

resource "aws_s3_object" "image" {
  bucket       = aws_s3_bucket.image_bucket.id
  key          = "images/city-image.png"
  source       = "${path.module}/city-image.png"
  source_hash  = filemd5("${path.module}/city-image.png")
  content_type = "image/png"
}

output "bucket_name" {
  value = aws_s3_bucket.image_bucket.id
}

output "image_key" {
  value = aws_s3_object.image.key
} 
