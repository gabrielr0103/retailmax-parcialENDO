# Versión de Terraform y del proveedor de AWS que usa todo el equipo.
# Fijarlas evita que dos personas generen planes distintos con el mismo código.
terraform {
  required_version = ">= 1.10.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # El estado vive en S3 y cada workspace tiene el suyo (env:/dev, env:/qa, env:/prod).
  # use_lockfile bloquea el estado mientras alguien aplica cambios.
  backend "s3" {
    bucket       = "retailmax-terraform-estado"
    key          = "retailmax-dataops/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}
