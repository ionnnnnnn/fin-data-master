import time

from sqlalchemy import create_engine
import sqlalchemy
import pandas as pd
import tushare as ts
from datetime import datetime, timedelta
import logging
from dbUtil import ts_token, mysql_port, mysql_host_local, mysql_password_local, mysql_username_local, db, \
    stock_price_table

# ts接口服务
ts.set_token(ts_token)
ts_api = ts.pro_api()

# mysql
mysql_engine = create_engine(
    "mysql+pymysql://{}:{}@{}:{}/{}".format(mysql_username_local, mysql_password_local, mysql_host_local, mysql_port,
                                            db))

now = datetime.utcnow() + timedelta(hours=8) + timedelta(days=1)
yesterday = now.strftime("%Y%m%d")
yesterday_dash = now.strftime("%Y-%m-%d")
# log地址
log_path = "/root/cronjob/fincode/cronjob/logfile"


def test_stock_price_exists(table):
    """查询是否已经爬取昨日数据
    Args:
        table (str):
    Returns:
        DataFrame
    """
    query = "select * from {} where time='{}' limit 1".format(table, yesterday_dash)
    res = pd.read_sql_query(query, mysql_engine)
    return res


def stock_price_cronjob():
    # log
    logging.basicConfig(level=logging.INFO, filename=log_path, filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")

    if not test_stock_price_exists(stock_price_table).empty:
        logging.info('already exists stock price data for {}'.format(yesterday_dash))
        return

    df = ts_api.daily(trade_date=yesterday)
    df['time'] = df['trade_date'].astype('int32')
    df = df.drop(columns=['trade_date'])
    df['companyId'] = df['ts_code']
    df = df.drop(columns=['ts_code'])
    logging.info('Got stock price data for {} with len: {}'.format(yesterday_dash, len(df)))

    df.to_sql(stock_price_table, mysql_engine, if_exists='append', index=False,
              dtype={'companyId': sqlalchemy.types.VARCHAR(length=255)}
              )
    logging.info('Successfully inserted')


if __name__ == "__main__":
    for i in range(0, 168):
        now = now - timedelta(days=1)
        yesterday = now.strftime("%Y%m%d")
        yesterday_dash = now.strftime("%Y-%m-%d")
        stock_price_cronjob()
        print("距离今天" + str(i) + "日的数据已经注入完成")
        time.sleep(0.005)
