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


from .models import *



api = Blueprint("api", __name__)


@api.route("/")
def index():
    return jsonify({"msg":"hello"})

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
@api.route("/login", methods=["POST"])
def login():
    ret = {"code":0, "msg":'', "token":''}
    json_data = request.get_json(force=True)
    email = json_data.get('email')
    password = json_data.get('pass')
    user = User.objects(userEmail=email).first()
    if user:
        if user.verify_pass(password):
            ret["code"] = 200
            ret["msg"] = "success"
            ret["token"] = user.token
            return jsonify(ret)
        ret["code"] = 500
        ret["msg"] = "faild"
        return jsonify(ret)
    return jsonify(ret)


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
@api.route("/register", methods=["POST"])
def register():
    ret = {"code":0, "msg":'', "token":''}
    json_data = request.get_json(force=True)
    username = json_data.get('username')
    email = json_data.get('email')
    password = json_data.get('pass')
    if not User.isexist(username, email):
        new_user = User.init(username, email, password)
        ret['code'] = 200
        ret['msg'] = 'success'
        ret['token'] = new_user.token
        return jsonify(ret)
    ret['code'] = 500
    ret['msg'] = 'faild'
    return jsonify(ret)

""" 获取用户信息接口 
    请求参数: ?token=token
    返回数据: 
    {
        'code':200,
        'msg':'success',
        'user':{
            'role': 1/admin, 0/user
            'name':username,
            'scoreData':scoreData,
            'score':score

        }
    }
"""
@api.route("/userInfo", methods=["GET"])
def userInfo():
    ret = {'code':0, 'msg':'', 'user':{}}
    token = request.args.get('token')
    user = User.verify_auth_token(token)
    ret['code'] = 400
    ret['msg'] = 'not login.'
    if user:
        ret['code'] = 200
        ret['msg'] = 'success'
        ret['user'] = {
            'role': user.role,
            'userName':user.userName,
            'scoreData':user.scoreData,
            'solvedCount':len(user.solveds),
            'score':user.score
        }
    return jsonify(ret)

""" 获取challenges数据接口 
    请求参数:
    ?ctype=Pwn&token=token （可选）
    返回数据:
    {
        "code":200,
        "msg":"success",
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
@api.route("/challenges", methods=["GET"])
def challenges():
    ret = {"code":0, "msg":'', 'challenges':[]}
    ctype = request.args.get('ctype')
    token = request.args.get('token')
    user = User.verify_auth_token(token)
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
        ret['challenges'].append(data)
    ret['code'] = 200
    ret['msg'] = 'success'
    return jsonify(ret)
        

""" 提交flag接口 
    请求数据:
    ?token=token&cid=cid&flag=flag
    返回数据:
    {
        "code":200,
        "msg":'success',
        "result":True/False
    }
"""
@api.route("/submit_flag", methods=['GET'])
def submit_flag():
    ret = {'code':0, 'msg':'', 'result':False}
    token = request.args.get('token')
    cid = request.args.get('cid')
    flag = request.args.get('flag')
    user = User.verify_auth_token(token)
    ret['result'] = False
    ret['code'] = 400
    ret['msg'] = 'not login.'
    if user:
        challenge = Challenge.objects(pk=cid).first()
        ret['result'] = False
        ret['msg'] = 'faild'
        ret['code'] = 300
        if challenge not in user.solveds:
            ret['code'] = 202
            if challenge.verify_flag(flag):
                user.solved_challenge(challenge)
                ret['result'] = True
                ret['code'] = 200
                ret['msg'] = 'success'
    return jsonify(ret)
    
    
""" 添加题目接口 
    请求数据:
    {
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
@api.route('/add_challenge', methods=['POST'])
def add_challenge():
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

""" 删除题目接口 
    请求参数:
    ?cid=cid

"""
@api.route('/del_challenge', methods=['GET'])
def del_challenge():
    ret = {'code':0, 'msg':''}
    cid = request.args.get('cid')
    Challenge.objects(id=cid).first().delete()
    Challenge.objects(id=cid).delete()
    ret['code'] = 200
    ret['msg'] = 'success'
    return jsonify(ret)

""" 获取公告信息接口 
    请求参数: /
    返回数据: 
    {
        'code':200,
        'msg':'success',
        'data':[]
    }
"""
@api.route('/announcements', methods=['GET'])
def announcements():
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
@api.route('/add_announcement', methods=['POST'])
def add_announcement():
    ret = {'code':0, 'msg':''}
    json_data = request.get_json(force=True)
    title = json_data['title']
    body = json_data['body']
    Announcement.init(title, body)
    ret['code'] = 200
    ret['msg'] = 'success'
    return jsonify(ret)

""" 删除公告接口 
    请求参数: ?aid=aid
    返回数据:
    {
        'code':200,
        'msg':'success'
    }
"""
@api.route('/del_announcement', methods=['GET'])
def del_announcement():
    ret = {'code':0, 'msg':''}
    aid = request.args.get('aid')
    Announcement.objects(pk=aid).delete()
    ret['code'] = 200
    ret['msg'] = 'success'
    return jsonify(ret)

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
@api.route('/score_card', methods=["GET"])
def score_card():
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