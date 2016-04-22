# -*- coding: utf-8 -*-

import query_string
from datetime import datetime


def secu_currency(code, typ_stock=None, typ_fund=None, typ_bond=None):
    code = code.strip()

    if typ_stock and typ_fund and typ_bond is None:
        coll_stock = getattr(query_string, '_'.join(('coll', typ_stock)))
        coll_fund = getattr(query_string, '_'.join(('coll', typ_fund)))
        secu_stock, secu_fund = coll_stock.get({'tick': code}), coll_fund.get({'tick': code})
        if secu_stock:
            secu = secu_stock['code']
            return (secu, 'HKD') if secu_stock['mkt']['code'] == '1055' else (secu, 'CNY')

        if secu_fund:
            return secu_fund['code'], 'CNY'

    if typ_bond and typ_stock is None and typ_fund is None:
        coll_bond = getattr(query_string, '_'.join(('coll', typ_bond)))
        try:
            return coll_bond.get({'tick': code})['code'], 'CNY'
        except(KeyError, AttributeError, TypeError, IndexError):
            pass
    return code, 'CNY'


def close_price(secu, trade_date, typ):
    # mysql = getattr(query_string, typ)
    from eggs.db.mysql_client import MySQLClient
    mysql = MySQLClient("192.168.251.95", "python_team", "python_team", "ada-fd")
    sql = "SELECT close_price from equity_price where secu_code=%s and trade_date <=%s" \
          "order by trade_date DESC limit 1"
    if secu:
        price = mysql.get(sql, *(secu, trade_date))
        if price:
            return price[0]


def total_equity(code, query_date, typ_vary, typ_stock):
    coll_vary = getattr(query_string, '_'.join(('coll', typ_vary)))
    coll_stock = getattr(query_string, '_'.join(('coll', typ_stock)))
    org_id = coll_stock.get({'code': code})
    year, month, day = [int(ymd) for ymd in query_date.split('-')]

    try:
        query = {'org.id': org_id['org']['id'], 'vdt': {'$lte': datetime(year, month, day)}}
        total = coll_vary.get(query, spec_sort=('vdt', -1))
        return float(total['total'])
    except (IndexError, KeyError, AttributeError, TypeError):
        pass
