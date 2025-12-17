# Día 4: Infraestructura como Código con Terraform

## De la Implementación Manual a la Automatizada

¡Bienvenido al Día 4! Hoy marca un cambio significativo en cómo implementamos nuestro Digital Twin. Pasamos de operar manualmente en la consola de AWS a usar Infraestructura como Código (IaC) con Terraform. Esta transformación aporta control de versiones, repetibilidad y la capacidad de desplegar múltiples entornos con un solo comando. ¡Al finalizar el día de hoy, estarás gestionando entornos de dev, test y producción como un ingeniero DevOps profesional!

## Qué aprenderás hoy

- **Fundamentos de Terraform** - Conceptos de Infraestructura como Código
- **Gestión de estado** - Cómo Terraform rastrea tus recursos
- **Workspaces** - Gestión de múltiples entornos
- **Despliegue automatizado** - Infraestructura lista con un solo comando
- **Aislamiento de entornos** - Separación de dev, test y producción
- **Opcional: Dominios personalizados** - Configuración profesional de DNS

## Parte 1: Borrón y cuenta nueva - Eliminar recursos manuales

Antes de abrazar la automatización, limpiemos todos los recursos que creamos manualmente en los Días 2 y 3. Este último recorrido por la consola te ayudará a reforzar lo que Terraform gestionará por nosotros.

### Paso 1: Eliminar la función Lambda

1. Inicia sesión en la consola de AWS como `aiengineer`
2. Ve a **Lambda**
3. Selecciona la función `twin-api`
4. Haz clic en **Actions** → **Delete**
5. Escribe "delete" para confirmar
6. Haz clic en **Delete**

### Paso 2: Eliminar API Gateway

1. Ve a **API Gateway**
2. Haz clic en `twin-api-gateway`
3. Haz clic en **Actions** → **Delete**
4. Escribe el nombre de la API para confirmar
5. Haz clic en **Delete**

### Paso 3: Vaciar y eliminar los buckets de S3

**Bucket de memoria:**
1. Ve a **S3**
2. Haz clic en tu bucket de memoria (ejemplo: `twin-memory-xyz`)
3. Haz clic en **Empty**
4. Escribe "permanently delete" para confirmar
5. Haz clic en **Empty**
6. Después de vaciar el bucket, haz clic en **Delete**
7. Escribe el nombre del bucket para confirmar
8. Haz clic en **Delete bucket**

**Bucket de frontend:**
1. Haz clic en tu bucket de frontend (ejemplo: `twin-frontend-xyz`)
2. Repite el proceso de vaciado y eliminación

### Paso 4: Eliminar la distribución de CloudFront

1. Ve a **CloudFront**
2. Selecciona tu distribución
3. Haz clic en **Disable** (si está habilitada)
4. Espera que el estado cambie a "Deployed" (5-10 minutos)
5. Una vez deshabilitada, haz clic en **Delete**
6. Haz clic en **Delete** para confirmar

### Paso 5: Verificar estado limpio

1. Revisa cada servicio para asegurar que no quedan recursos relacionados con twin:
   - Lambda: Sin funciones `twin-api`
   - API Gateway: Sin APIs `twin-api-gateway`
   - S3: Sin buckets que empiecen por `twin-`
   - CloudFront: Sin distribuciones de tu twin

✅ **Punto de control**: ¡Ahora tienes una cuenta AWS limpia, lista para que Terraform gestione todo!

## Parte 2: Entendiendo Terraform

### ¿Qué es Infraestructura como Código?

La Infraestructura como Código (IaC) trata la configuración de tu infraestructura como código fuente. En lugar de hacer clics en la consola, defines tu infraestructura en archivos de texto que pueden ser:
- **Versionados** - Sigue los cambios en el tiempo
- **Revisados** - Usa pull request para cambios en infraestructura
- **Automatizados** - Despliegue con pipelines CI/CD
- **Repetibles** - Crea entornos idénticos

### Conceptos clave de Terraform

**1. Recursos:** Los bloques de construcción - cada servicio de AWS que quieres crear
```hcl
resource "aws_s3_bucket" "example" {
  bucket = "my-bucket-name"
}
```

**2. Estado:** Registro de Terraform de lo que ha creado
- Almacenado en el archivo `terraform.tfstate`
- Relaciona tu configuración con recursos reales
- Crítico para actualizaciones y eliminaciones

**3. Proveedores (providers):** Plugins que interactúan con los proveedores de la nube
```hcl
provider "aws" {
  region = "us-east-1"
}
```

**4. Variables:** Parametrizan tu configuración
```hcl
variable "environment" {
  description = "Environment name"
  type        = string
}
```

**5. Workspaces:** Estado separado para diferentes entornos
- Cada workspace tiene su propio archivo de estado
- Perfecto para separar dev/test/prod

### Paso 1: Instalar Terraform

Desde agosto de 2025, la instalación de Terraform ha cambiado debido a actualizaciones de licencia. Usaremos la distribución oficial.

**Mac (usando Homebrew):**
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

