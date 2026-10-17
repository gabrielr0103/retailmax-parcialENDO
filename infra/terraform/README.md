# Infraestructura de RetailMax con Terraform

Un solo código crea los tres entornos. Lo que es igual en todos (bucket cifrado y privado, rol IAM con los mismos permisos, etiquetas) sale de `main.tf`, y lo que cambia está en un archivo por entorno:

| Entorno | Archivo | Qué tiene además del bucket y el rol |
|---|---|---|
| dev | `envs/dev.tfvars` | Instancia EC2 de trabajo. Los archivos de staging duran 7 días. |
| qa | `envs/qa.tfvars` | Nada más. Los archivos duran 30 días. |
| prod | `envs/prod.tfvars` | Base RDS PostgreSQL multi-AZ. Los archivos duran 90 días. |

## Archivos

- `versions.tf`: versión de Terraform, versión del proveedor de AWS y backend remoto en S3.
- `main.tf`: bucket S3 de staging, rol IAM, EC2 de dev y RDS de prod.
- `variables.tf` y `outputs.tf`.
- `envs/*.tfvars`: valores de cada entorno.
- `.terraform.lock.hcl`: hash exacto del proveedor, para que todos descarguen el mismo binario.
- `tests/`: un plan por entorno contra un AWS simulado. Corre en el CI sin credenciales.

## Por qué los entornos salen idénticos

1. Todos usan el mismo `main.tf`. Una diferencia entre qa y prod solo existe si está escrita en un tfvars, y ese archivo pasa por PR como cualquier código.
2. La versión de Terraform y la del proveedor están fijas, y el lock file amarra el hash del proveedor. El mismo commit da el mismo plan en cualquier máquina.
3. Cada workspace tiene su propio estado en S3. Aplicar en dev no toca qa ni prod.
4. `main.tf` frena el plan si el workspace no coincide con el tfvars, así nadie aplica `prod.tfvars` sobre dev por error.
5. Las pruebas de `tests/` revisan en cada PR que los tres entornos tengan el bucket versionado y privado y el rol del pipeline.

## Comandos

El bucket del estado (`retailmax-terraform-estado`) se crea una sola vez, antes de todo lo demás, porque Terraform necesita dónde guardar el estado. Después, la primera vez:

```bash
cd infra/terraform
terraform init
terraform workspace new dev
terraform workspace new qa
terraform workspace new prod
```

Crear o actualizar un entorno, por ejemplo qa:

```bash
terraform workspace select qa
terraform plan -var-file=envs/qa.tfvars -out=qa.tfplan
terraform apply qa.tfplan
```

Para dev y prod se cambia `qa` por el entorno. Si alguien modifica o borra algo de qa a mano, el mismo `plan` muestra la diferencia y el `apply` lo deja otra vez como dice el código.

Validar sin credenciales de AWS, igual que el CI:

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
TF_WORKSPACE=qa terraform test -filter=tests/qa.tftest.hcl -var-file=envs/qa.tfvars
```

Para eliminar un entorno temporal se selecciona su workspace y se corre `terraform destroy -var-file=envs/dev.tfvars`. La base de prod tiene `deletion_protection`, así que en prod ese comando falla hasta que un PR quite la protección.
