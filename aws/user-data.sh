#!/bin/bash
# Script de arranque de la instancia EC2 (Ubuntu 24.04). Terraform lo pasa como
# "datos de usuario" y se ejecuta una sola vez, la primera vez que arranca.
set -euxo pipefail

# 2 GB de swap: con 1 GB de RAM (t3.micro) la compilación del frontend se queda corta
if [ ! -f /swapfile ]; then
  fallocate -l 2G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# Docker Engine + plugin de Compose desde el repositorio oficial de Docker
apt-get update
apt-get install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sh
systemctl enable --now docker

# El usuario ubuntu puede usar docker sin sudo
usermod -aG docker ubuntu

# Código de la aplicación en /home/ubuntu/taberna (el .env se sube aparte)
if [ ! -d /home/ubuntu/taberna ]; then
  sudo -u ubuntu git clone ${repositorio} /home/ubuntu/taberna
fi
