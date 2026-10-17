# Versión de Terraform y del proveedor de AWS que usa todo el equipo.
# Fijarlas evita que dos personas generen planes distintos con el mismo código.
terraform {
  required_version = ">= 1.9.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
