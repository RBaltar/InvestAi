# InvestAi

## 📌 Sobre o Projeto
Aplicação criada com o intuito de buscar, analisar e prever informações sobre a bolsa de valores, indicando boas ações para compra e venda.

A aplicação realiza coleta de dados, treinamento de um modelo LSTM para previsões e disponibiliza uma API para consultas. Além disso, conta com um sistema de agendamento para manter os dados atualizados periodicamente.

## 🚀 Tecnologias Utilizadas
- **Linguagem:** Python
- **Framework Web:** FastAPI
- **Banco de Dados:** PostgreSQL e MongoDB
- **Machine Learning:** TensorFlow e Scikit-Learn
- **Coleta de Dados:** BeautifulSoup, Selenium, Requests
- **Agendamento:** Schedule, GitHub Actions
- **Hospedagem:** Render (Deploy automatizado)

## 📂 Estrutura do Projeto
```
.github/                   # Configuração do GitHub Actions
src/
├── api/                    # Implementação da API FastAPI
│   ├── main.py             # Inicialização da API
│   ├── routes/             # Rotas da API
│   │   ├── tickers.py      # Endpoint para listagem de tickers
│   │   ├── predictions.py  # Endpoint para previsões
|   |   ├── history.py      # Endpoint para histórico de ticker específico
|   |   ├── comparison.py   # Endpoint para comparar o valor do ticker previsto com o valor real
├── collectors/             # Scraper de dados financeiros
│   ├── data_collector.py   # Coleta de dados da StatusInvest
│   ├── selenium_scraper.py # Alternativa via Selenium
├── models/                 # Modelagem e treinamento do modelo LSTM
│   ├── predictor_lstm.py   # Implementação do modelo LSTM
├── preprocessing/          # Processamento dos dados antes do treinamento
├── scheduler/              # Agendamento de coleta de dados
│   ├── scheduler_collect.py # Agendador via Schedule
├── README.md               # Documentação do projeto
├── requirements.txt        # Dependências do projeto
```

## 🔥 Funcionalidades
✅ **Coleta de Dados:**
- Web Scraping da StatusInvest para obter dados financeiros.
- Armazena os dados em um banco PostgreSQL para histórico e MongoDB para logs.

✅ **Treinamento do Modelo:**
- Implementação de uma rede LSTM para prever valores futuros das ações.
- Treina um modelo para cada ativo disponível no banco de dados.

✅ **Previsão e Comparação:**
- Gera previsões para os próximos 10 dias.
- Compara previsões passadas com valores reais para avaliar a precisão.

✅ **API para Consultas:**
- **`/tickers`** → Retorna a lista de ativos disponíveis no banco.
- **`/predict/{ticker}`** → Retorna previsões futuras para um ativo específico.
- **`/compare?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&tickers=PETR4,VALE3`** → Compara previsões com valores reais.

✅ **Agendamento e Deploy Automático:**
- **GitHub Actions** roda a coleta periodicamente.
- **Render** mantém a API e o agendador rodando em produção.

## 🔧 Como Rodar o Projeto
### 1️⃣ Clonar o repositório
```bash
git clone https://github.com/seu-usuario/investai.git
cd investai
```

### 2️⃣ Criar e ativar um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3️⃣ Instalar as dependências
```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar variáveis de ambiente
Crie um arquivo `.env` com as credenciais do banco de dados:
```
DB_URL=postgresql://usuario:senha@localhost:5432/investimentos
MONGO_URL=mongodb://localhost:27017/
```

### 5️⃣ Rodar a API FastAPI
```bash
uvicorn api.main:app --reload
```

### 6️⃣ Testar a API
Acesse `http://127.0.0.1:8000/docs` para visualizar e testar os endpoints via Swagger.

### 7️⃣ Rodar o treinamento do modelo manualmente
```bash
python src/models/predictor_lstm.py
```

### 8️⃣ Rodar o agendador manualmente
```bash
python src/scheduler/scheduler_collect.py
```

## 📌 Próximos Passos
- Melhorar a interface gráfica com um painel de visualização interativo.
- Implementar caching para otimizar consultas na API.
- Adicionar métricas de erro nas previsões.
- Criar suporte para mais fontes de dados além da StatusInvest.

## 📜 Licença
Este projeto está sob a licença MIT. Sinta-se livre para contribuir e aprimorar! 🚀
