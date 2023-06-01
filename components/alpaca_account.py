from flask import Flask, render_template, request
import alpaca_trade_api as tradeapi
import config, json, requests

api = TradingClient(confing.API_KEY, config.SECRET_KEY, paper=True)
