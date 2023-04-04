import akshare as ak
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import get_stock

# 获取A股股票列表
def get_stock_list() -> pd.DataFrame:
    stock_list = get_stock.get_stock_info_code_name()
    return stock_list

# 获取股票价格数据
def get_stock_prices(stock_code, start_date, end_date) -> pd.DataFrame:
    try:
        stock_data = get_stock.get_stock_history(stock_code, start_date=start_date, end_date=end_date)
        
        return stock_data
    except Exception as e:
        print(f"Error fetching data for {stock_code}: {e}")
        return None

# 筛选符合条件的股票
def filter_stocks(stock_list: pd.DataFrame, start_date, end_date):
    filtered_stocks = []
    one_year_ago = datetime.datetime.strptime(start_date, "%Y%m%d") - datetime.timedelta(days=365)
    one_year_ago = one_year_ago.date()
    # one_year_ago_str = (one_year_ago).strftime("%Y%m%d")

    for _, row in stock_list.iterrows():
        stock_code = row['code']
        stock_name = row['name']
        list_date = row['list_date']

        if list_date > one_year_ago :
            # 上市不满一年
            continue
        if stock_code.startswith("688") or stock_name.startswith("ST") or stock_name.startswith("*ST"):
            # 科创、退市
            continue

        prices = get_stock_prices(stock_code, start_date=start_date, end_date=end_date)
        if prices is not None and len(prices) > 0:
            print('loop stock ---- ' + stock_code + ',' + stock_name)
            prices['code'] = stock_code
            prices['name'] = stock_name
            prices['date_month'] = prices['date'].str[:7]
            filtered_stocks.append(prices)

            # line_number = int(prices.shape[0])
            # for i in range(line_number):
            #     if (prices['close'].iloc[i] > 2):
            #         # 价格大于2元
            #         filtered_stocks.append(prices)

    return pd.concat(filtered_stocks)

# 每月1日选股
def select_stocks(stocks: pd.DataFrame, month, type=1) -> pd.DataFrame:
    # 1版：1号买，月底卖
    # 2版：随机一天买，月底卖
    # 3版：随机一天买，持股1/2/3/4周卖掉
    # 4版：买分属不同行业的10只股
    if (type == 1):
        stocks_this_month = stocks[stocks['date_month'] == month]
        stocks_month_firstday = stocks_this_month.groupby('code',as_index=False).apply(get_first_day)
        stocks_month_firstday = stocks_month_firstday[stocks_month_firstday['close'] > 2]
        stocks_100 = stocks_month_firstday.sort_values(by='close').iloc[:100]
        return stocks_100
    # if (type == 2):

    # if (type == 3):

    # if (type == 4):

    return stocks

def get_first_day(x):
    df = x.sort_values(by = 'date', ascending=True)
    return df.iloc[0]

# 计算收益
def calculate_performance(start_date, end_date):
    # ["code", "name", 'list_date', 'market_code']
    stock_list = get_stock_list()
    # ["date", "close", 'code', "name", 'date_month]
    filtered_stocks = filter_stocks(stock_list, start_date, end_date)
    trade_months = pd.date_range(start_date, end_date, freq='MS').strftime("%Y-%m").tolist()
    total_investment = 0
    total_profit = 0
    trade_record = pd.DataFrame(columns=['股票代码', '股票名称', '买入日期',  '买入价格', '卖出日期',  '卖出价格', '收益'])

    for trade_month in trade_months:
        selected_stocks = select_stocks(filtered_stocks, trade_month, 1)
        investment = 0
        profit = 0

        for _, row in selected_stocks.iterrows():
            stock_code = row['code']
            stock_name = row['name']
            buy_price = row['close']
            trade_date = row['date']
            num_shares = 10000 / buy_price
            investment += 10000

            # 计算月底卖出价格
            stock_prices = filtered_stocks.loc[(filtered_stocks['code'] == stock_code) & (filtered_stocks['date_month'] == trade_month)]
            month_lastday = stock_prices.sort_values(by='date').iloc[-1]
            sell_price = month_lastday['close']

            profit += num_shares * (sell_price - buy_price)
            print('sell stock ---- ' + trade_month + ',' + stock_code + ',' + stock_name + ' ---- 收益: ' + str(profit))
            record = {'股票代码': stock_code, '股票名称': stock_name, '买入日期':trade_date, '买入价格':buy_price, '卖出日期':month_lastday['date'], '卖出价格':sell_price, '收益':profit}
            trade_record = trade_record.append(record, ignore_index=True)

        total_investment += investment
        total_profit += profit
        print(f"Trade Date: {trade_month}, Investment: {investment}, Profit: {profit}")

    # 计算收益率和年化收益率
    roi = total_profit / total_investment
    annualized_roi = (1 + roi) ** (365 / ((datetime.datetime.strptime(end_date, "%Y%m%d") - datetime.datetime.strptime(start_date, "%Y%m%d")).days)) - 1

    print(f"Total Investment: {total_investment}, Total Profit: {total_profit}")
    print(f"Return on Investment (ROI): {roi * 100:.2f}%, Annualized ROI: {annualized_roi * 100:.2f}%")
    trade_record.to_csv('./trade_record_{}.csv'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
    print('csv is save')

    # 绘制收益曲线与沪深300指数的对比图
    # hs300 = get_stock.get_index_history("000300", start_date, end_date)
    # hs300.set_index('date', inplace=True)
    # hs300['close'] = hs300['close'].astype(float)
    # hs300['ROI'] = (hs300['close'].pct_change() + 1).cumprod()

    # plt.figure(figsize=(10, 6))
    # plt.plot(hs300['ROI'], label="HS300")
    # plt.plot((filtered_stocks['close'].pct_change() + 1).cumprod(), label="Strategy")
    # plt.legend(loc="best")
    # plt.title("Return Comparison")
    # plt.xlabel("Time")
    # plt.ylabel("Cumulative Return")
    # plt.grid()
    # plt.show()

start_date="20210101"
end_date="20210630"

if __name__ == '__main__':
    calculate_performance(start_date, end_date)