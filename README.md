Live KPI Dashboard (Streamlit)

Overview
- Starter project for a real-time KPI dashboard covering:
  - E-commerce sales (SQLite simulator)
  - Stock market trends (Alpha Vantage)
  - Crypto analytics (CoinGecko)
  - Social media engagement (Twitter placeholder)

Files
- streamlit_app.py: main Streamlit app
- fetchers.py: API fetch helpers
- data/db.py: SQLite init and sales simulator
- .env.example: example environment variables
- requirements.txt: Python deps

Quick start
1. Copy `.env.example` to `.env` and fill API keys.
2. Create virtualenv and install deps:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run streamlit_app.py
```
