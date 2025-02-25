# InvestAi

Aplicação criada com o intuito de buscar, analisar e prever informações sobre a bolsa de valores, indicando boas ações para compra e venda.

## 📌 Funcionalidades

- **Coleta de Dados**: Utiliza Web Scraping na plataforma [Status Invest](https://statusinvest.com.br/) para capturar informações relevantes sobre ativos da B3.
- **Armazenamento**: Os dados coletados são salvos em um banco **PostgreSQL**.
- **Monitoramento Contínuo**: Um agendador executa a coleta a cada 4 horas automaticamente.
- **Modelo de Previsão**: Utiliza **Redes Neurais LSTM** para prever os preços futuros das ações com base nos dados coletados.
- **Visualização**: Os resultados são apresentados em gráficos para facilitar a análise.

## 📂 Estrutura do Projeto
```
src/
│── api/                   # Implementação de APIs futuras
│── collectors/            # Scripts de coleta de dados
│   │── data_collector.py  # Web Scraper para Status Invest
│   │── selenium_scraper.py # Alternativa usando Selenium
│── models/                # Modelos de Machine Learning
│   │── predictor_lstm.py  # Implementação do modelo LSTM
│── preprocessing/         # Pré-processamento de dados
│── scheduler/             # Agendador de tarefas
│   │── scheduler_collect.py # Executa a coleta automaticamente
│── requirements.txt       # Dependências do projeto
│── README.md              # Documentação do projeto
```

## ⚙️ Tecnologias Utilizadas
- **Python** (Linguagem principal)
- **BeautifulSoup** (Web Scraping)
- **Selenium** (Alternativa para scraping dinâmico)
- **PostgreSQL** (Banco de dados relacional)
- **MongoDB** (Armazenamento de logs)
- **TensorFlow/Keras** (Modelo LSTM para previsão)
- **Pandas & NumPy** (Manipulação de dados)
- **Matplotlib** (Visualização dos dados)

## 🚀 Como Rodar o Projeto

### 🔧 Instalação das Dependências

```bash
pip install -r requirements.txt
```

### 📊 Executar a Coleta de Dados

```bash
python src/collectors/data_collector.py
```

### ⏳ Agendar a Coleta Automática

```bash
python src/scheduler/scheduler_collect.py
```

### 📈 Treinar o Modelo de Previsão

```bash
python src/models/predictor_lstm.py
```

## 🌎 Deploy na Nuvem
Para manter a aplicação rodando continuamente, recomendamos o uso do **Railway** ou **Render**. Veja os passos detalhados na documentação.

## 📌 Próximos Passos
- 🔄 Melhorar a precisão do modelo de previsão adicionando novos indicadores financeiros.
- 📈 Criar um frontend para visualizar as previsões diretamente.
- ☁️ Publicar a aplicação na nuvem para rodar de forma automática.

---

**Criado por Rafael Baltar** 🚀

