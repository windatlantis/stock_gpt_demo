import pandas as pd
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

if __name__ == '__main__':
    testPd()