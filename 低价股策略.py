import akshare as ak
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import get_stock

# 获取A股股票列表
def get_stock_list():
    stock_list = get_stock.get_stock_info_code_name()
    return stock_list

# 获取股票价格数据
def get_stock_prices(stock_code, start_date, end_date):
    try:
        stock_data = get_stock.get_stock_history(stock_code, start_date=start_date, end_date=end_date)
        
        return stock_data
    except Exception as e:
        print(f"Error fetching data for {stock_code}: {e}")
        return None

# 筛选符合条件的股票
def filter_stocks(stock_list, start_date, end_date):
    filtered_stocks = []
    one_year_ago = datetime.datetime.strptime(start_date, "%Y%m%d") - datetime.timedelta(days=365)
    one_year_ago = one_year_ago.date()
    one_year_ago_str = (one_year_ago).strftime("%Y%m%d")

    for _, row in stock_list.iterrows():
        stock_code = row['code']
        stock_name = row['name']
        list_date = row['list_date']

        print('loop stock ---- ' + stock_code + ',' + stock_name)
        if not (stock_code.startswith("688") or stock_name.startswith("ST") or stock_name.startswith("*ST")):
            prices = get_stock_prices(stock_code, start_date=one_year_ago_str, end_date=end_date)

            if prices is not None and len(prices) > 0:
                prices['code'] = stock_code
                prices['name'] = stock_name
                prices['list_date'] = list_date

                if (prices['close'].iloc[-1] > 2) and (prices['list_date'].iloc[-1] < one_year_ago):
                    filtered_stocks.append(prices)

    return pd.concat(filtered_stocks)

# 每月1日选股
def select_stocks(stocks, date):
    stocks = stocks[stocks['date'] == date]
    stocks = stocks.sort_values(by='close').iloc[:100]
    return stocks

# 计算收益
def calculate_performance(start_date, end_date):
    stock_list = get_stock_list()
    filtered_stocks = filter_stocks(stock_list, start_date, end_date)
    trade_dates = pd.date_range(start_date, end_date, freq='MS').strftime("%Y-%m-%d").tolist()
    total_investment = 0
    total_profit = 0

    for trade_date in trade_dates:
        selected_stocks = select_stocks(filtered_stocks, trade_date)
        investment = 0
        profit = 0

        for _, row in selected_stocks.iterrows():
            stock_code = row['code']
            stock_name = row['name']
            buy_price = row['close']
            num_shares = 10000 / buy_price
            investment += 10000

            # 计算月底卖出价格
            sell_date = (datetime.datetime.strptime(trade_date, "%Y-%m-%d") + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            stock_prices = filtered_stocks[filtered_stocks['code'] == stock_code]
            sell_price_row = stock_prices[stock_prices['date'] == sell_date]

            if not sell_price_row.empty:
                sell_price = sell_price_row.iloc[0]['close']
            else:
                sell_price = stock_prices.iloc[-1]['close']

            profit += num_shares * (sell_price - buy_price)
            print('sell stock ---- ' + trade_date + ',' + stock_code + ',' + stock_name + ' ---- 收益: ' + str(profit))

        total_investment += investment
        total_profit += profit
        print(f"Trade Date: {trade_date}, Investment: {investment}, Profit: {profit}")

    # 计算收益率和年化收益率
    roi = total_profit / total_investment
    annualized_roi = (1 + roi) ** (365 / ((datetime.datetime.strptime(end_date, "%Y%m%d") - datetime.datetime.strptime(start_date, "%Y%m%d")).days)) - 1

    print(f"Total Investment: {total_investment}, Total Profit: {total_profit}")
    print(f"Return on Investment (ROI): {roi * 100:.2f}%, Annualized ROI: {annualized_roi * 100:.2f}%")

    # 绘制收益曲线与沪深300指数的对比图
    hs300 = get_stock.get_index_history("000300", start_date, end_date)
    hs300.set_index('date', inplace=True)
    hs300['close'] = hs300['close'].astype(float)
    hs300['ROI'] = (hs300['close'].pct_change() + 1).cumprod()

    plt.figure(figsize=(10, 6))
    plt.plot(hs300['ROI'], label="HS300")
    plt.plot((filtered_stocks['close'].pct_change() + 1).cumprod(), label="Strategy")
    plt.legend(loc="best")
    plt.title("Return Comparison")
    plt.xlabel("Time")
    plt.ylabel("Cumulative Return")
    plt.grid()
    plt.show()

start_date="20210101"
end_date="20210630"

if __name__ == '__main__':
    calculate_performance(start_date, end_date)