import schedule
import time
import subprocess
import logging
from pymongo import MongoClient
from datetime import datetime

# Configuração do MongoDB
MONGO_URI = "mongodb://localhost:27017/"  # Se for remoto, coloque a URI do Atlas ou outro servidor
DB_NAME = "invest_ai"
COLLECTION_NAME = "logs_coleta"

# Conectar ao MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

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
