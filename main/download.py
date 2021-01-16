# -*- coding: utf-8 -*-
import datetime as dt
import os
import urllib.request
import zipfile
from typing import List

import pandas as pd
from dateutil.relativedelta import relativedelta as rel


def search_last_weekday(target_date: dt.date) -> dt.date:
    holiday_url = 'https://www.jpx.co.jp/corporate/about-jpx/calendar/index.html'
    holiday_dfs = pd.read_html(holiday_url)
    holiday_df = pd.concat([holiday_dfs[0], holiday_dfs[1]], axis=0)

    weekday_index = target_date.weekday()
    while weekday_index == 5 or weekday_index == 6 \
            or holiday_df['日付'].str.startswith(target_date.strftime('YYYY/mm/dd')).sum() > 0:
        target_date = target_date - rel(days=1)
        weekday_index = target_date.weekday()

    return target_date


def download_a_date_stock_price(target_date: dt.date, stock_codes: List) -> pd.DataFrame:
    work_folder = "..\\resource\\last_date_data\\"
    date_yyyymmdd = target_date.strftime('%Y%m%d')
    target_date_zip = 'T' + date_yyyymmdd[2:] + '.zip'
    target_date_csv = 'T' + date_yyyymmdd[2:] + '.csv'

    # 既にデータが存在すればダウンロードしない
    if not os.path.exists(work_folder + target_date_csv):
        url = 'http://mujinzou.com/d_data/' \
              + date_yyyymmdd[0:4] + 'd/' \
              + date_yyyymmdd[2:4] + '_' + date_yyyymmdd[4:6] + 'd/' \
              + target_date_zip
        urllib.request.urlretrieve(url, work_folder + target_date_zip)
        with zipfile.ZipFile(work_folder + target_date_zip) as existing_zip:
            existing_zip.extract(target_date_csv, work_folder)

    target_date_data = pd.read_csv(
        work_folder + target_date_csv,
        header=None,
        names=['Date', 'Code', 'Code2', 'Name', 'Open', 'High', 'Low', 'Close', 'Volume', 'Market'],
        encoding="SHIFT-JIS")
    # 銘柄コードに.Tを付加
    target_date_data['Code'] = [str(x) + '.T' for x in target_date_data['Code']]
    # 引数の銘柄のみ抜き出す
    target_date_data = target_date_data[target_date_data['Code'].isin(stock_codes)]

    before_transpose_data = pd.DataFrame(data=target_date_data.loc[:, ['Code', 'Close']].values)
    before_transpose_data.columns = ['Code', 'Date']
    # 転置前にマルチインデックス用の行を挿入
    before_transpose_data.insert(0, 'Type', 'Adj Close')

    stock_data_frame = before_transpose_data
    column_name = ['Close', 'High', 'Low', 'Open', 'Volume']
    for column in column_name:
        before_transpose_data = pd.concat(
            [before_transpose_data, stock_data_frame.assign(Type=column, Date=target_date_data[column].values)],
            ignore_index=True)

    after_transpose_data = before_transpose_data.set_index(['Type', 'Code']).drop_duplicates().T.rename(
        index={'Date': dt.datetime.strptime(date_yyyymmdd, '%Y%m%d')})

    return after_transpose_data
