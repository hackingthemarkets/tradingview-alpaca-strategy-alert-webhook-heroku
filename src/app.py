from flask import Flask, render_template, request, abort, jsonify, render_template_string
#import alpaca_trade_api as tradeapi
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
import config, json, requests, subprocess
from components import orderlogic
from commons import start


app = Flask(__name__)

# Declaring some variables
api = TradingClient(config.API_KEY, config.API_SECRET, paper=True)
accountInfo = api.get_account()
orderParams = GetOrdersRequest(status='all',limit=100,nested=True)
orders = api.get_orders(filter=orderParams)

# Start Up Message.
start.startMessage(accountInfo.buying_power,accountInfo.daytrade_count)

@app.route('/')
def dashboard():
    return render_template('dashboard.html', alpaca_orders=orders)

@app.route('/account', methods=['GET'])
def account():
    payload = f'{accountInfo}'
    pretty_json = json.dumps(payload, indent=4)
    html = f"<pre>{pretty_json}</pre>"
    return render_template_string(html)

@app.route('/webhook', methods=['POST'])
def webhook():
    webhook_message = json.loads(request.data)

    if webhook_message['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            'code': 'error',
            'message': 'nice try buddy'
        }
    else:
        # Declare some variable
        symbol = webhook_message['ticker']
        side = webhook_message['strategy']['order_action']
        price = webhook_message['strategy']['order_price']
        quantity = webhook_message['strategy']['order_contracts']
        comment = webhook_message['strategy']['comment']
        orderID = webhook_message['strategy']['order_id']

        try:
            orderlogic.executeOrder(webhook_message) # Execute Order with the Webhook

            # if a DISCORD URL is set in the config file, we will post to the discord webhook
            if config.DISCORD_WEBHOOK_URL and config.DISCORD_WEBBHOOK_ENABLED==True:
                
                chat_message = {
                    "username": "StrategyAlert",
                    "avatar_url": "https://i.imgur.com/4M34hi2.png",
                    "content": f"TradingView strategy alert triggered: {quantity} shares of {symbol} @ {price}"
                }
                requests.post(config.DISCORD_WEBHOOK_URL, json=chat_message)
            
            # return webhook_message
            return jsonify(message='Order executed successfully'), 200, webhook_message

        except Exception as e:
            # Handle the exception and return an error response
            error_message = "{}".format(e)

            # if a DISCORD URL is set in the config file, we will post to the discord webhook
            if config.DISCORD_WEBHOOK_URL and config.DISCORD_WEBBHOOK_ENABLED==True:
                chat_message = {
                    "username": "StrategyAlert",
                    "avatar_url": "https://i.imgur.com/4M34hi2.png",
                    "content": f"TradingView strategy: {error_message}"
                }
                requests.post(config.DISCORD_WEBHOOK_URL, json=chat_message)
            return jsonify(error=error_message), 500


#if __name__ == '__app__':
#    app.run(debug=True)