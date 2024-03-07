# Fincode-Data
## cronjob 定时任务
* 代码push后会自动更新服务器上的定时任务，不可修改文件名
* 在`requirement.txt`中注明需要的依赖包
## industry 行业信息
* 信息来源：http://www.csrc.gov.cn/pub/newsite/scb/ssgshyfljg/
* 分类结果见 `industry.csv`
## influxdb-to-mysql 股票数据迁移
### stock_price.py k线数据
| 字段 | 类型 | 描述 |
| --- | --- | --- |
| companyId | str | 股票代码 |
| time | date | 交易日期，如2020-02-03 |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| close | float | 收盘价 |
| pre_close | float | 昨收价 |
| change | float | 涨跌额 |
| pct_chg | float | 涨跌幅 （未复权） |
| vol | float | 成交量 （手） |
| amount | float | 成交额 （千元） |