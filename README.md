# 基于Flask框架搭建E-CTF-API


## 依赖
* MongoDB
* python3
* gunicorn

## 使用方法:
```shell
root:/E-CTF-API/$> pip3 install -r requirements.txt
root:/E-CTF-API/$> gunicorn --config=config.py run:app
```