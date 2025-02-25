import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import logging
from sqlalchemy import create_engine

# Configuração do log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class LSTMPredictor:
    def __init__(self, db_url="postgresql://postgres:1234@localhost:5432/investimentos"):
        """
        Inicializa a conexão com o banco de dados e configura os parâmetros do modelo.
        """
        self.db_engine = create_engine(db_url)
        self.lookback = 60  # Número de dias usados como entrada para a previsão
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        logging.info("✅ Conexão com o banco de dados estabelecida.")

    def get_tickers_from_db(self):
        """
        Busca todos os tickers disponíveis no banco de dados.
        """
        query = "SELECT DISTINCT ticker FROM acoes_historico"
        df_tickers = pd.read_sql(query, self.db_engine)
        
        tickers = df_tickers['ticker'].tolist()
        logging.info(f"📊 Lista de tickers carregada do banco: {tickers}")

        return tickers

    def load_stock_data(self, ticker):
        """
        Carrega os dados do banco de dados e retorna um DataFrame.
        """
        query = f"SELECT date, close FROM acoes_historico WHERE ticker = '{ticker}' ORDER BY date ASC"
        df = pd.read_sql(query, self.db_engine)

        if df.empty:
            logging.warning(f"⚠️ Nenhum dado encontrado para {ticker} no banco de dados.")
            return None

        logging.info(f"📊 Dados carregados para {ticker}. Total de registros: {len(df)}")

        df.set_index("date", inplace=True)
        return df

    def prepare_data(self, df):
        """
        Prepara os dados para entrada no modelo LSTM.
        """
        df['close'] = df['close'].ffill()  # Usa a forma segura de preencher valores nulos
        df.dropna(inplace=True)

        if len(df) <= self.lookback:
            logging.warning(f"⚠️ Dados insuficientes para treinar o modelo. Registros encontrados: {len(df)}, mínimo necessário: {self.lookback + 1}")
            return None, None

        df_scaled = self.scaler.fit_transform(df[['close']])
        X, y = [], []

        for i in range(self.lookback, len(df_scaled)):
            X.append(df_scaled[i-self.lookback:i, 0])
            y.append(df_scaled[i, 0])

        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))  # Ajuste para entrada no LSTM

        return X, y

    def build_model(self, input_shape):
        """
        Cria e compila o modelo LSTM.
        """
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        logging.info("✅ Modelo LSTM criado e compilado com sucesso!")
        return model

    def train_model(self, ticker):
        """
        Treina o modelo LSTM com os dados históricos do ativo.
        """
        df = self.load_stock_data(ticker)
        if df is None:
            return None

        # Valida antecipadamente se há registros suficientes ANTES de processar
        if len(df) <= self.lookback:
            logging.warning(f"⚠️ {ticker} tem apenas {len(df)} registros. Mínimo necessário: {self.lookback + 1}. Pulando este ativo.")
            return None

        X, y = self.prepare_data(df)
        if X is None or y is None:
            return None

        if self.model is None:
            self.model = self.build_model((X.shape[1], X.shape[2]))

        history = self.model.fit(X, y, epochs=50, batch_size=32, verbose=1)

        logging.info(f"✅ Treinamento concluído para {ticker}")
        return self.model, history

    def predict_future(self, ticker, days=10):
        """
        Faz previsões futuras com base no modelo treinado.
        """
        df = self.load_stock_data(ticker)
        if df is None:
            return None

        X, _ = self.prepare_data(df)
        if X is None:
            return None

        predictions = self.model.predict(X[-days:])
        predictions = self.scaler.inverse_transform(predictions)

        return predictions

    def save_predictions_to_db(self, ticker, predictions):
        """
        Salva as previsões futuras no banco de dados.
        """
        if predictions is None:
            logging.warning(f"⚠️ Nenhuma previsão gerada para {ticker}.")
            return

        dates = pd.date_range(start=pd.Timestamp.today(), periods=len(predictions), freq='D')
        df_predictions = pd.DataFrame({"date": dates, "ticker": ticker, "predicted_price": predictions.flatten()})

        try:
            df_predictions.to_sql("acoes_previsoes", self.db_engine, if_exists="append", index=False)
            logging.info(f"✅ Previsões para {ticker} salvas no banco com sucesso!")
        except Exception as e:
            logging.error(f"❌ Erro ao salvar previsões no banco para {ticker}: {e}")

if __name__ == "__main__":
    predictor = LSTMPredictor()
    
    # Carregar todos os tickers do banco
    tickers = predictor.get_tickers_from_db()

    for ticker in tickers:
        logging.info(f"📢 Iniciando treinamento para {ticker}")

        # **Se não houver registros suficientes, já pula para o próximo!**
        if predictor.load_stock_data(ticker) is None or len(predictor.load_stock_data(ticker)) <= predictor.lookback:
            logging.warning(f"⏩ {ticker} não tem dados suficientes. Pulando...")
            continue

        predictor.train_model(ticker)

        logging.info(f"📈 Gerando previsões para {ticker}")
        future_prices = predictor.predict_future(ticker, days=10)

        predictor.save_predictions_to_db(ticker, future_prices)

    print("✅ Processo finalizado com sucesso!")
