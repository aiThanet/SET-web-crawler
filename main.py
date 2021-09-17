from utils.strategy import Strategy

for remark in ['XD','XW', 'XR']:
    strategy = Strategy(start_date = '19-9-2021', end_date = '10-9-2022', remark=remark')
    strategy.generate()











