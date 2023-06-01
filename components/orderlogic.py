from flask import Flask, render_template, request
import alpaca_trade_api as tradeapi

import config, json, requests

api = tradeapi.REST(config.API_KEY, config.API_SECRET, paper=True)

# Get our account information.
account = api.get_account()

# Check if our account is restricted from trading.
if account.trading_blocked:
    print('Account is currently restricted from trading.')

# Check how much money we can use to open new positions.
print('${} is available as buying power.'.format(account.buying_power))
