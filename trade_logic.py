import json
import os
from datetime import datetime
import yfinance as yf
import pandas as pd

PORTFOLIO_FILE = 'portfolio.json'
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

def get_portfolio_path():
    return os.path.join(REPO_ROOT, PORTFOLIO_FILE)

def load_portfolio():
    path = get_portfolio_path()
    if not os.path.exists(path):
        return {
            "cash": 10000.00,
            "holdings": {},
            "transactions": []
        }
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode {path}. Returning initial portfolio.")
            # Create and save a fresh portfolio to fix the file
            initial_portfolio = {"cash": 10000.00, "holdings": {}, "transactions": []}
            save_portfolio(initial_portfolio)
            return initial_portfolio

def save_portfolio(portfolio):
    if os.environ.get('VERCEL') == '1':
        # Vercel environment is read-only. Prevent write attempts.
        return 
        
    path = get_portfolio_path()
    with open(path, 'w') as f:
        json.dump(portfolio, f, indent=4)

def get_current_price(ticker):
    """Fetches the current price of a ticker using yfinance (with the requested fix: no show_errors)."""
    try:
        ticker_data = yf.Ticker(ticker)
        # Fetch 1 day of 1-minute data for the most recent closing price
        data = ticker_data.history(period="1d", interval="1m", progress=False)
        if not data.empty:
            return data['Close'].iloc[-1]
        
        # Fallback to info if 1m data is not available (e.g., pre-market/after-hours)
        info = ticker_data.info
        if 'currentPrice' in info and info['currentPrice'] is not None:
            return info['currentPrice']
        
        return None
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return None

def buy_stock(ticker, quantity):
    portfolio = load_portfolio()
    price = get_current_price(ticker)
    
    if price is None or price <= 0:
        return False, f"Could not fetch a valid price for {ticker}."
    
    cost = price * quantity
    
    if portfolio['cash'] < cost:
        return False, "Insufficient cash."
    
    # Execute trade
    portfolio['cash'] -= cost
    portfolio['holdings'][ticker] = portfolio['holdings'].get(ticker, 0) + quantity
    
    # Record transaction
    transaction = {
        'type': 'BUY',
        'ticker': ticker,
        'quantity': quantity,
        'price': price,
        'cost': cost,
        'timestamp': datetime.now().isoformat()
    }
    portfolio['transactions'].append(transaction)
    
    save_portfolio(portfolio)
    return True, f"Bought {quantity} shares of {ticker} at ${price:.2f} each. Total cost: ${cost:.2f}."

def sell_stock(ticker, quantity):
    portfolio = load_portfolio()
    
    if ticker not in portfolio['holdings'] or portfolio['holdings'][ticker] < quantity:
        return False, f"Insufficient shares of {ticker} to sell."
    
    price = get_current_price(ticker)
    
    if price is None or price <= 0:
        return False, f"Could not fetch a valid price for {ticker}."
    
    revenue = price * quantity
    
    # Execute trade
    portfolio['cash'] += revenue
    portfolio['holdings'][ticker] -= quantity
    if portfolio['holdings'][ticker] == 0:
        del portfolio['holdings'][ticker] # Clean up zero-holding tickers
        
    # Record transaction
    transaction = {
        'type': 'SELL',
        'ticker': ticker,
        'quantity': quantity,
        'price': price,
        'revenue': revenue,
        'timestamp': datetime.now().isoformat()
    }
    portfolio['transactions'].append(transaction)
    
    save_portfolio(portfolio)
    return True, f"Sold {quantity} shares of {ticker} at ${price:.2f} each. Total revenue: ${revenue:.2f}."

def get_portfolio_status():
    portfolio = load_portfolio()
    
    total_value = portfolio['cash']
    holdings_status = []
    
    # Pre-fetch prices to minimize API calls and avoid repeated logic
    tickers = list(portfolio['holdings'].keys())
    prices = {t: get_current_price(t) for t in tickers}
    
    for ticker, quantity in portfolio['holdings'].items():
        price = prices.get(ticker)
        
        if price is None or price <= 0:
            current_value = 0
            price_str = "N/A"
        else:
            current_value = price * quantity
            total_value += current_value
            price_str = f"${price:.2f}"
            
        holdings_status.append({
            'ticker': ticker,
            'quantity': quantity,
            'current_price': price_str,
            'market_value': f"${current_value:.2f}"
        })
        
    return {
        'cash': f"${portfolio['cash']:.2f}",
        'total_value': f"${total_value:.2f}",
        'holdings': holdings_status,
        'transactions_count': len(portfolio['transactions'])
    }

if __name__ == '__main__':
    # Initial test trade to populate the file for Vercel deployment if needed
    print("Running a sample trade to initialize portfolio...")
    # First, ensure portfolio is loaded and saved to create the initial file
    save_portfolio(load_portfolio()) 
    
    # Running the full trader cycle instead of just a static buy
    # We will run this logic inside the next exec call instead to ensure the portfolio.json is updated *before* git commit
    pass