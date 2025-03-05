import os
import schedule
import time
import subprocess
import logging
from pymongo import MongoClient
from datetime import datetime

# Configuração do MongoDB
MONGO_URI = os.getenv("MONGO_URI")  # Pega a URI do ambiente

if not MONGO_URI:
    raise ValueError("❌ Erro: A variável de ambiente MONGO_URI não foi definida!")

client = MongoClient(MONGO_URI)
db = client.get_database()

print("✅ Conexão com MongoDB Atlas estabelecida com sucesso!")

# Configuração do log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def salvar_log_mongo(mensagem, status="INFO"):
    """
    Salva um log no MongoDB.
    """
    log_entry = {
        "timestamp": datetime.now(),
        "mensagem": mensagem,
        "status": status
    }
    collection.insert_one(log_entry)
    logging.info(f"📌 Log salvo no MongoDB: {mensagem}")

def executar_coleta():
    """
    Executa o script de web scraping automaticamente e salva os logs no MongoDB.
    """
    mensagem = "🚀 Iniciando a coleta de dados..."
    logging.info(mensagem)
    salvar_log_mongo(mensagem)

    try:
        subprocess.run(["python", "src/collectors/data_collector.py"], check=True)
        mensagem = "✅ Coleta concluída com sucesso!"
        salvar_log_mongo(mensagem, status="SUCCESS")
        logging.info(mensagem)
    except subprocess.CalledProcessError as e:
        mensagem = f"❌ Erro ao executar a coleta: {e}"
        salvar_log_mongo(mensagem, status="ERROR")
        logging.error(mensagem)

# Agendar para rodar a cada 4 horas, começando às 00h
schedule.every().day.at("10:00").do(executar_coleta)
schedule.every(1).hours.do(executar_coleta)

mensagem = "⏳ Agendador iniciado! Coleta rodará a cada 1 hora..."
salvar_log_mongo(mensagem)
logging.info(mensagem)

# Loop infinito para manter o agendador rodando
while True:
    schedule.run_pending()
    time.sleep(60)  # Verifica a cada 60 segundos
