# -*- coding: utf-8 -*-
import datetime
import urllib

import pandas as pd
import pymysql as sql
import ray
import yfinance as yf

data = pd.read_csv("..\\resource\\sample.csv", header=None, names=['code'])

stocks = [str(s) + ".T" for s in data.code]
tickers = yf.Tickers(" ".join(stocks))

conn = sql.connect(user="root", password="zA3sN82vTsk5Gq", host="localhost", database="stock")
conn.autocommit(False)
cur = conn.cursor()

ray.init(num_cpus=4)


def add_key(df, stock_code):
    if df.size == 0:
        return None
    df.insert(0, "stock_code", stock_code)
    df.insert(1, "stock_Date", [day.strftime('%Y-%m-%d') for day in df.index])
    if df.isnull().values.sum() != 0:
        return df.where(pd.notnull(df), None)
    return df


def create_in_query(df, table_name):
    columns = [column.replace(" ", "_") for column in df.columns]
    insert = "INSERT INTO stock." \
             + table_name \
             + " (" \
             + ', '.join(columns) \
             + ") VALUES (" \
             + ', '.join(["%s"] * len(df.columns)) \
             + ")"
    return insert


last_get_date = pd.read_sql("select stock_code, max(stock_date) as stock_date from stock.history group by Stock_code;"
                            , conn, index_col="stock_code", parse_dates=['stock_date'])


def get_last_date(target_code):
    if target_code in last_get_date.index:
        return str(last_get_date.loc[[target_code], ['stock_date']])
    else:
        return '1999-01-01'


errorList = []
tickers_obj_id = ray.put(tickers)


@ray.remote
def insert_data(tickers_obj, target_ticker_i):
    try:
        target_ticker = tickers_obj.tickers[target_ticker_i]
        code = target_ticker.ticker[0:-2]

        # history
        hist = add_key(target_ticker.history(start=get_last_date(target_ticker), end=str(datetime.date.today())), code)
        try:
            info = target_ticker.info["sharesOutstanding"]
        except urllib.error.HTTPError as he:
            info = target_ticker.info["sharesOutstanding"]

        hist.insert(len(hist.columns), "shares_Out_standing", info)
        cur.executemany(create_in_query(hist, "history"), hist.values.tolist())

        # # financials
        # financials = add_key(target_ticker.financials.T, i)
        # cur.executemany(create_in_query(financials, "financials"), financials.values.tolist())
        #
        # # balance_sheet
        # balance_sheet = add_key(target_ticker.balance_sheet.T, i)
        # cur.executemany(create_in_query(balance_sheet, "balance_sheet"), balance_sheet.values.tolist())
        #
        # # cash_flow
        # cash_flow = add_key(target_ticker.cashflow.T, i)
        # cur.executemany(create_in_query(cash_flow, "cashflow"), cash_flow.values.tolist())

        conn.rollback()
        # conn.commit()
        print(str(datetime.datetime.now()) + " :" + str(code) + " :" + str(i))
    except Exception as ie:
        conn.rollback()
        errorList.append(code)
        print(str(datetime.datetime.now()) + " :" + str(code) + " :" + str(i) + str(type(ie)))


try:
    for i in range(len(tickers.tickers)):
        insert_data.remote(tickers_obj_id, i)

except Exception as e:
    conn.rollback()
    raise e
finally:
    conn.rollback()
    cur.close()
    conn.close()
    print(errorList)
