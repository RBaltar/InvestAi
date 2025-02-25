from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import logging

# Configuração do log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_stock_data_selenium(ticker):
    """
    Usa Selenium para extrair informações do StatusInvest.
    """
    options = Options()
    options.add_argument("--headless")  # Executa sem abrir o navegador
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = f"https://statusinvest.com.br/acoes/{ticker}"
    driver.get(url)

    try:
        # Espera até 10 segundos para os elementos aparecerem
        wait = WebDriverWait(driver, 10)

        # Capturar o HTML da página para debug
        page_source = driver.page_source
        logging.info(f"🔍 HTML coletado para {ticker} (trecho inicial): {page_source[:500]}")

        # Tenta encontrar os elementos com WebDriverWait
        price = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "value"))).text.replace(',', '.')
        pe = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='P/L']/following-sibling::strong"))).text.replace(',', '.')
        dividend_yield = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Dividend Yield']/following-sibling::strong"))).text.replace('%', '').replace(',', '.')
        roe = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='ROE']/following-sibling::strong"))).text.replace(',', '.')
        market_value = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Valor de mercado']/following-sibling::strong"))).text.replace('.', '').replace(',', '.')
        volume = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Volume diário']/following-sibling::strong"))).text.replace('.', '').replace(',', '.')

        data = {
            "ticker": ticker,
            "price": float(price) if price else None,
            "price_earnings": float(pe) if pe else None,
            "dividend_yield": float(dividend_yield) if dividend_yield else None,
            "roe": float(roe) if roe else None,
            "market_value": float(market_value) if market_value else None,
            "volume": int(volume) if volume else None,
        }

        logging.info(f"✅ Dados coletados para {ticker}: {data}")

    except Exception as e:
        logging.error(f"❌ Erro ao coletar dados para {ticker}: {e}")
        data = None

    driver.quit()
    return data

if __name__ == "__main__":
    tickers = ["PETR4", "VALE3", "ITUB4", "BBDC4"]  # Teste inicial
    all_data = []

    for ticker in tickers:
        stock_data = fetch_stock_data_selenium(ticker)
        if stock_data:
            all_data.append(stock_data)

    df = pd.DataFrame(all_data)
    print(df)
