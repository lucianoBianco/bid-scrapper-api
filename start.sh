#!/bin/bash

# Ativar o ambiente virtual
source /home/your_user/api/bid-scrapper-api/venv/bin/activate

# Rodar o Gunicorn em segundo plano
nohup gunicorn -w 4 -b 127.0.0.1:5000 app:app &

# Verifique se o Gunicorn iniciou corretamente
echo "Gunicorn rodando em segundo plano..."
