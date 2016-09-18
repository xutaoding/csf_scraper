程序描述：
============
    该程序主要是抓取东方财富网站的A股研报和港股研报， 将抓取的数据做处理并存到mongo
    
抓取来源
----
http://data.eastmoney.com/report/
    
    
程序分类：

（1）：er_update.py：   抓取A股研报数据

（2）：hk_update.py:    抓取港股研报数据
    
程序部署：
---------
（1）：原先的程序部署在 192.168.250.206：/home/xutaoding/csf_scraper/

（2）：远程仓库：git@gitlab.chinascope.net:scraper/csf_scraper.git


程序执行：
--------
    使用 screen 相关命令，使程序后台运行：
    (1): python execute.py
    (1): python hk_update.py
    关于详细的定时抓取，请详看代码
    
    
数据补抓：
---------
（1）：A股研报, 即可补抓某一天或几天的数据， 相同数据不会插入Mongo中：

    query_date = ['0000-00-00', '0000-00-00']
    
    ErUpdate().main(query_date)
    
    运行： python er_update.py

（2）：港股研报（相同数据不会插入Mongo中）：

    query_date = ['0000-00-00', '0000-00-00']
    
    ErUpdate().spider(query_date)
    
    运行： python hk_update.py
    

    
