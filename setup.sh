#!/bin/bash

# Atualizar pacotes e instalar dependências
sudo apt update
sudo apt install -y python3-pip python3-dev python3-venv nginx

# Criar e ativar ambiente virtual
python3 -m venv /home/your_user/api/bid-scrapper-api/venv
source /home/your_user/api/bid-scrapper-api/venv/bin/activate

# Instalar dependências do projeto
pip install --upgrade pip
pip install flask gunicorn selenium beautifulsoup4

# Baixar o ChromeDriver (ajuste conforme necessário, dependendo da versão do Chrome)
wget https://chromedriver.storage.googleapis.com/133.0.6943.53/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d /usr/local/bin/

# Garantir permissões adequadas para o ChromeDriver
sudo chmod +x /usr/local/bin/chromedriver

# Configuração do Nginx e Gunicorn será feita manualmente a seguir
