import websocket, json, talib, numpy
from binance.client import Client
from binance.enums import *
import math
import os
import datetime

SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"
RSI_PERIOD = 200
Trade1 = 'BTC'
Trade2 = 'TUSD'
TRADE_SYMBOL = Trade1 + Trade2
INTERWAL = 1
last = 0
closes = []
client = Client()

file = 'last.txt'
 
for root, dirs, files in os.walk(r'C:\Users\user\Desktop\ProjektyPython\Rsi'):
    for name in files:
       
        # As we need to get the provided python file,
        # comparing here like this
        if name == file: 
            path = os.path.abspath(os.path.join(root, name))

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        # print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))


def on_open(ws):
    global last
    print('opened connection')
    f = open(path, "r")
    last = float(f.read())
    print(last)
    frame = client.get_historical_klines(TRADE_SYMBOL, str(INTERWAL)+"m",  str(RSI_PERIOD*INTERWAL) + " minutes ago UTC")
    for i in range(len(frame)):
        closes.append(float(frame[i][4]))
def on_close(ws):
    print('closed connection')


def on_message(ws, message):
    global closes
    global last
    
    json_message = json.loads(message)
    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        #print("candle closed at {}".format(close))
        del closes[0]
        closes.append(float(close))

        np_closes = numpy.array(closes)
        ema_12 = talib.EMA(np_closes, 12)
        ema_26 = talib.EMA(np_closes, 26)
        ema_200 = talib.EMA(np_closes, 200)
        macd = ema_12 - ema_26
        signal = talib.EMA(macd, 9)
        #rsi = talib.RSI(np_closes[-21:], 20)

        ema_200 = ema_200[-1]
        macd = macd[-1]
        signal = signal[-1]
        #print(np_closes[-1] < ema_200, macd < 0, signal < 0, signal < macd, np_closes[-1] < last)
        if np_closes[-1] < ema_200 and macd < 0 and signal < 0 and signal < macd:
            balance2 = client.get_asset_balance(asset=Trade2)
            float_balance2 = float(balance2['free'])/float(close)
            TRADE_QUANTITY = float(math.floor(float_balance2*1000)/1000)
            #print(last)
            if TRADE_QUANTITY > 0.0:
                print(datetime.datetime.now())
                print("Buy! Buy! Buy! ", " TQ= ", TRADE_QUANTITY, "Price: ", np_closes[-1])
                order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                f = open(path, "w")
                last = np_closes[-1]
                f.write(str(np_closes[-1]))
                print()

        if np_closes[-1] > ema_200 and macd > 0 and signal > 0 and signal > macd:
            balance1 = client.get_asset_balance(asset=Trade1)
            float_balance1 = float(balance1['free'])
            TRADE_QUANTITY = float(math.floor(float_balance1*1000)/1000)
            #print(last)
            if TRADE_QUANTITY > 0.0 and np_closes[-1] > last:
                print(datetime.datetime.now())
                print("Sell! Sell! Sell! ", " TQ= ", TRADE_QUANTITY, "Price: ", np_closes[-1])
                order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                f = open(path, "w")
                last = np_closes[-1]
                f.write(str(np_closes[-1]))
                print()


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
