# -*- coding:utf-8 -*-

from ConfigParser import ConfigParser
import codecs

config = ConfigParser()
config.readfp(codecs.open(r'config.cfg', 'r', 'utf8'))
skill = config.get('Skill', 'skill', 0)
city = config.get('City', 'city')
district = config.get('District', 'district', 0)
bizArea = config.get('BizArea', 'bizArea', 0)
gj = config.get('Experience', 'gj', 0)
xl = config.get('Degree', 'xl', 0)
jd = config.get('Staged', 'jd', 0)
hy = config.get('Field', 'hy', 0)
yx = config.get('Salary', 'yx', 0)
gx = config.get('Type', 'gx', 0)


