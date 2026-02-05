import time
import random
import json
from trade_logic import load_portfolio, get_portfolio_status, buy_stock, sell_stock, get_current_price

# A list of stocks for the bot to trade
TICKERS = ['GOOG', 'AMZN', 'TSLA', 'NVDA', 'AAPL', 'MSFT'] 

def automated_trading_cycle():
    portfolio = load_portfolio()
    status = get_portfolio_status()
    print(f"--- Trading Cycle Started ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---")
    
    # Clean and convert cash
    cash = float(status['cash'].replace('$', '').replace(',', ''))
    
    # 1. Buy Strategy (If we have substantial cash, buy a random stock)
    if cash > 2000: 
        ticker = random.choice(TICKERS)
        price = get_current_price(ticker)
        
        if price and price > 0:
            # Spend max 10% of cash, but at least 1 share, max 5 shares
            max_affordable = int((cash * 0.1) / price) 
            quantity_to_buy = max(1, min(random.randint(1, 5), max_affordable))
            
            success, message = buy_stock(ticker, quantity_to_buy)
            print(f"BUY: {ticker} - {message}")
        else:
            print(f"SKIP: Could not get valid price for {ticker}.")


    # 2. Sell Strategy (30% chance to sell a random holding)
    holdings = portfolio.get('holdings', {})
    tradable_holdings = [k for k, v in holdings.items() if v >= 1]
    
    if tradable_holdings and random.random() < 0.3:
        ticker = random.choice(tradable_holdings)
        held_quantity = holdings[ticker]
        quantity_to_sell = random.randint(1, min(held_quantity, 3)) # Sell 1-3 shares
        
        success, message = sell_stock(ticker, quantity_to_sell)
        print(f"SELL: {ticker} - {message}")

    print(f"--- Cycle Finished. Current Total Value: {get_portfolio_status()['total_value']} ---")

if __name__ == '__main__':
    # Run a few cycles to make the initial portfolio more interesting
    print("Running initial trading cycles...")
    for _ in range(3):
        automated_trading_cycle()
        time.sleep(1) # Wait briefly to avoid hitting rate limits too fast
    
    print("\nInitial setup complete. Portfolio status:")
    # print(json.dumps(get_portfolio_status(), indent=2)) # Avoid complex output here, just for logic setup
    pass