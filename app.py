from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_website(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "page-title"))
        )
    except Exception as e:
        driver.quit()
        return {"error": f"Erro ao carregar os dados: {str(e)}"}

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    product_name = soup.select_one('.page-title .base')
    product_name = product_name.get_text(strip=True) if product_name else "N/A"

    price_wrapper = soup.find('span', attrs={'data-price-type': 'finalPrice'})
    price = price_wrapper.select_one('.price').get_text(strip=True) if price_wrapper else "N/A"

    driver.quit()

    return {
        "product_name": product_name,
        "price": price
    }

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
