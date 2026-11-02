# Despliegue de App 2 en AWS EC2 (Terraform)

Una sola instancia Linux con Docker Compose: `proxy` (Caddy, HTTPS) → `frontend` (nginx + SPA) → `backend` (FastAPI). Solo Caddy publica puertos (80 y 443). Sin base de datos ni servicios de datos; el único volumen guarda el certificado TLS de Caddy.

La infraestructura está en `aws/terraform/`. Terraform crea el par de claves SSH, el grupo de seguridad `taberna-sg`, la instancia y una IP elástica, que no cambia al parar y arrancar la instancia. Al arrancar, la instancia ejecuta `aws/user-data.sh`, que crea 2 GB de swap, instala Docker y clona el repositorio en `/home/ubuntu/taberna`.

## Datos del despliegue

| Dato | Valor |
|---|---|
| Región | `us-east-1` (variable `region`) |
| Tipo de instancia | `t3.micro` (1 GB + 2 GB de swap) |
| Imagen (AMI) | `ubuntu-noble-24.04-amd64-server-20261023` |
| Disco | 16 GB gp3 |
| IP pública | `52.21.114.192` (IP elástica: no cambia al parar la instancia) |
| Dominio | `lateberna.manoloplr.com` (variable `dominio`; sin ella, la IP con guiones en sslip.io) |
| URL | https://lateberna.manoloplr.com |
| Commit desplegado | `f936c2c` |
| Versiones | Terraform `1.16.5`, Docker `29.9.2`, Compose `v5.7.0` |

## 0. Requisitos en el PC

- Terraform 1.6 o superior: `winget install Hashicorp.Terraform`
- AWS CLI: `winget install Amazon.AWSCLI`, y credenciales con `aws configure`. En AWS Academy (Learner Lab) se copian de **AWS Details → AWS CLI** a `C:\Users\<usuario>\.aws\credentials`; caducan al cerrar el laboratorio.
- **Los ficheros de Docker tienen que estar subidos a GitHub** (`docker/`, `docker-compose*.yml`, `.dockerignore`), porque la instancia clona el repositorio.

## 1. Crear la infraestructura

```powershell
cd aws\terraform
terraform init
terraform plan
terraform apply
terraform output
```

`apply` deja la clave privada en `aws\terraform\taberna.pem`. Ni ese archivo ni el `terraform.tfstate` van a Git (están en `.gitignore`): el estado contiene la clave.

El SSH queda abierto solo para la IP pública desde la que ejecutas Terraform. Si cambias de red, vuelve a ejecutar `terraform apply`.

Espera dos o tres minutos a que termine `user-data.sh`. Se puede comprobar con:

```powershell
ssh -i taberna.pem ubuntu@IP_PUBLICA "cloud-init status --wait && docker --version"
```

## 1 bis. Dominio propio

Con la variable `dominio` en `terraform.tfvars` (aquí, `dominio = "lateberna.manoloplr.com"`), las salidas `dominio` y `url` usan ese nombre. Sin ella, se usa `<ip-con-guiones>.sslip.io`, que se resuelve solo.

En el proveedor DNS del dominio hay que crear un registro **A** de `lateberna` que apunte a la IP elástica (`terraform output ip_publica`, aquí `52.21.114.192`). Caddy pide el certificado en cuanto el nombre resuelve a la instancia.

## 2. Subir el `.env`

Desde `aws\terraform`:

```powershell
scp -i taberna.pem ..\..\.env ubuntu@IP_PUBLICA:taberna/.env
ssh -i taberna.pem ubuntu@IP_PUBLICA
```

Ya en la instancia, añade el dominio (el de `terraform output dominio`) y protege el archivo:

```bash
cd taberna
echo "DOMINIO=lateberna.manoloplr.com" >> .env
chmod 600 .env
```

El `.env` necesita `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, `CLERK_SECRET_KEY` y `VITE_CLERK_PUBLISHABLE_KEY` (ver `.env.example`). La IA es Groq: `LLM_BASE_URL=https://api.groq.com/openai/v1` y `LLM_MODEL=qwen/qwen3.8-27b`.

Para cambiar solo la IA, edita las líneas `LLM_*` del `.env` de la instancia y recrea el backend:

```bash
docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d --force-recreate backend
```

## 3. Clerk

En el panel de Clerk hay que permitir el origen de `terraform output url` (https://lateberna.manoloplr.com). El backend ya lo recibe como `FRONTEND_ORIGIN`.

## 4. Arrancar

```bash
docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.aws.yml ps
```

La primera vez tarda unos minutos (compilación y certificado). Comprobación:

```bash
curl https://lateberna.manoloplr.com/api/health      # {"status":"ok"}
curl -X POST https://lateberna.manoloplr.com/api/calcular -H "Content-Type: application/json" -d '{}'   # 401 sin sesión
```

Logs: `docker compose -f docker-compose.yml -f docker-compose.aws.yml logs -f backend`.

Los contenedores tienen `restart: unless-stopped`: tras reiniciar la instancia vuelven a arrancar solos. La IP es elástica, así que parar y arrancar la instancia no cambia ni la IP ni el dominio.

## 5. Actualizar

```bash
cd taberna && git pull
docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d --build
```

## 6. Retirar los recursos al terminar

```powershell
cd aws\terraform
terraform destroy
```

Borra la instancia, su disco, la IP elástica, el grupo de seguridad y el par de claves. Después hay que borrar el registro DNS del dominio.
