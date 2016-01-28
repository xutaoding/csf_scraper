程序描述：
============
    该程序主要是抓取智投APP的下载量， 主要从现有的下载平台：
    百度手机助手，安卓市场，360手机助手， 豌豆荚， 华为应用， 91手机助手， 腾讯宝， 掌上应用汇， 小米， 机锋市场
    
    
程序部署：
---------
（1）：目前程序部署在Amazon beijing 54.223.52.50: /opt/scraper/autumn/crawler/

（2）：原先的程序部署在 192.168.250.206：/home/xutaoding/autumn/crawler/

（3）： 远程仓库：git@gitlab.chinascope.net:scraper/csf_scraper.git
    

程序执行：
--------
    使用 screen 相关命令，使程序后台运行：python mobile_app.py
    关于详细的定时抓取，请详看代码

    