**Mac/Linux (manual):**
1. Visita: https://developer.hashicorp.com/terraform/install
2. Descarga el paquete adecuado para tu sistema
3. Extrae y mueve a tu PATH:
```bash
# Ejemplo para Mac (ajusta la URL para tu sistema)
curl -O https://releases.hashicorp.com/terraform/1.10.0/terraform_1.10.0_darwin_amd64.zip
unzip terraform_1.10.0_darwin_amd64.zip
sudo mv terraform /usr/local/bin/
```

**Windows:**
1. Visita: https://developer.hashicorp.com/terraform/install
2. Descarga el paquete de Windows
3. Extrae el archivo .exe
4. Agrega a tu PATH:
   - Haz clic derecho en "Este equipo" → Propiedades
   - Configuración avanzada del sistema → Variables de entorno
   - Edita PATH y agrega el directorio de Terraform

**Verificar instalación:**
```bash
terraform --version
```

Deberías ver algo como: `Terraform v1.10.0` (la versión puede variar)

### Paso 2: Actualiza .gitignore

Agrega entradas específicas de Terraform a tu `.gitignore`:

```gitignore
# Terraform
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl
terraform.tfstate.d/
*.tfvars
!terraform.tfvars
!prod.tfvars

# Paquetes Lambda
lambda-deployment.zip
lambda-package/

# Archivos de entorno
.env
.env.*

# Node
node_modules/
out/
.next/

# Python
__pycache__/
*.pyc
.venv/
uv.lock

# IDE
.vscode/
.idea/
*.swp
.DS_Store
```

## Parte 3: Crear la configuración de Terraform

### Paso 1: Crear la estructura de directorios de Terraform

En el explorador de archivos de Cursor (la barra lateral izquierda):

1. Haz clic derecho en el espacio en blanco bajo todos los archivos
2. Selecciona **Nueva Carpeta**
3. Llámala `terraform`

La estructura del proyecto ahora tendrá:
```
twin/
├── backend/
├── frontend/
├── memory/
└── terraform/   (nuevo)
```

### Paso 2: Crear la configuración del proveedor

Crea `terraform/versions.tf`:

```hcl
terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  # Usa la configuración AWS CLI (aws configure)
}

provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}
```

### Paso 3: Definir variables

Crea `terraform/variables.tf`:

```hcl
variable "project_name" {
  description = "Prefijo de nombre para todos los recursos"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "El nombre del proyecto solo debe contener letras minúsculas, números y guiones."
  }
}

variable "environment" {
  description = "Nombre del entorno (dev, test, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "El entorno debe ser uno de: dev, test, prod."
  }
}

variable "bedrock_model_id" {
  description = "ID del modelo Bedrock"
  type        = string
  default     = "amazon.nova-micro-v1:0"
}

variable "lambda_timeout" {
  description = "Timeout de la función Lambda en segundos"
  type        = number
  default     = 60
}

variable "api_throttle_burst_limit" {
  description = "Límite de ráfaga de API Gateway"
  type        = number
  default     = 10
}

variable "api_throttle_rate_limit" {
  description = "Límite de tasa de API Gateway"
  type        = number
  default     = 5
}

variable "use_custom_domain" {
  description = "Vincular un dominio personalizado a CloudFront"
  type        = bool
  default     = false
}

variable "root_domain" {
  description = "Nombre del dominio raíz, ej. midominio.com"
  type        = string
  default     = ""
}
```

### Paso 4: Crear la infraestructura principal

Crea `terraform/main.tf`:

