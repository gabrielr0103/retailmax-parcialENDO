# Infraestructura de RetailMax. El mismo código crea dev, qa y prod:
# lo que cambia entre entornos está en envs/<entorno>.tfvars.

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Proyecto      = "RetailMax"
      Entorno       = var.entorno
      GestionadoPor = "Terraform"
    }
  }
}

locals {
  nombre = "retailmax-${var.entorno}"
  # En los nombres de los recursos qa aparece como staging, igual que en config/qa.yaml
  sufijo_bucket = var.entorno == "qa" ? "staging" : var.entorno
}

# Frena el plan si alguien usa el tfvars de un entorno en el workspace de otro.
resource "terraform_data" "verificar_workspace" {
  lifecycle {
    precondition {
      condition     = terraform.workspace == var.entorno
      error_message = "El workspace activo no coincide con var.entorno. Corre: terraform workspace select ${var.entorno}"
    }
  }
}

# ---------------------------------------------------------------
# S3: datos de staging del pipeline
# ---------------------------------------------------------------

resource "aws_s3_bucket" "datos_staging" {
  bucket = "retailmax-${local.sufijo_bucket}-datos"
}

resource "aws_s3_bucket_versioning" "datos_staging" {
  bucket = aws_s3_bucket.datos_staging.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "datos_staging" {
  bucket = aws_s3_bucket.datos_staging.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "datos_staging" {
  bucket = aws_s3_bucket.datos_staging.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "datos_staging" {
  bucket = aws_s3_bucket.datos_staging.id

  rule {
    id     = "borrar-staging-viejo"
    status = "Enabled"

    filter {
      prefix = "staging/"
    }

    expiration {
      days = var.dias_retencion_staging
    }

    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
}

# ---------------------------------------------------------------
# IAM: rol del pipeline con permisos restringidos
# ---------------------------------------------------------------

data "aws_iam_policy_document" "asumir_rol" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "pipeline" {
  name                 = "${local.nombre}-pipeline"
  description          = "Rol del pipeline de datos: solo lee y escribe en el bucket de su entorno"
  assume_role_policy   = data.aws_iam_policy_document.asumir_rol.json
  max_session_duration = 3600
}

# Sin permiso de borrar, sin acceso a otros buckets y sin acciones de IAM.
data "aws_iam_policy_document" "acceso_bucket" {
  statement {
    sid       = "ListarSoloSuBucket"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.datos_staging.arn]
  }

  statement {
    sid       = "LeerYEscribirObjetos"
    actions   = ["s3:GetObject", "s3:PutObject"]
    resources = ["${aws_s3_bucket.datos_staging.arn}/*"]
  }

  statement {
    sid       = "NegarSinTLS"
    effect    = "Deny"
    actions   = ["s3:*"]
    resources = [aws_s3_bucket.datos_staging.arn, "${aws_s3_bucket.datos_staging.arn}/*"]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_iam_role_policy" "acceso_bucket" {
  name   = "acceso-bucket-${var.entorno}"
  role   = aws_iam_role.pipeline.id
  policy = data.aws_iam_policy_document.acceso_bucket.json
}

resource "aws_iam_instance_profile" "pipeline" {
  name = "${local.nombre}-pipeline"
  role = aws_iam_role.pipeline.name
}

# ---------------------------------------------------------------
# EC2: máquina de trabajo de DEV
# ---------------------------------------------------------------

data "aws_ami" "amazon_linux" {
  count       = var.crear_ec2_dev ? 1 : 0
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

resource "aws_instance" "dev" {
  count = var.crear_ec2_dev ? 1 : 0

  ami                  = data.aws_ami.amazon_linux[0].id
  instance_type        = var.tipo_instancia_dev
  iam_instance_profile = aws_iam_instance_profile.pipeline.name

  # Exige IMDSv2 para pedir las credenciales temporales del rol
  metadata_options {
    http_tokens = "required"
  }

  root_block_device {
    volume_size = 20
    encrypted   = true
  }

  tags = {
    Name = "${local.nombre}-trabajo"
  }
}

# ---------------------------------------------------------------
# RDS: base de datos de PROD
# ---------------------------------------------------------------

data "aws_vpc" "principal" {
  default = true
}

data "aws_subnets" "principal" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.principal.id]
  }
}

resource "aws_db_subnet_group" "prod" {
  count      = var.crear_rds_prod ? 1 : 0
  name       = "${local.nombre}-bd"
  subnet_ids = data.aws_subnets.principal.ids
}

resource "aws_security_group" "bd" {
  count       = var.crear_rds_prod ? 1 : 0
  name        = "${local.nombre}-bd"
  description = "PostgreSQL accesible solo desde la VPC"
  vpc_id      = data.aws_vpc.principal.id

  ingress {
    description = "PostgreSQL desde la VPC"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.principal.cidr_block]
  }
}

resource "aws_db_instance" "prod" {
  count = var.crear_rds_prod ? 1 : 0

  identifier            = "${local.nombre}-bd"
  engine                = "postgres"
  engine_version        = "16"
  instance_class        = var.clase_rds
  allocated_storage     = var.almacenamiento_rds_gb
  max_allocated_storage = 100
  db_name               = "retailmax_prod"
  username              = "retailmax_admin"

  # La contraseña la genera y la guarda Secrets Manager; no queda en el código ni en el estado
  manage_master_user_password = true

  db_subnet_group_name   = aws_db_subnet_group.prod[0].name
  vpc_security_group_ids = [aws_security_group.bd[0].id]
  publicly_accessible    = false
  storage_encrypted      = true
  multi_az               = true

  backup_retention_period   = 7
  deletion_protection       = true
  skip_final_snapshot       = false
  final_snapshot_identifier = "${local.nombre}-bd-final"
}
