# -*- coding: UTF-8 -*-
import query_string


def data_by_table_type(query, keys, typ):
    # Note `keys` parameter must is a tuple or list:
    # (1): keys include one ot more value that also a tuple or list.
    # (2): if len(keys) == 1, this function return a value, otherwise return more values.
    coll_assert = typ == 'stock' or typ == 'exec' or typ == 'vary' or typ == 'curr'
    assert coll_assert, '`typ` must one of all collection type including `stock`, `exec`, `vary`'

    rets = []
    length_keys = len(keys)
    collection = getattr(query_string, '_'.join(('coll', typ)))
    result = collection.get(query)
    try:
        # result will return one or more values to `keys`
        for field_key in keys:
            value = result
            for key in field_key:
                value = value[key.strip()]
            rets.append(value)
        return rets[0] if length_keys == 1 else rets
    except (KeyError, TypeError, AttributeError):
        pass
    return '' if length_keys == 1 else [''] * len(keys)


def ratio(changes, secu, typ_stock, typ_vary):
    """
    typ_stock: is coll_stock
    typ_vary: is coll_vary
    """
    assert typ_stock == 'stock' or typ_vary == 'vary', '`typ_stock` or `typ_vary` is not unexpected.'

    coll_stock = getattr(query_string, '_'.join(('coll', typ_stock)))
    coll_vary = getattr(query_string, '_'.join(('coll', typ_vary)))

    change = abs(int(changes.strip()))
    org_dict = coll_stock.get({'code': secu}, {'org': 1})
    org_id = org_dict.get('org', {}).get('id')
    if org_id is None:
        return '0.0', '0.0'

    field_keys = {'vdt': 1, 'share': 1, 'total': 1}
    result = coll_vary.get({'org.id': org_id}, field_keys, spec_sort=('vdt', -1))

    total = result.get('total')
    total_ratio = '%.5f' % round((change / float(total)) * 100, 5) if total else '0.00000'
    amt_128 = [d['amt'] for d in result.get('share', {}) if d.get('typ') == '128']
    circulation_ratio = '%.5f' % round((change / float(amt_128[0])) * 100, 5) if amt_128 else '0.00000'
    return total_ratio, circulation_ratio


if __name__ == '__main__':
    pass
