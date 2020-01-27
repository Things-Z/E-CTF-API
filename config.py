'''
-------------------------------------------------
    File name:    config.py
    Description:    gunicorn启动配置文件
    Author:     RGDZ
    Data:    2020/01/27 20:00:57
-------------------------------------------------
   Version:    
   Contact:    rgdz.gzu@qq.com
   License:    (C)Copyright 2020-2021
'''

bind = "0.0.0.0:8080"
timeout = 10
workers = 4
threads = 2