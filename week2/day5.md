# Día 5: CI/CD con GitHub Actions

## Del desarrollo local al DevOps profesional

¡Bienvenido al último día de la Semana 2! Hoy implementamos el ciclo DevOps completo: desde el control de versiones hasta el despliegue continuo y el desmontaje de la infraestructura. Configurarás GitHub Actions para desplegar automáticamente tu Gemelo Digital cada vez que hagas push de código, gestionarás múltiples entornos desde una interfaz web y te asegurarás de que todo pueda eliminarse de forma limpia al terminar. ¡Así es como los equipos profesionales gestionan la infraestructura en producción!

## Qué aprenderás hoy

- **Git y GitHub** - Control de versiones para infraestructura y código
- **Gestión de estado remoto** - Estado de Terraform en S3 con bloqueo
- **GitHub Actions** - Pipelines CI/CD para despliegues automáticos
- **GitHub Secrets** - Gestión segura de credenciales
- **Autenticación OIDC** - Autenticación moderna en AWS sin claves persistentes
- **Flujos multi-entorno** - Despliegues automáticos y manuales
- **Limpieza de infraestructura** - Estrategias de desmontaje completo

## Parte 1: Limpia la infraestructura existente

Antes de configurar CI/CD, eliminemos todos los entornos existentes para empezar de cero.

### Paso 1: Destruye todos los entornos

Utilizaremos los scripts de destrucción creados el Día 4 para limpiar los entornos dev, test y prod.

**Mac/Linux:**
```bash

# Destruir entorno dev
./scripts/destroy.sh dev

# Destruir entorno test  
./scripts/destroy.sh test

# Destruir entorno prod (si lo creaste)
./scripts/destroy.sh prod
```

**Windows (PowerShell):**
```powershell

# Destruir entorno dev
.\scripts\destroy.ps1 -Environment dev

# Destruir entorno test
.\scripts\destroy.ps1 -Environment test

# Destruir entorno prod (si lo creaste)
.\scripts\destroy.ps1 -Environment prod
```

Cada destrucción tomará 5-10 minutos ya que se eliminan las distribuciones de CloudFront.

### Paso 2: Limpia los workspaces de Terraform

Después de destruir los recursos, elimina los workspaces:

```bash
cd terraform

# Cambia al workspace por defecto
terraform workspace select default

# Elimina los workspaces
terraform workspace delete dev
terraform workspace delete test
terraform workspace delete prod

cd ..
```

### Paso 3: Verifica el estado limpio

1. Revisa la consola de AWS para asegurarte de que no quedan recursos relacionados con twin:
   - Lambda: No debe haber funciones comenzando con `twin-`
   - S3: No debe haber buckets comenzando con `twin-`
   - API Gateway: No debe haber APIs comenzando con `twin-`
   - CloudFront: No debe haber distribuciones de twin

✅ **Punto de control**: ¡Tu cuenta de AWS está limpia y lista para despliegue CI/CD!

## Parte 2: Inicializa el repositorio Git

### Paso 1: Crea `.gitignore`

Asegúrate de que tu `.gitignore` en la raíz del proyecto (`twin/.gitignore`) sea completo:

```gitignore
# Terraform
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl
terraform.tfstate.d/
*.tfvars.secret

# Paquetes Lambda
lambda-deployment.zip
lambda-package/

# Almacenamiento de memoria (contiene el historial de conversaciones)
memory/

# Archivos de entorno
.env
.env.*
!.env.example

# Node
node_modules/
out/
.next/
*.log

# Python
__pycache__/
*.pyc
.venv/
venv/

# IDE
.vscode/
.idea/
*.swp
.DS_Store
Thumbs.db

# AWS
.aws/
```

### Paso 2: Crea archivo de entorno de ejemplo

Crea `.env.example` para ayudar a otros a entender las variables de entorno necesarias:

```bash
# Configuración de AWS
AWS_ACCOUNT_ID=tu_ID_de_cuenta_de_12_dígitos
DEFAULT_AWS_REGION=us-east-1

# Configuración del proyecto
PROJECT_NAME=twin
```

### Paso 3: Inicializa el repositorio Git

Primero, limpia cualquier repositorio git que pueda haber sido creado por las herramientas:

**Mac/Linux:**
```bash
cd twin

# Elimina cualquier repo git creado por create-next-app o uv (si existen)
rm -rf frontend/.git backend/.git 2>/dev/null

# Inicializa el repositorio git con "main" como rama principal
git init -b main

# Si recibes un error de que -b no está soportado (versiones antiguas de git):
# git init
# git checkout -b main

# Configura git (cambia por tus datos)
git config user.name "Tu Nombre"
git config user.email "tu.email@ejemplo.com"
```

**Windows (PowerShell):**
```powershell
cd twin

# Elimina cualquier repo git creado por create-next-app o uv (si existen)
Remove-Item -Path frontend/.git -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path backend/.git -Recurse -Force -ErrorAction SilentlyContinue

# Inicializa el repositorio git con "main" como rama principal
git init -b main

# Si recibes un error de que -b no está soportado (versiones antiguas de git):
# git init
# git checkout -b main

# Configura git (cambia por tus datos)
git config user.name "Tu Nombre"
git config user.email "tu.email@ejemplo.com"
```

Tras configurar git, continua agregando y registrando cambios:

```bash
# Agrega todos los archivos
git add .

# Crea el commit inicial
git commit -m "Commit inicial: Infraestructura y aplicación de Digital Twin"
```

### Paso 4: Crea repositorio en GitHub

