provider "aws" {
  region = "eu-central-1"
}

# You cannot create a new backend by simply defining this and then
# immediately proceeding to "terraform apply". The S3 backend must
# be bootstrapped according to the simple yet essential procedure in
# https://github.com/cloudposse/terraform-aws-tfstate-backend#usage
module "terraform_state_backend" {
  source     = "cloudposse/tfstate-backend/aws"
  version    = "1.5.0"
  stage      = local.environment
  name       = local.project
  attributes = ["state"]

  terraform_backend_config_file_path = "."
  terraform_backend_config_file_name = "backend.tf"
  force_destroy                      = false
}


locals {
  cidr        = "10.0.0.0/24"
  environment = "poc"
  project     = "free-genai-bootcamp"
  common_tags = {
    Terraform   = "true"
    Environment = local.environment
    Project     = local.project
  }
}
