data "aws_availability_zones" "available_azs" {
  state = "available"

  filter {
    name   = "zone-type"
    values = ["availability-zone"]
  }
}
