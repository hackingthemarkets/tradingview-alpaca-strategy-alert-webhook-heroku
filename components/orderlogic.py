from flask import Flask, render_template, request
#import alpaca_trade_api as tradeapi
import alpaca.trading.requests
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
import math

import config, json, requests

# Declare some variables.
canTrade = True
slippage = config.RISK_EXPOSURE + 1
api = TradingClient(config.API_KEY, config.API_SECRET, paper=True) #api stuff

# Get our account information.
account = api.get_account()




# Webhook Variables
#price = webhook_message['strategy']['order_price']
#quantity = webhook_message['strategy']['order_contracts']
#symbol = webhook_message['ticker']
#side = webhook_message['strategy']['order_action']
#tp = webhook_message['strategy']['tp']


# ============================== Execution Logic =================================
def executeOrder(symbol,side,quantity,price,tp):

    # Check if our account is restricted from trading.
    if account.trading_blocked:
        canTrade = False
        print('Error: Account is currently restricted from trading.')
        return 'Error: Account is currently restricted from trading.'
    else:
        canTrade = True

    if (side=='buy' and canTrade==True and account.daytrade_count<3):

        quantity = math.floor((account.non_marginable_buying_power * config.RISK_EXPOSURE) / price) #Position Size Based on Risk Exposure
        order = api.submit_order(symbol, quantity, side, 'limit', 'gtc', limit_price=price*slippage)

    elif (side=='sell' and canTrade==True):

        position = api.get_open_posistion(symbol) # Check if Position Exists before Sell

        if (position.status_code == 200 and tp=='yes'):

            quantity = position.qty()*config.TAKEPROFIT_POSITION
            order = api.submit_order(symbol, quantity, side, price, 'market', 'gtc')

        elif (position.status_code == 200 and tp=='no'):

            order = api.submit_order(symbol, quantity, side, price, 'market', 'gtc')

        else:
            print('Error: No Existing Position')
            return 'Error: No Existing Position' 
    else:
        print('Error: Order is invalid')
        return 'Error: Order is invalid'



# Check how much money we can use to open new positions.
print('${} is available as buying power.'.format(account.buying_power))
