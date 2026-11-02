locals {
  dominio = var.dominio != "" ? var.dominio : "${replace(aws_eip.taberna.public_ip, ".", "-")}.sslip.io"
}

output "ip_publica" {
  description = "IP pública de la instancia"
  value       = aws_eip.taberna.public_ip
}

output "dominio" {
  description = "Valor para DOMINIO en el .env de la instancia"
  value       = local.dominio
}

output "url" {
  description = "Dirección pública de la aplicación (añadirla también en Clerk)"
  value       = "https://${local.dominio}"
}

output "ssh" {
  description = "Comando para entrar en la instancia"
  value       = "ssh -i taberna.pem ubuntu@${aws_eip.taberna.public_ip}"
}

output "ami" {
  description = "Imagen usada (para documentarla)"
  value       = data.aws_ami.ubuntu.name
}
