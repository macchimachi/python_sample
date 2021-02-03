# -*- coding: utf-8 -*-
import datetime as dt

import yfinance as yf
from dateutil.relativedelta import relativedelta as rel

if dt.datetime.now().hour.__int__() >= 15:
    end_day = dt.date.today()
else:
    end_day = dt.date.today() - rel(days=1)

do_download_history = False
# history = download.download_current_history(end_day, do_download_history)

data = yf.Tickers("TOPIX 1301.T")
his = data.tickers[0].history(start="2019-01-01", end=end_day)
sum = 1
