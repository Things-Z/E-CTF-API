'''
-------------------------------------------------
    File name:    __init__.py
    Description:    数据模型文件
    Author:     RGDZ
    Data:    2020/01/16 20:55:09
-------------------------------------------------
   Version:    v1.0
   Contact:    rgdz.gzu@qq.com
   License:    (C)Copyright 2020-2021
'''
import PIL
import time
import datetime
from hashlib import md5

from flask_mongoengine import MongoEngine, mongoengine
from itsdangerous import SignatureExpired, BadSignature
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from ..config import Config

db = MongoEngine()

cTypes = ['Android', 'Crypto', 'Misc', 'Pwn', 'Reverse', 'Web']

# class User(db.Document):
#     pass


class Challenge(db.Document):
    """ 题目数据模型 """
    tIdx = db.IntField(required=True)
    title = db.StringField(required=True)
    description = db.StringField(required=True)
    score = db.IntField(required=True)
    flag = db.StringField(required=True)
    createTime = db.IntField(required=True)

    # 解题人数
    solvers = db.ListField(default=[])

    @staticmethod
    def init(tIdx, title, des, score, flag):
        new_challenge = Challenge(tIdx=tIdx, 
                                title=title, 
                                description=des, 
                                score=score, 
                                flag=flag,
                                createTime=int(time.time()))
        new_challenge.save()

    @property
    def ctype(self):
        return cTypes[self.tIdx]


    def verify_flag(self, flag):
        if self.flag == flag:
            return True
        return False

    def delete(self):
        for uid in self.solvers:
            user = User.objects(pk=uid).first()
            user.solveds.remove(self)
            user.scoreData[cTypes[self.tIdx]] -= self.score
            user.score -= self.score
            user.save()

class User(db.Document):
    """ 用户数据模型 """
    # 基础数据
    role = db.IntField(required=True, default=0)
    userName = db.StringField(max_length=10, unique=True, required=True)
    userEmail = db.StringField(max_length=30, unique=True, required=True)
    password = db.StringField(max_length=32)
    createTime = db.IntField(required=True)

    # 题目数据
    solveds = db.ListField(db.ReferenceField(Challenge), default=[])
    score = db.IntField(default=0)
    scoreDFS = db.ListField(default={})
    scoreData = db.DictField(default=dict(zip(cTypes, [0 for i in range(len(cTypes))])))
    lastTime = db.IntField(default=0)
    @staticmethod
    def init(username, email, password):
        new_user = User(userName=username, 
                        userEmail=email, 
                        password=User.encrypt(password),
                        createTime=int(time.time()),
                        lastTime=int(time.time()),
                        scoreDFS=[[int(time.time())*1000, 0]]
                        )
        new_user.save()
        return new_user
    
    @staticmethod
    def encrypt(str):
        return md5(str.encode("utf-8")).hexdigest()

    def verify_pass(self, password):
        if self.password == User.encrypt(password):
            return True
        return False

    @property
    def solvedStatic(self):
        data = dict(zip(cTypes, [{'solveds':0,'total':0} for i in range(len(cTypes))]))
        for challenge in Challenge.objects().all():
            data[cTypes[challenge.tIdx]]['total'] +=1
            if str(self.id) in challenge.solvers:
                data[cTypes[challenge.tIdx]]['solveds'] += 1
        return data

    @property
    def isAdmin(self):
        if self.role == 1:
            return True
        return False

    @property
    def token(self):
        """ 生成TOKEN
            ret: token, expiration
        """
        s = Serializer(Config.SECRET_KEY, expires_in=Config.USER_TOKEN_EXPIRES)
        token = s.dumps({'id':str(self.id)}).decode('utf-8')
        return token

    @staticmethod
    def verify_auth_token(token):
        """ 验证token
        token: 需要验证的token
        ret: _token 验证通过的token or False
        """
        s = Serializer(Config.SECRET_KEY)
        try:
            _token = s.loads(token)
            user = User.objects(pk=_token['id']).first()
        except:
            return None    # valid token,but expired
        return user

    @staticmethod
    def isexist(username=None, email=None):
        if User.objects(userName=username).first():
            return True
        if User.objects(userEmail=email).first():
            return True
        return False

    def solved_challenge(self, chanllenge):
        self.solveds.append(chanllenge)
        self.scoreData[cTypes[chanllenge.tIdx]] += chanllenge.score
        self.score += chanllenge.score
        chanllenge.solvers.append(str(self.id))
        self.lastTime = int(time.time())*1000
        self.scoreDFS.append([self.lastTime, self.score])
        self.save()
        chanllenge.save()

    @staticmethod
    def static():
        data = []
        rank = 1
        for user in User.objects().order_by('-score'):
            data.append({
                'uid' : str(user.id),
                'rank': rank,
                'name': user.userName,
                'solved': len(user.solveds),
                'score': user.score,
                'lastTime':user.lastTime
            })
            rank+=1
        # 排名临时解决 TODO:优化排名算法
        for i in range(len(data)):
            for j in range(i+1, len(data)):
                if data[i]['score'] == data[j]['score']:
                    if data[i]['lastTime'] > data[j]['lastTime']:
                        data[i]['rank'], data[j]['rank'] = data[j]['rank'], data[i]['rank']
                        data[i], data[j] = data[j], data[i]
        return data

class Announcement(db.Document):
    """ 公告数据 """
    title = db.StringField(max_length=20,required=True)
    body = db.StringField(required=True)
    createTime = db.IntField(required=True)

    @staticmethod
    def init(title, body):
        new_ann = Announcement(title=title, body=body, createTime=int(time.time()))
        new_ann.save()

    @property
    def date(self):
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(self.createTime))