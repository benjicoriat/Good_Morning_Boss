import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()  # Load .env file

def load_config(config_file: str = 'config/user_profile.txt') -> Dict:
    """
    Load user config from .txt file (key=value format).
    Fallback to defaults if file missing.
    Format example:
    tickers=SDIV,TMC,PFF
    portfolio_SDIV_shares=100
    portfolio_SDIV_buy_price=16.5
    weather_city=Montreal,CA
    hist_days=1825
    cash_available=10000.0
    """
    config = {
        'tickers': ['SDIV', 'TMC', 'PFF', 'SCM', 'NVO', 'KBWD', 'PNNT', 'PFLT', 'DX', 'TATT', 'RCAT', 'GRND'],
        'portfolio': {},
        'weather_city': 'Montreal,CA',
        'hist_days': 365 * 5,
        'cash_available': 0.0
    }
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    if key == 'tickers':
                        config['tickers'] = value.split(',')
                    elif key.startswith('portfolio_'):
                        _, ticker, field = key.split('_', 2)
                        config['portfolio'].setdefault(ticker, {})[field] = float(value)
                    elif key == 'hist_days' or key == 'cash_available':
                        config[key] = float(value)
                    else:
                        config[key] = value
    return config

def get_api_keys() -> Dict[str, Optional[str]]:
    """
    Load Groq key and SMTP settings from env vars. Fallback to None.
    """
    return {
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': os.getenv('SMTP_PORT'),
        'SMTP_USER': os.getenv('SMTP_USER'),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD'),
        'EMAIL_TO': os.getenv('EMAIL_TO')
    }