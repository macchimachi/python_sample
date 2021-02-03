# -*- coding: utf-8 -*-
import datetime as dt
import os
import urllib.request
import zipfile
from typing import List

import pandas as pd
import yfinance as yf
from dateutil.relativedelta import relativedelta as rel


def search_business_days_before(target_date: dt.date, how_long_ago: int = 0) -> dt.date:
    if type(target_date) is not dt.date:
        raise ValueError

    if how_long_ago < 0:
        raise ValueError

    holiday_url = 'https://www.jpx.co.jp/corporate/about-jpx/calendar/index.html'
    holiday_df = pd.concat(pd.read_html(holiday_url), axis=0)
    holiday_ary = [dt.datetime.strptime(x[:10], '%Y/%m/%d').date() for x in holiday_df['日付']]

    if not (holiday_ary[0].year <= target_date.year <= holiday_ary[-1].year):
        raise ValueError

    business_ary = [x for x in pd.date_range(start=dt.datetime(holiday_ary[0].year, 1, 1),
                                             end=target_date,
                                             freq="B") if x not in holiday_ary]

    target_index = how_long_ago + 1
    if len(business_ary) < target_index:
        raise ValueError

    return business_ary[-target_index]


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


def download_current_history(end_day: dt.date, do_download_history: bool) -> pd.DataFrame:
    data_csv = pd.read_csv("..\\resource\\sample.csv", header=None, names=['code'])
    stocks = [str(s) + ".T" for s in data_csv.code]

    last_weekday: dt.date = search_business_days_before(end_day)
    before_a_year: dt.date = last_weekday - rel(years=1)

    # ダウンロードするか
    stock_data_csv = "..\\resource\\stock_data.csv"
    if do_download_history:
        history: pd.DataFrame = yf.download(stocks, start=before_a_year,
                                            end=last_weekday, group_by='column')
        history.dropna(how='all', inplace=True)
        history.to_csv(path_or_buf=stock_data_csv)
    else:
        history: pd.DataFrame = pd.read_csv(stock_data_csv, index_col=0, header=[0, 1], parse_dates=True)

    if last_weekday not in history.index.values:
        last_weekday_stock_price = download_a_date_stock_price(
            last_weekday, history.columns.levels[1].values)
        history = history.append(last_weekday_stock_price)

    return history
