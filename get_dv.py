from utils.benefit import Benefit
from utils.stock import Stock
import asyncio


benefit = Benefit(debug=False)
stock = Stock(symbol='HTC')


# asyncio.run(stock.get_stock_quote())
# print(stock._stock_stats)
asyncio.run(stock.get_historical_quote(21))