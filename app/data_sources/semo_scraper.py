import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import PriceForecast
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_URL = "https://reports.sem-o.com/api/v1/dynamic"

ENDPOINTS = {
    "bm_025": "BM-025",  # Imbalance Price Report
    "bm_026": "BM-026",  # System Price
    "bm_084": "BM-084",  # Currency exchange rates
    "bm_095": "BM-095",  # Market Cost View
}


def fetch_report(endpoint: str, start_date: str, end_date: str, page_size: int = 5000):
    url = f"{BASE_URL}/{endpoint}"
    params = {
        "StartTime": f">={start_date}",
        "EndTime": f"<={end_date}",
        "sort_by": "StartTime",
        "order_by": "ASC",
        "Jurisdiction": "All",
        "page_size": page_size,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("items", [])


def parse_and_store_imbalance_price_report(db: Session, data: list):
    for item in data:
        try:
            timestamp = datetime.fromisoformat(item["StartTime"])
            price = float(item["ImbalancePriceAmountEUR"])
            forecast = PriceForecast(
                forecast_time=timestamp,
                predicted_price=price,
                actual_price=None,
                market_type="BM",
                region="ALL",
                source="SEMO-BM025",
            )
            db.add(forecast)
        except Exception as e:
            logger.warning(f"BM-025 parse error: {e} | item: {item}")


def parse_and_store_system_price(db: Session, data: list):
    for item in data:
        try:
            timestamp = datetime.fromisoformat(item["StartTime"])
            price = float(item["PriceAmountEUR"])
            forecast = PriceForecast(
                forecast_time=timestamp,
                predicted_price=price,
                actual_price=None,
                market_type="BM",
                region="ALL",
                source="SEMO-BM026",
            )
            db.add(forecast)
        except Exception as e:
            logger.warning(f"BM-026 parse error: {e} | item: {item}")


def parse_and_store_curr_exchange_rates(db: Session, data: list):
    for item in data:
        try:
            timestamp = datetime.fromisoformat(item["StartTime"])
            rate = float(item["ExchangeRate"])
            logger.info(f"BM-084 exchange rate {timestamp}: {rate} EUR/GBP")
        except Exception as e:
            logger.warning(f"BM-084 parse error: {e} | item: {item}")


def parse_and_store_market_cost_view(db: Session, data: list):
    for item in data:
        try:
            timestamp = datetime.fromisoformat(item["StartTime"])
            cost = float(item.get("TotalMarketCost", 0))
            logger.info(f"BM-095 market cost {timestamp}: {cost} EUR")
        except Exception as e:
            logger.warning(f"BM-095 parse error: {e} | item: {item}")


def run_semo_scraper():
    db_gen = get_db()
    db = next(db_gen)

    today = datetime.utcnow().date()
    start = today - timedelta(days=1)
    end = today

    logger.info("Fetching SEMO BM-025 imbalance price data...")
    bm_025_data = fetch_report(ENDPOINTS["bm_025"], start.isoformat(), end.isoformat())
    parse_and_store_imbalance_price_report(db, bm_025_data)

    logger.info("Fetching SEMO BM-026 system price data...")
    bm_026_data = fetch_report(ENDPOINTS["bm_026"], start.isoformat(), end.isoformat())
    parse_and_store_system_price(db, bm_026_data)

    logger.info("Fetching SEMO BM-084 exchange rate data...")
    bm_084_data = fetch_report(ENDPOINTS["bm_084"], start.isoformat(), end.isoformat())
    parse_and_store_curr_exchange_rates(db, bm_084_data)

    logger.info("Fetching SEMO BM-095 cost view data...")
    bm_095_data = fetch_report(ENDPOINTS["bm_095"], start.isoformat(), end.isoformat())
    parse_and_store_market_cost_view(db, bm_095_data)

    db.commit()
    logger.info("SEMO data successfully scraped and saved.")


if __name__ == "__main__":
    run_semo_scraper()
