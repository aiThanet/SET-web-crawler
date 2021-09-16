import requests
from bs4 import BeautifulSoup

def parseFloat(num):
    # in case of number is N/A
    try:
        num = float(num)
    except:
        num = 0
    return num

def month_to_number(month):
    months = {
        'ม.ค.' : 1,
        'ก.พ.' : 2,
        'มี.ค.' : 3,
        'เม.ย.' : 4,
        'พ.ค.' : 5,
        'ม.ิย.' : 6,
        'ก.ค.' : 7,
        'ส.ค.' : 8,
        'ก.ย.' : 9,
        'ต.ค.' : 10,
        'พ.ย.' : 11,
        'ธ.ค.' : 12
    }
    return months.get(month, -1)

def getSETList(SET_LIST='100'):
    # get set100,set50 list
    r = requests.get(
        "https://marketdata.set.or.th/mkt/sectorquotation.do?sector=SET%s&language=en&country=US" % SET_LIST)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.select("table")[2]
    lists = table.select('tr')
    lists.pop(0)
    symbols = []
    for l in lists:
        symbols.append(l.select('td')[0].text.strip())
    return symbols   


stock_info_tab_urls = {
    "Stock Quotes": "https://www.settrade.com/C04_01_stock_quote_p1.jsp?txtSymbol=###&ssoPageId=9&selectPage=1",
    "Historical Quotes": "https://www.settrade.com/C04_02_stock_historical_p1.jsp?txtSymbol=###&ssoPageId=10&selectPage=2",
    "Company Highlight": 3,
    "Board of Directors": 4,
    "Major Shareholders": 5,
    "Financial Stmt.": 6,
    "Right & Benefits": 7,
    "Sector Comparison": 8,
    "Company News": 9
}
