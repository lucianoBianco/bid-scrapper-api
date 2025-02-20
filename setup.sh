#!/bin/bash

echo "🚀 Iniciando configuração do ambiente..."

# Atualizar pacotes e instalar dependências básicas
sudo apt update
sudo apt install -y python3-pip python3-venv python3-dev unzip wget curl git nginx

# Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências do Python
pip install --upgrade pip
pip install -r requirements.txt

# Instalar o ChromeDriver e o Google Chrome
echo "🖥 Instalando Chrome e ChromeDriver..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb || sudo apt --fix-broken install -y
rm google-chrome-stable_current_amd64.deb

wget https://chromedriver.storage.googleapis.com/133.0.6943.53/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm chromedriver_linux64.zip

# Configurar o Nginx
echo "🛠 Configurando Nginx..."
sudo cp nginx/bid-scrapper-api /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/bid-scrapper-api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# Configurar systemd para rodar o serviço automaticamente
echo "🔄 Configurando serviço systemd..."
sudo cp systemd/bid-scrapper.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bid-scrapper

echo "✅ Setup finalizado com sucesso!"
