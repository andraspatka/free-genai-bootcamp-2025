terraform {
  required_version = ">= 1.0.0"

  backend "s3" {
    region  = "eu-central-1"
    bucket  = "poc-free-genai-bootcamp-state"
    key     = "terraform.tfstate"
    profile = ""
    encrypt = "true"

    dynamodb_table = "poc-free-genai-bootcamp-state-lock"
  }
}