```hcl
# Fuente de datos para obtener el ID actual de cuenta AWS
data "aws_caller_identity" "current" {}

locals {
  aliases = var.use_custom_domain && var.root_domain != "" ? [
    var.root_domain,
    "www.${var.root_domain}"
  ] : []

  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Bucket S3 para memoria de conversación
resource "aws_s3_bucket" "memory" {
  bucket = "${local.name_prefix}-memory-${data.aws_caller_identity.current.account_id}"
  tags   = local.common_tags
}

resource "aws_s3_bucket_public_access_block" "memory" {
  bucket = aws_s3_bucket.memory.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "memory" {
  bucket = aws_s3_bucket.memory.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Bucket S3 para el sitio web estático del frontend
resource "aws_s3_bucket" "frontend" {
  bucket = "${local.name_prefix}-frontend-${data.aws_caller_identity.current.account_id}"
  tags   = local.common_tags
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "404.html"
  }
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend.arn}/*"
      },
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.frontend]
}

# Rol IAM para Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${local.name_prefix}-lambda-role"
  tags = local.common_tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_role.name
}

resource "aws_iam_role_policy_attachment" "lambda_bedrock" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
  role       = aws_iam_role.lambda_role.name
}

resource "aws_iam_role_policy_attachment" "lambda_s3" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  role       = aws_iam_role.lambda_role.name
}

# Función Lambda
resource "aws_lambda_function" "api" {
  filename         = "${path.module}/../backend/lambda-deployment.zip"
  function_name    = "${local.name_prefix}-api"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_handler.handler"
  source_code_hash = filebase64sha256("${path.module}/../backend/lambda-deployment.zip")
  runtime          = "python3.13"
  architectures    = ["x86_64"]
  timeout          = var.lambda_timeout
  tags             = local.common_tags

  environment {
    variables = {
      CORS_ORIGINS     = var.use_custom_domain ? "https://${var.root_domain},https://www.${var.root_domain}" : "https://${aws_cloudfront_distribution.main.domain_name}"
      S3_BUCKET        = aws_s3_bucket.memory.id
      USE_S3           = "true"
      BEDROCK_MODEL_ID = var.bedrock_model_id
    }
  }

  # Asegurar que Lambda espera a que la distribución exista
  depends_on = [aws_cloudfront_distribution.main]
}

# API Gateway HTTP API
resource "aws_apigatewayv2_api" "main" {
  name          = "${local.name_prefix}-api-gateway"
  protocol_type = "HTTP"
  tags          = local.common_tags

  cors_configuration {
    allow_credentials = false
    allow_headers     = ["*"]
    allow_methods     = ["GET", "POST", "OPTIONS"]
    allow_origins     = ["*"]
    max_age           = 300
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true
  tags        = local.common_tags

  default_route_settings {
    throttling_burst_limit = var.api_throttle_burst_limit
    throttling_rate_limit  = var.api_throttle_rate_limit
  }
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.api.invoke_arn
}

# Rutas de API Gateway
resource "aws_apigatewayv2_route" "get_root" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "post_chat" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /chat"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "get_health" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Permiso de Lambda para API Gateway
resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

# Distribución de CloudFront
resource "aws_cloudfront_distribution" "main" {
  aliases = local.aliases
  
  viewer_certificate {
    acm_certificate_arn            = var.use_custom_domain ? aws_acm_certificate.site[0].arn : null
    cloudfront_default_certificate = var.use_custom_domain ? false : true
    ssl_support_method             = var.use_custom_domain ? "sni-only" : null
    minimum_protocol_version       = "TLSv1.2_2021"
  }

  origin {
    domain_name = aws_s3_bucket_website_configuration.frontend.website_endpoint
    origin_id   = "S3-${aws_s3_bucket.frontend.id}"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  tags                = local.common_tags

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.frontend.id}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }
}

# Opcional: configuración de dominio personalizado (solo si use_custom_domain = true)
data "aws_route53_zone" "root" {
  count        = var.use_custom_domain ? 1 : 0
  name         = var.root_domain
  private_zone = false
}

resource "aws_acm_certificate" "site" {
  count                     = var.use_custom_domain ? 1 : 0
  provider                  = aws.us_east_1
  domain_name               = var.root_domain
  subject_alternative_names = ["www.${var.root_domain}"]
  validation_method         = "DNS"
  lifecycle { create_before_destroy = true }
  tags = local.common_tags
}

resource "aws_route53_record" "site_validation" {
  for_each = var.use_custom_domain ? {
    for dvo in aws_acm_certificate.site[0].domain_validation_options :
    dvo.domain_name => dvo
  } : {}

  zone_id = data.aws_route53_zone.root[0].zone_id
  name    = each.value.resource_record_name
  type    = each.value.resource_record_type
  ttl     = 300
  records = [each.value.resource_record_value]
}

resource "aws_acm_certificate_validation" "site" {
  count           = var.use_custom_domain ? 1 : 0
  provider        = aws.us_east_1
  certificate_arn = aws_acm_certificate.site[0].arn
  validation_record_fqdns = [
    for r in aws_route53_record.site_validation : r.fqdn
  ]
}

resource "aws_route53_record" "alias_root" {
  count   = var.use_custom_domain ? 1 : 0
  zone_id = data.aws_route53_zone.root[0].zone_id
  name    = var.root_domain
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.main.domain_name
    zone_id                = aws_cloudfront_distribution.main.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "alias_root_ipv6" {
  count   = var.use_custom_domain ? 1 : 0
  zone_id = data.aws_route53_zone.root[0].zone_id
  name    = var.root_domain
  type    = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.main.domain_name
    zone_id                = aws_cloudfront_distribution.main.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "alias_www" {
  count   = var.use_custom_domain ? 1 : 0
  zone_id = data.aws_route53_zone.root[0].zone_id
  name    = "www.${var.root_domain}"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.main.domain_name
    zone_id                = aws_cloudfront_distribution.main.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "alias_www_ipv6" {
  count   = var.use_custom_domain ? 1 : 0
  zone_id = data.aws_route53_zone.root[0].zone_id
  name    = "www.${var.root_domain}"
  type    = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.main.domain_name
    zone_id                = aws_cloudfront_distribution.main.hosted_zone_id
    evaluate_target_health = false
  }
}
```

### Paso 5: Definir outputs (salidas)

Crea `terraform/outputs.tf`:

