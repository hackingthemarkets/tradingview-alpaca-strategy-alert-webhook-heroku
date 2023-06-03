from flask import Flask, render_template, request, abort
#import alpaca_trade_api as tradeapi
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
import config, json, requests, subprocess
from components import orderlogic


# Start ngrok process
#ngrok_process = subprocess.Popen(['ngrok', 'http', '5000'])

# Print the ngrok URL
#print("Ngrok URL:", ngrok_process.stdout.readline().strip().decode())


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
    comment = webhook_message['strategy']['comment']
    orderID = webhook_message['strategy']['order_id']

    # if a DISCORD URL is set in the config file, we will post to the discord webhook
    if config.DISCORD_WEBHOOK_URL and config.DISCORD_WEBBHOOK_ENABLED==True:
        chat_message = {
            "username": "StrategyAlert",
            "avatar_url": "https://i.imgur.com/4M34hi2.png",
            "content": f"TradingView strategy alert triggered: {quantity} shares of {symbol} @ {price}"
        }

        requests.post(config.DISCORD_WEBHOOK_URL, json=chat_message)
    

    
    try:
        orderlogic.executeOrder(webhook_message)
        raise Exception("Something went wrong")
    except Exception as e:
        error_message = "An error occurred: {}".format(e)
        return error_message, 500  # Return error message with HTTP status code 500
    
    return webhook_message
 
