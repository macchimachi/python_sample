# -*- coding: utf-8 -*-

import yfinance as yf
import numpy as np
import pandas as pd

ticker = yf.Ticker("7203.T")
hist = ticker.history(start="2020-11-25", end="2020-11-27")
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
