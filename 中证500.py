import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(start_date, end_date):
    """
    获取股票数据
    """
    stock_zz500 = ak.stock_zh_a_daily(symbol="000905.SH", start_date=start_date, end_date=end_date)
    stock_zz500.rename(columns={"close": "close_price", "trade_date": "date"}, inplace=True)
    stock_zz500["date"] = pd.to_datetime(stock_zz500["date"])
    stock_zz500.set_index("date", inplace=True)
    return stock_zz500

def get_concentration_ratio(date):
    """
    获取筹码集中度
    """
    stock_concentration = ak.stock_em_crd_d(date=date)
    stock_concentration.set_index("证券代码", inplace=True)
    concentration_ratio = stock_concentration["筹码集中度"].astype(float) / 100
    return concentration_ratio

def get_moving_average(stock_data, days):
    """
    计算移动平均线
    """
    ma = stock_data["close_price"].rolling(window=days).mean()
    return ma

def get_buy_stock(stock_data, concentration_ratio, ma_days):
    """
    选择符合买入条件的股票
    """
    buy_stock = None
    filtered_stocks = stock_data[stock_data["market_value"] > 0].index
    for stock in filtered_stocks:
        stock_concentration = concentration_ratio.get(stock, None)
        if stock_concentration is None or stock_concentration > 0.15:
            continue
        ma = get_moving_average(stock_data[stock], ma_days)
        if stock_data[stock]["close_price"][-1] > ma[-1]:
            if buy_stock is None or stock_data[stock]["market_value"] < buy_stock["market_value"]:
                buy_stock = {"code": stock, "market_value": stock_data[stock]["market_value"][-1], "buy_price": stock_data[stock]["close_price"][-1]}
    return buy_stock

def backtest(start_date, end_date):
    """
    回测函数
    """
    stock_data = get_stock_data(start_date, end_date)
    balance = 1.0
    buy_date = None
    buy_stock = None
    transactions = []
    for date in stock_data.index:
        if buy_stock is None:
            concentration_ratio = get_concentration_ratio(date)
            buy_stock = get_buy_stock(stock_data.loc[:date], concentration_ratio, 21)
            if buy_stock is not None:
                buy_date = date
                buy_stock["shares"] = balance / buy_stock["buy_price"]
                balance = 0.0
                transactions.append({"date": buy_date, "code": buy_stock["code"], "price": buy_stock["buy_price"], "action": "buy", "shares": buy_stock["shares"]})
        else:
            holding_days = (date - buy_date).days
            if holding_days >= 26 or (holding_days >= 1 and stock_data.loc[date, buy_stock["code"]]["close_price"] / buy_stock["buy_price"] - 1.0 < max_profit - 0.06):
                max_profit = (stock_data.loc[buy_date:date, buy_stock["code"]]["close_price"] / buy_stock["buy_price"]).max() - 1.0
                current_profit = (stock_data.loc[date, buy_stock["code"]]["close_price"] / buy_stock["buy_price"]) - 1.0
                if current_profit >= 0.3:
                    continue
                elif current_profit < 0.3 and current_profit < max_profit - 0.06:
                    sell_price = stock_data.loc[date, buy_stock["code"]]["close_price"]
                    balance = buy_stock["shares"] * sell_price
                    transactions.append({"date": date, "code": buy_stock["code"], "price": sell_price, "action": "sell", "shares": buy_stock["shares"]})
                    buy_stock = None
                    buy_stock = get_buy_stock(stock_data.loc[date:], get_concentration_ratio(date), 21)
                    if buy_stock is not None:
                        buy_date = date
                        buy_stock["shares"] = balance / buy_stock["buy_price"]
                        balance = 0.0
                        transactions.append({"date": buy_date, "code": buy_stock["code"], "price": buy_stock["buy_price"], "action": "buy", "shares": buy_stock["shares"]})
                elif current_profit < -0.1:
                    sell_price = stock_data.loc[date, buy_stock["code"]]["close_price"]
                    balance = buy_stock["shares"] * sell_price
                    transactions.append({"date": date, "code": buy_stock["code"], "price": sell_price, "action": "sell", "shares": buy_stock["shares"]})
                    buy_stock = None
                    buy_stock = get_buy_stock(stock_data.loc[date:], get_concentration_ratio(date), 21)
                    if buy_stock is not None:
                        buy_date = date
                        buy_stock["shares"] = balance / buy_stock["buy_price"]
                        balance = 0.0
                        transactions.append({"date": buy_date, "code": buy_stock["code"], "price": buy_stock["buy_price"], "action": "buy", "shares": buy_stock["shares"]})
    if buy_stock is not None:
        sell_price = stock_data.iloc[-1][buy_stock["code"]]["close_price"]
        balance = buy_stock["shares"] * sell_price
        transactions.append({"date": stock_data.index[-1], "code": buy_stock["code"], "price": sell_price, "action": "sell", "shares": buy_stock["shares"]})
    total_return = balance / 1.0 - 1.0
    annualized_return = ((1.0 + total_return) ** (252.0 / len(stock_data.index))) - 1.0
    return total_return, annualized_return, transactions

start_date = "2021-01-01"
end_date = "2023-03-01"

total_return, annualized_return, transactions = backtest(start_date, end_date)

print("总回报：{:.2%}".format(total_return))
print("年化回报：{:.2%}".format(annualized_return))
print("交易明细：")
for transaction in transactions:
    print("{}\t{}\t{}\t{}\t{}".format(transaction["date"].strftime("%Y-%m-%d"), transaction["code"], transaction["price"], transaction["action"], transaction["shares"]))

