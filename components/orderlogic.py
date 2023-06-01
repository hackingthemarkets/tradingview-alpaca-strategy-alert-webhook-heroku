from flask import Flask, render_template, request
import alpaca_trade_api as tradeapi

import config, json, requests

# Declare some variables.
var bool canTrade = True

# Get our account information.
api = tradeapi.REST(config.API_KEY, config.API_SECRET, paper=True)
account = api.get_account()

# Check if our account is restricted from trading.
if account.trading_blocked:
    canTrade = False
    print('Account is currently restricted from trading.')
    else
        
# Check how much money we can use to open new positions.
print('${} is available as buying power.'.format(account.buying_power))
