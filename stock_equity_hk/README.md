程序描述：
============
    该程序主要是抓取港股股本数据， 每日更新， 将抓取的数据做处理并存到mongo
    
    
程序分类：

stock_equity.py：   抓取港股股本数据

    
    
程序部署：
---------
（1）：原先的程序部署在 192.168.250.206：/home/xutaoding/csf_scraper/

（2）：远程仓库： git@gitlab.chinascope.net:scraper/csf_scraper.git


程序执行：
--------
    使用 screen 相关命令，使程序后台运行：python stock_equity.py
    关于详细的定时抓取，请详看代码
    
    
数据补抓：
---------
（1）：更新港股股本数据， 并插入Mongo中：

    运行： python stock_equity.py 00000
    
（2）：向配置文件里增加港股上市公司代码（必须是5位数）-> config_stock_equity.txt

    

    
