output "bucket_datos_staging" {
  description = "Bucket de datos de staging del entorno"
  value       = aws_s3_bucket.datos_staging.bucket
}

output "rol_pipeline" {
  description = "ARN del rol que usa el pipeline"
  value       = aws_iam_role.pipeline.arn
}

output "ec2_dev_id" {
  description = "ID de la instancia de dev (null en qa y prod)"
  value       = one(aws_instance.dev[*].id)
}

output "rds_prod_endpoint" {
  description = "Host de la base de datos de prod (null en dev y qa)"
  value       = one(aws_db_instance.prod[*].address)
}
