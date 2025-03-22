
resource "aws_autoscaling_group" "asg" {
  launch_configuration = aws_launch_configuration.launch_config.id
  min_size             = 0
  max_size             = 1
  desired_capacity     = 0
  vpc_zone_identifier  = ["subnet-12345678"] # Replace with your subnet ID

  dynamic "tag" {
    for_each = local.common_tags
    content {
      key                 = each.key
      value               = each.value
      propagate_at_launch = true
    }

  }

  lifecycle {
    ignore_changes = [desired_capacity]
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

# Inspiration for running vllm on EC2
# https://aws.amazon.com/blogs/machine-learning/serving-llms-using-vllm-and-amazon-ec2-instances-with-aws-ai-chips/
resource "aws_launch_configuration" "launch_config" {
  name = "${local.environment}-${local.project}-launch-configuration"
  # Deep Learning AMI Neuron (Ubuntu 22.04) 20241221
  image_id      = "ami-05f04e4216ff500c0"
  instance_type = "inf2.xlarge"

  spot_price = "0.50" # Set your desired max spot price

  iam_instance_profile = aws_iam_instance_profile.ssm_instance_profile.id

  user_data = <<-EOF
              #!/bin/bash
              cat > /app/Dockerfile <<'DOCKERFILE_EOF'
              # default base image
              ARG BASE_IMAGE="public.ecr.aws/neuron/pytorch-inference-neuronx:2.1.2-neuronx-py310-sdk2.20.0-ubuntu20.04"
              FROM \$BASE_IMAGE
              RUN echo "Base image is \$BASE_IMAGE"
              # Install some basic utilities
              RUN apt-get update && \\
                  apt-get install -y \\
                      git \\
                      python3 \\
                      python3-pip \\
                      ffmpeg libsm6 libxext6 libgl1
              ### Mount Point ###
              # When launching the container, mount the code directory to /app
              ARG APP_MOUNT=/app
              VOLUME [ \$APP_MOUNT ]
              WORKDIR \$APP_MOUNT/vllm
              RUN python3 -m pip install --upgrade pip
              RUN python3 -m pip install --no-cache-dir fastapi ninja tokenizers pandas
              RUN python3 -m pip install sentencepiece transformers==4.36.2 -U
              RUN python3 -m pip install transformers-neuronx --extra-index-url=https://pip.repos.neuron.amazonaws.com -U
              RUN python3 -m pip install --pre neuronx-cc==2.15.* --extra-index-url=https://pip.repos.neuron.amazonaws.com -U
              ENV VLLM_TARGET_DEVICE neuron
              RUN git clone https://github.com/vllm-project/vllm.git && \\
                  cd vllm && \\
                  git checkout v0.6.2 && \\
                  python3 -m pip install -U \\
                      cmake>=3.26 ninja packaging setuptools-scm>=8 wheel jinja2 \\
                      -r requirements-neuron.txt && \\
                  pip install --no-build-isolation -v -e . && \\
                  pip install --upgrade triton==3.0.0
              CMD ["/bin/bash"]
              DOCKERFILE_EOF
              EOF

  ebs_block_device {
    device_name           = "/dev/sdh"
    volume_size           = 100
    volume_type           = "gp3"
    delete_on_termination = true
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
  start_time             = "2025-03-23T00:00:00Z" # UTC time for midnight
  recurrence             = "cron(0 0 * * ? *)"    # Every day at midnight UTC
}
