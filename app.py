from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_website(url):
  print(f"Iniciando scrape da URL: {url}")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--single-process")
    options.add_argument("--disable-javascript")
    options.add_argument("--remote-debugging-port=9222")
    options.binary_location = "/snap/bin/chromium"  # Caminho do Chromium no Snap
    
    try:
        print("Iniciando Chromium...")
        service = webdriver.ChromeService(executable_path='/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
        print("Chromium iniciado com sucesso")
        
        print(f"Acessando URL: {url}")
        driver.get(url)
        print("URL acessada com sucesso")

    except Exception as e:
        return {"error": f"Erro ao carregar os dados: {str(e)}"}

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "page-title"))
        )
    except Exception as e:
        driver.quit()
        return {"error": f"Erro ao carregar os dados: {str(e)}"}

    try:
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

        driver.quit()
        print("Scrape finalizado com sucesso")

        return {
            "product_name": product_name,
            "price": price
        }
    except Exception as e:
        print(f"Erro durante o scrape: {str(e)}")
        if 'driver' in locals():
            try:
                driver.quit()
            except:
                pass
        return {"error": f"Erro durante o scrape: {str(e)}"}
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
