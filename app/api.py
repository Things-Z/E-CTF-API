'''
-------------------------------------------------
    File name:    api.py
    Description:    api接口
    Author:     RGDZ
    Data:    2020/01/17 12:35:26
-------------------------------------------------
   Version:    v1.0
   Contact:    rgdz.gzu@qq.com
   License:    (C)Copyright 2020-2021
'''

from flask import Blueprint, request, jsonify
from functools import wraps

from .models import *



api = Blueprint("api", __name__)

class Code:
    """ 后台状态枚举类 """
    NULL = 0 # 什么都没有
    ERROR = 100 # 执行错误
    SUCCESS = 200 #成功
    NOT_ADMIN = 300 # 非管理员
    NOT_LOGIND = 400 #未登录
    TOKEN_LOSE = 500 #Token 失效
    FLAG_ERROR = 600 # flag 错误
    FLAG_EXISTED = 700 # flag 已提交

# 接口权限控制装饰器
def require_login(func):
    """ 登录控制 """
    @wraps(func)
    def wrapper(*args, **kw):
        ret={'code':Code.NOT_LOGIND}
        token = request.get_json(force=True).get('token')
        if token:
            user = User.verify_auth_token(token)
            if user:
                ret['code'] = Code.SUCCESS
                return func(user=user, ret=ret)
            ret:['code'] = Code.TOKEN_LOSE
        return func(user=None, ret=ret)
    return wrapper

def admin(func):
    """ 管理员权限控制 """
    @wraps(func)
    def wrapper(user: User, ret: {}):
        if user:
            if user.isAdmin:
                ret['code'] = Code.SUCCESS
                return func(user, ret)
            ret['code'] = Code.NOT_ADMIN
        return jsonify(ret)
    return wrapper


# API接口

@api.route("/")
def index():
    return jsonify({"msg":"hello"})


@api.route("/login", methods=["POST"])
def login():
    """ 登录接口
        请求数据:
        {
            "email":email,
            "pass":pass
        }
        返回数据:
        {
            "code":200,
            "msg":"success",
            "token":token
        }
    """
    ret = {"code":Code.NULL, "token":''}
    json_data = request.get_json(force=True)
    email = json_data.get('email')
    password = json_data.get('pass')
    user = User.objects(userEmail=email).first()
    if user:
        if user.verify_pass(password):
            ret["code"] = Code.SUCCESS
            ret["token"] = user.token
            return jsonify(ret)
        ret["code"] = Code.ERROR
        return jsonify(ret)
    return jsonify(ret)



@api.route("/register", methods=["POST"])
def register():
    """ 注册接口
        请求数据:
        {
            "username": username,
            "email": email,
            "pass": password
        }
        返回数据:
        {
            "code":200
            "token":token
        }
    """
    ret = {"code":Code.NULL, "token":''}
    json_data = request.get_json(force=True)
    username = json_data.get('username')
    email = json_data.get('email')
    password = json_data.get('pass')
    if not User.isexist(username, email):
        new_user = User.init(username, email, password)
        ret['code'] = Code.SUCCESS
        ret['token'] = new_user.token
        return jsonify(ret)
    ret['code'] = Code.ERROR
    return jsonify(ret)


@api.route("/userInfo", methods=["GET"])
@require_login
def userInfo(user: User, ret: {}):
    """ 获取用户信息接口 
        请求数据: 
        {
            'token':token
        }
        返回数据: 
        {
            'code':200,
            'user':{
                'role': 1/admin, 0/user
                'name':username,
                'scoreData':scoreData,
                'score':score

            }
        }
    """
    if user:
        ret.update({
        'user':{
            'role': user.role,
            'userName':user.userName,
            'scoreData':user.scoreData,
            'solvedCount':len(user.solveds),
            'score':user.score
        }
    })
    return jsonify(ret)


@api.route("/challenges", methods=["GET"])
@require_login
def challenges(user: User, ret: {}):
    """ 获取challenges数据接口 
        请求数据:
        {
            'ctype':'Pwn',
            'toke':'token' （可选）
        }
        返回数据:
        {
            "code":200,
            "challenges":[
                {
                    'cid':cid,
                    'type':type,
                    'title':title,
                    'des':des,
                    'socre':score,
                    'solved':solved (根据token)
                },
                ...
            ]
        }
    """
    ctype = request.get_json(force=True).get('ctype')
    challenges = Challenge.objects(tIdx=cTypes.index(ctype)).order_by("-createTime")
    for challenge in challenges:
        data = {
            'cid':str(challenge.id),
            'type':challenge.ctype,
            'title':challenge.title,
            'des': challenge.description,
            'score': challenge.score,
            'solved': False
            }
        if user:
            data.update({'solved':challenge in user.solveds})
        ret.update({
            'challenges':data
        })
    return jsonify(ret)
        


