import yfinance as yf
import datetime

triggers = ["stock", "price", "market", "quote"]

def run(user_input: str) -> dict:
    tickers = ["AAPL", "TSLA", "GOOG", "MSFT", "AMZN", "NVDA"]
    query_ticker = "AAPL"
    for symbol in tickers:
        if symbol.lower() in user_input.lower():
            query_ticker = symbol
            break

    try:
        stock = yf.Ticker(query_ticker)
        info = stock.info

        return {
            "agent": "FinanceAgent",
            "timestamp": datetime.datetime.now().isoformat(),
            "ticker": query_ticker,
            "price": info.get("currentPrice", "N/A"),
            "previousClose": info.get("previousClose", "N/A"),
            "marketCap": info.get("marketCap", "N/A"),
            "currency": info.get("currency", "USD"),
            "summary": info.get("longBusinessSummary", "")[:300]
        }

    except Exception as e:
        return {
            "agent": "FinanceAgent",
            "error": str(e),
            "ticker": query_ticker,
            "timestamp": datetime.datetime.now().isoformat()
        }
