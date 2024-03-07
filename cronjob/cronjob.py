import time
from lxml import etree

import sqlalchemy
import base64
import requests
import pandas as pd
import tushare as ts
from datetime import datetime, timedelta
import logging
from dbUtil import ts_token, stock_price_table, create_stock_engine

# ts接口服务
ts.set_token(ts_token)
ts_api = ts.pro_api()

# mysql
mysql_engine = create_stock_engine("local")

# 时间设置
# now = datetime.utcnow() + timedelta(hours=8)
# yesterday = now.strftime("%Y%m%d")
# yesterday_int = int(yesterday)
yesterday = '20230519'
yesterday_int = 20230519
# log地址
log_path = "/root/cronjob/fincode/cronjob/logfile"


def test_stock_price_exists(table):
    """查询是否已经爬取昨日数据
    Args:
        table (str): 
    Returns:
        DataFrame
    """
    query = "select * from {} where time='{}' limit 1".format(table, yesterday_int)
    res = pd.read_sql_query(query, mysql_engine)
    return res


def stock_price_cronjob():
    # log
    logging.basicConfig(level=logging.INFO, filename=log_path, filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")

    # if not test_stock_price_exists(stock_price_table).empty:
    #     logging.info('already exists stock price data for {}'.format(yesterday_int))
    #     print('already exists stock price data for {}'.format(yesterday_int))
    #     return

    df = ts_api.daily(trade_date=yesterday)
    df['time'] = df['trade_date'].astype('int32')
    df = df.drop(columns=['trade_date'])
    df['companyId'] = df['ts_code']
    df = df.drop(columns=['ts_code'])
    logging.info('Got stock price data for {} with len: {}'.format(yesterday_int, len(df)))
    print('Got stock price data for {} with len: {}'.format(yesterday_int, len(df)))

    df.to_sql(stock_price_table, mysql_engine, if_exists='append', index=False,
              dtype={'companyId': sqlalchemy.types.VARCHAR(length=255)}
              )
    logging.info('Successfully inserted')
    print('Successfully inserted')


# def logout(flag: bool):
#     decode1 = base64.b64decode(b"MTgxMjUwMDIy")
#     username = str(decode1)[2:len(decode1) + 2]
#     decode2 = base64.b64decode(b"aWNpbWVuY2VAMDcxNQ==")
#     passwd = str(decode2)[2:len(decode2) + 2]
#     if flag:
#         url = "http://p.nju.edu.cn/portal_io/logout"
#     else:
#         url = "http://p.nju.edu.cn/portal_io/login?username=" + username + "&password=" + passwd
#     res = requests.get(url)
#     print(res)

def logout(flag: bool):
    username = "191250206"
    passwd = "123456789:Zwx"
    if flag:
        url = "http://p2.nju.edu.cn/api/portal_io/logout"
        # data = {
        #     "domain": "default"
        # }
    else:
        url = "http://p2.nju.edu.cn/api/portal_io/login?username=" + username + "&password=" + passwd
        # data = {
        #     "domain": "default",
        #     "username": username,
        #     "password": passwd
        # }
    res = requests.get(url)
    print(res)
    print(res.content)


if __name__ == "__main__":
    # logout(True)
    # time.sleep(2)
    # logout(False)
    stock_price_cronjob()
#     url = 'https://www.baidu.com/'
#     g
# et_resp = requests.get(url)
#     print(get_resp.content)
#     logout(True)