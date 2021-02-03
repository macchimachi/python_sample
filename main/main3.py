# -*- coding: utf-8 -*-
import datetime as dt

import matplotlib.pyplot as plt
import pandas as pd
from dateutil.relativedelta import relativedelta as rel

import download

if dt.datetime.now().hour.__int__() >= 15:
    end_day = dt.date.today()
else:
    end_day = dt.date.today() - rel(days=1)

do_download_history = False
history = download.download_current_history(end_day, do_download_history)

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

# 75日平均の乖離率が2%以下
close_mean_75 = Adj_Close.rolling(window=75).mean()
compare = Adj_Close / close_mean_75 - 1
dissociation = compare.tail(1).T.rename(columns={compare.index[-1]: 'difference'})
dissociation = dissociation.query('-0.05 <= difference <= 0')
target = dissociation.index.values

# 結果反映
Adj_Close = Adj_Close.reindex(columns=target)
close_mean_75 = Adj_Close.rolling(window=75).mean()

# 3,2,1か月前の順で低くなる
month = [1, 2, 3]
last_day = close_mean_75.index[-1]
df_few_month = pd.DataFrame(index=close_mean_75.columns, columns=[])
for a_month in month:
    few_month_ago = last_day - rel(months=a_month)
    df_few_month['month_ago_' + str(a_month)] = close_mean_75[:few_month_ago].iloc[-1]
diff_month = df_few_month.diff(-1, axis=1).query('month_ago_1 <= 0 and month_ago_2 <=0')
target = diff_month.index.values
# 結果反映
Adj_Close = Adj_Close.reindex(columns=target)
close_mean_75 = Adj_Close.rolling(window=75).mean()

# # 直近の75日移動平均の傾きがプラス、2か月前はマイナス
# diff_75 = close_mean_75.diff()
# two_month_ago = last_day - rel(months=2)
# df_concat = pd.DataFrame(index=diff_75.columns, columns=[])
# df_concat['last_day'] = diff_75.iloc[-1]
# df_concat['two_month_ago'] = diff_75[:two_month_ago].iloc[-1]
# df_concat = df_concat.query('last_day >= 0 and two_month_ago <=0')
# target = df_concat.index.values

# 結果反映
Adj_Close = Adj_Close.reindex(columns=target)
close_mean_75 = Adj_Close.rolling(window=75).mean()
volume = volume.reindex(columns=target)
close_mean_25 = Adj_Close.rolling(window=25).mean()

for code in Adj_Close.columns.values:
    plt_df = pd.DataFrame(Adj_Close[code])
    plt_df.columns = ['Adj_Close']
    plt_df = plt_df.assign(close_mean_75=close_mean_75[code])
    plt_df = plt_df.assign(close_mean_25=close_mean_25[code])
    plt_df.plot()
    plt.title(code)
    plt.show()

sum = 1
