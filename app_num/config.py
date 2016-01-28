# -*- coding: utf-8 -*-

CONFIG = {
    'baidu':
        {
            'url': 'http://shouji.baidu.com/soft/item?docid=7473420&from=as&f=item%40app%40otherid%401',
            'conf': {'type': 1, 'selector': '.download-num'}
        },

    'hiapk':
        {
            'url': 'http://apk.hiapk.com/appinfo/com.csf.samradar',
            'conf': {'type': 2, 'selector': 'span[class="font14"]', 'eq': 1, 'platform': 'hiapk'}
        },

    'apk_360':
        {
            'url': 'http://zhushou.360.cn/detail/index/soft_id/2186624?recrefer=SE_D_%E6%99%BA%E6%8A%95',
            'conf': {'type': 7, 'selector': '.s-3', 'eq': 0}
        },

    'wandoujia':
        {
            'url': 'http://www.wandoujia.com/apps/com.csf.samradar',
            'conf': {'type': 9, 'selector': 'span[class="item"]'}
        },

    'huawei':
        {
            'url': 'http://appstore.huawei.com/app/C10196295',
            'conf': {'type': 10, 'selector': 'span[class="grey sub"]'}
        },

    'app_91':
        {
            'url': 'http://apk.91.com/Soft/Android/com.csf.samradar-15.html',
            'conf': {'type': 3, 'selector': '.s_info li', 'eq': 1}
        },

    'app_qq':
        {
            'url': 'http://android.myapp.com/myapp/detail.htm?apkName=com.csf.samradar',
            'conf': {'type': 4, 'selector': '.det-ins-num'}
        },
}

