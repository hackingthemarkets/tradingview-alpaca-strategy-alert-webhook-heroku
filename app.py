from flask import Flask, render_template, request
import alpaca_trade_api as tradeapi
import config, json, requests
from orderlogic import executeOrder


app = Flask(__name__)

api = tradeapi.REST(config.API_KEY, config.API_SECRET, base_url='https://paper-api.alpaca.markets')

# Vars

# Get the last 100 closed orders
orders = api.list_orders(
    status='closed',
    limit=100,
    nested=True  # show nested multi-leg orders
)
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

    executeOrder(symbol,side,quantity,price,tp)
    
    # if a DISCORD URL is set in the config file, we will post to the discord webhook
    if config.DISCORD_WEBHOOK_URL:
        chat_message = {
            "username": "strategyalert",
            "avatar_url": "https://i.imgur.com/4M34hi2.png",
            "content": f"tradingview strategy alert triggered: {quantity} {symbol} @ {price}"
        }

        requests.post(config.DISCORD_WEBHOOK_URL, json=chat_message)

    return webhook_message
