module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.19.0"

  name                 = "${local.environment}-${local.project}-vpc"
  cidr                 = local.cidr
  azs                  = slice(data.aws_availability_zones.available_azs.names, 0, 2)
  enable_dns_support   = true
  enable_dns_hostnames = true
  enable_nat_gateway   = false

  public_subnets = [cidrsubnet(local.cidr, 2, 1)]

  tags = local.common_tags
}
