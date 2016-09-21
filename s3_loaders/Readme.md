说明：
---
将s3上的文件拉倒指定的指定北京亚马逊54.223.46.84服务器

程序部署：
-----
部署位置：54.223.46.84：/opt/scraper/s3_loaders

执行命令：python s3_loaders/jobs.py

进程查找：screen -ls(s3_loaders即是)

远程仓储：git@gitlab.chinascope.net:scraper/csf_scraper.git 下s3_loaders包

    http://gitlab.chinascope.net/scraper/csf_scraper/tree/master/s3_loaders


备注：
---
若从s3拉取文件， 改程序可共用， 如需要改变相关配置即可