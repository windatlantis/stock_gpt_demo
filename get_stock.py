# -*- coding:utf-8 -*-
"""
@Time : 2023/3/22 22:21
@Author: windatlantis
@File : get_stock.py
"""
import akshare as ak

import pandas as pd


def get_stock_info_code_name():
    """
        沪深科创股票代码和股票简称数据
                code   name     market_code
        0     000001   平安银行  sz000001
        1     000002  万  科Ａ   sz000002
        2     000004   国华网安  sz000004
        3     000005   ST星源   sz000005
    :return:
    """

    big_df = pd.DataFrame()
    stock_sh = ak.stock_info_sh_name_code(symbol="主板A股")
    stock_sh = stock_sh[["证券代码", "证券简称", "上市日期"]]
    stock_sh['market_code'] = 'sh' + stock_sh["证券代码"]

    stock_sz = ak.stock_info_sz_name_code(indicator="A股列表")
    stock_sz["A股代码"] = stock_sz["A股代码"].astype(str).str.zfill(6)
    stock_sz['market_code'] = 'sz' + stock_sz["A股代码"]
    stock_sz["A股上市日期"] = pd.to_datetime(stock_sz["A股上市日期"]).dt.date
    big_df = pd.concat([big_df, stock_sz[["A股代码", "A股简称", 'A股上市日期', 'market_code']]], ignore_index=True)
    big_df.columns = ["证券代码", "证券简称", '上市日期', 'market_code']

    stock_kcb = ak.stock_info_sh_name_code(symbol="科创板")
    stock_kcb = stock_kcb[["证券代码", "证券简称", '上市日期']]
    stock_kcb['market_code'] = 'sh' + stock_kcb["证券代码"]

    big_df = pd.concat([big_df, stock_sh], ignore_index=True)
    big_df = pd.concat([big_df, stock_kcb], ignore_index=True)
    big_df.columns = ["code", "name", 'list_date', 'market_code']

    return big_df

def get_stock_history(stock_code, start_date, end_date):
    stock_zh_a_spot_df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date)
    price = stock_zh_a_spot_df[['日期', '收盘']]
    price.columns = ["date", "close"]

    return price

def get_index_history(index_code, start_date, end_date):
    index_zh_a_hist_df = ak.index_zh_a_hist(symbol=index_code, start_date=start_date, end_date=end_date)
    price = index_zh_a_hist_df[['日期', '收盘']]
    price.columns = ["date", "close"]

    return price

def get_all_stock_history(start_date, end_date):
    stock_code_name = get_stock_info_code_name()
    line_number = int(stock_code_name.shape[0])
    stock_df = pd.DataFrame()
    for i in range(line_number):
        cur = stock_code_name.iloc[i]
        temp = get_stock_history(cur['code'], start_date, end_date)
        stock_df = pd.concat([stock_df, temp], ignore_index=True)
    return stock_df

if __name__ == '__main__':
    stock_history = get_stock_history('000001', '20230201', '20230301')
    print(stock_history)
    #         日期     收盘
    # 0   2023-02-01  14.70
    # 1   2023-02-02  14.60
    # 2   2023-02-03  14.32
    # 3   2023-02-06  14.00
    # 4   2023-02-07  14.21
    # 5   2023-02-08  14.04
    # 6   2023-02-09  14.13
    # 7   2023-02-10  13.98
    # 8   2023-02-13  13.82
    # 9   2023-02-14  13.96
    # 10  2023-02-15  13.67
    # 11  2023-02-16  13.60
    # 12  2023-02-17  13.43
    # 13  2023-02-20  14.15
    # 14  2023-02-21  14.10
    # 15  2023-02-22  14.02
    # 16  2023-02-23  14.05
    # 17  2023-02-24  13.86
    # 18  2023-02-27  13.69
    # 19  2023-02-28  13.78
    # 20  2023-03-01  14.17