```hcl
output "api_gateway_url" {
  description = "URL de la API Gateway"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

output "cloudfront_url" {
  description = "URL de la distribución de CloudFront"
  value       = "https://${aws_cloudfront_distribution.main.domain_name}"
}

output "s3_frontend_bucket" {
  description = "Nombre del bucket S3 para el frontend"
  value       = aws_s3_bucket.frontend.id
}

output "s3_memory_bucket" {
  description = "Nombre del bucket S3 para almacenamiento de memoria"
  value       = aws_s3_bucket.memory.id
}

output "lambda_function_name" {
  description = "Nombre de la función Lambda"
  value       = aws_lambda_function.api.function_name
}

output "custom_domain_url" {
  description = "URL raíz del sitio en producción"
  value       = var.use_custom_domain ? "https://${var.root_domain}" : ""
}
```

### Paso 6: Crear los valores por defecto de las variables

Crea `terraform/terraform.tfvars`:

```hcl
project_name             = "twin"
environment              = "dev"
bedrock_model_id         = "amazon.nova-micro-v1:0"
lambda_timeout           = 60
api_throttle_burst_limit = 10
api_throttle_rate_limit  = 5
use_custom_domain        = false
root_domain              = ""
```

### Paso 7: Actualizar el frontend para utilizar variables de entorno

Antes de crear nuestros scripts de despliegue, necesitamos actualizar el frontend para que utilice variables de entorno para el URL de la API en lugar de hardcodearlo.

Actualiza `frontend/components/twin.tsx` - busca la llamada a fetch (alrededor de la línea 43) y reemplaza:

