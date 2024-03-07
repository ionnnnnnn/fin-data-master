from sqlalchemy import create_engine, Column, String, Integer, REAL, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy
import pandas as pd
import logging

# mysql配置
from dbUtil import create_stock_engine

table = "stock_tip_overall"

mysql_engine = create_stock_engine("remote")
DBSession = sessionmaker(bind=mysql_engine)
session = DBSession()
Base = declarative_base()
Base.metadata.create_all(mysql_engine)

# log地址
log_path = "/root/cronjob/fincode/cronjob/stock_tip_profitindex_job"


class StockTipOverall(Base):
    __tablename__ = table

    stock_id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, primary_key=True)
    history_profit_rate = Column(REAL)
    history_match_rate = Column(REAL)
    profit_index = Column(REAL)

    # industry_id = Column(Integer)
    # day_span = Column(Integer)
    # industry_match_rate = Column(REAL)
    # is_deleted = Column(Integer)
    # gmt_created = Column(DateTime)
    # gmt_modified = Column(DateTime)

    def __iter__(self):
        for attr in dir(self):
            if (not attr.startswith("_")) and (not attr == "metadata"):
                yield attr


# 传入 min-25%-50%-75%-max 五个匹配率数值
# 这五个数值分别对应 0.6-0.7-0.8-0.9-1
# 由这五个点对构建出四个一次函数
def build_profit_func(m0, m1, m2, m3, m4):
    k1 = 0.1 / (m1 - m0)
    b1 = 0.7 - k1 * m1
    k2 = 0.1 / (m2 - m1)
    b2 = 0.8 - k2 * m2
    k3 = 0.1 / (m3 - m2)
    b3 = 0.9 - k3 * m3
    k4 = 0.1 / (m4 - m3)
    b4 = 1 - k4 * m4

    def profit_func(profit_rate, match_rate):
        m = 0
        if (match_rate >= m4):
            m = 1
        elif (match_rate < m4 and match_rate >= m3):
            m = k4 * match_rate + b4
        elif (match_rate < m3 and match_rate >= m2):
            m = k3 * match_rate + b3
        elif (match_rate < m2 and match_rate >= m1):
            m = k2 * match_rate + b2
        elif (match_rate < m1 and match_rate >= m0):
            m = k1 * match_rate + b1
        else:
            m = 0
        return profit_rate * m

    return profit_func


def stock_tip_profitindex_job():
    # log
    # logging.basicConfig(level=logging.INFO, filename=log_path, filemode="a+",
    #                 format="%(asctime)-15s %(levelname)-8s %(message)s")

    # 获取全部收益率大于 0 的股票-策略信息
    data = session.query(StockTipOverall).filter(StockTipOverall.history_profit_rate > 0).all()
    # 将对象数组转换为 DataFrame
    df_dict = {
        'stock_id': [],
        'strategy_id': [],
        'history_profit_rate': [],
        'history_match_rate': [],
        'profit_index': [],
        # 'industry_id': [],
        # 'day_span': [],
        # 'industry_match_rate': [],
        # 'is_deleted': [],
        # 'gmt_created': [],
        # 'gmt_modified': []
    }
    for obj in data:
        for attr in df_dict:
            df_dict[attr].append(getattr(obj, attr))
    df = pd.DataFrame.from_records(df_dict)
    # 构建收益指数计算函数
    description = df.describe()['history_match_rate']
    profit_func = build_profit_func(
        description['min'],
        description['25%'],
        description['50%'],
        description['75%'],
        description['max']
    )
    # 计算收益指数
    for index, row in df.iterrows():
        df.loc[index, 'profit_index'] = profit_func(df.loc[index, 'history_profit_rate'],
                                                    df.loc[index, 'history_match_rate'])
    # 更新数据库
    record_arr = df.to_dict(orient='records')
    session.bulk_update_mappings(
        StockTipOverall,
        record_arr
    )
    session.commit()


if __name__ == "__main__":
    stock_tip_profitindex_job()