1. Ve a [github.com](https://github.com) e inicia sesión
2. Haz clic en el icono **+** arriba a la derecha → **New repository**
3. Configura tu repositorio:
   - Nombre del repositorio: `digital-twin` (o el que prefieras)
   - Descripción: "AI Digital Twin desplegado en AWS con Terraform"
   - Público o privado: elige (privado recomendado si usas datos personales reales)
   - NO inicialices con README, .gitignore ni licencia
4. Haz clic en **Create repository**

### Paso 5: Haz push a GitHub

Tras crear el repositorio, GitHub te mostrará los comandos a usar:

```bash
# Agrega GitHub como remoto (cambia YOUR_USERNAME por tu usuario de GitHub)
git remote add origin https://github.com/YOUR_USERNAME/digital-twin.git

# Haz push a GitHub (ya estás en la rama main)
git push -u origin main
```

Si se solicita autenticación:
- Usuario: Tu usuario de GitHub
- Contraseña: Usa un Token de Acceso Personal (PAT), no tu contraseña
  - Ve a GitHub → Settings → Developer settings → Personal access tokens
  - Genera un token con permisos `repo`

✅ **Punto de control**: ¡Tu código ya está en GitHub! Refresca la página de tu repositorio para ver los archivos.

## Parte 3: Configura S3 como backend para el estado de Terraform

### Paso 1: Crea recursos para gestión de estado

Crea `terraform/backend-setup.tf`:

```hcl
# Este archivo crea el bucket S3 y la tabla DynamoDB para el estado de Terraform
# Ejecútalo una vez por cuenta AWS y luego elimínalo

resource "aws_s3_bucket" "terraform_state" {
  bucket = "twin-terraform-state-${data.aws_caller_identity.current.account_id}"
  
  tags = {
    Name        = "Terraform State Store"
    Environment = "global"
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "twin-terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "Terraform State Locks"
    Environment = "global"
    ManagedBy   = "terraform"
  }
}

# Nota: aws_caller_identity.current ya está definido en main.tf

output "state_bucket_name" {
  value = aws_s3_bucket.terraform_state.id
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.terraform_locks.name
}
```

### Paso 2: Crea los recursos backend - nota: una línea es diferente para Mac/Linux o PC:

```bash
cd terraform

# IMPORTANTE: Asegúrate de estar en el workspace por defecto
terraform workspace select default

# Inicializa Terraform
terraform init

# Aplica solo los recursos del backend (copia y pega toda esta línea, cambia según tu SO)

# Versión Mac/Linux:
terraform apply -target=aws_s3_bucket.terraform_state -target=aws_s3_bucket_versioning.terraform_state -target=aws_s3_bucket_server_side_encryption_configuration.terraform_state -target=aws_s3_bucket_public_access_block.terraform_state -target=aws_dynamodb_table.terraform_locks
# Versión PC:
terraform apply --% -target="aws_s3_bucket.terraform_state" -target="aws_s3_bucket_versioning.terraform_state" -target="aws_s3_bucket_server_side_encryption_configuration.terraform_state" -target="aws_s3_bucket_public_access_block.terraform_state" -target="aws_dynamodb_table.terraform_locks"

# Verifica que los recursos estén creados
terraform output
```

El bucket y la tabla DynamoDB están listos para guardar el estado de Terraform.

### Paso 3: Elimina el archivo de setup

Ahora que existen los recursos backend, elimina el archivo de setup:

```bash
rm backend-setup.tf
```

### Paso 4: Actualiza scripts para backend S3

Hay que modificar los scripts de despliegue y destrucción para funcionar con el backend S3.

#### Actualiza deploy.sh

Actualiza `scripts/deploy.sh` para incluir la configuración del backend. Busca la línea de `terraform init` y reemplázala así:

```bash
# Línea antigua:
terraform init -input=false

# Nuevas líneas:
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${DEFAULT_AWS_REGION:-us-east-1}
terraform init -input=false \
  -backend-config="bucket=twin-terraform-state-${AWS_ACCOUNT_ID}" \
  -backend-config="key=${ENVIRONMENT}/terraform.tfstate" \
  -backend-config="region=${AWS_REGION}" \
  -backend-config="dynamodb_table=twin-terraform-locks" \
  -backend-config="encrypt=true"
```

Actualiza `scripts/deploy.ps1` de manera similar:

```powershell
# Línea antigua:
terraform init -input=false

# Nuevas líneas:
$awsAccountId = aws sts get-caller-identity --query Account --output text
$awsRegion = if ($env:DEFAULT_AWS_REGION) { $env:DEFAULT_AWS_REGION } else { "us-east-1" }
terraform init -input=false `
  -backend-config="bucket=twin-terraform-state-$awsAccountId" `
  -backend-config="key=$Environment/terraform.tfstate" `
  -backend-config="region=$awsRegion" `
  -backend-config="dynamodb_table=twin-terraform-locks" `
  -backend-config="encrypt=true"
```

#### Actualiza destroy.sh

Reemplaza tu `scripts/destroy.sh` por esta versión con soporte para backend S3:

```bash
#!/bin/bash
set -e

# Verifica si el parámetro de entorno fue suministrado
if [ $# -eq 0 ]; then
    echo "❌ Error: Se requiere el parámetro de entorno"
    echo "Uso: $0 <entorno>"
    echo "Ejemplo: $0 dev"
    echo "Entornos disponibles: dev, test, prod"
    exit 1
fi

ENVIRONMENT=$1
PROJECT_NAME=${2:-twin}

echo "🗑️ Preparando destrucción de la infraestructura ${PROJECT_NAME}-${ENVIRONMENT}..."

cd "$(dirname "$0")/../terraform"

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${DEFAULT_AWS_REGION:-us-east-1}

echo "🔧 Inicializando Terraform con backend S3..."
terraform init -input=false \
  -backend-config="bucket=twin-terraform-state-${AWS_ACCOUNT_ID}" \
  -backend-config="key=${ENVIRONMENT}/terraform.tfstate" \
  -backend-config="region=${AWS_REGION}" \
  -backend-config="dynamodb_table=twin-terraform-locks" \
  -backend-config="encrypt=true"

if ! terraform workspace list | grep -q "$ENVIRONMENT"; then
    echo "❌ Error: El workspace '$ENVIRONMENT' no existe"
    echo "Workspaces disponibles:"
    terraform workspace list
    exit 1
fi

terraform workspace select "$ENVIRONMENT"

echo "📦 Vaciando buckets S3..."

FRONTEND_BUCKET="${PROJECT_NAME}-${ENVIRONMENT}-frontend-${AWS_ACCOUNT_ID}"
MEMORY_BUCKET="${PROJECT_NAME}-${ENVIRONMENT}-memory-${AWS_ACCOUNT_ID}"

if aws s3 ls "s3://$FRONTEND_BUCKET" 2>/dev/null; then
    echo "  Vaciando $FRONTEND_BUCKET..."
    aws s3 rm "s3://$FRONTEND_BUCKET" --recursive
else
    echo "  Bucket frontend no encontrado o ya vacío"
fi

if aws s3 ls "s3://$MEMORY_BUCKET" 2>/dev/null; then
    echo "  Vaciando $MEMORY_BUCKET..."
    aws s3 rm "s3://$MEMORY_BUCKET" --recursive
else
    echo "  Bucket memory no encontrado o ya vacío"
fi

echo "🔥 Ejecutando terraform destroy..."

if [ ! -f "../backend/lambda-deployment.zip" ]; then
    echo "Creando paquete lambda de prueba para la destrucción..."
    echo "dummy" | zip ../backend/lambda-deployment.zip -
fi

if [ "$ENVIRONMENT" = "prod" ] && [ -f "prod.tfvars" ]; then
    terraform destroy -var-file=prod.tfvars -var="project_name=$PROJECT_NAME" -var="environment=$ENVIRONMENT" -auto-approve
else
    terraform destroy -var="project_name=$PROJECT_NAME" -var="environment=$ENVIRONMENT" -auto-approve
fi

echo "✅ ¡Infraestructura de $ENVIRONMENT destruida!"
echo ""
echo "💡 Para eliminar el workspace completamente, ejecuta:"
echo "   terraform workspace select default"
echo "   terraform workspace delete $ENVIRONMENT"
```

Haz lo mismo con `scripts/destroy.ps1`:

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$Environment,
    [string]$ProjectName = "twin"
)

if ($Environment -notmatch '^(dev|test|prod)$') {
    Write-Host "Error: Entorno inválido '$Environment'" -ForegroundColor Red
    Write-Host "Entornos disponibles: dev, test, prod" -ForegroundColor Yellow
    exit 1
}

Write-Host "Preparando destrucción de $ProjectName-$Environment..." -ForegroundColor Yellow

Set-Location (Join-Path (Split-Path $PSScriptRoot -Parent) "terraform")

$awsAccountId = aws sts get-caller-identity --query Account --output text
$awsRegion = if ($env:DEFAULT_AWS_REGION) { $env:DEFAULT_AWS_REGION } else { "us-east-1" }

Write-Host "Inicializando Terraform con backend S3..." -ForegroundColor Yellow
terraform init -input=false `
  -backend-config="bucket=twin-terraform-state-$awsAccountId" `
  -backend-config="key=$Environment/terraform.tfstate" `
  -backend-config="region=$awsRegion" `
  -backend-config="dynamodb_table=twin-terraform-locks" `
  -backend-config="encrypt=true"

$workspaces = terraform workspace list
if (-not ($workspaces | Select-String $Environment)) {
    Write-Host "Error: El workspace '$Environment' no existe" -ForegroundColor Red
    Write-Host "Workspaces disponibles:" -ForegroundColor Yellow
    terraform workspace list
    exit 1
}

terraform workspace select $Environment

Write-Host "Vaciando buckets S3..." -ForegroundColor Yellow

$FrontendBucket = "$ProjectName-$Environment-frontend-$awsAccountId"
$MemoryBucket = "$ProjectName-$Environment-memory-$awsAccountId"

try {
    aws s3 ls "s3://$FrontendBucket" 2>$null | Out-Null
    Write-Host "  Vaciando $FrontendBucket..." -ForegroundColor Gray
    aws s3 rm "s3://$FrontendBucket" --recursive
} catch {
    Write-Host "  Bucket frontend no encontrado o ya vacío" -ForegroundColor Gray
}

try {
    aws s3 ls "s3://$MemoryBucket" 2>$null | Out-Null
    Write-Host "  Vaciando $MemoryBucket..." -ForegroundColor Gray
    aws s3 rm "s3://$MemoryBucket" --recursive
} catch {
    Write-Host "  Bucket memory no encontrado o ya vacío" -ForegroundColor Gray
}

Write-Host "Ejecutando terraform destroy..." -ForegroundColor Yellow

if ($Environment -eq "prod" -and (Test-Path "prod.tfvars")) {
    terraform destroy -var-file=prod.tfvars `
                     -var="project_name=$ProjectName" `
                     -var="environment=$Environment" `
                     -auto-approve
} else {
    terraform destroy -var="project_name=$ProjectName" `
                     -var="environment=$Environment" `
                     -auto-approve
}

Write-Host "¡Infraestructura $Environment destruida!" -ForegroundColor Green
Write-Host ""
Write-Host "  Para eliminar el workspace completamente, ejecuta:" -ForegroundColor Cyan
Write-Host "   terraform workspace select default" -ForegroundColor White
Write-Host "   terraform workspace delete $Environment" -ForegroundColor White
```

## Parte 4: Configura los secretos del repositorio GitHub

### Paso 1: Crea un rol IAM de AWS para GitHub Actions

A partir de agosto de 2025, GitHub recomienda usar OpenID Connect (OIDC) para autentificación en AWS. Es más seguro que almacenar claves de acceso de larga duración.

Crea `terraform/github-oidc.tf`:

```hcl
# Crea un rol IAM que GitHub Actions puede asumir
# Ejecútalo una vez y luego elimina el archivo

variable "github_repository" {
  description = "Repositorio GitHub en formato 'owner/repo'"
  type        = string
}

# Nota: aws_caller_identity.current ya está definido en main.tf

# Proveedor OIDC de GitHub
# Si ya existe en tu cuenta, deberás importarlo:
# terraform import aws_iam_openid_connect_provider.github arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com
resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
  
  client_id_list = [
    "sts.amazonaws.com"
  ]
  
  # Este thumbprint viene de la documentación de GitHub
  # Verifica el valor en: https://github.blog/changelog/2023-06-27-github-actions-update-on-oidc-integration-with-aws/
  thumbprint_list = [
    "1b511abead59c6ce207077c0bf0e0043b1382612"
  ]
}

# Rol IAM para GitHub Actions
resource "aws_iam_role" "github_actions" {
  name = "github-actions-twin-deploy"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_repository}:*"
          }
        }
      }
    ]
  })
  
  tags = {
    Name        = "GitHub Actions Deploy Role"
    Repository  = var.github_repository
    ManagedBy   = "terraform"
  }
}

# Adjunta políticas necesarias
resource "aws_iam_role_policy_attachment" "github_lambda" {
  policy_arn = "arn:aws:iam::aws:policy/AWSLambda_FullAccess"
  role       = aws_iam_role.github_actions.name
}

resource "aws_iam_role_policy_attachment" "github_s3" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  role       = aws_iam_role.github_actions.name
}

resource "aws_iam_role_policy_attachment" "github_apigateway" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator"
  role       = aws_iam_role.github_actions.name
}

resource "aws_iam_role_policy_attachment" "github_cloudfront" {
  policy_arn = "arn:aws:iam::aws:policy/CloudFrontFullAccess"
  role       = aws_iam_role.github_actions.name
}

resource "aws_iam_role_policy_attachment" "github_iam_read" {
  policy_arn = "arn:aws:iam::aws:policy/IAMReadOnlyAccess"
  role       = aws_iam_role.github_actions.name
}

resource "aws_iam_role_policy_attachment" "github_bedrock" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
  role       = aws_iam_role.github_actions.name
}

resource "aws_iam_role_policy_attachment" "github_dynamodb" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
  role       = aws_iam_role.github_actions.name
}

resource "aws_iam_role_policy_attachment" "github_acm" {
  policy_arn = "arn:aws:iam::aws:policy/AWSCertificateManagerFullAccess"
  role       = aws_iam_role.github_actions.name
}

resource "aws_iam_role_policy_attachment" "github_route53" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonRoute53FullAccess"
  role       = aws_iam_role.github_actions.name
}

# Política personalizada para permisos adicionales
resource "aws_iam_role_policy" "github_additional" {
  name = "github-actions-additional"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:GetRole",
          "iam:GetRolePolicy",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",
          "iam:UpdateAssumeRolePolicy",
          "iam:PassRole",
          "iam:TagRole",
          "iam:UntagRole",
          "iam:ListInstanceProfilesForRole",
          "sts:GetCallerIdentity"
        ]
        Resource = "*"
      }
    ]
  })
}

output "github_actions_role_arn" {
  value = aws_iam_role.github_actions.arn
}
```

### Paso 2: Crea el rol de GitHub Actions

```bash
cd terraform

# IMPORTANTE: Asegúrate de estar en el workspace por defecto
terraform workspace select default

# Verifica primero si el proveedor OIDC ya existe

**Mac/Linux:**
```bash
aws iam list-open-id-connect-providers | grep token.actions.githubusercontent.com
```

**Windows (PowerShell):**
```powershell
aws iam list-open-id-connect-providers | Select-String "token.actions.githubusercontent.com"
```

Si existe, verás un ARN como: `arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com`

En ese caso, impórtalo primero:

**Mac/Linux:**
```bash
# Obtén tu Account ID de AWS
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Tu AWS Account ID es: $AWS_ACCOUNT_ID"

# Solo si ya existe el proveedor:
# terraform import aws_iam_openid_connect_provider.github arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com
```

**Windows (PowerShell):**
```powershell
# Obtén tu Account ID de AWS
$awsAccountId = aws sts get-caller-identity --query Account --output text
Write-Host "Tu AWS Account ID es: $awsAccountId"

# Solo si ya existe el proveedor:
# terraform import aws_iam_openid_connect_provider.github "arn:aws:iam::${awsAccountId}:oidc-provider/token.actions.githubusercontent.com"
```

### Aplica los recursos OIDC de GitHub

Ahora aplica los recursos. El comando depende de si el proveedor OIDC ya existe:

#### Escenario A: OIDC NO existe (primera vez)

Si el comando grep/Select-String no devolvió nada, el OIDC no existe aún. Créalo junto con el rol IAM:

**⚠️ IMPORTANTE**: Sustituye `YOUR_GITHUB_USERNAME` por tu verdadero usuario de GitHub.  
Por ejemplo: si tu usuario de GitHub es 'johndoe', usa: `johndoe/digital-twin`  
**NOTA**: No pongas la URL, solo el usuario/repositorio.

**Mac/Linux:**
```bash
# Aplica TODOS los recursos incluyendo OIDC
terraform apply -target=aws_iam_openid_connect_provider.github -target=aws_iam_role.github_actions -target=aws_iam_role_policy_attachment.github_lambda -target=aws_iam_role_policy_attachment.github_s3 -target=aws_iam_role_policy_attachment.github_apigateway -target=aws_iam_role_policy_attachment.github_cloudfront -target=aws_iam_role_policy_attachment.github_iam_read -target=aws_iam_role_policy_attachment.github_bedrock -target=aws_iam_role_policy_attachment.github_dynamodb -target=aws_iam_role_policy_attachment.github_acm -target=aws_iam_role_policy_attachment.github_route53 -target=aws_iam_role_policy.github_additional -var="github_repository=YOUR_GITHUB_USERNAME/digital-twin"
```

**Windows (PowerShell):**
```powershell
# Aplica TODOS los recursos incluyendo OIDC
terraform apply -target="aws_iam_openid_connect_provider.github" -target="aws_iam_role.github_actions" -target="aws_iam_role_policy_attachment.github_lambda" -target="aws_iam_role_policy_attachment.github_s3" -target="aws_iam_role_policy_attachment.github_apigateway" -target="aws_iam_role_policy_attachment.github_cloudfront" -target="aws_iam_role_policy_attachment.github_iam_read" -target="aws_iam_role_policy_attachment.github_bedrock" -target="aws_iam_role_policy_attachment.github_dynamodb" -target="aws_iam_role_policy_attachment.github_acm" -target="aws_iam_role_policy_attachment.github_route53" -target="aws_iam_role_policy.github_additional" -var="github_repository=YOUR_GITHUB_USERNAME/digital-twin"
```

#### Escenario B: OIDC ya existe (lo importaste)

Si importaste el proveedor, crea solo el rol IAM y las políticas:

**⚠️ IMPORTANTE**: Usa el mismo nombre de repo que durante la importación.

**Mac/Linux:**
```bash
# Aplica SOLO el rol IAM y políticas (NO el proveedor OIDC)
terraform apply -target=aws_iam_role.github_actions -target=aws_iam_role_policy_attachment.github_lambda -target=aws_iam_role_policy_attachment.github_s3 -target=aws_iam_role_policy_attachment.github_apigateway -target=aws_iam_role_policy_attachment.github_cloudfront -target=aws_iam_role_policy_attachment.github_iam_read -target=aws_iam_role_policy_attachment.github_bedrock -target=aws_iam_role_policy_attachment.github_dynamodb -target=aws_iam_role_policy_attachment.github_acm -target=aws_iam_role_policy_attachment.github_route53 -target=aws_iam_role_policy.github_additional -var="github_repository=YOUR_GITHUB_USERNAME/your-repo-name"
```

**Windows (PowerShell):**
```powershell
# Aplica SOLO el rol IAM y políticas (NO el proveedor OIDC)
terraform apply -target="aws_iam_role.github_actions" -target="aws_iam_role_policy_attachment.github_lambda" -target="aws_iam_role_policy_attachment.github_s3" -target="aws_iam_role_policy_attachment.github_apigateway" -target="aws_iam_role_policy_attachment.github_cloudfront" -target="aws_iam_role_policy_attachment.github_iam_read" -target="aws_iam_role_policy_attachment.github_bedrock" -target="aws_iam_role_policy_attachment.github_dynamodb" -target="aws_iam_role_policy_attachment.github_acm" -target="aws_iam_role_policy_attachment.github_route53" -target="aws_iam_role_policy.github_additional" -var="github_repository=myrepo/digital-twin"
```

### Obtén el ARN del rol y limpia

Después de aplicar:

```bash
# Anota el ARN mostrado en el output
terraform output github_actions_role_arn

# Elimina archivo de setup
rm github-oidc.tf    # Mac/Linux
Remove-Item github-oidc.tf    # PowerShell Windows
```

**Importante**: Guarda el ARN. Lo necesitarás para el siguiente paso.

### Paso 3: Configura el backend de Terraform

Ya con los recursos creados, configura el backend de S3.

Crea `terraform/backend.tf`:

```hcl
terraform {
  backend "s3" {
    # Estos valores los establecerán los scripts de despliegue
    # Para desarrollo local, pueden pasarse vía -backend-config
  }
}
```

Este archivo indica a Terraform usar S3 para guardar su estado. Los detalles se pasan con banderas `-backend-config`.

### Paso 4: Agrega secretos a GitHub

1. Ve a tu repositorio GitHub
2. Haz clic en la pestaña **Settings**
3. En el menú izquierdo, selecciona **Secrets and variables** → **Actions**
4. Haz clic en **New repository secret** para cada uno:

**Secreto 1: AWS_ROLE_ARN**
- Nombre: `AWS_ROLE_ARN`
- Valor: El ARN del rol de terraform output (ej: `arn:aws:iam::123456789012:role/github-actions-twin-deploy`)

**Secreto 2: DEFAULT_AWS_REGION**
- Nombre: `DEFAULT_AWS_REGION`
- Valor: `us-east-1` (o tu región preferida)

**Secreto 3: AWS_ACCOUNT_ID**
- Nombre: `AWS_ACCOUNT_ID`
- Valor: El ID de 12 dígitos de tu cuenta AWS

### Paso 5: Verifica los secretos

Después de agregarlos, deberías tener 3 secretos:
- AWS_ROLE_ARN
- DEFAULT_AWS_REGION  
- AWS_ACCOUNT_ID

✅ **Punto de control**: ¡GitHub puede autenticarse con AWS de forma segura!

## Parte 5: Crear workflows de GitHub Actions

### Paso 1: Crea el directorio de workflows

En el panel del explorador de Cursor (barra izquierda):

1. Haz clic derecho en algún espacio vacío o la raíz del proyecto
2. Selecciona **New Folder**
3. Nómbralo `.github`
4. Haz clic derecho sobre la carpeta `.github` creada
5. Selecciona **New Folder**
6. Nómbralo `workflows`

Ahora tienes `.github/workflows/` en tu proyecto.

### Paso 2: Crea workflow de despliegue

Crea `.github/workflows/deploy.yml`:

```yaml
name: Desplegar Gemelo Digital

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Entorno a desplegar'
        required: true
        default: 'dev'
        type: choice
        options:
          - dev
          - test
          - prod

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    name: Desplegar en ${{ github.event.inputs.environment || 'dev' }}
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment || 'dev' }}
    
    steps:
      - name: Clonar el código
        uses: actions/checkout@v4

      - name: Configurar credenciales AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          role-session-name: github-actions-deploy
          aws-region: ${{ secrets.DEFAULT_AWS_REGION }}

      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Instalar uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Configurar Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_wrapper: false  # Importante: desactivar wrapper para outputs puros

      - name: Configurar Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Ejecutar script de despliegue
        run: |
          # Variables de entorno para el script
          export AWS_ACCOUNT_ID=${{ secrets.AWS_ACCOUNT_ID }}
          export DEFAULT_AWS_REGION=${{ secrets.DEFAULT_AWS_REGION }}
          
          # Haz ejecutable el script y ejecútalo
          chmod +x scripts/deploy.sh
          ./scripts/deploy.sh ${{ github.event.inputs.environment || 'dev' }}
        env:
          AWS_ROLE_ARN: ${{ secrets.AWS_ROLE_ARN }}
          
      - name: Obtener URLs del despliegue
        id: deploy_outputs
        working-directory: ./terraform
        run: |
          terraform workspace select ${{ github.event.inputs.environment || 'dev' }}
          echo "cloudfront_url=$(terraform output -raw cloudfront_url)" >> $GITHUB_OUTPUT
          echo "api_url=$(terraform output -raw api_gateway_url)" >> $GITHUB_OUTPUT
          echo "frontend_bucket=$(terraform output -raw s3_frontend_bucket)" >> $GITHUB_OUTPUT

      - name: Invalidar CloudFront
        run: |
          DISTRIBUTION_ID=$(aws cloudfront list-distributions \
            --query "DistributionList.Items[?Origins.Items[?DomainName=='${{ steps.deploy_outputs.outputs.frontend_bucket }}.s3-website-${{ secrets.DEFAULT_AWS_REGION }}.amazonaws.com']].Id | [0]" \
            --output text)
          
          if [ "$DISTRIBUTION_ID" != "None" ] && [ -n "$DISTRIBUTION_ID" ]; then
            aws cloudfront create-invalidation \
              --distribution-id $DISTRIBUTION_ID \
              --paths "/*"
          fi

      - name: Resumen del Despliegue
        run: |
          echo "✅ ¡Despliegue completo!"
          echo "🌐 URL CloudFront: ${{ steps.deploy_outputs.outputs.cloudfront_url }}"
          echo "📡 API Gateway: ${{ steps.deploy_outputs.outputs.api_url }}"
          echo "🪣 Bucket frontend: ${{ steps.deploy_outputs.outputs.frontend_bucket }}"
```

### Paso 3: Crea workflow de destrucción

Crea `.github/workflows/destroy.yml`:

```yaml
name: Destruir entorno

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Entorno a destruir'
        required: true
        type: choice
        options:
          - dev
          - test
          - prod
      confirm:
        description: 'Escribe el nombre del entorno para confirmar la destrucción'
        required: true

permissions:
  id-token: write
  contents: read

jobs:
  destroy:
    name: Destruir ${{ github.event.inputs.environment }}
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}
    
    steps:
      - name: Verificar confirmación
        run: |
          if [ "${{ github.event.inputs.confirm }}" != "${{ github.event.inputs.environment }}" ]; then
            echo "❌ ¡La confirmación no coincide con el nombre del entorno!"
            echo "Ingresaste: '${{ github.event.inputs.confirm }}'"
            echo "Se esperaba: '${{ github.event.inputs.environment }}'"
            exit 1
          fi
          echo "✅ Confirmada la destrucción de ${{ github.event.inputs.environment }}"

      - name: Clonar el código
        uses: actions/checkout@v4

      - name: Configurar credenciales AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          role-session-name: github-actions-destroy
          aws-region: ${{ secrets.DEFAULT_AWS_REGION }}

      - name: Configurar Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_wrapper: false  # Importante: desactivar wrapper para outputs puros

      - name: Ejecutar script de destrucción
        run: |
          # Variables de entorno para el script
          export AWS_ACCOUNT_ID=${{ secrets.AWS_ACCOUNT_ID }}
          export DEFAULT_AWS_REGION=${{ secrets.DEFAULT_AWS_REGION }}
          
          # Haz ejecutable el script y ejecútalo
          chmod +x scripts/destroy.sh
          ./scripts/destroy.sh ${{ github.event.inputs.environment }}
        env:
          AWS_ROLE_ARN: ${{ secrets.AWS_ROLE_ARN }}

      - name: Destrucción completada
        run: |
          echo "✅ ¡El entorno ${{ github.event.inputs.environment }} ha sido destruido!"