```typescript
// Busca esta línea:
const response = await fetch('http://localhost:8000/chat', {

// Reemplaza por:
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/chat`, {
```

Este cambio permite al frontend:
- Usar `http://localhost:8000` durante el desarrollo local
- Usar el URL de producción de la API (definido por variable de entorno) cuando se despliegue

**Nota**: Next.js requiere que las variables de entorno accesibles desde el navegador tengan el prefijo `NEXT_PUBLIC_`.

## Parte 4: Crear scripts de despliegue

### Paso 1: Crear el directorio de scripts

En el explorador de archivos de Cursor (barra lateral izquierda):

1. Haz clic derecho en el espacio vacío debajo de los archivos
2. Selecciona **Nueva Carpeta**
3. Llama a la carpeta `scripts`

### Paso 2: Crear el script de shell para Mac/Linux

**Importante**: Todos los estudiantes (incluidos los usuarios de Windows) deben crear este archivo, ya que se usará en GitHub Actions en el Día 5.

Crea `scripts/deploy.sh`:

```bash
#!/bin/bash
set -e

ENVIRONMENT=${1:-dev}          # dev | test | prod
PROJECT_NAME=${2:-twin}

echo "🚀 Desplegando ${PROJECT_NAME} en ${ENVIRONMENT}..."

# 1. Construir el paquete Lambda
cd "$(dirname "$0")/.."        # raíz del proyecto
echo "📦 Construyendo paquete Lambda..."
(cd backend && uv run deploy.py)

# 2. Workspace y terraform apply
cd terraform
terraform init -input=false

if ! terraform workspace list | grep -q "$ENVIRONMENT"; then
  terraform workspace new "$ENVIRONMENT"
else
  terraform workspace select "$ENVIRONMENT"
fi

# Usar prod.tfvars para el entorno de producción
if [ "$ENVIRONMENT" = "prod" ]; then
  TF_APPLY_CMD=(terraform apply -var-file=prod.tfvars -var="project_name=$PROJECT_NAME" -var="environment=$ENVIRONMENT" -auto-approve)
else
  TF_APPLY_CMD=(terraform apply -var="project_name=$PROJECT_NAME" -var="environment=$ENVIRONMENT" -auto-approve)
fi

echo "🎯 Aplicando Terraform..."
"${TF_APPLY_CMD[@]}"

API_URL=$(terraform output -raw api_gateway_url)
FRONTEND_BUCKET=$(terraform output -raw s3_frontend_bucket)
CUSTOM_URL=$(terraform output -raw custom_domain_url 2>/dev/null || true)

# 3. Construir y desplegar el frontend
cd ../frontend

# Crear archivo .env.production con el URL de la API
echo "📝 Definiendo API URL para producción..."
echo "NEXT_PUBLIC_API_URL=$API_URL" > .env.production

npm install
npm run build
aws s3 sync ./out "s3://$FRONTEND_BUCKET/" --delete
cd ..

# 4. Mensajes finales
echo -e "\n✅ ¡Despliegue completo!"
echo "🌐 CloudFront URL : $(terraform -chdir=terraform output -raw cloudfront_url)"
if [ -n "$CUSTOM_URL" ]; then
  echo "🔗 Dominio personalizado  : $CUSTOM_URL"
fi
echo "📡 API Gateway    : $API_URL"
```

**Solo para usuarios Mac/Linux** - hazlo ejecutable:
```bash
chmod +x scripts/deploy.sh
```

**Usuarios Windows**: No es necesario ejecutar el comando chmod, solo crea el archivo.

### Paso 3: Crear el script PowerShell para Windows

**Usuarios Mac/Linux**: Pueden omitir este paso, solo es necesario para Windows.

Crea `scripts/deploy.ps1`:

```powershell
param(
    [string]$Environment = "dev",   # dev | test | prod
    [string]$ProjectName = "twin"
)
$ErrorActionPreference = "Stop"

Write-Host "Desplegando $ProjectName en $Environment ..." -ForegroundColor Green

# 1. Construir el paquete Lambda
Set-Location (Split-Path $PSScriptRoot -Parent)   # raíz del proyecto
Write-Host "Construyendo paquete Lambda..." -ForegroundColor Yellow
Set-Location backend
uv run deploy.py
Set-Location ..

# 2. Workspace y terraform apply
Set-Location terraform
terraform init -input=false

if (-not (terraform workspace list | Select-String $Environment)) {
    terraform workspace new $Environment
} else {
    terraform workspace select $Environment
}

if ($Environment -eq "prod") {
    terraform apply -var-file=prod.tfvars -var="project_name=$ProjectName" -var="environment=$Environment" -auto-approve
} else {
    terraform apply -var="project_name=$ProjectName" -var="environment=$Environment" -auto-approve
}

$ApiUrl        = terraform output -raw api_gateway_url
$FrontendBucket = terraform output -raw s3_frontend_bucket
try { $CustomUrl = terraform output -raw custom_domain_url } catch { $CustomUrl = "" }

# 3. Construir y desplegar el frontend
Set-Location ..\frontend

# Crear archivo .env.production con el URL de la API
Write-Host "Definiendo API URL para producción..." -ForegroundColor Yellow
"NEXT_PUBLIC_API_URL=$ApiUrl" | Out-File .env.production -Encoding utf8

npm install
npm run build
aws s3 sync .\out "s3://$FrontendBucket/" --delete
Set-Location ..

# 4. Resumen final
$CfUrl = terraform -chdir=terraform output -raw cloudfront_url
Write-Host "¡Despliegue completo!" -ForegroundColor Green
Write-Host "CloudFront URL : $CfUrl" -ForegroundColor Cyan
if ($CustomUrl) {
    Write-Host "Dominio personalizado  : $CustomUrl" -ForegroundColor Cyan
}
Write-Host "API Gateway    : $ApiUrl" -ForegroundColor Cyan

```

## Parte 5: Desplegar entorno de desarrollo

### Paso 1: Inicializar Terraform

```bash
cd terraform
terraform init
```

Deberías ver:
```
Initializing the backend...
Initializing provider plugins...
- Installing hashicorp/aws v6.x.x...
Terraform has been successfully initialized!
```

### Paso 2: Desplegar usando el script

**Mac/Linux desde la raíz del proyecto:**
```bash
./scripts/deploy.sh dev
```

**Windows (PowerShell) desde la raíz del proyecto:**
```powershell
.\scripts\deploy.ps1 -Environment dev
```

El script hará:
1. Construir el paquete Lambda
2. Crear un workspace `dev` en Terraform
3. Desplegar toda la infraestructura
4. Construir y desplegar el frontend
5. Mostrar las URLs

### Paso 3: Probar tu entorno de desarrollo

1. Visita el URL de CloudFront mostrado en la salida
2. Prueba la funcionalidad del chat
3. Verifica que todo funciona como antes

✅ **Punto de control**: ¡Tu entorno dev está desplegado ahora vía Terraform!

## Parte 6: Desplegar entorno de test

Ahora vamos a desplegar un entorno de test completamente separado:

### Paso 1: Desplegar entorno de test

**Mac/Linux:**
```bash
./scripts/deploy.sh test
```

**Windows (PowerShell):**
```powershell
.\scripts\deploy.ps1 -Environment test
```

### Paso 2: Verificar recursos separados

Revisa la consola de AWS - verás recursos separados para test:
- Función Lambda `twin-test-api`
- Bucket S3 `twin-test-memory`
- Bucket S3 `twin-test-frontend`
- API Gateway `twin-test-api-gateway`
- Distribución de CloudFront separada

### Paso 3: Probar ambos entornos

1. Abre la URL de CloudFront de dev en una pestaña del navegador
2. Abre la URL de CloudFront de test en otra pestaña
3. Ten conversaciones diferentes - ¡están completamente aislados!

## Parte 7: Destruir la infraestructura

Cuando termines con un entorno, es importante limpiarlo correctamente. Como los buckets S3 deben estar vacíos antes de ser eliminados, crearemos scripts para manejar esto automáticamente.

### Paso 1: Crear script destroy para Mac/Linux

Crea `scripts/destroy.sh`:

```bash
#!/bin/bash
set -e

# Comprobar si el parámetro de entorno ha sido proporcionado
if [ $# -eq 0 ]; then
    echo "❌ Error: Se requiere parámetro de entorno"
    echo "Uso: $0 <entorno>"
    echo "Ejemplo: $0 dev"
    echo "Entornos disponibles: dev, test, prod"
    exit 1
fi

ENVIRONMENT=$1
PROJECT_NAME=${2:-twin}

echo "🗑️ Preparando para destruir la infraestructura de ${PROJECT_NAME}-${ENVIRONMENT}..."

# Ir al directorio terraform
cd "$(dirname "$0")/../terraform"

# Comprobar si existe el workspace
if ! terraform workspace list | grep -q "$ENVIRONMENT"; then
    echo "❌ Error: El workspace '$ENVIRONMENT' no existe"
    echo "Workspaces disponibles:"
    terraform workspace list
    exit 1
fi

# Seleccionar el workspace
terraform workspace select "$ENVIRONMENT"

echo "📦 Vaciando los buckets S3..."

# Obtener el ID de cuenta AWS para los nombres de los buckets
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Nombres de los buckets con ID de cuenta
FRONTEND_BUCKET="${PROJECT_NAME}-${ENVIRONMENT}-frontend-${AWS_ACCOUNT_ID}"
MEMORY_BUCKET="${PROJECT_NAME}-${ENVIRONMENT}-memory-${AWS_ACCOUNT_ID}"

# Vaciar el bucket de frontend si existe
if aws s3 ls "s3://$FRONTEND_BUCKET" 2>/dev/null; then
    echo "  Vaciando $FRONTEND_BUCKET..."
    aws s3 rm "s3://$FRONTEND_BUCKET" --recursive
else
    echo "  Bucket frontend no encontrado o ya vacío"
fi

# Vaciar el bucket de memoria si existe
if aws s3 ls "s3://$MEMORY_BUCKET" 2>/dev/null; then
    echo "  Vaciando $MEMORY_BUCKET..."
    aws s3 rm "s3://$MEMORY_BUCKET" --recursive
else
    echo "  Bucket memory no encontrado o ya vacío"
fi

echo "🔥 Ejecutando terraform destroy..."

# Ejecutar terraform destroy automático
if [ "$ENVIRONMENT" = "prod" ] && [ -f "prod.tfvars" ]; then
    terraform destroy -var-file=prod.tfvars -var="project_name=$PROJECT_NAME" -var="environment=$ENVIRONMENT" -auto-approve
else
    terraform destroy -var="project_name=$PROJECT_NAME" -var="environment=$ENVIRONMENT" -auto-approve
fi

echo "✅ ¡Infraestructura de ${ENVIRONMENT} destruida!"
echo ""
echo "💡 Para eliminar completamente el workspace, ejecuta:"
echo "   terraform workspace select default"
echo "   terraform workspace delete $ENVIRONMENT"
```

Hazlo ejecutable:
```bash
chmod +x scripts/destroy.sh
```

### Paso 2: Crear script destroy para Windows

Crea `scripts/destroy.ps1`:

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$Environment,
    [string]$ProjectName = "twin"
)

