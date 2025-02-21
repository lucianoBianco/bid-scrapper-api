from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import tempfile
import shutil
import os
import uuid

app = Flask(__name__)

# Criar diretório base para as sessões do Chrome
CHROME_DATA_DIR = "/tmp/chrome_data"
if not os.path.exists(CHROME_DATA_DIR):
    os.makedirs(CHROME_DATA_DIR)

def scrape_website(url):
    print(f"Iniciando scrape da URL: {url}")
    
    # Criar subdiretório único para esta sessão
    session_id = str(uuid.uuid4())
    user_data_dir = os.path.join(CHROME_DATA_DIR, session_id)
    os.makedirs(user_data_dir, exist_ok=True)
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Nova versão do headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--single-process")
    options.add_argument("--disable-javascript")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--remote-debugging-port=0")  # Porta aleatória
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.binary_location = "/snap/bin/chromium"
    
    driver = None
    try:
        print("Iniciando Chromium...")
        service = webdriver.ChromeService(
            executable_path='/usr/bin/chromedriver',
            log_path='/tmp/chromedriver.log'
        )
        driver = webdriver.Chrome(service=service, options=options)
        print("Chromium iniciado com sucesso")
        
        print(f"Acessando URL: {url}")
        driver.get(url)
        print("URL acessada com sucesso")
        
        try:
            WebDriverWait(driver, 10).until(  # Aumentado para 10 segundos
                EC.presence_of_element_located((By.CLASS_NAME, "page-title"))
            )
        except Exception as e:
            print(f"Erro ao esperar elemento: {str(e)}")
            return {"error": f"Erro ao carregar os dados: {str(e)}"}

        html = driver.page_source
        print("HTML capturado")
        
        soup = BeautifulSoup(html, "html.parser")
        print("BS4 parser criado")

        product_name = soup.select_one('.page-title .base')
        product_name = product_name.get_text(strip=True) if product_name else "N/A"
        print(f"Nome do produto: {product_name}")

        price_wrapper = soup.find('span', attrs={'data-price-type': 'finalPrice'})
        price = price_wrapper.select_one('.price').get_text(strip=True) if price_wrapper else "N/A"
        print(f"Preço: {price}")

        return {
            "product_name": product_name,
            "price": price
        }
    except Exception as e:
        print(f"Erro durante o scrape: {str(e)}")
        return {"error": f"Erro durante o scrape: {str(e)}"}
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"Erro ao fechar driver: {str(e)}")
        try:
            # Limpar diretório da sessão
            shutil.rmtree(user_data_dir, ignore_errors=True)
        except Exception as e:
            print(f"Erro ao limpar diretório: {str(e)}")

@app.route("/")
def health_check():
    return jsonify({"status": "ok", "message": "API is running"}), 200

@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL não fornecida"}), 400

    result = scrape_website(url)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
