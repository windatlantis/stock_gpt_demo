import pandas as pd
import numpy as np
import datetime

def testPd():
    df = pd.DataFrame(columns=['date', 'date_month'])
    df['date'] = [datetime.datetime(2023, 1, 1, 10, 0, 0), datetime.datetime(2023, 2, 1, 10, 0, 0), datetime.datetime(2023, 2, 3, 10, 0, 0)]
    df['date_month'] = ['@', '@', '@']
    print(df)
    df['date_month'] = df['date'].dt.strftime("%Y%m")
    df['day'] = df['date'].dt.day
    print(df)
    cl = df[df['day'] == 1 & df['date_month'].str.endswith('02')]
    print(cl)

def test_date_range():
    trade_dates = pd.date_range('20210101', '20210630', freq='MS').strftime("%Y-%m").tolist()
    print(trade_dates)

def test_pd_group():
    company=["A","B","C"]
    data = pd.DataFrame({
        "company":[company[x] for x in np.random.randint(0,len(company),10)],
        "salary":np.random.randint(5,50,10),
        "age":np.random.randint(15,50,10)
        }
    )
    print(data)
    oldest_staff = data.groupby('company',as_index=False).apply(get_oldest_staff)
    print(oldest_staff)
    top_100 = oldest_staff.sort_values(by='age').iloc[:100]
    print(top_100)

def get_oldest_staff(x):
        df = x.sort_values(by = 'age',ascending=True)
        return df.iloc[-1]

if __name__ == '__main__':
    # testPd()
    # test_date_range()
    test_pd_group()