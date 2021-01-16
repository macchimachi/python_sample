# -*- coding: utf-8 -*-
import concurrent
import datetime
import time
import traceback
import urllib

import numpy as np
import pandas as pd
import pymysql as sql
import threaded
import yfinance as yf

start = datetime.datetime.now()
data = pd.read_csv("..\\resource\\toushou_all.csv", header=None, names=['code'])

stocks = [str(s) + ".T" for s in data.code]

data = yf.download(stocks, start="2017-01-01",
                    end="2017-04-30", group_by='tickers')

tickers = yf.Tickers(" ".join(stocks))
conn = sql.connect(user="root", password="zA3sN82vTsk5Gq", host="localhost", database="stock")
conn.autocommit(False)
cur = conn.cursor()

threaded.ThreadPooled.configure(max_workers=3)


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


last_get_date = pd.read_sql("select stock_code, max(stock_date) as stock_date from stock.history group by Stock_code;",
                            conn, index_col="stock_code", parse_dates=["stock_date"])

last_get_date["stock_date"] = last_get_date["stock_date"].apply(lambda x: x + datetime.timedelta(days=1))


def get_last_date(target_code):
    if target_code in last_get_date.index:
        return last_get_date.loc[target_code, 'stock_date'].strftime('%Y-%m-%d')
    else:
        return '1999-01-01'


errorList = []


@threaded.ThreadPooled
def insert_data(target_ticker_i):
    try:
        target_ticker = tickers.tickers[target_ticker_i]
        code_i: int = int(target_ticker.ticker[0:-2])

        hist = add_key(target_ticker.history(start=get_last_date(code_i), end=str(datetime.date.today())), code_i)
        if hist is None:
            return
        if len(hist) == 0:
            return
        try:
            info = target_ticker.info["sharesOutstanding"]
        except urllib.error.HTTPError as he:
            info = target_ticker.info["sharesOutstanding"]
        except (KeyError, IndexError) as ke:
            info = None

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

        # conn.rollback()
        conn.commit()
        print(str(datetime.datetime.now() - start) + " :" + str(code_i) + " :" + str(target_ticker_i))
        time.sleep(3)
    except Exception as ie:
        conn.rollback()
        errorList.append(code_i)
        print(str(datetime.datetime.now() - start) + " :" + str(code_i) + " :" + str(target_ticker_i) + str(ie))
        print(traceback.format_exc())


# index = np.array_split(range(len(tickers.tickers)), 40)

try:
    concurrent.futures.wait([insert_data(i) for i in range(len(tickers.tickers))])

    # for i_sub in index:
    #     concurrent.futures.wait([insert_data(i) for i in i_sub])
    #     print("10秒待ち")
    #     time.sleep(10)
    #     print(i_sub)

    # for i in range(len(tickers.tickers)):
    #     insert_data(i)

except Exception as e:
    conn.rollback()
    raise e
finally:
    cur.close()
    conn.close()
    print(errorList)
