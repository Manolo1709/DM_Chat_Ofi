variable "region" {
  description = "Región de AWS (AWS Academy solo permite us-east-1 y us-west-2)"
  type        = string
  default     = "us-east-1"
}

variable "tipo_instancia" {
  description = "Tipo de instancia EC2"
  type        = string
  default     = "t3.micro"
}

variable "disco_gb" {
  description = "Tamaño del disco en GB"
  type        = number
  default     = 16
}

variable "ssh_cidr" {
  description = "Rango con acceso SSH. Vacío = solo la IP pública desde la que se ejecuta Terraform"
  type        = string
  default     = ""
}

variable "repositorio" {
  description = "Repositorio que se clona en la instancia"
  type        = string
  default     = "https://github.com/Manolo1709/DM_Chat_Ofi.git"
}

variable "dominio" {
  description = "Dominio propio (p. ej. lataberna.manoloplr.com). Vacío = <ip>.sslip.io"
  type        = string
  default     = ""
}
