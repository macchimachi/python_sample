# -*- coding: utf-8 -*-
import datetime as dt

import investpy
import matplotlib.pyplot as plt
import numpy as np
# import japanize_matplotlib
import japanize_matplotlib
import pandas as pd
from dateutil.relativedelta import relativedelta as rel

import download

if dt.datetime.now().hour.__int__() >= 15:
    end_day = dt.date.today()
else:
    end_day = dt.date.today() - rel(days=1)

do_download_history = False
history = download.download_current_history(end_day, do_download_history)

last_weekday: dt.date = end_day
before_a_year: dt.date = last_weekday - rel(years=1)

indices_JP = investpy.get_indices(country='japan').sort_values('symbol')
# indices_JP = indices_JP.sort_values('symbol')

history_topix = investpy.get_index_historical_data(index='TOPIX', country='japan',
                                                   from_date=history.index[0].strftime('%d/%m/%Y'),
                                                   to_date=history.index[-1].strftime('%d/%m/%Y'),
                                                   as_json=False, order='ascending')
history_topix = history_topix.iloc[:, :-1]
history_topix.insert(0, 'Adj Close', history_topix['Close'])
history_topix = history_topix.reindex(sorted(history_topix.columns), axis=1)
# history_topix.columns = np.stack([history_topix.columns, ['TOPIX'] * len(history_topix.columns)], 1)

# 出来高10万株以上
volume = history.loc[:, 'Volume']
volume_mean = volume.mean()
target = volume_mean[volume_mean > 100000].index.values
# 結果反映
Adj_Close = history.loc[:, 'Adj Close']
Adj_Close = Adj_Close.reindex(columns=target)

# 終値100円以上
Adj_Close_mean = Adj_Close.mean()
Adj_Close_mean = Adj_Close_mean[Adj_Close_mean > 99]
target = Adj_Close_mean[Adj_Close_mean <= 5000].index.values
# 結果反映
Adj_Close = Adj_Close.reindex(columns=target)
volume = volume.reindex(columns=target)

# 出来高 * 終値が1億以上
values = Adj_Close * volume
values_mean = values.mean()
target = values_mean[values_mean >= 100000000].index.values
# 結果反映
Adj_Close = Adj_Close.reindex(columns=target)
volume = volume.reindex(columns=target)
Open = history.loc[:, 'Open'].reindex(columns=target)

TOPIX_Adj_Close = history_topix.iloc[:, 1]
TOPIX_Adj_Close.columns = ['TOPIX']
Adj_Close_add_topix = pd.concat([Adj_Close, TOPIX_Adj_Close], axis=1, join='inner')
Adj_Close_change = Adj_Close_add_topix.pct_change()
Adj_Close_change_topix = pd.DataFrame(Adj_Close_change.iloc[:, :-1].values - Adj_Close_change.iloc[:, -1:].values,
                                      index=Adj_Close_change.index, columns=Adj_Close_change.columns[:-1])
Open_Close_change = pd.DataFrame(
    ((Adj_Close.values - Open.values) / Open.values),  # - Adj_Close_change.iloc[:, -1:].values,
    index=Adj_Close.index, columns=Adj_Close.columns)
# Adj_Close_change_topix.plot()
xmin, xmax = -0.2, 0.2
ymin, ymax = -0.2, 0.2
plt.scatter(x=Adj_Close_change_topix.values[1:-1], y=Open_Close_change.values[2:], s=1)
plt.title('全量')
plt.xlabel('前日終値との比較 topixの影響切り')
plt.ylabel('次の日始値から終値の変化')
plt.xlim(xmin, xmax)
plt.ylim(ymin, ymax)
plt.hlines([np.median(Adj_Close_change_topix.values[1:-1])], xmin, xmax, "blue", linestyles='dashed')
plt.vlines([np.median(Open_Close_change.values[2:])], ymin, ymax, "blue", linestyles='dashed')

# 75日平均の乖離率
close_mean_75 = Adj_Close.rolling(window=75).mean()
compare = Adj_Close / close_mean_75 - 1
compare_bool_top = compare <= 0.05
compare_bool_btm = compare >= 0
compare_bool = compare_bool_top & compare_bool_btm
# dissociation = compare.tail(1).T.rename(columns={compare.index[-1]: 'difference'})
# dissociation = dissociation.query('-0.01 <= difference <= 0.01')
# target = dissociation.index.values
times = 10
plt.scatter(x=Adj_Close_change_topix.values[compare_bool][1:-1], y=Open_Close_change.values[compare_bool][2:], s=1)
plt.hlines([np.median(Adj_Close_change_topix.values[compare_bool][1:-1])], xmin/times, xmax/times, "black", linestyles='dashed')
plt.vlines([np.median(Open_Close_change.values[compare_bool][2:])], ymin/times, ymax/times, "black", linestyles='dashed')
plt.show()
sum = 1
