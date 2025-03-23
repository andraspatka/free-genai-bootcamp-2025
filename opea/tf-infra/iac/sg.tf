resource "aws_security_group" "allow_outbound_https" {
  name        = "${local.environment}-${local.project}-allow-outbound-https"
  description = "Allow outbound HTTPS connections to AWS service endpoints"
  vpc_id      = module.vpc.vpc_id

  # Allow outbound connections on port 443
  egress {
    from_port = 443
    to_port   = 443
    protocol  = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  egress {
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }
}
