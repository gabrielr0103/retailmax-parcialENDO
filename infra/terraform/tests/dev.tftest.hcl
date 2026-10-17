# Plan de dev contra un AWS simulado. Se corre con:
#   TF_WORKSPACE=dev terraform test -filter=tests/dev.tftest.hcl -var-file=envs/dev.tfvars

mock_provider "aws" {
  source = "./tests/mocks"
}

run "base_igual_a_los_otros_entornos" {
  command = plan

  assert {
    condition     = aws_s3_bucket.datos_staging.bucket == "retailmax-dev-datos"
    error_message = "El bucket de dev debe llamarse retailmax-dev-datos"
  }

  assert {
    condition     = aws_s3_bucket_versioning.datos_staging.versioning_configuration[0].status == "Enabled"
    error_message = "El bucket debe tener versionamiento"
  }

  assert {
    condition     = aws_s3_bucket_public_access_block.datos_staging.block_public_policy
    error_message = "El bucket no puede ser público"
  }

  assert {
    condition     = aws_iam_role.pipeline.name == "retailmax-dev-pipeline"
    error_message = "Falta el rol del pipeline"
  }
}

run "dev_tiene_ec2_y_no_rds" {
  command = plan

  assert {
    condition     = length(aws_instance.dev) == 1
    error_message = "dev debe crear la instancia EC2"
  }

  assert {
    condition     = aws_instance.dev[0].metadata_options[0].http_tokens == "required"
    error_message = "La instancia debe exigir IMDSv2"
  }

  assert {
    condition     = length(aws_db_instance.prod) == 0
    error_message = "dev no debe crear RDS"
  }
}

run "tfvars_de_otro_entorno_se_rechaza" {
  command = plan

  variables {
    entorno = "prod"
  }

  expect_failures = [terraform_data.verificar_workspace]
}