# Validar parámetro de entorno
if ($Environment -notmatch '^(dev|test|prod)$') {
    Write-Host "Error: Entorno '$Environment' no válido" -ForegroundColor Red
    Write-Host "Entornos disponibles: dev, test, prod" -ForegroundColor Yellow
    exit 1
}

Write-Host "Preparando para destruir la infraestructura $ProjectName-$Environment..." -ForegroundColor Yellow

# Ir al directorio terraform
Set-Location (Join-Path (Split-Path $PSScriptRoot -Parent) "terraform")

# Comprobar si existe el workspace
$workspaces = terraform workspace list
if (-not ($workspaces | Select-String $Environment)) {
    Write-Host "Error: El workspace '$Environment' no existe" -ForegroundColor Red
    Write-Host "Workspaces disponibles:" -ForegroundColor Yellow
    terraform workspace list
    exit 1
}

# Seleccionar el workspace
terraform workspace select $Environment

Write-Host "Vaciando los buckets S3..." -ForegroundColor Yellow

# Obtener ID de cuenta AWS para los nombres de los buckets
$awsAccountId = aws sts get-caller-identity --query Account --output text

# Definir nombres de buckets con ID de cuenta
$FrontendBucket = "$ProjectName-$Environment-frontend-$awsAccountId"
$MemoryBucket = "$ProjectName-$Environment-memory-$awsAccountId"

# Vaciar el bucket de frontend si existe
try {
    aws s3 ls "s3://$FrontendBucket" 2>$null | Out-Null
    Write-Host "  Vaciando $FrontendBucket..." -ForegroundColor Gray
    aws s3 rm "s3://$FrontendBucket" --recursive
} catch {
    Write-Host "  Bucket frontend no encontrado o ya vacío" -ForegroundColor Gray
}

# Vaciar el bucket de memoria si existe
try {
    aws s3 ls "s3://$MemoryBucket" 2>$null | Out-Null
    Write-Host "  Vaciando $MemoryBucket..." -ForegroundColor Gray
    aws s3 rm "s3://$MemoryBucket" --recursive
} catch {
    Write-Host "  Bucket memory no encontrado o ya vacío" -ForegroundColor Gray
}

Write-Host "Ejecutando terraform destroy..." -ForegroundColor Yellow

