程序描述：
============
    该程序主要是抓取上海交易所和深圳交易所的大宗加以数据， 将抓取的数据做处理并存到mongo
    
    
程序分类：

（1）：sha_block.py：   抓取上海交易所的融资融券数据

（2）：secu_bond.py:    抓取省政交易所融资融券中债券数据

（3）：szse_security.py:   抓取省政交易所融资融券中股票和基金数据    
    
程序部署：
---------
（1）：原先的程序部署在 192.168.250.206：/home/xutaoding/csf_scraper/

（2）：远程仓库：git@gitlab.chinascope.net:scraper/csf_scraper.git


程序执行：
--------
    使用 screen 相关命令，使程序后台运行：python block_trade.py
    关于详细的定时抓取，请详看代码
    
    
数据补抓：
---------
（1）：上交所：python sha_block.py 0000-00-00, 即可补抓某一天的数据， 相同数据不会插入Mongo中

（2）：深交所：

    （a）: 债券：重新设定 SzxBond 类的_crawl_pages属性： python secu_bond.py, 相同数据不会插入Mongo中
    
    （a）: 股票与基金：重新设定 SzxSecurity 类的_crawl_pages属性： python szse_security.py, 相同数据不会插入Mongo中

    
