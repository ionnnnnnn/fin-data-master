from sqlalchemy import create_engine

ts_token = '53cd3b985c649c978160c6ec04bce24f4fbd2ebcb4673e8f2fba9a43'

# mysql配置
mysql_host = "116.63.159.1"
mysql_username = "root"
mysql_password = "FinGra2022#"
mysql_host_local = "localhost"
mysql_port = 3306
mysql_username_local = "root"
# mysql_password_local = "FinGra2022#"
mysql_password_local = "123456"
# mysql_port_local = 43306
mysql_port_local = 3306

db = "fincode"
stock_price_table = "stock_price"
stock_detail_table = "stock_detail"
stock_table = "stock"
industry_table = "industry"


def create_stock_engine(mode):
    if mode == "local":
        # mysql
        return create_engine(
            "mysql+pymysql://{}:{}@{}:{}/{}".format(mysql_username_local, mysql_password_local, mysql_host_local,
                                                    mysql_port_local, db))
    elif mode == "remote":
        return create_engine(
            "mysql+pymysql://{}:{}@{}:{}/{}".format(mysql_username, mysql_password, mysql_host, mysql_port, db))