```

### Paso 4: Haz commit y push de todos los cambios

```bash
# Agrega todos los cambios (workflows, backend.tf, scripts actualizados)
git add .

# Revisa lo que se va a commitear
git status

# Commit
git commit -m "Agregar CI/CD con GitHub Actions, backend S3 y scripts actualizados"

# Push a GitHub
git push
```

## Parte 6: Prueba despliegues

### Paso 1: Despliegue dev automático

Al hacer push a main, GitHub Actions debería desplegar automáticamente en dev:

1. Ve a tu repositorio GitHub
2. Haz clic en la pestaña **Actions**
3. Deberías ver el workflow "Deploy Digital Twin" en ejecución
4. Haz click para ver el progreso
5. Espera que finalice (5-10 minutos)

Una vez finalizado:

6. Expande el paso **"Deployment Summary"** al final del workflow
7. Verás tus URLs de despliegue:
   - 🌐 **URL CloudFront**: `https://[algo].cloudfront.net` - aquí está tu Gemelo Digital
   - 📡 **API Gateway**: El endpoint backend
   - 🪣 **Bucket frontend**: El nombre del bucket S3
8. Abre la URL de CloudFront para ver tu Gemelo Digital en el navegador

### Paso 2: Despliegue manual en test

Despleguemos en el entorno de pruebas:

