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


resource "aws_iam_instance_profile" "ssm_instance_profile" {
  name = "${local.environment}-${local.project}-ssm-instance-profile"
  role = aws_iam_role.ssm_role.name
}