@api.route("/submit_flag", methods=['GET'])
@require_login
def submit_flag(user: User, ret: {}):
    """ 提交flag接口 
        请求数据:
        {
            'token':token,
            'cid':cid,
            'flag':flag
        }
        返回数据:
        {
            "code":200,
        }
    """
    json_data = request.get_json(force=True)
    cid = json_data.get('cid')
    flag = json_data.get('flag')
    if user:
        challenge = Challenge.objects(pk=cid).first()
        ret['code'] = Code.FLAG_EXISTED
        if challenge not in user.solveds:
            ret['code'] = Code.FLAG_ERROR
            if challenge.verify_flag(flag):
                user.solved_challenge(challenge)
                ret['code'] = Code.SUCCESS
    return jsonify(ret)
    
    

@api.route('/add_challenge', methods=['POST'])
@require_login
@admin
def add_challenge(admin: User, ret: {}):
    """ 添加题目接口 
        请求数据:
        {
            'token':token
            'type':type,
            'title':title,
            'des':des,
            'score':score,
            'flag':flag
        }
        返回数据:
        {
            "code":200,
            "msg":'success',
        }
    """
    ret = {'code':0, 'msg':''}
    json_data = request.get_json(force=True)
    tIdx = cTypes.index(json_data.get('type'))
    title = json_data.get('title')
    des = json_data.get('des')
    score = json_data.get('score')
    flag = json_data.get('flag')
    Challenge.init(tIdx, title, des, score, flag)
    ret['code'] = 200
    ret['msg'] = 'success'
    return jsonify(ret)


@api.route('/del_challenge', methods=['GET'])
@require_login
@admin
def del_challenge():
    """ 删除题目接口 
        请求参数:
        ?cid=cid
    """
    ret = {'code':0, 'msg':''}
    cid = request.args.get('cid')
    Challenge.objects(id=cid).first().delete()
    Challenge.objects(id=cid).delete()
    ret['code'] = 200
    ret['msg'] = 'success'
    return jsonify(ret)


@api.route('/announcements', methods=['GET'])
def announcements():
    """ 获取公告信息接口 
        请求参数: /
        返回数据: 
        {
            'code':200,
            'msg':'success',
            'data':[]
        }
    """
    ret = {
        'code':200,
        'msg':'success',
        'anncs':[]
    }
    for annc in Announcement.objects().order_by("-createTime"):
        ret['anncs'].append({
            'aid':str(annc.id),
            'title':annc.title,
            'body':annc.body,
            'createTime':annc.date
        })
    return jsonify(ret)


@api.route('/add_announcement', methods=['POST'])
@require_login
@admin
def add_announcement():
    """ 添加公告接口 
        请求数据: 
        {
            'title':title,
            'body':body
        }
        返回数据:
        {
            'code':200,
            'msg':'success'
        }
    """
    ret = {'code':0, 'msg':''}
    json_data = request.get_json(force=True)
    title = json_data['title']
    body = json_data['body']
    Announcement.init(title, body)
    ret['code'] = 200
    ret['msg'] = 'success'
    return jsonify(ret)


@api.route('/del_announcement', methods=['GET'])
@require_login
@admin
def del_announcement():
    """ 删除公告接口 
        请求参数: ?aid=aid
        返回数据:
        {
            'code':200,
            'msg':'success'
        }
    """
    ret = {'code':0, 'msg':''}
    aid = request.args.get('aid')
    Announcement.objects(pk=aid).delete()
    ret['code'] = 200
    ret['msg'] = 'success'
    return jsonify(ret)


@api.route('/score_card', methods=["GET"])
def score_card():
    """ 计分板数据接口
        返回数据:
        {
            'code':200,
            'msg':success,
            'data':[
                {
                    'rank': 1,
                    'name': 'aaa',
                    'solved': 5,
                    'score': 900
                },
                ...
            ]
        }
    """
    ret = {'code':0, 'msg':'', 'data':[]}
    rank = 1
    for user in User.objects().order_by('-score'):
        ret['data'].append({
            'rank': rank,
            'name': user.userName,
            'solved': len(user.solveds),
            'score': user.score
        })
        rank+=1
    ret['code'] = 200
    ret['msg'] = 'success'
    return jsonify(ret)