1. En GitHub, ve a **Actions**
2. Haz click en **Deploy Digital Twin** a la izquierda
3. Haz click en el menú **Run workflow**
4. Selecciona:
   - Rama: `main`
   - Entorno: `test`
5. Haz click en **Run workflow**
6. Observa el progreso

### Paso 3: Despliegue manual en producción

Si tienes dominio personalizado:

1. En GitHub, ve a **Actions**
2. Haz click en **Deploy Digital Twin**
3. Haz click en **Run workflow**
4. Selecciona:
   - Rama: `main`
   - Entorno: `prod`
5. Haz click en **Run workflow**

### Paso 4: Verifica los despliegues

Después de cada despliegue:
1. Revisa el resumen del workflow para la URL de CloudFront
2. Accede a la URL y prueba tu Gemelo Digital
3. Mantén una conversación para verificar que funciona

✅ **Punto de control**: ¡Ahora tienes CI/CD desplegando en varios entornos!

## Parte 7: Soluciona el problema de foco de UI y añade avatar

Solucionemos el molesto problema de foco y, opcionalmente, añade foto de perfil.

### Paso 1: Añadir foto de perfil (opcional)

Si tienes una foto de perfil:

1. Añade tu foto como `frontend/public/avatar.png`
2. Que sea pequeña (menos de 100KB idealmente)
3. Mejor si es cuadrada (ej: 200x200px)

