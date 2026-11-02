# Una instancia EC2 con Docker para App 2. Usa la VPC por defecto de la cuenta.

# Ubuntu Server 24.04 LTS oficial de Canonical
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}

# IP pública de quien ejecuta Terraform, para limitar el SSH a ella
data "http" "mi_ip" {
  url = "https://checkip.amazonaws.com"
}

locals {
  ssh_cidr = var.ssh_cidr != "" ? var.ssh_cidr : "${chomp(data.http.mi_ip.response_body)}/32"
}

# Par de claves SSH generado aquí; la privada se guarda en taberna.pem (fuera de Git)
resource "tls_private_key" "ssh" {
  algorithm = "ED25519"
}

resource "aws_key_pair" "taberna" {
  key_name   = "taberna"
  public_key = tls_private_key.ssh.public_key_openssh
}

resource "local_sensitive_file" "clave_privada" {
  content         = tls_private_key.ssh.private_key_openssh
  filename        = "${path.module}/taberna.pem"
  file_permission = "0600"
}

resource "aws_security_group" "taberna" {
  name        = "taberna-sg"
  description = "La Taberna: SSH restringido, HTTP y HTTPS"
}

resource "aws_vpc_security_group_ingress_rule" "ssh" {
  security_group_id = aws_security_group.taberna.id
  description       = "SSH solo desde la IP de administracion"
  ip_protocol       = "tcp"
  from_port         = 22
  to_port           = 22
  cidr_ipv4         = local.ssh_cidr
}

resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.taberna.id
  description       = "HTTP (Lets Encrypt y redireccion a HTTPS)"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "https" {
  security_group_id = aws_security_group.taberna.id
  description       = "HTTPS"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "todo" {
  security_group_id = aws_security_group.taberna.id
  description       = "Salida a internet (paquetes, imagenes Docker, IA, Clerk)"
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_instance" "taberna" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.tipo_instancia
  key_name               = aws_key_pair.taberna.key_name
  vpc_security_group_ids = [aws_security_group.taberna.id]

  user_data = templatefile("${path.module}/../user-data.sh", {
    repositorio = var.repositorio
  })

  root_block_device {
    volume_size           = var.disco_gb
    volume_type           = "gp3"
    delete_on_termination = true
  }

  # Exige IMDSv2 (buena práctica de seguridad en EC2)
  metadata_options {
    http_tokens = "required"
  }

  tags = {
    Name = "la-taberna"
  }
}

# IP elástica: la dirección no cambia al parar y arrancar la instancia
resource "aws_eip" "taberna" {
  domain   = "vpc"
  instance = aws_instance.taberna.id

  tags = {
    Name = "la-taberna"
  }
}
