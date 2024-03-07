# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 15:23:40 2021

@author: wenha
"""
from sqlalchemy import create_engine
import sqlalchemy
import json
import pandas as pd
import tushare as ts
from datetime import datetime, timedelta
from dbUtil import ts_token, stock_detail_table, stock_table, industry_table, create_stock_engine

# ts接口服务
ts.set_token(ts_token)
ts_api = ts.pro_api()

# mysql
mysql_engine = create_stock_engine("remote")

# 时间设置
now = datetime.utcnow() + timedelta(hours=8)
yesterday = now.strftime("%Y%m%d")
yesterday_dash = now.strftime("%Y-%m-%d")


def load_industry_data():
    df = pd.read_csv("industry.csv")
    df = df.drop(columns=['idx'])
    industry_map = {}
    industry_df = pd.DataFrame(columns=('id', 'name'))
    i = 0
    row = {"id": -1, "name": "未匹配到领域的股票"}
    industry_df.loc[len(industry_df)] = row
    for col in df.columns:
        row = {"id": i, "name": col}
        industry_df.loc[len(industry_df)] = row
        for index in df.index:
            industry_map[df[col].loc[index]] = i
        i += 1
    return industry_map, industry_df


def stock_job():
    industry_map, industry_df = load_industry_data()
    df = ts_api.stock_basic(exchange='', list_status='L', fields='name,ts_code')
    # 插入一列
    df['industry_id'] = df['name']
    for i in range(len(df)):
        row = df.iloc[i]
        if row['ts_code'] in industry_map:
            df.iloc[i, df.columns.get_loc('industry_id')] = industry_map[row['ts_code']]
        else:
            df.iloc[i, df.columns.get_loc('industry_id')] = -1

    df.to_sql(stock_table, mysql_engine, if_exists='append', index=False)


def industry_job():
    industry_map, industry_df = load_industry_data()
    industry_df.to_sql(industry_table, mysql_engine, if_exists='append', index=False)


def stock_detail_job():
    industry_map, industry_df = load_industry_data()
    df = ts_api.stock_basic(exchange='', list_status='L',
                            fields='name,enname,ts_code,list_date,area,fullname,market,industry')
    # 插入两列
    df['ext_info'] = df['fullname']
    df['industry_id'] = df['industry']
    df['stock_id'] = df['industry']
    for i in range(len(df)):
        row = df.iloc[i]
        stock_id = int(get_id_by_stock_code(row['ts_code'])['id'][0])
        df.iloc[i, df.columns.get_loc('stock_id')] = stock_id
        ext_info = {"fullname": row["fullname"], "market": row["market"], "industry_name": row["industry"]}
        df.iloc[i, df.columns.get_loc('ext_info')] = json.dumps(ext_info, ensure_ascii=False)
        if row['ts_code'] in industry_map:
            df.iloc[i, df.columns.get_loc('industry_id')] = industry_map[row['ts_code']]
        else:
            df.iloc[i, df.columns.get_loc('industry_id')] = -1

    df = df.drop(columns=['fullname'])
    df = df.drop(columns=['market'])
    df = df.drop(columns=['industry'])

    df.to_sql(stock_detail_table, mysql_engine, if_exists='append', index=False)


def get_id_by_stock_code(ts_code):
    """查询是否已经爬取昨日数据
    Args:
        ts_code:
        table (str):
    Returns:
        DataFrame
    """
    query = "select id from {} where ts_code='{}'".format("stock", ts_code)
    res = pd.read_sql_query(query, mysql_engine)
    return res


if __name__ == "__main__":
    industry_job()
    stock_job()
    stock_detail_job()
