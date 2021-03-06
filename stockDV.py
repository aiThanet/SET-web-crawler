import json
import sys
import requests
import csv
import datetime

from bs4 import BeautifulSoup
from operator import itemgetter
from tqdm import tqdm

SET100 = ['ACE', 'ADVANC', 'AEONTS', 'AMATA', 'AOT', 'AP', 'AWC', 'BAM', 'BANPU', 'BBL', 'BCH', 'BCP', 'BCPG', 'BDMS', 'BEC', 'BEM', 'BGRIM', 'BH', 'BJC', 'BPP', 'BTS', 'CBG', 'CENTEL', 'CHG', 'CK', 'CKP', 'COM7', 'CPALL', 'CPF', 'CPN', 'CRC', 'DELTA', 'DOHOME', 'DTAC', 'EA', 'EGCO', 'EPG', 'ESSO', 'GFPT', 'GLOBAL', 'GPSC', 'GULF', 'GUNKUL', 'HANA', 'HMPRO', 'INTUCH', 'IRPC', 'IVL', 'JAS', 'JMART', 'JMT', 'KBANK', 'KCE', 'KKP', 'KTB', 'KTC', 'LH', 'MAJOR', 'MBK', 'MEGA', 'MINT', 'MTC', 'OR', 'ORI', 'OSP', 'PLANB', 'PRM', 'PTG', 'PTT', 'PTTEP', 'PTTGC', 'QH', 'RATCH', 'RBF', 'RS', 'SAWAD', 'SCB', 'SCC', 'SCGP', 'SPALI', 'SPRC', 'STA', 'STEC', 'SUPER', 'TASCO', 'TCAP', 'THANI', 'TISCO', 'TMB', 'TOA', 'TOP', 'TPIPP', 'TQM', 'TRUE', 'TTW', 'TU', 'TVO', 'VGI', 'WHA', 'WHAUP']

keyToDisplayName = {
    'symbol':'Sym', 
    'price':'Price', 
    'price_his':'PriceHis', 
    'div_yield':'DY', 
    'rate_return':'DY%', 
    'compare_his':'diffPrice/DY%', 
    'higtest_price_in52week':'H52', 
    'lowest_price_in52week':'L52', 
    'avg_pe':'AvgPE', 
    'last_pe':'PE', 
    'score':'Score',
    'isSET100':'isSET100',
    'XD_date' : 'XD_date'
}

def parseFloat(num):
    # in case of number is N/A
    try:
        num = float(num)
    except:
        num = 0
    return num


def getPrice(symbol,history_length = 10):
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

    div_yield = 0.0 if price == 0 else (rate_return*100/price)

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

    r = requests.get(
        'https://www.settrade.com/C04_02_stock_historical_p1.jsp?txtSymbol=%s&ssoPageId=9&selectPage=2' % (symbol), headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'})
    soup = BeautifulSoup(r.text, 'html5lib')
    tables = soup.select('table.table-info.table-hover tbody')
    price_table = tables[0].select('tr')
    price_his = []
    for row in price_table:
        price_his.append(parseFloat(row.select('td')[3].text.strip()))

    avg_price_his = sum(price_his[:history_length]) / history_length

    

    r = requests.get(
        'https://www.settrade.com/C04_07_stock_rightsandbenefit_p1.jsp?txtSymbol=%s&ssoPageId=15&selectPage=7' % (symbol), headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'})
    soup = BeautifulSoup(r.text, 'html5lib')
    divide_tables = soup.select('table.table-info.table-hover tbody')
    first_row = divide_tables[0].select('tr')[0]
    
    XD_date = str(first_row.select('td')[0].text)

    return {
        'symbol': symbol,
        'price_his' : price_his[:history_length],
        'price': price,
        'div_yield': div_yield,
        'rate_return': rate_return,
        'compare_his' : ((avg_price_his - price) / rate_return) if rate_return else 0,
        'higtest_price_in52week': higtest_price_in52week,
        'lowest_price_in52week': lowest_price_in52week,
        'avg_pe': sum(stat_pe)/len(stat_pe),
        'last_pe': stat_pe[-1],
        'avg_price_his' : avg_price_his,
        'isSET100' : symbol in SET100,
        'XD_date' : "'"+XD_date
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
            sym, _type = line.split(" - ")
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
    # SET100 = getSETList(SET_LIST='100')
    
    display_list = []
    for sym in tqdm(symbol_list):
        stock = getPrice(sym)
        if stock['price'] != 0:
            display_list.append(stock)

    # key for normalize
    normalize_keys = ['div_yield', 'price', 'avg_pe', 'last_pe','compare_his']
    normalize(display_list, normalize_keys)

    # calculate score from normalized key
    for i in display_list:
        i['score'] = 0.5 * i['n_div_yield'] + 0.1 * int(i['isSET100']) + 2 * i['n_compare_his']
    # sort by score
    display_list.sort(
        key=lambda i: i['score'], reverse=True)

    display_csv = []
    
    display_key = [keyToDisplayName[k] for k in keyToDisplayName]
    display_csv.append(display_key)

    # print("\n\n")
    # print('\t\t|'.join(display_key))

    # write to csv
    floatTo2Precise(display_list)
    for stock in display_list:
        row = []
        for key in keyToDisplayName:
            row.append(stock[key])
        display_csv.append(row)
        # print('\t\t|'.join([str(r) for r in row]))

    with open('result%s.csv' % datetime.datetime.now().strftime('%Y-%m-%d %H-%M'), 'w') as file:
        writer = csv.writer(file)
        writer.writerows(display_csv)


main()
