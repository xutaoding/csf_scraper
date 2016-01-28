程序描述：
============
    该程序主要是抓取上海交易所网站 和 深圳交易所网站的融资融券数据， 将抓取的数据做处理并存到mongo
    
    
程序分类：

（1）：sha_mt.py：   抓取上交所融资融券数据

（2）：szx_mt.py:    抓取深交所融资融券数据
    
    
程序部署：
---------
（1）：原先的程序部署在 192.168.250.206：/home/xutaoding/csf_scraper/

（2）：远程仓库


程序执行：
--------
    使用 screen 相关命令，使程序后台运行：python margin_trading.py
    关于详细的定时抓取，请详看代码
    
    
数据补抓：
---------
（1）：上交所融资融券数据 即可补抓某一天或几天的数据， 相同数据不会插入Mongo中：

    运行： python sha_mt.py 0000-00-00

（2）：深交所融资融券数据（相同数据不会插入Mongo中）：

    query_date = '0000-00-00'
    SzxMarginTrading(query_date).main()
    运行： python szx_mt.py

    

    
