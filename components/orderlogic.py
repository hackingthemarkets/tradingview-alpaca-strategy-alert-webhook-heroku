from flask import Flask, render_template, request
#import alpaca_trade_api as tradeapi
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
import math

import config, json, requests

# Declare some variables

canTrade = True
slippage = config.RISK_EXPOSURE + 1
api = TradingClient(config.API_KEY, config.API_SECRET, paper=True) #api stuff

# Get our account information
account = api.get_account()




# Webhook Variables
#price = webhook_message['strategy']['order_price']
#quantity = webhook_message['strategy']['order_contracts']
#symbol = webhook_message['ticker']
#side = webhook_message['strategy']['order_action']
#tp = webhook_message['strategy']['tp']


# ============================== Execution Logic =================================
def executeOrder(webhook_message):
    symbol = webhook_message['ticker']
    side = webhook_message['strategy']['order_action']
    price = webhook_message['strategy']['order_price']
    qty = webhook_message['strategy']['order_contracts']
    comment = webhook_message['strategy']['comment']
    orderID = webhook_message['strategy']['order_id']
    print(symbol, side, price, qty, side, 'limit', 'gtc', comment, orderID)

    # Check if our account is restricted from trading.
    if account.trading_blocked:
        canTrade = False
        print('Error: Account is currently restricted from trading.')
        return 'Error: Account is currently restricted from trading.'
    elif (int(account.daytrade_count)< 3): # Check if were approaching PDT limit
        canTrade = False
        print('Error: Approaching Day Trade Limit')
        return 'Error: Approaching Day Trade Limit'
    else:
        canTrade = True

    # Execution    

    if (side=='buy' and canTrade==True):
        cashAvailable = int(round(float(account.non_marginable_buying_power)))
        quantity = round((cashAvailable * config.RISK_EXPOSURE) / price) #Position Size Based on Risk Exposure
        orderData = LimitOrderRequest(symbol=webhook_message['ticker'], qty=quantity, side = webhook_message['strategy']['order_action'], type='limit', time_in_force='gtc', limit_price = webhook_message['strategy']['order_price'])
        order = api.submit_order(orderData)

    elif (side=='sell' and canTrade==True):

        position = api.get_open_position(symbol) # Check if Position Exists before Sell
        
        if (position.status_code == 200 and orderID=='TP'):
            qty = position.qty()*config.TAKEPROFIT_POSITION
            order = api.submit_order(symbol, quantity, side, price, 'market', 'gtc')

        elif (position.status_code == 200 and orderID=='Exit'):

            order = api.submit_order(symbol, quantity, side, price, 'market', 'gtc')

        else:
            print('Error: No Existing Position')
            return 'Error: No Existing Position' 
    else:
        print('Error: Order is invalid')
        return 'Error: Order is invalid'




# Check how much money we can use to open new positions.
print(
    '${} is available as buying power.'.format(account.buying_power),
)

