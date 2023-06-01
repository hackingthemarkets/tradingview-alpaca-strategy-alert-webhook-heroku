from flask import Flask, render_template, request
import alpaca_trade_api as tradeapi
import config, json, requests

api = TradingClient(confing.API_KEY, config.SECRET_KEY, paper=True)

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest

trading_client = TradingClient('api-key', 'secret-key')

# Get our account information.
account = trading_client.get_account()

# Check if our account is restricted from trading.
if account.trading_blocked:
    print('Account is currently restricted from trading.')

# Check how much money we can use to open new positions.
print('${} is available as buying power.'.format(account.buying_power))

