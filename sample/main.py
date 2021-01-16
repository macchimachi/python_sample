# -*- coding: utf-8 -*-
import inspect

import pandas as pd
import yfinance as yf


data = yf.download("1301.T 7500.T 1312.T 1432.T", start="2017-01-01",
                    end="2017-04-30", group_by='tickers')
print(data)
df = data['1301.T']

ticker = yf.Ticker("1301.T")

code_i: int = int(ticker.ticker[0:-2])
hist = ticker.history(start="2020-11-26", end="2020-12-03")
print(hist)

financials = ticker.financials
print(financials)

balance_sheet = ticker.balance_sheet
print(balance_sheet)

cashflow = ticker.cashflow
print(cashflow)

splits = ticker.splits
print(splits)

info = ticker.info
aa = info.items()
df = pd.DataFrame(list(info.items()), columns=['info', 'value'])
df.to_csv("C:\\home\\python_sample\\main\\aaa.csv")
print(info)
