from utils.browser import AsyncBrowser
from utils.tool import *
import asyncio

class Stock:

    def __init__(self, symbol, debug=False):
        self._symbol = symbol
        self._debug = debug
        self._browser = AsyncBrowser(debug=self._debug)

    def get_settrade_page_url(self, page):
        return stock_info_tab_urls[page].replace('###',self._symbol)

    async def get_stock_quote(self):
        url = self.get_settrade_page_url("Stock Quotes")

        response = await self._browser.get(**{'url': url})

        last_price = parseFloat(response.select("div.round-border div h1")[0].text.strip())

        stock_stats = {'ราคาล่าสุด': last_price}
        stats = response.select("div.row.content-box-stt div div.col-xs-12.col-md-6")
        for stat in stats:
         
            topic = stat.find(class_="text-left col-xs-8")
            value = stat.find(class_="text-right col-xs-4")
            stock_stats[topic.text] = value.text

        self._stock_stats = stock_stats

    async def get_historical_quote(self, n = 120):
        url = self.get_settrade_page_url("Historical Quotes") + f'&max={n}'
        

        response = await self._browser.get(**{'url': url})
        history_table = response.select('table.table-info.table-hover tbody tr')
       
        topics = ["วันที่","ราคาเปิด","ราคาสูงสุด","ราคาต่ำสุด","ราคาเฉลี่ย","ราคาปิด","เปลี่ยน","แปลง","%เปลี่ยน","แปลง","ปริมาณ","(พันหุ้น)","มูลค่า","(ล้านบาท)","SET","Index","%เปลี่ยน","แปลง"]
        price_history = [topics]
        for row in history_table:
            row_info = []
            infos = row.select("td")
            
            for i in range(len(infos)):
                row_info.append(infos[i].text)
            price_history.append(row_info)
            
        self._price_history = price_history
        
        



   
