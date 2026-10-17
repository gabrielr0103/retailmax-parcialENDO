variable "entorno" {
  description = "Entorno que se crea. Tiene que coincidir con el workspace activo."
  type        = string

  validation {
    condition     = contains(["dev", "qa", "prod"], var.entorno)
    error_message = "El entorno debe ser dev, qa o prod."
  }
}

variable "region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "dias_retencion_staging" {
  description = "Días que se guardan los archivos de la carpeta staging/ del bucket antes de borrarse"
  type        = number
  default     = 30
}

variable "crear_ec2_dev" {
  description = "Crea la instancia EC2 de trabajo. Solo se activa en dev."
  type        = bool
  default     = false
}

variable "tipo_instancia_dev" {
  description = "Tipo de la instancia EC2 de dev"
  type        = string
  default     = "t3.micro"
}

variable "crear_rds_prod" {
  description = "Crea la base de datos RDS. Solo se activa en prod."
  type        = bool
  default     = false
}

variable "clase_rds" {
  description = "Clase de la instancia RDS"
  type        = string
  default     = "db.t4g.micro"
}

variable "almacenamiento_rds_gb" {
  description = "Almacenamiento inicial de la base de datos, en GB"
  type        = number
  default     = 20
}
