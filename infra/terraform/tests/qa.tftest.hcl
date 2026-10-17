# Plan de qa contra un AWS simulado. Se corre con:
#   TF_WORKSPACE=qa terraform test -filter=tests/qa.tftest.hcl -var-file=envs/qa.tfvars

mock_provider "aws" {
  source = "./tests/mocks"
}

run "base_igual_a_los_otros_entornos" {
  command = plan

  assert {
    condition     = aws_s3_bucket.datos_staging.bucket == "retailmax-staging-datos"
    error_message = "En qa el bucket debe llamarse retailmax-staging-datos"
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
    condition     = aws_iam_role.pipeline.name == "retailmax-qa-pipeline"
    error_message = "Falta el rol del pipeline"
  }
}

run "qa_no_crea_ec2_ni_rds" {
  command = plan

  assert {
    condition     = length(aws_instance.dev) == 0 && length(aws_db_instance.prod) == 0
    error_message = "qa solo lleva bucket y rol"
  }
}
