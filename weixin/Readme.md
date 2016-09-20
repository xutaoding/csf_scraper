程序描述：
============
    该程序主要是根据arvin提供的一些词从搜狗微信上抓取相应的微信文章， 基于selenium + phantomjs
    
抓取来源：
-----
1：http://weixin.sogou.com/?p=73141200

输入词抓取文章
    
程序分类：
-------
csf_scraper/weixin/wx_phantomjs.py: 主要利用改程序来抓取

    
程序部署：
---------
（1）：程序部署在 192.168.1.56:/opt/scrapyer/weixin

（2）：远程仓库：git@gitlab.chinascope.net:scraper/csf_scraper.git


程序执行：
--------
    使用 screen 相关命令，使程序后台运行：python wx_phantomjs.py
    关于详细的定时抓取，请详看代码
    
    进程查找： screen -ls（名称为weixin即可）
    
    
数据方面：
-------
关键词来源：Mongo 192.168.250.208 news -> news_conp
数据存储位置： Mongo 192.168.100.20 py_crawl -> weixin


    
