# Personalized Newsletter Bot: Good Morning Boss - Executive Edition

This app generates a daily personalized newsletter/report on your portfolio, including news, weather, market stats, and allocation recommendations. It outputs a PDF and optionally emails it.

## Setup
1. Clone repo: `git clone <repo-url>`
2. Install deps: `pip install -r requirements.txt`
3. Set API keys in `.env` (or config/user_profile.txt):
   - GROQ_API_KEY=your_key
   - OPENWEATHER_API_KEY=your_key
   - etc.
4. Edit config/user_profile.txt for tickers, holdings, city.
5. Run: `python main.py`

## Features
- Fetches real-time market data, news, weather.
- Analyzes sentiment, clusters topics.
- Optimizes portfolio allocation (MVO + LLM).
- Generates PDF report.
- Sends email (if configured).

## Potential Issues & Mitigations
- API Rate Limits: Delays added; fallbacks to cached/local.
- Missing Data: Graceful handling with defaults/logs.
- Security: Env vars for keys; no hardcodes.
- Scalability: Modular for web app integration.

## Future: Full App
- Backend: Add FastAPI for API endpoints.
- Frontend: React for user config/dashboard.
- Scheduling: Use cron/Celery for daily runs.

## Tests
Add unit tests in tests/ folder (e.g., pytest).