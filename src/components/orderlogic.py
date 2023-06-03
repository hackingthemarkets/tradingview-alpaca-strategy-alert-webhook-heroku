from flask import Flask, render_template, request, abort
#import alpaca_trade_api as tradeapi
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, ClosePositionRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.common import exceptions
import app
import config, json, requests, math

# Declaring some variables
api = TradingClient(config.API_KEY, config.API_SECRET, paper=True)
accountInfo = api.get_account()
slippage = config.RISK_EXPOSURE + 1



def tradingValid():
    # Check if our account is restricted from trading.
    if accountInfo.trading_blocked:
        print('Error: Account is currently restricted from trading.')
        return 'Error: Account is currently restricted from trading.'
    elif (int(accountInfo.daytrade_count) > 3): # Check if were approaching PDT limit
        print('Error: Approaching Day Trade Limit')
        return 'Error: Approaching Day Trade Limit'
    else:
        return True

# ============================== Execution Logic =================================
def executeOrder(webhook_message):

    # Declaring Some Variables from the WebHook
    symbol_WH = webhook_message['ticker']
    side_WH = webhook_message['strategy']['order_action']
    price_WH = webhook_message['strategy']['order_price']
    qty_WH = webhook_message['strategy']['order_contracts']
    comment_WH = webhook_message['strategy']['comment']
    orderID_WH = webhook_message['strategy']['order_id']
    print(symbol_WH, side_WH, price_WH, qty_WH, side_WH, 'limit', 'gtc', comment_WH, orderID_WH)

    # Check if our account is restricted from trading.
    

    # Order Execution    
    if tradingValid():
        # Buy Side
        if side_WH=='buy':
            cashAvailable = int(round(float(accountInfo.non_marginable_buying_power)))
            quantity = round((cashAvailable * config.RISK_EXPOSURE) / price_WH) #Position Size Based on Risk Exposure
            orderData = LimitOrderRequest(symbol=symbol_WH, qty=quantity, side=side_WH, type='limit', time_in_force='gtc', limit_price=price_WH)
            order = api.submit_order(orderData)

        # Sell Side    
        elif (side_WH == 'sell'):
            
            try:
                # Check if Position Exists before Sell
                position = api.get_open_position(symbol_WH)
                if orderID_WH == 'TP':
                    close_options = ClosePositionRequest(percentage=config.TAKEPROFIT_POSITION)
                    order = api.close_position(symbol=symbol_WH,close_options=close_options)
                elif orderID_WH == 'Exit' or comment_WH == 'CL':
                    order = api.close_position(symbol=symbol_WH)
                else:
                    print('Error: No Existing Position')
                    return 'Error: No Existing Position'   
                raise Exception("Something went wrong")
            except exceptions.APIError as e:
                raise e
    else:
        return tradingValid()

