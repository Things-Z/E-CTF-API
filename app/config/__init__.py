'''
-------------------------------------------------
    File name:    __init__.py
    Description:    config配置文件
    Author:     RGDZ
    Data:    2020/01/16 20:54:35
-------------------------------------------------
   Version:    v1.0
   Contact:    rgdz.gzu@qq.com
   License:    (C)Copyright 2020-2021
'''
import os

class Config:
    """ 基础配置 """
    DEBUG = True
    
    """ 安全配置 """
    SECRET_KEY = os.urandom(16) # 部署上线时需要修改此处为固定值
    PARTICIPAN_KEY_LENGTH = 4
    USER_TOKEN_EXPIRES = 3600*24 # 客户端token有效期 1天

    """ 数据库配置 """
    # mongodb
    MONGO_DB = 'E-CTF'
    MONGO_SERVER_HOST = 'localhost'
    MONGO_SERVER_PORT = 27017
    MONGO_SERVER_PASSWORD = ''

    MONGODB_SETTINGS = {
        'db': MONGO_DB,
        'host': MONGO_SERVER_HOST,
        # 'password': MONGO_SERVER_PASSWORD,
        'port': MONGO_SERVER_PORT
    }