# Ejecutar terraform destroy con auto-approve
if ($Environment -eq "prod" -and (Test-Path "prod.tfvars")) {
    terraform destroy -var-file=prod.tfvars -var="project_name=$ProjectName" -var="environment=$Environment" -auto-approve
} else {
    terraform destroy -var="project_name=$ProjectName" -var="environment=$Environment" -auto-approve
}

Write-Host "¡Infraestructura de $Environment destruida!" -ForegroundColor Green
Write-Host ""
Write-Host "  Para eliminar completamente el workspace, ejecuta:" -ForegroundColor Cyan
Write-Host "   terraform workspace select default" -ForegroundColor White
Write-Host "   terraform workspace delete $Environment" -ForegroundColor White
```

### Paso 3: Usando los scripts de destrucción

Para destruir un entorno específico:

**Mac/Linux:**
```bash
# Destruir entorno dev
./scripts/destroy.sh dev

# Destruir entorno test
./scripts/destroy.sh test

# Destruir entorno prod
./scripts/destroy.sh prod
```

**Windows (PowerShell):**
```powershell
# Destruir entorno dev
.\scripts\destroy.ps1 -Environment dev

# Destruir entorno test
.\scripts\destroy.ps1 -Environment test

# Destruir entorno prod
.\scripts\destroy.ps1 -Environment prod
```

### ¿Qué se destruye?

Los scripts de destrucción:
1. Vacían los buckets S3 (frontend y memory)
2. Eliminan todos los recursos de AWS creados por Terraform:
   - Funciones Lambda
   - API Gateway
   - Buckets S3
   - Distribuciones de CloudFront
   - Roles y políticas IAM
   - Registros de Route 53 (si hay dominio personalizado)
   - Certificados ACM (si hay dominio personalizado)

### Notas importantes

- **CloudFront**: Las distribuciones pueden tardar 5-15 minutos en eliminarse completamente
- **Workspaces**: Los scripts destruyen recursos pero dejan el workspace. Para eliminar completamente un workspace:
  ```bash
  terraform workspace select default
  terraform workspace delete dev  # o test, prod
  ```
- **Ahorro de costes**: Siempre destruye entornos no usados para evitar cargos

## Parte 8: OPCIONAL - Añadir dominio personalizado

Si quieres un dominio profesional para tu twin en producción, sigue estos pasos.

### Paso 1: Registrar un dominio (si es necesario)

**Importante**: Registrar dominios requiere permisos de facturación, así que deberás iniciar sesión como **root user** para este paso.

**Opción A: Registrar a través de AWS Route 53**
1. Cierra sesión de tu usuario IAM
2. Inicia sesión en la consola de AWS como **root user**
3. Ve a Route 53 en la consola de AWS
4. Haz clic en **Registered domains** → **Register domain**
5. Busca tu dominio deseado
6. Agrega al carrito y finaliza la compra (normalmente $12-40/año según el dominio)
7. Espera el registro (5-30 minutos)
8. Una vez registrado, vuelve a iniciar sesión como tu usuario IAM (`aiengineer`) para continuar

**Opción B: Usar dominio existente**
- Si ya posees un dominio:
  - Transfiere el DNS a Route 53, o
  - Crea la zona alojada y actualiza los nameservers en tu registrador

### Paso 2: Crear zona alojada (si no se creó automáticamente)

Si Route 53 no creó la zona alojada automáticamente:
1. Ve a Route 53 → **Hosted zones**
2. Haz clic en **Create hosted zone**
3. Escribe tu dominio
4. Tipo: Public hosted zone
5. Haz clic en **Create**

### Paso 3: Crear configuración de producción

Crea `terraform/prod.tfvars`:

```hcl
project_name             = "twin"
environment              = "prod"
bedrock_model_id         = "amazon.nova-lite-v1:0"  # Mejor modelo para producción
lambda_timeout           = 60
api_throttle_burst_limit = 20
api_throttle_rate_limit  = 10
use_custom_domain        = true
root_domain              = "tudominio.com"  # Reemplaza por tu dominio real
```

### Paso 4: Desplegar producción con dominio

**Mac/Linux:**
```bash
./scripts/deploy.sh prod
```

**Windows (PowerShell):**
```powershell
.\scripts\deploy.ps1 -Environment prod
```

El despliegue hará:
1. Crear certificado SSL en ACM
2. Validar propiedad del dominio vía DNS
3. Configurar CloudFront con tu dominio
4. Crear registros de Route 53

**Nota**: La validación del certificado puede tardar 5-30 minutos. El script esperará.

### Paso 5: Probar tu dominio personalizado

Una vez desplegado:
1. Visita `https://tudominio.com`
2. Visita `https://www.tudominio.com`
3. ¡Ambas deben mostrar tu Digital Twin!

## Comprendiendo los Workspaces de Terraform

### Cómo los workspaces aíslan entornos

Cada workspace mantiene su propio archivo de estado:
```
terraform.tfstate.d/
├── dev/
│   └── terraform.tfstate
├── test/
│   └── terraform.tfstate
└── prod/
    └── terraform.tfstate
```

