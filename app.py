import os
from flask import Flask, render_template_string
from trade_logic import get_portfolio_status, load_portfolio

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Mock Trading Platform Status</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; color: #333; }
        .container { max-width: 800px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
        h1 { color: #007bff; text-align: center; }
        .status-box { background: #e9ecef; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        .status-box p { margin: 5px 0; font-size: 1.1em; }
        .status-box strong { color: #000; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
        th { background-color: #007bff; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .warning { color: #dc3545; }
    </style>
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <div class="container">
        <h1>Mock Trading Platform Dashboard</h1>
        
        <div class="status-box">
            <h2>Overall Status</h2>
            <p><strong>Total Portfolio Value:</strong> {{ status.total_value }}</p>
            <p><strong>Cash Balance:</strong> {{ status.cash }}</p>
            <p><strong>Holdings Count:</strong> {{ status.holdings | length }}</p>
            <p><strong>Total Transactions:</strong> {{ status.transactions_count }}</p>
            <p class="warning">Data is refreshed every 30 seconds.</p>
        </div>

        <h2>Current Holdings</h2>
        {% if status.holdings %}
        <table>
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Quantity</th>
                    <th>Current Price</th>
                    <th>Market Value</th>
                </tr>
            </thead>
            <tbody>
                {% for holding in status.holdings %}
                <tr>
                    <td>{{ holding.ticker }}</td>
                    <td>{{ holding.quantity }}</td>
                    <td>{{ holding.current_price }}</td>
                    <td>{{ holding.market_value }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>No stock holdings yet.</p>
        {% endif %}
        
        <h2>Recent Transactions (Last 5)</h2>
        {% set transactions = raw_portfolio.transactions | reverse %}
        {% if transactions %}
        <table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Type</th>
                    <th>Ticker</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                {% for tx in transactions | slice(5) %}
                <tr>
                    <td>{{ tx.timestamp.split('T')[0] }} {{ tx.timestamp.split('T')[1].split('.')[0] }}</td>
                    <td style="color: {{ 'green' if tx.type == 'BUY' else 'red' }}; font-weight: bold;">{{ tx.type }}</td>
                    <td>{{ tx.ticker }}</td>
                    <td>{{ tx.quantity }}</td>
                    <td>${{ "%.2f"|format(tx.price) }}</td>
                    <td>${{ "%.2f"|format(tx.cost if tx.type == 'BUY' else tx.revenue) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>No transactions recorded yet.</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    status = get_portfolio_status()
    raw_portfolio = load_portfolio()
    return render_template_string(HTML_TEMPLATE, status=status, raw_portfolio=raw_portfolio)

if __name__ == '__main__':
    # Vercel/production environments often use an environmental variable for the port
    # For local running, we use 5000.
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))