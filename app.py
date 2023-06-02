from flask import Flask, render_template, request
#import alpaca_trade_api as tradeapi
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
import config, json, requests
from components import orderlogic


app = Flask(__name__)

api = TradingClient(config.API_KEY, config.API_SECRET, paper=True)

# Vars

# Get the last 100 orders
orderParams = GetOrdersRequest(
    status='all',
    limit=100,
    nested=True  # show nested multi-leg orders
)
orders = api.get_orders(filter=orderParams)
accountInfo = api.get_account()

@app.route('/')
def dashboard():
    return render_template('dashboard.html', alpaca_orders=orders)

@app.route('/account', methods=['GET'])
def account():
    return f'{accountInfo}'

@app.route('/webhook', methods=['POST'])
def webhook():
    webhook_message = json.loads(request.data)

    if webhook_message['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            'code': 'error',
            'message': 'nice try buddy'
        }
    
    symbol = webhook_message['ticker']
    side = webhook_message['strategy']['order_action']
    price = webhook_message['strategy']['order_price']
    quantity = webhook_message['strategy']['order_contracts']
    tp = webhook_message['strategy']['tp']

    orderlogic.executeOrder(symbol,side,quantity,price,tp)
    
    # if a DISCORD URL is set in the config file, we will post to the discord webhook
    if config.DISCORD_WEBHOOK_URL:
        chat_message = {
            "username": "strategyalert",
            "avatar_url": "https://i.imgur.com/4M34hi2.png",
            "content": f"tradingview strategy alert triggered: {quantity} {symbol} @ {price}"
        }

        requests.post(config.DISCORD_WEBHOOK_URL, json=chat_message)

    return webhook_message