### Paso 2: Actualiza el componente Twin

Modifica `frontend/components/twin.tsx` para solucionar el foco y añadir avatar.

Busca la función `sendMessage` y añade una ref para el input. Aquí tienes el componente actualizado completo:

```typescript
'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

export default function Twin() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string>('');
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage.content,
                    session_id: sessionId || undefined,
                }),
            });

            if (!response.ok) throw new Error('Fallo al enviar el mensaje');

            const data = await response.json();

            if (!sessionId) {
                setSessionId(data.session_id);
            }

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Error:', error);
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: 'Lo siento, he encontrado un error. Por favor intenta de nuevo.',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
            // Volver a enfocar el input después de enviar el mensaje
            setTimeout(() => {
                inputRef.current?.focus();
            }, 100);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    // Verifica si existe avatar
    const [hasAvatar, setHasAvatar] = useState(false);
    useEffect(() => {
        // Verificar si existe avatar.png
        fetch('/avatar.png', { method: 'HEAD' })
            .then(res => setHasAvatar(res.ok))
            .catch(() => setHasAvatar(false));
    }, []);

    return (
        <div className="flex flex-col h-full bg-gray-50 rounded-lg shadow-lg">
            {/* Header */}
            <div className="bg-gradient-to-r from-slate-700 to-slate-800 text-white p-4 rounded-t-lg">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                    <Bot className="w-6 h-6" />
                    Gemelo Digital IA
                </h2>
                <p className="text-sm text-slate-300 mt-1">Tu compañero de curso de IA</p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center text-gray-500 mt-8">
                        {hasAvatar ? (
                            <img 
                                src="/avatar.png" 
                                alt="Avatar de Gemelo Digital" 
                                className="w-20 h-20 rounded-full mx-auto mb-3 border-2 border-gray-300"
                            />
                        ) : (
                            <Bot className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                        )}
                        <p>¡Hola! Soy tu Gemelo Digital.</p>
                        <p className="text-sm mt-2">¡Pregunta lo que quieras sobre despliegue de IA!</p>
                    </div>
                )}

                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex gap-3 ${
                            message.role === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                    >
                        {message.role === 'assistant' && (
                            <div className="flex-shrink-0">
                                {hasAvatar ? (
                                    <img 
                                        src="/avatar.png" 
                                        alt="Avatar de Gemelo Digital" 
                                        className="w-8 h-8 rounded-full border border-slate-300"
                                    />
                                ) : (
                                    <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center">
                                        <Bot className="w-5 h-5 text-white" />
                                    </div>
                                )}
                            </div>
                        )}

                        <div
                            className={`max-w-[70%] rounded-lg p-3 ${
                                message.role === 'user'
                                    ? 'bg-slate-700 text-white'
                                    : 'bg-white border border-gray-200 text-gray-800'
                            }`}
                        >
                            <p className="whitespace-pre-wrap">{message.content}</p>
                            <p
                                className={`text-xs mt-1 ${
                                    message.role === 'user' ? 'text-slate-300' : 'text-gray-500'
                                }`}
                            >
                                {message.timestamp.toLocaleTimeString()}
                            </p>
                        </div>

                        {message.role === 'user' && (
                            <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                                    <User className="w-5 h-5 text-white" />
                                </div>
                            </div>
                        )}
                    </div>
                ))}

                {isLoading && (
                    <div className="flex gap-3 justify-start">
                        <div className="flex-shrink-0">
                            {hasAvatar ? (
                                <img 
                                    src="/avatar.png" 
                                    alt="Avatar de Gemelo Digital" 
                                    className="w-8 h-8 rounded-full border border-slate-300"
                                />
                            ) : (
                                <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center">
                                    <Bot className="w-5 h-5 text-white" />
                                </div>
                            )}
                        </div>
                        <div className="bg-white border border-gray-200 rounded-lg p-3">
                            <div className="flex space-x-2">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-gray-200 p-4 bg-white rounded-b-lg">
                <div className="flex gap-2">
                    <input
                        ref={inputRef}
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyPress}
                        placeholder="Escribe tu mensaje..."
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-600 focus:border-transparent text-gray-800"
                        disabled={isLoading}
                        autoFocus
                    />
                    <button
                        onClick={sendMessage}
                        disabled={!input.trim() || isLoading}
                        className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}
```

