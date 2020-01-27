'''
-------------------------------------------------
    File name:    run.py
    Description:    启动flask
    Author:     RGDZ
    Data:    2020/01/17 12:39:33
-------------------------------------------------
   Version:    v1.0
   Contact:    rgdz.gzu@qq.com
   License:    (C)Copyright 2020-2021
'''

from app import app

if __name__ == "__main__":
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run()