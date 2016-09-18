程序描述：
============
    该程序主要是抓取上海交易所网站 和 深圳交易所网站的高管增减持数据， 将抓取的数据做处理并存到mongo
    
抓取来源：
-----
1：http://www.szse.cn/main/disclosure/jgxxgk/djggfbd/

2：http://www.sse.com.cn/disclosure/credibility/change/
    
程序分类：

（1）：sha_executives.py：   抓取上交所高管增减持数据

（2）：szx_executives.py:    抓取深交所高管增减持数据
    
程序部署：
---------
（1）：原先的程序部署在 192.168.250.206：/home/xutaoding/csf_scraper/

（2）：远程仓库：git@gitlab.chinascope.net:scraper/csf_scraper.git


程序执行：
--------
    使用 screen 相关命令，使程序后台运行：python spider.py
    关于详细的定时抓取，请详看代码
    
    
数据补抓：
---------
（1）：上交所高管增减持数据 即可补抓某一天或几天的数据， 相同数据不会插入Mongo中：

    更新当天： python sha_executives.py
    更新历史： python sha_executives.py 0000-00-00 0000-00-00

（2）：深交所高管增减持数据（相同数据不会插入Mongo中）：

    start = '0000-00-00'
    end = '0000-00-00'
    SzxExecutives(start, end).main()
    运行： python szx_executives.py

    

    