### Paso 3: Haz commit y push del arreglo

```bash
# Agrega los cambios
git add frontend/components/twin.tsx
git add frontend/public/avatar.png  # Solo si agregaste avatar

# Commit
git commit -m "Solucionar el foco y añadir soporte para avatar"

# Push para disparar el despliegue
git push
```

¡Esto disparará el despliegue en dev automáticamente!

### Paso 4: Verifica el arreglo

Cuando el workflow de GitHub Actions termine:

1. Visita tu URL en CloudFront del entorno dev
2. Escribe un mensaje
3. El input debe recuperar el foco automáticamente tras la respuesta
4. Si agregaste avatar, aparecerá en vez del icono bot

✅ **Punto de control**: ¡El problema de foco está solucionado!

## Parte 8: Explora la consola de AWS y CloudWatch

Veamos qué pasa tras bambalinas en AWS.

### Paso 1: Inicia sesión como usuario IAM

Ingresa a la consola AWS como `aiengineer` (tu usuario IAM).

### Paso 2: Explora funciones Lambda

1. Navega a **Lambda**
2. Deberías ver tres funciones:
   - `twin-dev-api`
   - `twin-test-api`
   - `twin-prod-api` (si la desplegaste)
3. Haz clic en `twin-dev-api`
4. Ve a la pestaña **Monitor**
5. Visualiza:
   - Gráfico de invocaciones
   - Métricas de duración
   - Conteo de errores
   - Tasa de éxito

