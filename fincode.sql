drop database if exists `fincode`;
create database `fincode`;
use `fincode`;
drop table if exists `stock_detail`;
drop table if exists `stock`;
drop table if exists `industry`;
create table industry
(
    id           int                                  not null
        primary key,
    name         varchar(255)                         null,
    is_deleted   tinyint(1) default 0                 null,
    gmt_created  datetime   default CURRENT_TIMESTAMP null,
    gmt_modified datetime   default CURRENT_TIMESTAMP null
);

create table stock
(
    id           int unsigned auto_increment
        primary key,
    name         varchar(32)                          null,
    ts_code      varchar(32)                          null,
    industry_id  int                                  null,
    is_deleted   tinyint(1) default 0                 null,
    gmt_created  datetime   default CURRENT_TIMESTAMP null,
    gmt_modified datetime   default CURRENT_TIMESTAMP null,
    constraint stock_industry_id_fk
        foreign key (industry_id) references industry (id)
);

create table stock_detail
(
    id           int auto_increment
        primary key,
    stock_id     int unsigned                         null,
    name         varchar(32)                          null,
    enname       varchar(255)                         null,
    ts_code      varchar(32)                          null,
    list_date    varchar(32)                          null,
    area         varchar(32)                          null,
    industry_id  int                                  null,
    is_deleted   tinyint(1) default 0                 null,
    gmt_created  datetime   default CURRENT_TIMESTAMP null,
    gmt_modified datetime   default CURRENT_TIMESTAMP null,
    ext_info     text                                 null,
    constraint stock_detail_stock_fk
        foreign key (stock_id) references stock (id)
);
drop table if exists `stock_price`;
create table stock_price
(
    id        bigint auto_increment
        primary key,
    amount    double      null,
    `change`  double      null,
    close     double      null,
    high      double      null,
    low       double      null,
    open      double      null,
    companyId varchar(32) null,
    pct_chg   double      null,
    pre_close double      null,
    vol       double      null,
    time      int         null
);
