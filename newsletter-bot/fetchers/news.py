from typing import List, Tuple
import json
from utils import groq_query, safe_api_call
from config import get_api_keys

def get_headlines(ticker: str, newsapi_key: Optional[str] = None) -> List[Tuple[str, str]]:
    """
    Use Groq for news headlines (replaced RSS and NewsAPI).
    """
    api_keys = get_api_keys()
    prompt = f"Provide up to 12 real-time news headlines for stock {ticker}, with titles and links. Return as JSON list of [title, link] pairs."
    response = safe_api_call(groq_query, prompt, api_keys['GROQ_API_KEY'])
    if not response:
        return []
    try:
        return json.loads(response)
    except Exception:
        return []