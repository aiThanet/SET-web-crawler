from utils.browser import AsyncBrowser
from utils.tool import *
import asyncio

class Benefit:

    def __init__(self, debug=False, remarks=['XD','XR','XW'], max_index = 6):
        self._debug = debug
        self._remarks = remarks
        self._max_index = max_index
        self._browser = AsyncBrowser(debug=self._debug)

    async def get_benefit(self, all_result, index=1):
        payload = { 'url': f'https://www.set.or.th/set/xcalendar.do?eventType=&index={index}&language=th&country=TH' }
        response = await self._browser.get(**payload)

        month_info = response.select("div ul li.active")[0].text.strip()
        month, year = self.get_month_year(month_info)

        table = response.table.tbody.select("td")

        result = {}
        for row in table:
            date = row.find(align="right")
            if date:
                date = date.text.strip()
                benefit_list = []
                benefits = row.find_all(align="center")
                for benefit in benefits:
                    info = benefit.text.split('-')
                    stock_name = info[0].strip()
                    remark = info[1].strip()
                    if remark in self._remarks:
                        benefit_list.append([stock_name, remark])
                result[date] = benefit_list
        
        all_result[f'{month}-{year}'] = result

    def get_month_year(self, month_info):
        month, year = month_info.split()
        return month_to_number(month), int(year)-543

    def print_debug(self, text):
        if(self._debug):
            print(text)

    async def get_all_benefit(self):
        result = {}
        loop = asyncio.get_event_loop()
        coroutines = [self.get_benefit(result, i) for i in range(self._max_index)]
        await asyncio.gather(*coroutines)

        return result



# async def get_benefit():
#         global re
#         b = AsyncBrowser(debug=False)
#         payload = { 'url': f'https://www.set.or.th/set/xcalendar.do?eventType=&index=1&language=th&country=TH' }
#         response = await b.get(**payload)
#         re = response
#         return response
# asyncio.run(get_benefit())


