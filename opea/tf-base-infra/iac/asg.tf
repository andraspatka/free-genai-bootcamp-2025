
resource "aws_autoscaling_group" "asg" {
  name = "${local.environment}-${local.project}-asg"
  launch_template {
    id      = aws_launch_template.launch_template.id
    version = "$Latest"
  }
  min_size            = 0
  max_size            = 1
  desired_capacity    = 0
  vpc_zone_identifier = [module.vpc.public_subnets[0]]

  dynamic "tag" {
    for_each = local.common_tags
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }

  }

  lifecycle {
    ignore_changes = [desired_capacity]
  }
}

resource "aws_security_group" "allow_outbound_https" {
  name        = "${local.environment}-${local.project}-allow-outbound-https"
  description = "Allow outbound HTTPS connections to AWS service endpoints"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

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

resource "aws_iam_role" "ssm_role" {
  name = "${local.environment}-${local.project}-ssm-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Effect = "Allow"
        Sid    = ""
      },
    ]
  })
}
resource "aws_iam_role_policy_attachment" "ssm_role_policy" {
  role       = aws_iam_role.ssm_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_policy" "ssm_parameter_policy" {
  name = "${local.environment}-${local.project}-ssm-parameter-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter"
        ]
        Resource = [aws_ssm_parameter.hf_token.arn]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = ["arn:aws:kms:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:key/aws/ssm"]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ssm_parameter_policy" {
  policy_arn = aws_iam_policy.ssm_parameter_policy.arn
  role       = aws_iam_role.ssm_role.name
}

resource "aws_ssm_parameter" "hf_token" {
  name  = "/${local.environment}-${local.project}/hf-token"
  type  = "SecureString"
  value = "dummy-value"

  lifecycle {
    ignore_changes = [value]
  }
}

# Inspiration for running vllm on EC2
# https://aws.amazon.com/blogs/machine-learning/serving-llms-using-vllm-and-amazon-ec2-instances-with-aws-ai-chips/
resource "aws_launch_template" "launch_template" {
  name = "${local.environment}-${local.project}-launch-template"
  # Deep Learning AMI Neuron (Ubuntu 22.04) 20241221
  image_id      = "ami-05f04e4216ff500c0"
  instance_type = "inf2.xlarge"

  key_name = "genai-test-ssh-keypair"

  instance_market_options {
    market_type = "spot"
    spot_options {
      max_price = "0.50"
    }
  }

  iam_instance_profile {
    name = aws_iam_instance_profile.ssm_instance_profile.name
  }

  user_data = base64encode(templatefile("${path.module}/user_data.tftpl", {
    environment = local.environment
    project     = local.project
  }))

  block_device_mappings {
    device_name = "/dev/sdh"
    ebs {
      volume_size           = 100
      volume_type           = "gp3"
      delete_on_termination = true
    }
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_put_response_hop_limit = 1
    http_tokens                 = "required"
  }

  network_interfaces {
    associate_public_ip_address = true
    security_groups             = [aws_security_group.allow_outbound_https.id]
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_iam_instance_profile" "ssm_instance_profile" {
  name = "${local.environment}-${local.project}-ssm-instance-profile"
  role = aws_iam_role.ssm_role.name
}

resource "aws_autoscaling_schedule" "scale_down_schedule" {
  autoscaling_group_name = aws_autoscaling_group.asg.name
  scheduled_action_name  = "${local.environment}-${local.project}-scale-down-midnight"
  desired_capacity       = 0
  start_time             = "2025-03-24T00:00:00Z" # UTC time for midnight
  recurrence             = "0 0 * * *"            # Every day at midnight UTC
}
