import yfinance as yf
from typing import Dict

def get_company_events(ticker: str) -> Dict:
    try:
        t = yf.Ticker(ticker)
        out = {
            'earnings': t.calendar.to_dict() if hasattr(t, 'calendar') and t.calendar is not None else {},
            'dividends': t.dividends.tail(5).to_dict() if hasattr(t, 'dividends') and t.dividends is not None else {},
            'info_sector': t.info.get('sector') if hasattr(t, 'info') and t.info else None
        }
        return out
    except Exception:
        return {}