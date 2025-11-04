import datetime as dt
import time
import logging
from typing import Optional, Any
import json
from groq import Groq

def today() -> dt.date:
    return dt.datetime.now().date()

def date_to_str(d: dt.date) -> str:
    return d.strftime('%Y-%m-%d')

def safe_api_call(func, *args, retries: int = 3, delay: float = 2.0, **kwargs) -> Optional[Any]:
    """
    Wrapper for API calls: retries on failure, delays for rate limits.
    """
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.warning(f'API call failed (attempt {attempt+1}): {e}')
            time.sleep(delay)
    logging.error(f'API call failed after {retries} attempts')
    return None

def groq_query(prompt: str, api_key: Optional[str], model: str = 'llama3-8b-8192') -> str:
    """
    Query Groq for response. Used for all data fetching now.
    """
    if not api_key:
        raise ValueError('No GROQ_API_KEY configured')
    client = Groq(api_key=api_key)
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": "You have access to real-time data. Provide accurate, up-to-date information in the requested format."},
                      {"role": "user", "content": prompt}],
            model=model,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f'Groq query failed: {e}')
        return ''