import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import logging
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

# Configuração do log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class LSTMPredictor:
    def __init__(self, db_url="postgresql://postgres:1234@localhost:5432/investimentos"):
        """Inicializa a conexão com o banco de dados e configura os parâmetros do modelo."""
        self.db_engine = create_engine(db_url)
        self.lookback = 60  # Número de dias usados como entrada para a previsão
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        logging.info("✅ Conexão com o banco de dados estabelecida.")

    def get_tickers_from_db(self):
        """Busca todos os tickers disponíveis no banco de dados."""
        query = "SELECT DISTINCT ticker FROM acoes_historico"
        df_tickers = pd.read_sql(query, self.db_engine)
        tickers = df_tickers['ticker'].tolist()
        logging.info(f"📊 Lista de tickers carregada do banco: {tickers}")
        return tickers

    def load_stock_data(self, ticker):
        """Carrega os dados históricos do ativo a partir do banco de dados."""
        query = f"SELECT date, close FROM acoes_historico WHERE ticker = '{ticker}' ORDER BY date ASC"
        df = pd.read_sql(query, self.db_engine)

        if df.empty:
            logging.warning(f"⚠️ Nenhum dado encontrado para {ticker}.")
            return None

        logging.info(f"📊 Dados carregados para {ticker}. Registros: {len(df)}")
        df.set_index("date", inplace=True)
        return df

    def prepare_data(self, df):
        """Prepara os dados para entrada no modelo LSTM."""
        df['close'] = df['close'].ffill()
        df.dropna(inplace=True)

        if len(df) <= self.lookback:
            logging.warning(f"⚠️ Dados insuficientes ({len(df)}) para treinamento. Mínimo necessário: {self.lookback + 1}")
            return None, None

        df_scaled = self.scaler.fit_transform(df[['close']])
        X, y = [], []

        for i in range(self.lookback, len(df_scaled)):
            X.append(df_scaled[i-self.lookback:i, 0])
            y.append(df_scaled[i, 0])

        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))

        return X, y

    def build_model(self, input_shape):
        """Cria e compila o modelo LSTM."""
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
        """Treina o modelo LSTM para o ativo especificado."""
        df = self.load_stock_data(ticker)
        if df is None or len(df) <= self.lookback:
            logging.warning(f"⏩ {ticker} não tem dados suficientes. Pulando...")
            return None

        X, y = self.prepare_data(df)
        if X is None or y is None:
            return None

        if self.model is None:
            self.model = self.build_model((X.shape[1], X.shape[2]))

        self.model.fit(X, y, epochs=50, batch_size=32, verbose=1)
        logging.info(f"✅ Treinamento concluído para {ticker}")

    def predict_future(self, ticker, days=10):
        """Gera previsões futuras com base no modelo treinado."""
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
        """Salva previsões futuras no banco de dados."""
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

    def plot_predictions(self, predictions_dict):
        """Plota previsões de todas as ações de forma interativa."""
        plt.figure(figsize=(12, 6))
        
        for ticker, predictions in predictions_dict.items():
            dates = pd.date_range(start=pd.Timestamp.today(), periods=len(predictions), freq='D')
            plt.plot(dates, predictions, label=ticker)

        plt.title("Previsões para os próximos 10 dias")
        plt.xlabel("Data")
        plt.ylabel("Preço Previsto")
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.xticks(rotation=45)
        plt.grid()
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    predictor = LSTMPredictor()

    tickers = predictor.get_tickers_from_db()
    predictions_dict = {}

    for ticker in tickers:
        logging.info(f"📢 Iniciando treinamento para {ticker}")

        df_ticker = predictor.load_stock_data(ticker)
        if df_ticker is None or len(df_ticker) <= predictor.lookback:
            logging.warning(f"⏩ {ticker} não tem dados suficientes. Pulando...")
            continue

        predictor.train_model(ticker)
        logging.info(f"📈 Gerando previsões para {ticker}")
        future_prices = predictor.predict_future(ticker, days=10)

        if future_prices is not None:
            predictions_dict[ticker] = future_prices.flatten()
            predictor.save_predictions_to_db(ticker, future_prices)

    predictor.plot_predictions(predictions_dict)
    print("✅ Processo finalizado com sucesso!")