### Gestión de workspaces

**Listar workspaces:**
```bash
terraform workspace list
```

**Cambiar workspace:**
```bash
terraform workspace select dev
```

**Ver el workspace actual:**
```bash
terraform workspace show
```

### Nombrado de recursos

Los recursos son nombrados con prefijo de entorno:
- Dev: `twin-dev-api`, `twin-dev-memory`
- Test: `twin-test-api`, `twin-test-memory`
- Prod: `twin-prod-api`, `twin-prod-memory`

## Optimización de Costes

### Configuración específica por entorno

Nuestra configuración usa diferentes parámetros según el entorno:

**Desarrollo:**
- Modelo Nova Micro (el más barato)
- Throttling bajo en API
- Sin dominio personalizado

**Test:**
- Modelo Nova Micro
- Throttling estándar
- Sin dominio personalizado

**Producción:**
- Modelo Nova Lite (más calidad)
- Límites de throttling más altos
- Dominio personalizado con SSL

### Consejos para ahorrar gastos

1. **Destruye entornos no usados** - No dejes test funcionando innecesariamente
2. **Usa modelos adecuados** - Nova Micro para dev/test
3. **Configura el throttling de API** - Evita gastos inesperados
4. **Monitorea con etiquetas** - Todos los recursos están etiquetados por entorno

## Resolución de problemas (Troubleshooting)

### Problemas de estado de Terraform

Si Terraform se confunde sobre los recursos:

```bash
# Actualiza el estado desde AWS
terraform refresh

# Si el recurso existe en AWS pero no en el estado
terraform import aws_lambda_function.api twin-dev-api
```

### Fallos del script de despliegue

**"Lambda package not found"**
- Asegúrate de que Docker esté corriendo
- Ejecuta `cd backend && uv run deploy.py` manualmente

**"S3 bucket already exists"**
- Los nombres de buckets deben ser únicos globalmente
- Cambia project_name en terraform.tfvars

**"Certificate validation timeout"**
- Verifica que Route 53 tenga los registros de validación
- Espera más tiempo (puede tardar hasta 30 minutos)

### Frontend sin actualizarse

Después del despliegue, CloudFront puede cachear contenido antiguo:

```bash
# Obtener ID de la distribución
aws cloudfront list-distributions --query "DistributionList.Items[?Comment=='twin-dev'].Id" --output text

# Hacer invalidación
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
```

## Buenas prácticas

### 1. Control de versiones

Siempre sube tus archivos Terraform al control de versiones:
```bash
git add terraform/*.tf terraform/*.tfvars
git commit -m "Add Terraform infrastructure"
```

Nunca subas:
- Archivos `terraform.tfstate`
- Directorio `.terraform/`
- Credenciales AWS

### 2. Revisa antes de aplicar

Antes de ejecutar cambios:
```bash
terraform plan
```

### 3. Usa variables

No pongas valores fijos, usa variables:
```hcl
# Correcto
bucket = "${local.name_prefix}-memory"

# Incorrecto
bucket = "twin-dev-memory"
```

### 4. Etiqueta todo

Nuestra configuración etiqueta todos los recursos:
```hcl
tags = {
  Project     = var.project_name
  Environment = var.environment
  ManagedBy   = "terraform"
}
```

## ¡Lo que lograste hoy!

- ✅ Aprendiste Infraestructura como Código con Terraform
- ✅ Automatizaste el despliegue completo en AWS
- ✅ Creaste múltiples entornos aislados
- ✅ Hiciste despliegues con un solo comando
- ✅ Configuraste scripts profesionales de despliegue
- ✅ Opcional: Configuraste dominio personalizado con SSL

## Resumen de Arquitectura

Tu Terraform gestiona:

```
Configuración Terraform
    ├── Buckets S3 (Frontend + Memory)
    ├── Lambda con rol IAM
    ├── API Gateway con rutas
    ├── Distribución CloudFront
    └── Opcional: Route 53 + Certificado ACM

Gestionado mediante Workspaces:
    ├── dev/   (Entorno de desarrollo)
    ├── test/  (Entorno de pruebas)
    └── prod/  (Producción con dominio personalizado)
```

## Próximos pasos

Mañana (Día 5) agregaremos CI/CD con GitHub Actions:
- Tests automatizados en cada pull request
- Pipelines de despliegue para cada entorno
- Revisión de cambios en infraestructura
- Rollbacks automáticos
- Eliminación completa de infraestructura

¡Tu Digital Twin ya tiene Infraestructura como Código profesional que cualquier equipo puede desplegar y gestionar!

## Recursos

- [Documentación de Terraform](https://www.terraform.io/docs)
- [Proveedor AWS de Terraform](https://registry.terraform.io/providers/hashicorp/aws/latest)
- [Buenas prácticas con Terraform](https://www.terraform-best-practices.com/)
- [Buenas prácticas IAM de AWS](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

¡Felicidades por automatizar el despliegue de tu infraestructura! 🚀