import json
import sys
import requests
from bs4 import BeautifulSoup
import csv
import datetime
from operator import itemgetter

min_div_yield = 0
max_div_yield = 10


def parseFloat(num):
    try:
        num = float(num)
    except:
        num = 0
    return num


def getPrice(symbol):
    r = requests.get(
        'https://www.settrade.com/C04_01_stock_quote_p1.jsp?txtSymbol=%s&ssoPageId=9&selectPage=1' % (symbol))
    soup = BeautifulSoup(r.text, 'html.parser')
    price = parseFloat(soup.select(
        "div.round-border div h1")[0].text.strip())

    rate_return = parseFloat(soup.select(
        "div.row.content-box-stt div")[15].text.strip())

    higtest_price_in52week, lowest_price_in52week = soup.select(
        "div.row.content-box-stt div div")[28].text.strip().split('/')

    higtest_price_in52week = parseFloat(higtest_price_in52week)
    lowest_price_in52week = parseFloat(lowest_price_in52week)

    div_yield = 0 if rate_return == 0 else (rate_return*100/price)
    diffL52 = (price - lowest_price_in52week) * 100 / price
    return {
        'symbol': symbol,
        'div_yield': div_yield,
        'price': price,
        'rate_return': rate_return,
        'higtest_price_in52week': higtest_price_in52week,
        'lowest_price_in52week': lowest_price_in52week,
        'diffL52': diffL52
    }
    # print(symbol, "%.2f%%" % div_yield, price, rate_return, sep='\t|')


def min_value(rank_norm, key):
    return min(map(itemgetter(key), rank_norm))


def max_value(rank_norm, key):
    return max(map(itemgetter(key), rank_norm))


def normalize_key(rank_norm, key):
    max_val = max_value(rank_norm, key)
    min_val = min_value(rank_norm, key)
    delta = max_val-min_val
    for d in rank_norm:
        d['n_'+key] = (d[key]-min_val)/delta
    print(rank_norm)
    return rank_norm


def normalize(lists, keys):
    for k in keys:
        lists = normalize_key(lists, k)
    return lists


def getSET100():
    r = requests.get(
        "https://marketdata.set.or.th/mkt/sectorquotation.do?sector=SET100&language=en&country=US")
    soup = BeautifulSoup(r.text, 'html.parser')
    set100_table = soup.select("table")[2]
    lists = set100_table.select('tr')
    lists.pop(0)
    symbols = []
    for l in lists:
        symbols.append(l.select('td')[0].text.strip())
    return symbols


def getSET50():
    r = requests.get(
        "https://marketdata.set.or.th/mkt/sectorquotation.do?sector=SET50&language=en&country=US")
    soup = BeautifulSoup(r.text, 'html.parser')
    set100_table = soup.select("table")[2]
    lists = set100_table.select('tr')
    lists.pop(0)
    symbols = []
    for l in lists:
        symbols.append(l.select('td')[0].text.strip())
    return symbols


def floatTo2Precise(lists):
    for l in lists:
        for k in l.keys():
            if isinstance(l[k], float):
                l[k] = "%.2f" % l[k]


def main():
    symbol_list = getSET100()
    # print(symbol_list)
    symbol_list = ["JAS", "CPALL", "PTT", "PTTEP"]
    print("SYMBOL", "DY", "PRICE", "D", "H52", "L52", sep='\t|')
    display_list = []
    for sym in symbol_list:
        stock = getPrice(sym)
        # print(stock['symbol'], stock['div_yield'],
        #       stock['price'], stock['rate_return'], stock['higtest_price_in52week'], stock['lowest_price_in52week'], sep='\t|')
        display_list.append(stock)

    normalize(display_list, ['div_yield', 'price'])

    display_list.sort(key=lambda i: i['div_yield'], reverse=True)

    display_csv = []
    display_csv.append(["SYMBOL", "DY", "PRICE", "D", "H52", "L52", "diffL52"])

    print("\n\n")
    print("SYMBOL", "DY", "PRICE", "D", "H52", "L52", sep='\t|')
    floatTo2Precise(display_list)
    for stock in display_list:
        row = []
        row.append(stock['symbol'])
        row.append(stock['div_yield'])
        row.append(stock['price'])
        row.append(stock['rate_return'])
        row.append(stock['higtest_price_in52week'])
        row.append(stock['lowest_price_in52week'])
        row.append(stock['diffL52'])
        display_csv.append(row)
        print(stock['symbol'], stock['div_yield'],
              stock['price'], stock['rate_return'], stock['higtest_price_in52week'], stock['lowest_price_in52week'], sep='\t|')

    with open('result%s.csv' % datetime.datetime.now().strftime('%Y-%m-%d %H-%M'), 'w') as file:
        writer = csv.writer(file)
        writer.writerows(display_csv)


main()
