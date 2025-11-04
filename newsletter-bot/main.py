import logging
import os
from datetime import datetime
from config import load_config, get_api_keys
from utils import today, date_to_str
from fetchers.market import fetch_current_prices, get_macro_snapshot, get_stats_for_ticker
from fetchers.weather import get_weather_day
from fetchers.news import get_headlines
from analyzers.sentiment import sentiment_from_headlines, cluster_headlines
from analyzers.events import get_company_events
from analyzers.allocation import allocation_engine, heuristic_recommendation
from reporters.pdf import assemble_pdf_advanced
from sender.email import send_email_report  # Added back

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()])

def build_full_report(out_pdf: str = 'gmb_executive_report.pdf') -> dict:
    """
    Orchestrates the full report generation.
    Handles errors at high level.
    """
    config = load_config()
    api_keys = get_api_keys()
    tickers = config.get('tickers', [])
    portfolio = config.get('portfolio', {})
    weather_city = config.get('weather_city', 'Montreal,CA')
    dtoday = today()

    logging.info(f'Starting report for {date_to_str(dtoday)}')

    try:
        # Fetch weather
        weather = get_weather_day(dtoday, weather_city, api_keys.get('GROQ_API_KEY'))
        logging.info(f'Weather fetched: {weather}')
    except Exception as e:
        weather = {'error': str(e)}
        logging.error(f'Weather fetch failed: {e}')

    try:
        # Macro snapshot
        macro = get_macro_snapshot()
    except Exception as e:
        macro = {}
        logging.error(f'Macro fetch failed: {e}')

    try:
        # Prices
        prices = fetch_current_prices(tickers)
    except Exception as e:
        prices = {}
        logging.error(f'Prices fetch failed: {e}')

    # Per-ticker data
    rows = []
    news_bundle = {}
    for t in tickers:
        try:
            stats = get_stats_for_ticker(t, hist_days=config.get('hist_days', 365*5))
            headlines = get_headlines(t)
            titles = [h[0] for h in headlines]
            sent = sentiment_from_headlines(titles)
            clusters = cluster_headlines(titles, n_clusters=3) if titles else {}
            events = get_company_events(t)
            shares = portfolio.get(t, {}).get('shares', 0)
            buy = portfolio.get(t, {}).get('buy_price', 0)
            price = prices.get(t)
            mv = (price * shares) if price else 0
            cost = buy * shares
            pnl = mv - cost
            pnl_pct = (pnl / cost) if cost else None
            rows.append({
                'ticker': t,
                **stats,
                'sentiment_compound': sent.get('compound'),
                'headlines': titles,
                'clusters': clusters,
                'events': events,
                'shares': shares,
                'buy_price': buy,
                'price': price,
                'market_value': mv,
                'cost': cost,
                'pnl': pnl,
                'pnl_pct': pnl_pct
            })
            news_bundle[t] = {'headlines': headlines, 'sentiment': sent, 'clusters': clusters}
        except Exception as e:
            logging.error(f'Failed processing ticker {t}: {e}')
            continue  # Skip bad tickers

    import pandas as pd
    df = pd.DataFrame(rows).set_index('ticker') if rows else pd.DataFrame()

    # Allocation
    try:
        alloc = allocation_engine(tickers, df, cash_available=config.get('cash_available', 0.0))
        # Fallback heuristic if optimization fails
        if not alloc.get('weights'):
            alloc['heuristic'] = heuristic_recommendation(df)
    except Exception as e:
        alloc = {}
        logging.error(f'Allocation failed: {e}')

    # Build PDF
    try:
        assemble_pdf_advanced(out_pdf, tickers, portfolio, macro, df, news_bundle)
    except Exception as e:
        logging.error(f'PDF assembly failed: {e}')

    # Send email if configured
    if api_keys.get('SMTP_SERVER') and api_keys.get('SMTP_USER') and api_keys.get('SMTP_PASSWORD') and api_keys.get('EMAIL_TO'):
        try:
            send_email_report(out_pdf, date_to_str(dtoday), api_keys)
            logging.info('Email sent successfully')
        except Exception as e:
            logging.error(f'Email sending failed: {e}')

    return {'date': date_to_str(dtoday), 'macro': macro, 'prices': prices, 'df': df, 'alloc': alloc, 'news': news_bundle}

if __name__ == '__main__':
    report = build_full_report()
    logging.info('Allocation weights (MVO):')
    logging.info(report.get('alloc', {}).get('weights', {}))
    if report.get('alloc', {}).get('groq_explanation'):
        logging.info('Groq explanation:')
        logging.info(report['alloc']['groq_explanation'])
    logging.info('Report finished.')