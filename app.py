from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import subprocess
import time
import uuid

app = Flask(__name__)

def kill_chrome_processes():
    # Tenta matar todos os processos do Chrome/Chromium antes de iniciar
    try:
        subprocess.run(['pkill', '-f', 'chrome'], stderr=subprocess.DEVNULL)
        subprocess.run(['pkill', '-f', 'chromium'], stderr=subprocess.DEVNULL)
        subprocess.run(['pkill', '-f', 'chromedriver'], stderr=subprocess.DEVNULL)
        time.sleep(1)  # Espera um pouco para os processos terminarem
    except Exception as e:
        print(f"Erro ao tentar matar processos: {str(e)}")

def scrape_website(url):
    print(f"Iniciando scrape da URL: {url}")
    
    # Tenta matar processos Chrome existentes
    kill_chrome_processes()
    
    # Usa diretório temporário com nome aleatório que garante ser único
    temp_dir = f"/tmp/chrome-{uuid.uuid4()}"
    os.makedirs(temp_dir, exist_ok=True)
    
    options = webdriver.ChromeOptions()
    # Força um perfil temporário completamente novo
    options.add_argument(f"--user-data-dir={temp_dir}")
    options.add_argument("--incognito")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-javascript")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--headless=new")  # Nova versão do modo headless
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Adiciona argumentos que ajudam a evitar problemas de sessão
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--single-process")
    # Especifica o caminho para o chromium
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
            WebDriverWait(driver, 10).until(
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
                print("Driver fechado com sucesso")
            except Exception as e:
                print(f"Erro ao fechar driver: {str(e)}")
                
        # Tenta limpar o diretório temporário
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass
            
        # Garante que todos os processos do Chrome sejam encerrados após o uso
        kill_chrome_processes()

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