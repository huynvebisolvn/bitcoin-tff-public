from flask import Flask, request, render_template
from datetime import datetime
import ccxt
import time
import json
import requests

def buy(SYMBOL):
    try:
        usdt_available = float(exchange.fetch_balance()['USDT']['free'])
        price = float(exchange.fetchTicker(SYMBOL)['last'])
        qty = float(exchange.amount_to_precision(SYMBOL, usdt_available/price*0.99))
        exchange.create_order(SYMBOL, 'market', 'buy', qty)
        time.sleep(3)
        buy(SYMBOL)
    except:
        pass

def sell(SYMBOL):
    try:
        btc_available = float(exchange.fetch_balance()['BTC']['free'])
        qty = float(exchange.amount_to_precision(SYMBOL, btc_available))
        exchange.create_order(SYMBOL, 'market', 'sell', qty)
        time.sleep(3)
        sell(SYMBOL)
    except:
        pass

def fetch_orders(SYMBOL):
    last_trade = exchange.fetchOrders(symbol=SYMBOL, limit=10)
    last_trade.reverse()
    return last_trade

def checkbuy(SYMBOL):
    last_trade = exchange.fetchOrders(symbol=SYMBOL, limit=1)[0]
    if last_trade['side'].lower() == 'sell':
        return True
    time = last_trade['info']['time']
    server_time = exchange.fetchTime()
    diff = datetime.utcfromtimestamp(int(str(server_time)[:10])) - datetime.utcfromtimestamp(int(str(time)[:10]))
    return diff.seconds >= 1800

app = Flask(__name__)

#DEV
API_KEY = "glltLvPt5T9zJkbUG6OBHm0cZeA4IWVKFuOHGny0HB5TaKwuM8JwI1T0xQHOdlrd"
API_SECRET = "KGIWPCFm7pk2BE9Xc0HaHW6itFSLXTRr5CcvsT7Mtj6Xtyj3rY17qa1l480sRWrD"
exchange = ccxt.binance({ 'apiKey': API_KEY, 'secret': API_SECRET, 'enableRateLimit': True, 'options': {'defaultType': 'spot', 'adjustForTimeDifference': True } })
exchange.set_sandbox_mode(True)

@app.template_filter()
def format_dateTime(value):
    try:
        return datetime.utcfromtimestamp(int(str(value)[:10])+25200)
    except:
        return value

@app.route('/wake', methods=['POST'])
def wake():
    return {
        'code': '200',
        'message': 'wake up success'
    }

@app.route('/')
def welcome():
    orders = fetch_orders('BTC/USDT')
    usdt = float(exchange.fetch_balance()['USDT']['free'])
    btc = float(exchange.fetch_balance()['BTC']['free'])
    ip = '#404' #requests.get('http://ipinfo.io/json').json()['ip']
    return render_template('index.html', orders=orders, usdt=usdt, btc=btc, ip=ip)

@app.route("/long/", methods=['POST'])
def longbtc():
    if (checkbuy('BTC/USDT')):
        buy('BTC/USDT')
    return {
        'code': '200',
        'message': 'btc order success'
    }

@app.route("/longclose/", methods=['POST'])
def longclosebtn():
    sell('BTC/USDT')
    return {
        'code': '200',
        'message': 'btc order success'
    }

@app.route('/btc', methods=['POST'])
def btc():
    bot = json.loads(request.data)
    if bot['ORDER'] == 'long':
        if (checkbuy('BTC/USDT')):
            buy('BTC/USDT')
    if bot['ORDER'] == 'long_close':
        sell('BTC/USDT')
    return {
        'code': '200',
        'message': 'btc order success'
    }

#if __name__ == "__main__":
#    app.run(host='127.0.0.1', port=5000, debug=True)

