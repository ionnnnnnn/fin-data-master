from influxdb import DataFrameClient
from sqlalchemy import create_engine
import pandas as pd

# 获取全部股票列表
stocks = open("industry/stock.txt").read().split()

# 连接influxDB
influx_client = DataFrameClient(host="47.101.33.219", port="8086",
                         username="influx", password="zhaowenqi",
                         database="stock")

# MySQL的用户名、密码、IP地址、端口、数据库名
mysql_engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format('fincode', 'Fincode2021', 'rm-uf6t9264z8gy7e6ut7o.mysql.rds.aliyuncs.com', '3306', 'fincode'))


def wrap_quote(s: str) -> str:
    return "'" + s + "'"


def influxdb_to_mysql(code: str):
    print(code, end = " ")
    query = "select * from stock where companyId={}".format(wrap_quote(code))
    df = influx_client.query(query)['stock']
    df['time'] = pd.to_datetime(df.index)
    df['time'] = df['time'].astype('datetime64[us]')
    print("export", end = " ")
    df.to_sql('stock_price',mysql_engine,if_exists='append',index=False)
    print("import")

if __name__ == '__main__':
    for code in stocks:
        influxdb_to_mysql(code)
    