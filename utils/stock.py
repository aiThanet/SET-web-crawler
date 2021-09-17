from utils.browser import AsyncBrowser
from utils.tool import *
import asyncio
import csv

class Stock:

    def __init__(self, symbol, top_list = [], max_history = 30, debug=False):
        self._symbol = symbol
        self._top_list = top_list
        self._max_history = max_history
        self._debug = debug
        self._browser = AsyncBrowser(debug=self._debug)

    def get_all_info(self):
        task1 = self.get_stock_quote()
        task2 = self.get_historical_quote()
        task3 = self.get_right_benefits()
        coroutines = [task1, task2, task3]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*coroutines))

    async def f_get_all_info(self):
        
        task1 = self.get_stock_quote()
        task2 = self.get_historical_quote()
        task3 = self.get_right_benefits()
        coroutines = [task1, task2, task3]
        try :
            await asyncio.gather(*coroutines)
        except Exception as e:
            print(f"Error at sym: {self._symbol} message: {e}")

    def get_settrade_page_url(self, page):
        return stock_info_tab_urls[page].replace('###',self._symbol)

    def get_template(self):

        last_price = parseFloat(self._stock_stats['ราคาล่าสุด'])

        price_his = [parseFloat(price_history[4]) for price_history in self._price_history[1:]]
        avg_price_his = sum(price_his) / len(price_his)
        
        last_dividend = parseFloat(self._stock_stats['เงินปันผลต่อหุ้น (บาท)'])
        percentage_last_dividend = ((last_dividend * 100) / last_price) if last_price else 0.0
        
        
        return {
            'symbol': self._symbol,
            'ราคาล่าสุด': last_price,
            'เฉลี่ยราคาย้อนหลัง30วัน' : "{:.4f}".format(avg_price_his),
            'ราคาเฉลี่ยย้อนหลัง30วัน' : price_his,
        
            'ปันผล': "{:.4f}".format(last_dividend),
            '%ปันผล': percentage_last_dividend,
            'เปรียบเทียบ ปันผล/ราคาย้อนหลัง' : ((avg_price_his - last_price) / last_dividend) if last_dividend else 0.0,
            'ราคาสูงสุด/ต่ำสุดในรอบ 52 สัปดาห์': self._stock_stats['ราคาสูงสุด/ต่ำสุดในรอบ 52 สัปดาห์ *,**'],
           
            'SET100' : self._symbol in self._top_list,
            'วันที่ขึ้นเครื่องหมายล่าสุด' : self._benefit_history[1][0]
        }

    async def get_stock_quote(self):
        url = self.get_settrade_page_url("Stock Quotes")
        response = await self._browser.get(**{'url': url})

        last_price = response.select("div.round-border div h1")[0].text.strip()

        stock_stats = {'ราคาล่าสุด': last_price}
        stats = response.select("div.row.content-box-stt div div.col-xs-12.col-md-6")
        for stat in stats:
         
            topic = stat.find(class_="text-left col-xs-8")
            value = stat.find(class_="text-right col-xs-4")
            stock_stats[topic.text] = value.text

        self._stock_stats = stock_stats

    async def get_historical_quote(self):
        url = self.get_settrade_page_url("Historical Quotes") + f'&max={self._max_history}'
        response = await self._browser.get(**{'url': url})

        history_table = response.select('table.table-info.table-hover tbody tr')
       
        topics = ["วันที่","ราคาเปิด","ราคาสูงสุด","ราคาต่ำสุด","ราคาเฉลี่ย","ราคาปิด","เปลี่ยน","แปลง","%เปลี่ยน","แปลง","ปริมาณ","(พันหุ้น)","มูลค่า","(ล้านบาท)","SET","Index","%เปลี่ยน","แปลง"]
        price_history = [topics]
        for row in history_table:
            infos = row.select("td")
            row_info = [infos[i].text for i in range(len(infos))]
            price_history.append(row_info)
            
        self._price_history = price_history

    async def get_right_benefits(self):
        url = self.get_settrade_page_url("Right & Benefits")
        response = await self._browser.get(**{'url': url})
        
        dividend_table = response.select('table.table-info.table-hover tbody tr')

        topics = ["วันที่","ราคาเปิด","ราคาสูงสุด","ราคาต่ำสุด","ราคาเฉลี่ย","ราคาปิด","เปลี่ยน","แปลง","%เปลี่ยน","แปลง","ปริมาณ","(พันหุ้น)","มูลค่า","(ล้านบาท)","SET","Index","%เปลี่ยน","แปลง"]
        benefit_history = [topics]
        for row in dividend_table:
            infos = row.select("td")
            row_info = [infos[i].text for i in range(len(infos))]
            benefit_history.append(row_info)

        self._benefit_history = benefit_history

    def save_info(self, path="./"):
        with open(path + '/' + self._symbol + '-price-history', 'w') as f:
            writer = csv.writer(f)
            for row in self._price_history:
                 writer.writerow(row)
        with open(path + '/' + self._symbol + '-right-benefits', 'w') as f:
            writer = csv.writer(f)
            for row in self._benefit_history:
                 writer.writerow(row)
        

        
        



   
