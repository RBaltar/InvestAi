import requests
import os
import pandas as pd
from sqlalchemy import create_engine
import logging
from bs4 import BeautifulSoup
from datetime import datetime

# Configuração do log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DataCollector:
   import os
from sqlalchemy import create_engine

class DataCollector:
    def __init__(self):
        """Inicializa a conexão com o banco de dados."""
        db_url = os.getenv("POSTGRES_URI")  # Obtém a URL do PostgreSQL da variável de ambiente
        if not db_url:
            raise ValueError("❌ Erro: A variável de ambiente POSTGRES_URI não foi definida!")

        self.db_engine = create_engine(db_url)
        self.base_url = "https://statusinvest.com.br/acoes/"
        logging.info("✅ Conexão com o banco de dados estabelecida.")

    def get_ibovespa_tickers(self):
        """Retorna uma lista de tickers do IBOVESPA para coleta de dados."""
        tickers = ["PETR4", "VALE3", "ITUB4", "BBDC4", "ABEV3", 
                   "BBAS3", "B3SA3", "WEGE3", "RENT3", "EQTL3"]
        logging.info(f"📊 Lista de tickers para monitoramento: {tickers}")
        return tickers

    def fetch_stock_data(self, tickers: list) -> pd.DataFrame:
        """Obtém dados via web scraping no site StatusInvest."""
        all_data = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }

        for ticker in tickers:
            try:
                url = f"{self.base_url}{ticker}"
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    logging.error(f"❌ Erro ao acessar {url}, código {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")

                # DEBUG: Exibir parte do HTML para verificar estrutura
                # print(soup.prettify()[:2000])  # Mostra os primeiros 2000 caracteres do HTML para análise

                def extract_value(label):
                    """Extrai valores com base no nome do indicador no HTML"""
                    try:
                        label_element = soup.find("h3", string=label)
                        if label_element:
                            value_element = label_element.find_next("strong", class_="value")
                            return float(value_element.text.strip().replace(',', '.').replace('%', '').replace('.', '')) if value_element else None
                        return None
                    except Exception as e:
                        logging.warning(f"⚠️ Erro ao extrair {label} para {ticker}: {e}")
                        return None

                try:
                    price_tag = soup.select_one("strong.value")  # Classe real do preço no StatusInvest
                    close_price = float(price_tag.text.strip().replace(',', '.')) if price_tag else None
                except Exception as e:
                    logging.warning(f"⚠️ Erro ao extrair preço de fechamento para {ticker}: {e}")
                    close_price = None

                pe = extract_value("P/L")
                dividend_yield = extract_value("Dividend Yield")
                roe = extract_value("ROE")
                market_value = extract_value("Valor de mercado")  # Agora corretamente extraído
                volume = extract_value("VOLUME (dia)")

                all_data.append(pd.DataFrame([{
                    "date": datetime.now().date(),
                    "ticker": ticker,
                    "close": close_price,
                    "price_earnings": pe,
                    "dividend_yield": dividend_yield,
                    "roe": roe,
                    "market_value": market_value,
                    "volume": volume
                }]))

                logging.info(f"✅ Dados coletados para {ticker}")

            except Exception as e:
                logging.error(f"❌ Erro ao buscar dados de {ticker}: {e}")

        if all_data:
            result = pd.concat(all_data, ignore_index=True)
            logging.info("✅ Todos os dados coletados com sucesso!")
            return result
        else:
            logging.warning("⚠️ Nenhum dado válido encontrado para os tickers.")
            return pd.DataFrame()

    def save_to_database(self, df: pd.DataFrame, table_name: str):
        """Salva os dados coletados no banco de dados."""
        if df.empty:
            logging.warning(f"⚠️ Nenhum dado para salvar na tabela {table_name}.")
            return

        try:
            df.to_sql(table_name, self.db_engine, if_exists="append", index=False)
            logging.info(f"✅ Dados salvos na tabela {table_name} com sucesso!")
        except Exception as e:
            logging.error(f"❌ Erro ao salvar dados no banco: {e}")

if __name__ == "__main__":
    collector = DataCollector()

    # Buscar os principais ativos automaticamente
    tickers = collector.get_ibovespa_tickers()

    if tickers:
        df_prices = collector.fetch_stock_data(tickers)
        collector.save_to_database(df_prices, "acoes_historico")

        print("✅ Processo finalizado com sucesso!")
    else:
        print("❌ Não foi possível obter os principais ativos.")
