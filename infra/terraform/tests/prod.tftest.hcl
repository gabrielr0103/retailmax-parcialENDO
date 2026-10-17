# Plan de prod contra un AWS simulado. Se corre con:
#   TF_WORKSPACE=prod terraform test -filter=tests/prod.tftest.hcl -var-file=envs/prod.tfvars

mock_provider "aws" {
  source = "./tests/mocks"
}

run "base_igual_a_los_otros_entornos" {
  command = plan

  assert {
    condition     = aws_s3_bucket.datos_staging.bucket == "retailmax-prod-datos"
    error_message = "El bucket de prod debe llamarse retailmax-prod-datos"
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
    condition     = aws_iam_role.pipeline.name == "retailmax-prod-pipeline"
    error_message = "Falta el rol del pipeline"
  }
}

run "prod_tiene_rds_protegida_y_no_ec2" {
  command = plan

  assert {
    condition     = length(aws_instance.dev) == 0
    error_message = "prod no debe crear la instancia de trabajo"
  }

  assert {
    condition     = length(aws_db_instance.prod) == 1
    error_message = "prod debe crear la base RDS"
  }

  assert {
    condition = alltrue([
      aws_db_instance.prod[0].multi_az,
      aws_db_instance.prod[0].storage_encrypted,
      aws_db_instance.prod[0].deletion_protection,
      !aws_db_instance.prod[0].publicly_accessible,
    ])
    error_message = "La base de prod debe ser multi-AZ, cifrada, protegida contra borrado y privada"
  }
}
