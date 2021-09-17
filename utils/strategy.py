from datetime import datetime
from utils.benefit import Benefit
from utils.stock import Stock
from utils.tool import getSETList, normalize, floatTo2Precise
import asyncio
import uvloop
import csv


class Strategy:
    def __init__(self, start_date = '1-9-2021', end_date = '31-10-2021', top = 100, remark = 'XD'):
        self._start_date = datetime.strptime(start_date, "%d-%m-%Y")
        self._end_date = datetime.strptime(end_date, "%d-%m-%Y")
        self._top_set = getSETList(top)
        self._remark = remark
        self._stock_list = {}
        uvloop.install()
        benefit = Benefit(debug=False)
        self._benefit_list = benefit.get_all_benefit()

    def date_filter(self, date):
        now = datetime.strptime(date, "%d-%m-%Y")
        return now >= self._start_date and now <= self._end_date

    def get_info(self):
        coroutines = []
        fliter_benefit_date = filter(self.date_filter, self._benefit_list.keys())

        for benefit_date in fliter_benefit_date:
            for benefit in self._benefit_list[benefit_date]:
                if benefit[1] == self._remark:
                    print(benefit[0])
                    symbol = benefit[0]
                    stock = Stock(symbol=symbol, top_list = self._top_set)
                    coroutines.append(stock.f_get_all_info())
                    self._stock_list[symbol] = stock
        asyncio.run(self.run_task(coroutines))


    async def run_task(self,tasks):
        await asyncio.gather(*tasks)

    def calculate_score(self, stock_infos):
        for stock in stock_infos:
            stock['คะแนน'] = 0.5 * stock['n_%ปันผล'] + (0.1 * int(stock['SET100'])) + stock['เปรียบเทียบ ปันผล/ราคาย้อนหลัง']
        stock_infos.sort(key=lambda stock: stock['คะแนน'], reverse=True)
        stock['คะแนน'] = "{:.4f}".format(stock['คะแนน'])

    def generate_report(self, stock_infos):
        topics = ['symbol','ราคาล่าสุด','เฉลี่ยราคาย้อนหลัง30วัน','ราคาเฉลี่ยย้อนหลัง30วัน','ปันผล','%ปันผล','เปรียบเทียบ ปันผล/ราคาย้อนหลัง','คะแนน','ราคาสูงสุด/ต่ำสุดในรอบ 52 สัปดาห์','SET100','วันที่ขึ้นเครื่องหมายล่าสุด']
        output = [topics]
        floatTo2Precise(stock_infos)
        for stock in stock_infos:
            row = [stock[topic] for topic in topics]
            output.append(row)
        # print('\t\t|'.join([str(r) for r in row]))

        with open('result%s.csv' % datetime.now().strftime('%Y-%m-%d %H-%M'), 'w') as file:
            writer = csv.writer(file)
            writer.writerows(output)

    def generate(self):
        self.get_info()

        stock_infos = []

        for symbol in self._stock_list:
            stock_infos.append(self._stock_list[symbol].get_template())

        normalize_keys = ['ราคาล่าสุด', '%ปันผล','เปรียบเทียบ ปันผล/ราคาย้อนหลัง']
        normalize(stock_infos, normalize_keys)

        self.calculate_score(stock_infos)
        self.generate_report(stock_infos)

    
