import yfinance as yf
import pandas as pd
import math
from typing import List, Dict, Optional
import time
from utils import safe_api_call

MACRO_TICKERS = {'S&P 500': 'SPY', 'NASDAQ': 'QQQ', 'VIX': '^VIX', '10Y': '^TNX', 'DXY': 'DX-Y.NYB'}

def fetch_current_prices(tickers: List[str]) -> Dict[str, Optional[float]]:
    """
    Fetch latest prices with fallback and delay using yfinance.
    """
    def _fetch():
        data = yf.download(tickers, period='1d', interval='1m', progress=False, threads=True)
        if data.empty:
            raise ValueError('Empty data')
        out = {}
        close = data['Close']
        for t in tickers:
            try:
                out[t] = float(close[t].dropna().iloc[-1]) if not close[t].dropna().empty else None
            except KeyError:
                out[t] = None
        return out

    prices = safe_api_call(_fetch)
    if not prices:  # Fallback per ticker
        prices = {}
        for t in tickers:
            time.sleep(0.5)
            try:
                h = yf.Ticker(t).history(period='5d')
                prices[t] = float(h['Close'].dropna().iloc[-1]) if not h.empty else None
            except Exception:
                prices[t] = None
    return prices

def get_stats_for_ticker(ticker: str, hist_days: int = 365*5) -> Dict:
    df = safe_api_call(yf.download, ticker, period=f'{hist_days}d', interval='1d', progress=False)
    if df is None or df.empty:
        return {}
    close = df['Close'].dropna()
    if close.empty:
        return {}
    res = {
        'current_price': float(close.iloc[-1]),
        '52w_high': float(close.tail(252).max()),
        '52w_low': float(close.tail(252).min()),
    }
    horizons = {'1d':1, '1w':5, '1m':22, '3m':66, '6m':132, '1y':252, '5y':252*5}
    for k, v in horizons.items():
        if len(close) > v:
            res[k + '_ret'] = float(close.iloc[-1] / close.iloc[-v] - 1)
        else:
            res[k + '_ret'] = None
    daily = close.pct_change().dropna()
    res['vol_30d_ann'] = float(daily.tail(30).std() * math.sqrt(252)) if len(daily) >= 30 else None
    res['vol_90d_ann'] = float(daily.tail(90).std() * math.sqrt(252)) if len(daily) >= 90 else None
    return res

def get_macro_snapshot() -> Dict:
    out = {}
    for name, t in MACRO_TICKERS.items():
        info = safe_api_call(yf.Ticker(t).history, period='7d')
        out[name] = {'last': float(info['Close'].dropna().iloc[-1]) if info is not None and not info.empty else None}
    return out