# Respuestas fijas del AWS simulado. Con esto el plan corre sin credenciales.
mock_data "aws_iam_policy_document" {
  defaults = {
    json = "{\"Version\":\"2012-10-17\",\"Statement\":[]}"
  }
}

mock_data "aws_ami" {
  defaults = {
    id = "ami-0123456789abcdef0"
  }
}

mock_data "aws_vpc" {
  defaults = {
    cidr_block = "172.31.0.0/16"
  }
}
