import json
import sys
import requests
from bs4 import BeautifulSoup
import csv
import datetime
from operator import itemgetter


def parseFloat(num):
    # in case of number is N/A
    try:
        num = float(num)
    except:
        num = 0
    return num


def getPrice(symbol):
    # get price and stats
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

    div_yield = 0.0 if rate_return == 0 else (rate_return*100/price)
    diffL52 = (price - lowest_price_in52week) * 100 / price

    r = requests.get(
        'https://www.settrade.com/C04_06_stock_financial_p1.jsp?txtSymbol=%s&ssoPageId=13&selectPage=6' % (symbol), headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'})

    soup = BeautifulSoup(r.text, 'html5lib')
    tables = soup.select('table.table-hover.table-info tbody')

    account_table = tables[0].select('tr')
    stats_table = tables[1].select('tr')

    stat_price = [parseFloat(i.text.strip())
                  for i in stats_table[0].select('td')][1:6]
    stat_pe = [parseFloat(i.text.strip())
               for i in stats_table[3].select('td')][1:6]

    return {
        'symbol': symbol,
        'div_yield': div_yield,
        'price': price,
        'rate_return': rate_return,
        'higtest_price_in52week': higtest_price_in52week,
        'lowest_price_in52week': lowest_price_in52week,
        'diffL52': diffL52,
        'avg_pe': sum(stat_pe)/len(stat_pe),
        'last_pe': stat_pe[-1]
    }


def min_value(rank_norm, key):
    # for normalize
    return min(map(itemgetter(key), rank_norm))


def max_value(rank_norm, key):
    # for normalize
    return max(map(itemgetter(key), rank_norm))


def normalize_key(rank_norm, key):
    # normalize by a key
    max_val = max_value(rank_norm, key)
    min_val = min_value(rank_norm, key)
    delta = max_val-min_val
    for d in rank_norm:
        d['n_'+key] = (d[key]-min_val)/delta
    return rank_norm


def normalize(lists, keys):
    # normalize by keys
    for k in keys:
        lists = normalize_key(lists, k)
    return lists

def read_stock(file_name):
    STOCK_NAME = []
    with open(file_name) as fp:
        lines = fp.readlines()
        for line in lines:
            sym, _type = line.split("-")
            if _type.strip() == 'XD':
                STOCK_NAME.append(sym.strip())
    return STOCK_NAME


def getSETList(SET_LIST='100'):
    # get set100,set50 list
    r = requests.get(
        "https://marketdata.set.or.th/mkt/sectorquotation.do?sector=SET%s&language=en&country=US" % SET_LIST)
    soup = BeautifulSoup(r.text, 'html.parser')
    set100_table = soup.select("table")[2]
    lists = set100_table.select('tr')
    lists.pop(0)
    symbols = []
    for l in lists:
        symbols.append(l.select('td')[0].text.strip())
    return symbols


def floatTo2Precise(lists):
    # parse float to string with 2 precise
    for l in lists:
        for k in l.keys():
            if isinstance(l[k], float):
                l[k] = "%.2f" % l[k]


def main():

    symbol_list = read_stock("./STOCK_LIST")


    SET100 = getSETList(SET_LIST='100')
    # symbol_list = ["JAS", "CPALL", "PTT", "PTTEP"]
    # print("SYMBOL", "DY", "PRICE", "D", "H52", "L52", sep='\t|')
    display_list = []
    for sym in symbol_list:
        stock = getPrice(sym)
        display_list.append(stock)

    # key for normalize
    normalize_keys = ['div_yield', 'price', 'avg_pe', 'last_pe']
    normalize(display_list, normalize_keys)

    # calculate score from normalized key
    for i in display_list:
        i['score'] = 0.5*i['n_div_yield'] - 0.2 * \
            i['n_avg_pe'] - 0.3 * i['n_last_pe']
    # sort by score
    display_list.sort(
        key=lambda i: i['score'], reverse=True)

    display_csv = []
    display_key = ["sym", "dy", "price", "punpon",
                   "h52", "l52", "diff", 'avg_pe', 'l_pe', 'score','is_SET100']
    display_csv.append(display_key)

    print("\n\n")
    print('\t\t|'.join(display_key))

    # write to csv
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
        row.append(stock['avg_pe'])
        row.append(stock['last_pe'])
        row.append(stock['score'])
        row.append(stock['symbol'] in SET100)
        display_csv.append(row)
        print('\t\t|'.join([str(r) for r in row]))

    with open('result%s.csv' % datetime.datetime.now().strftime('%Y-%m-%d %H-%M'), 'w') as file:
        writer = csv.writer(file)
        writer.writerows(display_csv)


main()
