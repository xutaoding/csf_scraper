#!/usr/bin/env python
# -*- coding: utf-8 -*-


def secu_code(code, coll_stock, coll_fund):
    secu_stock = coll_stock.get({'tick': code})
    if secu_stock:
        return secu_stock['code']

    secu_fund = coll_fund.get({'tick': code})
    if secu_fund:
        return secu_fund['code']


def sha_seba(_secu_cd, se_ma, trade_date, sql_db):
    # 上海所 融券余额
    sql = 'select close_price from equity_price where secu_code=%s and trade_date<=%s ' \
          'order by trade_date DESC limit 1'
    price = sql_db.get(sql, *(_secu_cd, trade_date))
    if price:
        return float(price[0]) * float(se_ma)


def szx_fiba_bre(secu_cd, coll_in, date_dt):
    # 深圳证券交易所 前一日或更前一日融资余额
    query = {'secu': secu_cd, 'date': {'$lt': date_dt}}
    for doc in coll_in.query(query).sort([('date', -1)]).limit(10):
        try:
            return float(doc['fi']['ba'].strip())
        except Exception:
            pass
    return 0.0


def szx_sema_bre(secu_cd, coll_in, date_dt):
    # 深圳证券交易所 前一日或更前一日融券余量
    query = {'secu': secu_cd, 'date': {'$lt': date_dt}}
    for doc in coll_in.query(query).sort([('date', -1)]).limit(10):
        try:
            # print doc['se']['ma']
            return float(doc['se']['ma'].strip())
        except:
            return 0
    return 0.0