### Paso 3: Visualiza logs en CloudWatch

1. En Lambda, haz clic en **View CloudWatch logs**
2. Haz clic en el último log stream
3. Podrás ver:
   - Cada petición API
   - Llamadas al modelo Bedrock
   - Tiempos de respuesta
   - Cualquier error

### Paso 4: Revisa uso de Bedrock

1. Ve a **CloudWatch**
2. Haz clic en **Metrics** → **All metrics**
3. Haz clic en **AWS/Bedrock**
4. Selecciona **By Model Id**
5. Visualiza métricas:
   - InvocationLatency
   - InputTokenCount
   - OutputTokenCount

### Paso 5: Visualiza el almacenamiento S3 de memoria

1. Ve a **S3**
2. Haz clic en el bucket `twin-dev-memory`
3. Verás archivos JSON por cada sesión de conversación
4. Haz clic en un archivo para ver la conversación

### Paso 6: Métricas de API Gateway

1. Ve a **API Gateway**
2. Haz clic en `twin-dev-api-gateway`
3. Haz clic en **Dashboard**
4. Revisa:
   - Llamadas a la API
   - Latencia
   - Errores 4xx y 5xx

### Paso 7: Analítica de CloudFront

1. Ve a **CloudFront**
2. Haz clic en tu distribución dev
3. Ve a **Reports & analytics**
4. Revisa:
   - Estadísticas de caché
   - Objetos populares
   - Ubicación de visitantes

## Parte 9: Gestión de entornos vía GitHub

### Paso 1: Prueba destrucción de entorno

Probemos destruir un entorno desde GitHub Actions:

1. Ve a tu repositorio GitHub
2. Haz clic en **Actions**
3. Haz clic en **Destroy Environment** a la izquierda
4. Haz clic en **Run workflow**
5. Selecciona:
   - Rama: `main`
   - Entorno: `test`
   - Confirmar: Escribe `test` en el campo confirmación
6. Haz clic en **Run workflow**
7. Observa el progreso (5-10 minutos)

### Paso 2: Verifica destrucción

Después:

1. Revisa en AWS Console
2. Verifica que los recursos `twin-test-*` hayan desaparecido:
   - Función Lambda
   - API Gateway
   - Buckets S3
   - Distribución CloudFront

### Paso 3: Re-despliega test

Re-despliega test así:

1. En GitHub Actions, haz clic en **Deploy Digital Twin**
2. Ejecuta workflow en entorno: `test`
3. Espera a que finalice
4. Verifica que funcione

## Parte 10: Limpieza final y revisión de costos

### Paso 1: Destruye todos los entornos

Usa GitHub Actions para destruirlos todos:

1. Destruye dev:
   - Ejecuta **Destroy Environment**
   - Entorno: `dev`
   - Confirmar: escribe `dev`

2. Destruye test (si sigue activo):
   - Ejecuta **Destroy Environment**
   - Entorno: `test`
   - Confirmar: escribe `test`

3. Destruye prod (si existe):
   - Ejecuta **Destroy Environment**
   - Entorno: `prod`
   - Confirmar: escribe `prod`

### Paso 2: Inicia sesión como root

Verifiquemos que todo esté limpio y revisemos costos:

1. Cierra sesión como usuario IAM
2. Inicia sesión como **root**

### Paso 3: Verifica limpieza total

#### Opción A: Revisa servicios individualmente

Verifica que no quede nada del proyecto:

1. **Lambda**: No debe haber funciones `twin-`
2. **S3**: Solo debe quedar `twin-terraform-state-*`
3. **API Gateway**: Ninguna API `twin-`
4. **CloudFront**: Ninguna distribución twin
5. **DynamoDB**: Solo la tabla `twin-terraform-locks`
6. **IAM**: El rol `github-actions-twin-deploy` debe quedar

#### Opción B: Usa Resource Explorer (recomendado)

AWS Resource Explorer lista TODOS los recursos:

1. En AWS Console, busca **Resource Explorer**
2. Si no está listo, haz clic en **Quick setup** (solo una vez, 2 minutos)
3. Cuando esté listo, haz clic en **Resource search**
4. En la caja de búsqueda pon: `tag.Project:twin`
5. Verás todos los recursos con esa etiqueta

Para ver absolutamente TODO:

1. En Resource Explorer, clic en **Resource search**
2. Deja la caja vacía
3. Haz clic en **Search**
4. Verás TODOS los recursos de la cuenta
5. Usa **Type** para agrupar y busca cualquier cosa rara

#### Opción C: Usa AWS Tag Editor

Otra forma de ver recursos etiquetados:

1. En la consola AWS, busca **Tag Editor**
2. Elige:
   - Regiones: **All regions**
   - Tipos de recurso: **All supported resource types**
   - Etiquetas: Clave = `Project`, Valor = `twin`
3. Busca recursos
4. Verás todos los recursos del proyecto

#### Opción D: Checa el reporte de costos y uso

Para ver lo que realmente cuesta:

1. Ve a **Billing & Cost Management**
2. Haz clic en **Cost Explorer** → **Cost and usage**
3. Agrupa por: **Service**
4. Filtra: Últimos 7 días
5. Cualquier servicio con coste = recursos activos

### Paso 4: Revisa los costos

1. Entra a **Billing & Cost Management**
2. Haz clic en **Cost Explorer**
3. Pon últimos 7 días
4. Filtra por servicio para ver:
   - Lambda: normalmente < $1
   - API Gateway: normalmente < $1
   - S3: mínimo (centavos)
   - CloudFront: mínimo (centavos)
   - Bedrock: depende uso, normalmente < $5
   - DynamoDB: mínimo (centavos)

### Paso 5: Opcional - limpia los recursos de GitHub Actions

Los recursos restantes tienen coste casi nulo:
- **Rol IAM** (`github-actions-twin-deploy`): GRATIS
- **Bucket S3 de estado** (`twin-terraform-state-*`): ~ $0.02/mes
- **Tabla DynamoDB** (`twin-terraform-locks`): ~ $0/mes mientras no se use

**Coste mensual si se deja: menos de $0.05**

Si quieres eliminar absolutamente TODO:

