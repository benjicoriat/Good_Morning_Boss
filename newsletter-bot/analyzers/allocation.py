import numpy as np
import yfinance as yf
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, List
from config import get_api_keys
from groq import Groq

def mean_variance_opt(expected_returns: np.ndarray, cov: np.ndarray, risk_free: float = 0.0) -> np.ndarray:
    n = len(expected_returns)
    def neg_sharpe(w):
        port_ret = w.dot(expected_returns)
        port_vol = np.sqrt(w.dot(cov).dot(w))
        return - (port_ret - risk_free) / (port_vol + 1e-8)
    cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
    bounds = tuple((0, 1) for _ in range(n))
    x0 = np.array([1.0 / n] * n)
    res = minimize(neg_sharpe, x0, method='SLSQP', bounds=bounds, constraints=cons)
    return res.x if res.success else x0

def heuristic_recommendation(report_df: pd.DataFrame) -> Dict[str, str]:
    recs = {}
    for t, row in report_df.iterrows():
        score = 0
        score += (row.get('sentiment_compound', 0)) * 2
        score += (row.get('1m_ret', 0)) * 1
        score += ((row.get('price', 0) / row.get('buy_price', 1) - 1) if row.get('buy_price') else 0) * 1.5
        pnl_pct = row.get('pnl_pct', 0)
        score -= min(0, pnl_pct) * 1
        if score > 1.0:
            recs[t] = 'BUY'
        elif score < -0.8:
            recs[t] = 'SELL'
        else:
            recs[t] = 'HOLD'
    return recs

def groq_recommendation(prompt: str) -> Optional[str]:
    api_key = get_api_keys().get('GROQ_API_KEY')
    if not api_key:
        return None
    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        import logging
        logging.error(f'Groq request failed: {e}')
        return None

def allocation_engine(tickers: List[str], report_df: pd.DataFrame, cash_available: float = 0.0) -> Dict:
    mus = []
    price_series = {}
    for t in tickers:
        try:
            hist = yf.download(t, period='1y', interval='1d', progress=False)  # Reverted to yfinance
            close = hist['Close'].dropna()
            mu = float(close.pct_change().dropna().tail(63).mean()) * 252 if len(close) >= 60 else 0.0
            price_series[t] = close
            mus.append(mu)
        except Exception:
            mus.append(0.0)
    mus = np.array(mus)
    closes = pd.concat([price_series.get(t, pd.Series()).pct_change().rename(t) for t in tickers], axis=1).dropna()
    cov = closes.cov().values * 252 if closes.shape[0] >= 10 else np.diag(np.maximum(1e-6, np.abs(mus)))
    try:
        w = mean_variance_opt(mus, cov)
    except Exception:
        w = np.array([1.0 / len(tickers)] * len(tickers))
    weights = dict(zip(tickers, w.tolist()))
    prompt = 'You are an investment assistant. Given the following tickers and short stats, provide a concise allocation recommendation (weights summing to 1) and rationale.\n'
    for i, t in enumerate(tickers):
        prompt += f"{t}: expected_annual_return={mus[i]:.3f}, weight_mvo={weights[t]:.3f}\n"
    groq_resp = groq_recommendation(prompt)
    return {'weights': weights, 'groq_explanation': groq_resp}