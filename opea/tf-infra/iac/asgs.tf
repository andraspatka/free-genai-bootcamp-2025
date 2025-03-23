
resource "aws_autoscaling_group" "asg" {
  for_each = local.asgs
  name     = "${local.environment}-${local.project}-${each.key}-asg"
  launch_template {
    id      = aws_launch_template.launch_template[each.key].id
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

# Inspiration for running vllm on EC2
# https://aws.amazon.com/blogs/machine-learning/serving-llms-using-vllm-and-amazon-ec2-instances-with-aws-ai-chips/
resource "aws_launch_template" "launch_template" {
  for_each = local.asgs
  name     = "${local.environment}-${local.project}-${each.key}-launch-template"
  # Deep Learning AMI Neuron (Ubuntu 22.04) 20241221
  image_id      = each.value.ami
  instance_type = each.value.instance_type

  instance_market_options {
    market_type = "spot"
    spot_options {
      max_price = "0.50"
    }
  }

  iam_instance_profile {
    name = aws_iam_instance_profile.ssm_instance_profile.name
  }

  user_data = base64encode(templatefile("${path.module}/scripts/user_data_${each.key}.tftpl", {
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

resource "aws_autoscaling_schedule" "scale_down_schedule" {
  for_each               = local.asgs
  autoscaling_group_name = aws_autoscaling_group.asg[each.key].name
  scheduled_action_name  = "${local.environment}-${local.project}-${each.key}-scale-down-midnight"
  desired_capacity       = 0
  start_time             = "2025-03-24T00:00:00Z" # UTC time for midnight
  recurrence             = "0 0 * * *"            # Every day at midnight UTC
}

resource "aws_ssm_parameter" "hf_token" {
  name  = "/${local.environment}-${local.project}/hf-token"
  type  = "SecureString"
  value = "dummy-value"

  lifecycle {
    ignore_changes = [value]
  }
}