```bash
# Inicia sesión como usuario IAM, luego:
cd twin/terraform

# 1. Elimina el rol de GitHub Actions
aws iam detach-role-policy --role-name github-actions-twin-deploy --policy-arn arn:aws:iam::aws:policy/AWSLambda_FullAccess
aws iam detach-role-policy --role-name github-actions-twin-deploy --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam detach-role-policy --role-name github-actions-twin-deploy --policy-arn arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator
aws iam detach-role-policy --role-name github-actions-twin-deploy --policy-arn arn:aws:iam::aws:policy/CloudFrontFullAccess
aws iam detach-role-policy --role-name github-actions-twin-deploy --policy-arn arn:aws:iam::aws:policy/IAMReadOnlyAccess
aws iam detach-role-policy --role-name github-actions-twin-deploy --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
aws iam detach-role-policy --role-name github-actions-twin-deploy --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam detach-role-policy --role-name github-actions-twin-deploy --policy-arn arn:aws:iam::aws:policy/AWSCertificateManagerFullAccess
aws iam detach-role-policy --role-name github-actions-twin-deploy --policy-arn arn:aws:iam::aws:policy/AmazonRoute53FullAccess
aws iam delete-role-policy --role-name github-actions-twin-deploy --policy-name github-actions-additional
aws iam delete-role --role-name github-actions-twin-deploy

# 2. Vacía y elimina el bucket de estado
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws s3 rm s3://twin-terraform-state-${AWS_ACCOUNT_ID} --recursive
aws s3 rb s3://twin-terraform-state-${AWS_ACCOUNT_ID}

# 3. Elimina la tabla DynamoDB
aws dynamodb delete-table --table-name twin-terraform-locks
```

**Recomendación**: Deja esos recursos, no cuestan casi nada y te permiten redeplegar el proyecto fácilmente.

## ¡Felicidades! 🎉

¡Has completado la Semana 2 y construido un sistema de despliegue de IA de nivel producción!

### ¿Qué lograste esta semana?

**Día 1**: Gemelo Digital local con memoria  
**Día 2**: Despliegue en AWS con Lambda, S3, CloudFront  
**Día 3**: Integración de AWS Bedrock para respuesta IA  
**Día 4**: Automatización con Terraform y múltiples entornos  
**Día 5**: CI/CD con GitHub Actions

### Arquitectura Final

```
Repositorio GitHub
    ↓ (Push a main)
GitHub Actions (CI/CD)
    ↓ (Despliegue automático)
Infraestructura AWS
    ├── Entorno Dev
    ├── Entorno Test
    └── Entorno Prod

Cada entorno:
    ├── CloudFront → S3 (Frontend)
    ├── API Gateway → Lambda (Backend)
    ├── Bedrock (IA)
    └── S3 (Memoria)

Todo gestionado por:
    ├── Terraform (IaC)
    ├── GitHub Actions (CI/CD)
    └── S3 + DynamoDB (Estado)
```

### Habilidades clave que aprendiste

1. **Prácticas DevOps modernas**
   - Infraestructura como código
   - Pipelines CI/CD
   - Gestión multi-entorno
   - Pruebas y despliegue automatizado

2. **Dominio de servicios AWS**
   - Computación sin servidor (Lambda)
   - Gestión de APIs (API Gateway)
   - Hosting estático (S3, CloudFront)
   - Servicios de IA (Bedrock)
   - Gestión de estado (DynamoDB)

3. **Buenas prácticas de seguridad**
   - Autenticación OIDC
   - Roles y políticas IAM
   - Gestión de secretos
   - Acceso de mínimo privilegio

4. **Flujo profesional de desarrollo**
   - Control de versiones en Git
   - Pull requests (PRs)
   - Despliegues automatizados
   - Testeo de infraestructura

## Buenas prácticas a futuro

### Flujo de desarrollo

1. **Usa ramas para features siempre**  
   ```bash
   git checkout -b feature/nueva-feature
   # Haz cambios
   git push -u origin feature/nueva-feature
   # Crea pull request
   ```

2. **Testea en dev/test antes de prod**
   - Dev automático
   - Promoción manual a test
   - Cuidado en prod

3. **Monitorea costos regularmente**
   - Métricas en CloudWatch
   - Dashboard de facturación semanal
   - Alerta ante anomalías

### Recordatorios de seguridad

1. **Nunca subas secretos**
   - Usa GitHub Secrets
   - Usa variables de entorno
   - Considera AWS Secrets Manager

2. **Rota credenciales periódicamente**
   - Actualiza roles IAM
   - Refresca API keys
   - Revisa logs de acceso

3. **Aplica mínimo privilegio**
   - Solo los permisos necesarios
   - Roles separados por tareas
   - Auditoría periódica

## Solución de problemas comunes

### Fallos en GitHub Actions

**"Could not assume role"**
- Verifica el secreto AWS_ROLE_ARN
- Asegura que el nombre de repo coincide con OIDC
- Política de confianza correcta

**"Terraform state lock"**
- Puede estar desplegando otra persona
- Verifica la tabla DynamoDB
- Desbloquea: `terraform force-unlock LOCK_ID`

**"S3 bucket already exists"**
- Los nombres deben ser únicos globalmente
- Agrega sufijo aleatorio o tu ID de cuenta

### Problemas de despliegue

**El frontend no se actualiza**
- Invalida caché de CloudFront
- Verifica despliegue exitoso en GitHub Actions
- Comprueba sincronización S3

**API devuelve 403**
- Revisa configuración CORS
- Verifica despliegue API Gateway
- Checa permisos de Lambda

**Bedrock no responde**
- Verifica acceso al modelo
- Revisa permisos IAM de Bedrock
- Revisa logs en CloudWatch

## Próximos pasos y extensiones

### Mejoras potenciales

1. **Agregar tests**
   - Tests unitarios Lambda
   - Tests integración API
   - End-to-end con Cypress

2. **Mejorar monitoreo**
   - Dashboards personalizados CloudWatch
   - Alertas de errores
   - Monitoreo de rendimiento

3. **Agregar funcionalidades**
   - Autenticación de usuarios
   - Varias personalidades de twin
   - Analítica de conversación
   - Interfaz de voz

4. **Mejorar CI/CD**
   - Blue-green deployments
   - Canary releases
   - Rollbacks automáticos

### Recursos de aprendizaje

- [Documentación GitHub Actions](https://docs.github.com/actions)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Mejores prácticas Terraform](https://www.terraform.io/docs/cloud/guides/recommended-practices)
- [DevOps en AWS](https://aws.amazon.com/devops/)

## Notas finales

### Mantén bajos tus costos

Para minimizar costos:
1. Destruye entornos que no uses
2. Usa Nova Micro en desarrollo
3. Limita tasa de las APIs
4. Monitorea uso regularmente
5. Aprovecha el Free Tier de AWS

### Mantenimiento del repositorio

Mantén tu repo en forma:
1. Actualizaciones regulares de dependencias
2. Escaneo de seguridad con Dependabot
3. Documentación clara
4. Mensajes de commit significativos
5. Rama main protegida

¡Construiste algo increíble: una IA lista para producción y 100% automatizada con buenas prácticas DevOps! Así despliegan las compañías reales sus sistemas.

¡Gran trabajo completando la Semana 2! 🚀