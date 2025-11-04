import datetime as dt
from typing import Dict, Optional  # Added Optional import
import json
from utils import groq_query, safe_api_call
from config import get_api_keys

def get_weather_day(day: dt.date, location: str, api_key: Optional[str]) -> Dict:
    api_keys = get_api_keys()
    prompt = f"What is the real-time weather forecast for {location} on {day.strftime('%Y-%m-%d')}? Include temp, description, etc. Return as JSON dict."
    response = safe_api_call(groq_query, prompt, api_keys['GROQ_API_KEY'])
    if not response:
        return {'note': 'Groq query failed'}
    try:
        return json.loads(response)
    except Exception:
        return {'error': 'Parse failed', 'raw': response}