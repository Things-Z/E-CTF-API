# E-CTF-API

## 基于Flask框架搭建E-CTF-API
项目实例: [E-CTF](http://39.106.85.139/index)

配合[E-CTF-VUE](https://github.com/RGDZ-GZU/E-CTF-VUE.git)使用

## 依赖
* MongoDB
* python3
* gunicorn
* gevent

## 使用方法:
```shell
root:~/$> git clone https://github.com/RGDZ-GZU/E-CTF-API.git
root:~/E-CTF-API/$> pip3 install -r requirements.txt
root:~/E-CTF-API/$> pip3 install gunicorn gevent
root:~/E-CTF-API/$> gunicorn --config=config.py run:app
```