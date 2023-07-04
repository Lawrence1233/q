# coding:utf-8

from jinja2 import Template
from flask import *
import requests
import hashlib
import string
import random
import copy
import hashlib
from datetime import timedelta
import os
import rsa
import copy
import base64
import pickle
import sys
# import cv2
import re
import io
import time
from flask_wtf import FlaskForm, CSRFProtect    
server_start_time=time.time()
def remove_notes(text: str) -> str:
    text = re.sub(r'<!--(?!\[nodelete\]).*-->', '<!--notes-->', text, count=9999, flags=0)
    return text


def rd(n):
    t = ''
    for i in range(n): t += random.choice(string.ascii_lowercase)
    return t





app = Flask(__name__)


app.config["SECRET_KEY"] = rd(2048)
csrf=CSRFProtect(app)



idl = {}


class acc():
    def __init__(self,username,password):
        self.username=username
        self.password=hash(password)
        self.blocked=False#封号（禁止所有功能）
        self.muted=False#禁言
        self.exp=0
        self.lost=False
    def verify(self,password):#验证密码
        return hash(password) == self.password

    def block(self):
        self.blocked=True
    def deblock(self):
        self.blocked=False

    def mute(self):
        self.muted=True
    def demute(self):
        self.muted=False
    def loss(self):
        self.block()
        self.mute()
        self.password=rd(1024)
        self.username=rd(32)
        self.lost=True


account = {'name': ['password', 1]}  # level

new_account={'name':acc('admin',rd(1024)),
             None:acc('guest',rd(1920))}

logged = {}

official={}#认证
"account:name"


hash_salt = rd(1024).encode()

def hash(i):
    global hash_salt
    x = hashlib.sha256(hash_salt)
    x.update(i.encode('utf-8'))
    return x.hexdigest()



# input()
l = {'sample': [
    ['[name]', '[message]', '[time]', '[Undefined]', -1]
]}
last_create = 1

snapshot_list = {str(['null', 'hash']): [0, ['system', '...', '0000-00-00 00:00:00', 'NONE', 'China', 'None']]}
snap_max = 32



temp_lock = {'daklwjlkwa': [999999999999, 1]}
online = {'sample': 0}


notice = {}




u_last_online={}
"user:time(时间戳)"


id_last_online={}
"uid:time(时间戳)"

# 房间名:上一次访问时间戳

restart_time=30*60#n秒后重启


@app.before_request
def b4():
    global counter_,server_start_time,restart_time

    if time.time()-server_start_time>restart_time:
        print('*重启！')
        app.config["SECRET_KEY"] = rd(2048)
        l={}
        server_start_time=time.time()
        return '<meta http-equiv="refresh" content="3;url=/">服务器已重启，三秒后自动返回首页'




    if session.get('id') == None:
        session['id'] = hash(rd(32))
        idl[session['id']] = request.remote_addr

    if session.get('hacker') == True:
        del session['hacker']
        return '温馨提示:你最近的操作可能有恶意行为，请友善使用该网站。'
    for i in notice.items():
        if session.get(i[0]) == None:
            session[i[0]] = '1'
            return """
            <!Doctype html>
            <center>
            <h1>%s</h1>
            <h2><pre>%s</pre></h2>
            <i><small>如要访问正常功能，请刷新。</small></i>
            </center>
            """ % (i[1][0], i[1][1])

    if session.get('logged-in') == None:
        session['logged-in'] = False

    if session.get('logged-in') == True:
        if session.get('username') not in new_account:
            u = session.get('username')
            # session.clear()
            del session['key']
            del session['username']
            del session['logged-in']
            return '系统提示：你登录的账号"%s"已被管理员删除，登录状态已失效'%u
        if logged[session.get('username')] != session.get('key'):  # 登录失效
            u = session.get('username')
            del session['key']
            del session['username']
            del session['logged-in']
            return '紧急警告：账号"%s"已在其他设备登录，登录状态已失效' % u

    u_last_online[session.get('username')]=time.time()
    id_last_online[session.get('id')]=time.time()





    session['last_time'] = time.time()

    # if 'creator' in request.full_path:
    #     time.sleep(0.5)
    #
    # if 'snapshot' in request.full_path:
    #     time.sleep(0.5)
    #
    if 'CAPTCHA' in request.full_path:
        time.sleep(0.1)



"""
request.remote_addr,
                 request.headers,
                 time.time(),
                 time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                 request.full_path,
                 request.url,
                 request.form,
                 request.headers['User-Agent']"""

lock_account_list=[]#被锁定账号
lock_account_uidlist=[]#锁定登入在被锁定账户上的uid

roomkey={}


joinedid={}
"room:{id:time}"

verify_room={}
"room:uid"


verify_list={}
"room:[凭据,...]"
"凭据保存在session里"

creater={}
'room:creater'




firewall=[]
"room"



in_danger=[]#出现安全威胁的房间
"room"

counter_=0
@app.route('/')
def index():
    global  server_start_time

    username = session.get('username')
    
    if username == None:
        username = '陌生人'
    warning=False


    return remove_notes(
        render_template('index.html', time_=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), username=username,
                        logged=session.get('logged-in'),warning=warning,uid=session.get('id'),restart=int(server_start_time+restart_time-time.time())))


@app.route('/create-new-room')
def logon():
    # if session.get('username') in lock_account_list or session.get('id') in lock_account_uidlist:
    #     return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>',403

    if new_account[session.get('username')].blocked or session.get('username') in lock_account_list:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>', 403

    if new_account[session.get('username')].username=='guest':
        return render_template('403.html',text='处于游客状态时禁止使用此功能，请返回首页登录后重试。')

    return render_template('logon.html',tags='创建房间')

@app.route('/create-new-room/tags/<id>')
def createnewroom_tags(id):
    # if session.get('username') in lock_account_list or session.get('id') in lock_account_uidlist:
    #     return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>',403

    if new_account[session.get('username')].blocked or session.get('username') in lock_account_list:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>', 403

    tags=session.get('cnr_tags')
    if tags==None:
        return '房间不存在'
    if session.get('cnr_tags') != None:
        del session['cnr_tags']
    if session.get('ct_r') != None:
        del session['ct_r']
    return render_template('logon.html',tags=tags,id=id)

burn_after_reading={}#阅后即焚秒数
"room:time"
@app.route('/upload', methods=["POST"])
def upload():

    # if session.get('username') in lock_account_list or session.get('id') in lock_account_uidlist:
    #     return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>',403

    if new_account[session.get('username')].blocked or session.get('username') in lock_account_list:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>', 403

    global last_create,verify_room,l
    if 'python' in request.user_agent.string:
        print('屏蔽了一个爬虫')
        abort(404)

    id = request.form.get('id')

    if len(id) == 32:
        return '房间号长度不能为32位'

    if session.get('captcha_pass') == None:
        p = new_captcha(id, session.get('id'))
        session['q'] = p
        session['ct_r']=id
        return redirect('/CAPTCHA/%s/%s' % (id, p))

    if id not in session.get('captcha_pass'):
        p = new_captcha(id, session.get('id'))
        session['q'] = p
        session['ct_r'] = id
        return redirect('/CAPTCHA/%s/%s' % (id, p))

    if id in l:
        return '房间已存在<a href="/create-new-room">重新注册</a>'

    if request.form.get('verify') == 'on':
        verify_room[id]=session.get('id')
        verify_list[id]=[]

    if request.form.get('allow_snapshots') == 'on':
        allow_snapshots.append(id)

    if request.form.get('firewall') == 'on':
        firewall.append(id)

    last_create = time.time()
    joinedid[id]={}
    creater[id]=session.get('id')


    l[id] = [['un']]

    lock_the_room_(id, 5)

    online[id] = 0
    room_online[id]=0
    burn_after_reading[id]=float('inf')

    return redirect('/room/' + id)


@app.route('/view/room')
def view_room():
    if session.get('r') == None:
        return '你没有加入任何房间，<a href="/">返回首页</a>'
    lst=[]


    for i in session.get('r').items():
        returni=list(i)

        if session.get('use_token') != None:
            if returni[1] in session.get('use_token'):
                returni[1]='[不可用]'
        lst.append(returni)

    return render_template('view-room.html',list=lst)


@app.route('/login', methods=["POST"])
def login():
    id = request.form.get('id')
    if id in l:
        return redirect('/room/' + id)
    else:
        return '房间不存在'

verify_pass=[]
"通过管理员验证 直接存入k"

captcha_list={}
"hash(id+uid):text"

def shuffle_str(s):
    # 将字符串转换成列表
    str_list = list(s)
    # 调用random模块的shuffle函数打乱列表
    random.shuffle(str_list)
    # 将列表转字符串
    return ''.join(str_list)

word_bank=[
    "凝视","注视","扫视","环视","俯视","窥视","巡视","远望","眺望","瞭望","张望","探望","仰望","观察","瞻仰","鸟瞰","视察","欣赏","观赏","浏览",
    "鸟语花香","春暖花开","阳春三月","万物复苏","春风轻拂","春光明媚",
    "头重脚轻","指手画脚","愁眉苦脸","心明眼亮","目瞪口呆","张口结舌","交头接耳","眼疾手快","昂首挺胸","心灵手巧",
    "秋高气爽","五谷丰登","天高云淡","红叶似火","金风送爽","硕果累累"
]

@app.route('/CAPTCHA/reset')
def captcha_reset():
    if session.get('q') == None:
        return '致命错误：服务器没有记录任何与你有关的验证码，此错误出现在客户端。'
    i=session['q']
    room=captcha_list[i][2]
    del session['q']
    del captcha_list[i]
    return redirect('/room/%s'%room)


def new_captcha(id,uid):
    p=hash(id+uid)
    r=random.choice(word_bank)
    w=shuffle_str(r)
    captcha_list[p]=[w,word_bank.index(r),id,uid]
    return p

captcha=True

@app.route('/CAPTCHA/<room>/<id>')
def CAPTCHA(room,id):
    if session.get('q') == None:
        return '致命错误：服务器没有记录任何与你有关的验证码，此错误出现在客户端。<a href=\"/room/%s\">重试</a>'%room
    if session.get('q') != hash(room+session.get('id')):
        return '(异常操作)致命错误：验证码无效，此错误出现在客户端。如果您没有异常操作，请联系管理员。<a href=\"/room/%s\">重试</a>'%room
    return render_template('CAPTCHA.html',word=captcha_list[hash(room+session.get('id'))][0],id=id,room=room,started=captcha)



@app.route('/CAPTCHA/<room>/<id>/verify',methods=['POST'])
def CAPTCHA_verify(room,id):

    if session.get('q') == None:
        return '致命错误：服务器没有记录任何与你有关的验证码，此错误出现在客户端。<a href=\"/room/%s\">重试</a>'%id
    if session.get('q') != hash(room+session.get('id')):
        return '(异常操作)致命错误：验证码无效，此错误出现在客户端。如果您没有异常操作，请联系管理员。<a href=\"/room/%s\">重试</a>'%id

    if session.get('q') != id or id != hash(room+session.get('id')):
        return '致命错误：身份校验失败，请重置验证码后重试<a href=\"/room/%s\">重试</a>'%room


    word=request.form.get('v')
    if captcha:
        if word_bank[captcha_list[id][1]]!=word:
            del session['q']
            del captcha_list[id]#删除
            return '验证码错误，请重试。<a href=\"/create-new-room\">重试</a>'%room

    if session.get('captcha_pass') == None:
        session['captcha_pass']=[]
    session['captcha_pass'].append(captcha_list[id][2])


    if session.get('c-join') == True or captcha_list[id][2] in l:
        del session['c-join']
        return redirect('/room/%s' % captcha_list[id][2])
    else:
        session['cnr_tags']='您的验证已完成，请再重新提交一次表单'
        return redirect('/create-new-room/tags/%s'%session.get('ct_r'))


@app.route('/room/<id>')
def room302(id):
    if new_account[session.get('username')].username == 'guest':
        return render_template('403.html', text='处于游客状态时禁止使用此功能，请返回首页登录后重试。')

    if creater.get(id) != session.get('id'):
        if session.get('captcha_pass') == None:
            p=new_captcha(id,session.get('id'))
            session['q']=p
            session['c-join']=True
            return redirect('/CAPTCHA/%s/%s'%(id,p))

        if id not in session.get('captcha_pass'):
            p=new_captcha(id, session.get('id'))
            session['q'] = p
            session['c-join'] = True
            return redirect('/CAPTCHA/%s/%s'%(id,p))


    if id not in l:
        abort(404)

    if id in verify_room and creater[id] != session.get('id'):


        if session.get('verify') == None or session.get('verify')==[]:
            session['verify']={}
            k=rd(32)
            verify_list[id].append(k)
            session['verify'][id]=k
            return '请等待群聊管理员审核，ID：%s<br/><a href="/room/%s">刷新</a>'%(k,id)

        if session.get('verify')[id] in verify_pass:
            pass#通过验证
        else:
            return '请等待群聊管理员审核，ID：%s<br/><a href="/room/%s">刷新</a>' % (session.get('verify')[id], id)




    r=rd(32)
    roomkey[r]=id
    if session.get('r') == None:
        session['r']={}
    session['r'][r]=id
    return redirect('/room/%s/1' % r)

@app.route('/_reset')
def rs():
    id=session.get('target__')
    if id not in l:
        abort(404)

    r=rd(32)
    roomkey[r]=id
    if session.get('r') == None:
        session['r']={}
    session['r'][r]=id
    del session['target__']

    return redirect('/room/%s/1' % r)

room_online={}
"id:num"


@app.route('/room/<id>/<page>')
def room(id, page):#room main
    global verify_room,server_start_time,restart_time

    if new_account[session.get('username')].username=='guest':
        return render_template('403.html', text='处于游客状态时禁止使用此功能，请返回首页登录后重试。')

    try:
        int(page)
    except:
        abort(404)

    if int(page)<1:
        abort(404)

    if id not in roomkey:
        return '你无权访问此房间1（如果你没有异常操作，请前往：<a href=\"/view/room\">查看已加入的房间</a>）'
    if session.get('r') == None:
        return '你无权访问此房间2'

    if session['r'].get(id) == None:
        return '你无权访问此房间3'



    realname=session['r'].get(id)




    ars=False
    als=False
    if realname in allow_read_snapshots:
        ars=True
    if realname in allow_snapshots:
        als=True

    try:
        page = int(page)
    except:
        return '出错了'

    if session.get('join') == None:
        session['join']=[]

    if realname not in session.get('join'):
        room_online[realname] += 1
        session['join'].append(realname)
        if session.get('logged-in') == False:
            # l[realname].insert(0, ['jn', session.get('id'),False])
            pass
        else:
            if session.get('admin')==True:
                l[realname].insert(0, ['jn',session.get('username'),True])
            else:
                l[realname].insert(0, ['jn', session.get('username'), False])
        # joinedid[realname][session.get('id')]=time.time()#todo:bug

    if realname in session.get('join') and session.get('id') not in joinedid[realname]:
        room_online[realname] += 1
        if session.get('logged-in') == False:
            # l[realname].insert(0, ['jn', session.get('id'),False])
            pass
        else:
            if session.get('admin')==True:
                l[realname].insert(0, ['jn',session.get('username'),True])
            else:
                l[realname].insert(0, ['jn', session.get('username'), False])


    tips = ''
    name = request.values.get('name')
    text = request.values.get('text')
    if id in temp_lock:
        if not time.time() > temp_lock[id][0]:
            try:
                return '该房间已被锁定 %s 秒 持续到 %s 还有 %s 秒自动解除锁定' % (
                    temp_lock[realname][1], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(temp_lock[realname][0])),
                    round(temp_lock[realname][0] - time.time(), 3))
            except:
                return '该房间已被锁定 %s 秒 持续到 %s' % (
                    temp_lock[realname][1], '')

    if name == None:
        name = ''
    if text == None:
        text = ''







    if realname in l:

        for i in range(len(l[realname])-1):
            if len(l[realname][i]) > 3:

                if time.time()-l[realname][i][2]>burn_after_reading[realname]:
                    l[realname]=l[realname][:i]#焚毁信息
                    if len(l[realname])==0:
                        l[realname].append(['un'])
                    break
                    #信息以倒序排列，所以使用:i


        online[realname] = time.time()

        page_l = []
        for i in range(1, len(l[realname]) // 32 + 1):
            page_l.append(i)
        if len(l[realname]) % 32 != 0:
            page_l.append(len(page_l) + 1)
        if page > len(page_l):
            abort(404)

        joinedid[realname][session.get('id')]=time.time()

        jq=[]
        for i in joinedid[realname].items():
            if time.time()-i[1]>10:
                l[realname].insert(0, ['lv', i[0]])#退出
                room_online[realname]-=1
                jq.append(i[0])

        for i in jq:
            del joinedid[realname][i]

        creator=False
        _verify=False
        v_=False
        if session.get('id') == creater[realname]:
            creator = True
        if realname in verify_room:
            v_=True
            if session.get('id')==creater[realname]:
                creator=True
                if len(verify_list[realname])>0:
                    _verify=True

        res_member=False#
        if room in firewall:
            if session.get('use_token') != None:
                if room in session.get('use_token'):
                    res_member=True

        return remove_notes(
            render_template("room.html", id=id, message=l[realname][abs(1 - page) * 32:abs(1 - page) * 32 + 32], name=name,
                            text=text, tips=tips, page_l=page_l, page=page,logged_in=session.get('logged-in'),verify=_verify,creator=creator,v_=v_,online=room_online[realname],
                            als=als,ars=ars,official=official,restart=int(server_start_time+restart_time-time.time()),firewall=(realname in firewall),res_member=res_member))
    else:
        return '房间不存在'


@app.route('/v/<id>')
def ver(id):
    rid=id
    if session.get('r') == None:
        return "你无权查看此页面",403
    id = session.get("r").get(id)
    if creater[id] != session.get('id')  and session.get('admin') != True:
        return "你无权查看此页面",403

    return render_template('verify.html',list=verify_list[id],id=rid)

@app.route('/v/<id>/<uuid>/upload/<state>',methods=["POST"])
def ver_upload(id,state,uuid):
    rid=id
    id = session['r'].get(id)
    if creater[id] != session.get('id')  and session.get('admin') != True:
        return "你无权查看此页面",403

    if state == 'allow':
        verify_pass.append(uuid)
        verify_list[id].remove(uuid)
    elif state=="forbid":
        verify_list[id].remove(uuid)
    else:
        return '无效操作',403

    return redirect('/v/%s'%rid)

@app.route('/creator/chat_record/clear/<id>')
def creator_clear_record(id):
    rid=id
    id = session['r'].get(id)

    if creater[id] != session.get('id')  and session.get('admin') != True:
        abort(403)

    l[id]=[]
    system_say('已清除聊天记录',id)
    return redirect('/room/%s/1'%rid)

@app.route('/creator/allow_snapshot/true/<id>')
def creator_allow_snapshot_true(id):
    rid=id
    id = session['r'].get(id)

    if creater[id] != session.get('id')  and session.get('admin') != True:
        abort(403)

    if id not in allow_snapshots:
        allow_snapshots.append(id)
    system_say('允许拍摄快照', id)
    return redirect('/room/%s/1'%rid)

@app.route('/creator/allow_snapshot/false/<id>')
def creator_allow_snapshot_false(id):
    rid=id
    id = session['r'].get(id)

    if creater[id] != session.get('id')  and session.get('admin') != True:
        abort(403)

    if id in allow_snapshots:
        allow_snapshots.remove(id)
    system_say('禁止拍摄快照', id)
    return redirect('/room/%s/1'%rid)

@app.route('/creator/allow_read_snapshot/true/<id>')
def creator_allow_read_snapshot_true(id):
    rid=id
    id = session['r'].get(id)

    if creater[id] != session.get('id')  and session.get('admin') != True:
        abort(403)

    if id not in allow_read_snapshots:
        allow_read_snapshots.append(id)
    system_say('允许查看快照', id)
    return redirect('/room/%s/1'%rid)

@app.route('/creator/allow_read_snapshot/false/<id>')
def creator_allow_read_snapshot_false(id):
    rid=id
    id = session['r'].get(id)

    if creater[id] != session.get('id')  and session.get('admin') != True:
        abort(403)

    if id in allow_read_snapshots:
        allow_read_snapshots.remove(id)
    system_say('禁止查看快照', id)
    return redirect('/room/%s/1'%rid)

@app.route('/creator/advanced_firewall/on/<id>')
def creator_advanced_firewall_on(id):
    rid=id
    id = session['r'].get(id)

    if creater[id] != session.get('id')  and session.get('admin') != True:
        abort(403)

    if id not in firewall:
        firewall.append(id)
    system_say('高级防火墙已开启', id)
    return redirect('/room/%s/1'%rid)

@app.route('/creator/advanced_firewall/off/<id>')
def creator_advanced_firewall_off(id):
    rid=id
    id = session['r'].get(id)

    if creater[id] != session.get('id')  and session.get('admin') != True:
        abort(403)

    if id in firewall:
        firewall.remove(id)
    system_say_warning('高级防火墙已关闭', id)
    return redirect('/room/%s/1'%rid)




@app.route('/creator/dismiss/<id>')
def creator_dismiss(id):

    id = session['r'].get(id)

    if creater[id] != session.get('id')  and session.get('admin') != True:
        abort(403)
    del l[id]
    return redirect('/create-new-room')

@app.route('/creator/giveup/<id>')
def creator_giveup(id):
    rid=id
    id = session['r'].get(id)

    if creater[id] != session.get('id')  and session.get('admin') != True:
        abort(403)
    creater[id]='NONE'
    system_say('管理员已离职',id)
    return redirect('/room/%s/1'%rid)

def system_say(i,id):
    l[id].insert(0, ['sy',i])
    return

def system_say_warning(i,id):
    l[id].insert(0, ['wn',i])
    return

@app.route('/creator/set-verify-off/<id>')
def creator_set_verify_off(id):
    rid=id
    id = session['r'].get(id)



    if creater[id] != session.get('id')  and session.get('admin') != True:
        abort(403)

    if id not in verify_room:
        system_say('管理员试图关闭入群验证，但操作未成功。',id)

    del verify_room[id]
    system_say('入群验证已关闭',id)
    return redirect('/room/%s/1'%rid)

@app.route('/creator/set-verify-on/<id>')
def creator_set_verify_on(id):
    rid=id
    id = session['r'].get(id)

    if creater[id] != session.get('id')  and session.get('admin') != True:
        abort(403)

    verify_room[id]=session.get('id')
    system_say('入群验证已开启', id)
    return redirect('/room/%s/1'%rid)


@app.route('/creator/burn-after-reading/<id>',methods=["POST"])
def creator_burn_after_reading(id):
    rid=id
    id = session['r'].get(id)

    if creater[id] != session.get('id')  and session.get('admin') != True:
        abort(403)
    try:
        burn_after_reading[id]=float(request.form.get('sec'))
    except:
        burn_after_reading[id]=float('inf')
        return '无效输入，已更改为无穷秒后自毁消息。<a href=\"/room/%s/1\">返回</a>'%rid
    return redirect('/room/%s/1'%rid)


#

@app.route('/creator/panel/<id>')
def creator_panel(id):
    rid=id
    if session.get('r') == None:
        abort(403)
    id = session['r'].get(id)

    if creater[id] != session.get('id') and session.get('admin') != True:
        abort(403)
    # creater[id]='NONE'

    return render_template('panel.html',id=rid)

@app.route('/member/panel/<id>')
def member_panel(id):
    rid=id
    if session.get('r') == None:
        abort(403)
    id = session['r'].get(id)


    if room in firewall:
        if session.get('use_token') != None:
            if room in session.get('use_token'):
                return render_template('403.html',text='您是房间的受限成员，使用这个功能之前，您需要成为普通成员，请使用房间号登录。')

    # creater[id]='NONE'

    return render_template('member_panel.html',id=rid)

@app.route('/quick-sign-up')
def quick_sign_up():
    # if session.get('username') in lock_account_list or session.get('id') in lock_account_uidlist:
    #     return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>',403

    if new_account[session.get('username')].blocked or session.get('username') in lock_account_list:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>', 403

    username = '用户%s' % random.randint(1, 99999999999)
    password = hash(rd(1024))
    # account[username] = [password, 0]
    #test
    new_account[username]=acc(username,password)
    #


    session['logged-in'] = True
    logged[username] = hash(password + str(round(time.time(), 3)))
    session['key'] = logged[username]
    session['username'] = username
    return redirect('/')



@app.route('/tickle', methods=["POST"])
def tickle():



    if session.get('r') == None:
        abort(403)


    if session.get('logged-in') == True:
        # if len(account[session.get('username')]) >2:#封号
        #     abort(403)

        if new_account[session.get('username')].blocked or session.get('username') in lock_account_list:
            abort(403)

    room = request.form.get('room')
    sender = session.get('username')
    receiver = request.form.get('receiver')

    room = session['r'].get(room)



    if session.get('logged-in') == False:
        return '您未登录，为了保证网站安全，拍一拍功能不对游客（未登录的访客）开放。'

    if room not in l:
        return '房间不存在'

    # if receiver not in account:
    #     return '接收人不存在'
    #
    # if sender not in account:
    #     return '发送人不存在'

    if receiver not in new_account:
        return '接收人不存在'

    if sender not in new_account:
        return '发送人不存在'


    if sender == receiver:
        receiver = '自己'

    l[room].insert(0, ['tk', sender, receiver])
    return redirect('/room/%s' % room)

counter_2=0



@app.route('/room/<id>/upload', methods=["POST"])
def room_upload(id):
    global counter_2
    this_time=time.time()
    if id not in roomkey:
        return '你无权访问此房间1（如果你没有异常操作，请前往：<a href=\"/view/room\">查看已加入的房间</a>）'
    if session.get('r') == None:
        return '你无权访问此房间2'
    if session['r'].get(id) == None:
        return '你无权访问此房间3'
    dd=id
    id=session['r'].get(id)

    # global reader
    # response = reader.city(ip)


    if session.get('logged-in') == True:
        # if len(account[session.get('username')]) >2:
        #     return '你被禁止发言'

        if new_account[session.get('username')].blocked:
            return '你被禁止发言'

        if new_account[session.get('username')].muted:
            return '你被禁止发言'



    name = session['id']

    word = request.form.get('text')


    if id not in l:
        return '提交失败，房间不存在'

    counter_2+=1



    if session.get('logged-in') == False:
        nickname = '未登录'
        l[id].insert(0, [name, word, this_time, nickname,
                         0, len(l[id]), '游客', False])
    else:
        nickname = session.get('username')
        title = ''
        if len(word) > 15:
            # account[nickname][1] += 3
            new_account[nickname].exp+=3

        else:
            # account[nickname][1] += 1
            new_account[nickname].exp += 3

        # if account[nickname][1] / 500 >= 1:
        #     title = '平民'
        #
        # if account[nickname][1] / 500 >= 2:
        #     title = '士'
        #
        # if account[nickname][1] / 500 >= 3:
        #     title = '卿大夫'
        #
        # if account[nickname][1] / 500 >= 4:
        #     title = '诸侯'
        #
        # if account[nickname][1] / 500 >= 5:
        #     title = '天子'

        if new_account[nickname].exp / 500 >= 1:
            title = '平民'

        if new_account[nickname].exp / 500 >= 2:
            title = '士'

        if new_account[nickname].exp / 500 >= 3:
            title = '卿大夫'

        if new_account[nickname].exp / 500 >= 4:
            title = '诸侯'

        if new_account[nickname].exp / 500 >= 5:
            title = '天子'


        if title == '':
            title = '平民'

        # account[nickname][1]+=len(word)//15
        admin_=''
        if session.get('admin') == True:
            admin_='sv'

        if creater[id] == session.get('id'):
            admin_='rm'



        # l[id].insert(0, [name, word, this_time, nickname,
        #                  round(account[nickname][1] / 500, 1), len(l[id]), title,admin_])

        l[id].insert(0, [name, word, this_time, nickname,
                         round(new_account[nickname].exp / 500, 1), len(l[id]), title, admin_])

    online[id] = time.time()
    del roomkey[dd]
    del session['r'][dd]


    session['target__']=id

    return redirect('/_reset')

@app.template_global()
def int2time(time_):

    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time_)))

@app.template_global()
def now():
    return time.time()




@app.route('/clear_ip')
def clear_ip():
    for i in idl.items():
        idl[i[0]] = 'clear'
    return 'SUCCESS'


@app.route('/static/jquery.js')
def js():
    return render_template('jquery.js')

@app.route('/static/jsencrypt.min.js')
def js2():
    return render_template('jsencrypt.min.js')

@app.route('/static/scr.js')
def js3():
    return render_template('scr.js',pubkey=session.get('rsa_key'))




@app.route('/admin/lock/<room>/<s>')
def lock_the_room(room, s):
    if session.get('admin') != True:
        abort(404)
    temp_lock[room] = [time.time() + float(s), float(s)]
    return 'ok'

def lock_the_room_(room, s):

    temp_lock[room] = [time.time() + float(s), float(s)]
    return 'ok'

allow_snapshots=[]
'room'

allow_read_snapshots=[]
'room'

@app.route('/snapshot/<room>')
def snapshot(room):

    if room in firewall:
        if session.get('use_token') != None:
            if room in session.get('use_token'):
                system_say_warning('一个受限用户（“%s”，使用token登录）试图创建快照，已被拦截'%session.get('id'),room)
                # return '服务器已拒绝您的创建请求（原因：您以token登录此房间，已禁用快照功能，使用房间号登录以使用此功能）'
                return render_template('403.html',text='服务器已拒绝您的创建请求（原因：您以token登录此房间，已禁用快照功能，使用房间号登录以使用此功能）')

    if session.get('r') == None:

        if room in firewall:
            system_say_warning("***侦测到一个安全威胁*** 房间号可能泄露，请立即执行操作！ 一个未登录到此房间的用户“%s”正在使用房间号访问敏感页面" % session.get('id'), room)

        return '您无权拍摄此房间的快照'

    if room in session.get('r'):
        room=session.get('r')[room]#使用会话id
    else:



        if room in firewall:
            system_say_warning("***侦测到一个安全威胁*** 房间号可能泄露，请立即执行操作！ 一个未登录到此房间的用户“%s”正在使用房间号访问敏感页面" % session.get('id'), room)




        return '您无权拍摄此房间的快照'



    flag=False
    for i in session.get('r').items():
        if i[1] == room:
            flag=True

    if not flag:
        return '您无权拍摄此房间的快照'#鉴权



    if session.get('username') in lock_account_list or session.get('id') in lock_account_uidlist:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>',403

    if new_account[session.get('username')].blocked:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>', 403

    if room not in l:
        return '快照拍摄失败：房间不存在'


    if room not in allow_snapshots:
        return '管理员设置禁止拍摄快照'

    if str(snapshot_list.keys()).count(room) >= snap_max:
        return '快照拍摄失败：超过设定的极限（%s张）' % snap_max
    hash_ = hash(str(l[room]))
    if str([room, hash_]) in snapshot_list:
        return '快照拍摄失败：同一快照已存在 链接为/read-snapshot/%s/%s' % (room, hash_)
    # hash_=hash(str(l[room]))

    snapshot_list[str([room, hash_])] = [time.time(), copy.deepcopy(l[room]),session.get('id')]


    system_say('已创建快照，拍摄者：%s'%session.get('id'),room)
    return "快照拍摄成功 链接为/read-snapshot/%s/%s <a href=\"/view/room\">view/room</a>,或者<a href=\"/read-snapshot/%s/%s\">查看快照</a>" % (room, hash_,room, hash_)



@app.route('/read-snapshot/<room>/<hash_text>')
def read_snapshot(room, hash_text):


    if session.get('r') == None:
        return '您无权查看此房间的快照'

    flag=False
    for i in session.get('r').items():
        if i[1] == room:
            flag=True

    if not flag:
        return '您无权查看此房间的快照'#鉴权

    if str([room, hash_text]) not in snapshot_list:
        return "快照读取失败：快照不存在"

    if room not in allow_read_snapshots:
        return '管理员禁止查看快照'

    if session.get('use_token') != None:
        if room in session.get('use_token'):
            if room in firewall:
                system_say_warning("***侦测到一个安全威胁*** 房间号可能泄露，请立即执行操作！ 一个不安全的用户“%s”正在使用房间号访问敏感页面"%session.get('id'),room)

    if room in l:
        if room in firewall:
            system_say('"%s"正在查看快照（拍摄时间：%s）' % (session.get('id'),snapshot_list[str([room, hash_text])][0]), room)

    return render_template("snapshot.html", id='-',time=snapshot_list[str([room, hash_text])][0], message=snapshot_list[str([room, hash_text])][1],user=snapshot_list[str([room, hash_text])][2])



@app.route('/admin/del_all_room/')
def del_all_room():
    global l
    if session.get('admin') != True:
        abort(404)
    del l
    l = {}
    return 'OK'

admin_key=rd(16)

@app.route('/%s'%admin_key)
def admin1():
    session['admin']=True
    return redirect('/')


@app.route('/create_n')
def create_notice():
    if session.get('admin') != True:
        abort(404)
    return render_template('create_n.html')


@app.route('/create_n/upload', methods=["POST"])
def create_notice_upload():
    if session.get('admin') != True:
        abort(404)
    global notice
    title = request.form.get('title')
    txt = request.form.get('txt')
    notice[rd(32)] = (title, txt)
    return 'SUCCESS'


@app.route('/get_n')
def get_n():
    if session.get('admin') != True:
        abort(404)
    return str(notice)


@app.route('/del_n/<name>')
def del_n(name):
    if session.get('admin') != True:
        abort(404)
    global notice
    del notice[name]
    return 'SUCCESS'



@app.route('/website-proxy')
def website_proxy_ui():
    abort(403)
    return render_template('website-proxy-ui.html')


@app.route('/website-proxy/get', methods=["POST"])
def website_proxy():
    abort(403)
    url = str(request.form.get('url'))
    res = requests.get(url)
    res.encoding = 'utf-8'
    return res.text


@app.route('/server-time')
def servertime():
    abort(403)
    return str(time.time())





@app.route('/sign-up')
def signup():
    if session.get('username') in lock_account_list or session.get('id') in lock_account_uidlist:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>',403

    if new_account[session.get('username')].blocked:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>', 403

    return render_template('sign-up.html')


@app.route('/sign-up/upload', methods=["POST"])
def signup_upload():
    if session.get('username') in lock_account_list or session.get('id') in lock_account_uidlist:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>',403

    if new_account[session.get('username')].blocked:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>', 403



    time.sleep(1)
    # if random.randint(1, 100) < 0:
    #     return '<a href=\'/error/sign-up-00001\'>注册失败</a>，请重新提交<a href=\'/sign-up\'>注册申请</a>', 403

    username = request.form.get('username')
    password = request.form.get('password')

    blacklist=[
        'guest',
        'administrator',
        'admin'
    ]

    if username in blacklist:
        return '保留用户名，不可注册，<a href=\'/sign-up\'>返回</a>'

    if username == None or password == None or username == '' or password == '':
        return redirect('/sign-up')

    if len(username) < 3:
        return '注册失败，用户名必须大于3位，请重新提交<a href=\'/sign-up\'>注册申请</a>', 403

    # if username in account:
    #     return '注册失败，用户名已被注册，请重新提交<a href=\'/sign-up\'>注册申请</a>', 403

    if username in new_account:
        return '注册失败，用户名已被注册，请重新提交<a href=\'/sign-up\'>注册申请</a>', 403

    if password == '':
        password=rd(1024)

    new_account[username] = acc(username,password)
    session['logged-in'] = True
    logged[username] = hash(password + str(round(time.time(), 3)))
    session['key'] = logged[username]
    session['username'] = username

    with open(sys.path[0]+'\\new_account.dat','wb') as f:
        pickle.dump(new_account,f)



    return redirect('/')


@app.route('/logout')
def logout():

    if session.get('username') == None or session.get('key') == None:
        return redirect('/')
    del logged[session.get('username')]
    del session['key']
    del session['username']
    del session['logged-in']
    return redirect('/')


@app.route('/del-account')
def del_account():

    if new_account[session.get('username')].blocked:
        abort(403)

    if session.get('username') == None or session.get('key') == None:
        return redirect('/')
    session['want_to_delete_account']=time.time()

    return '<h1>删除账户</h1><br/>确定吗？您的账号将被<strong>永久性地从服务器中删除</strong>。<br/>注销成功后，您的用户名将会被释放给其他人使用（如果你不想别人使用你的用户名，请退出登录后选择冻结账户）。' \
           '<br/><strong>此操作不可逆，无反悔期。</strong><br/>' \
           '<a href="/del-account/false">退出注销</a><br/><a href="/del-account/true">确定注销</a>'

@app.route('/del-account/false')
def del_account_false():
    if session.get('username') in lock_account_list or session.get('id') in lock_account_uidlist:
        abort(403)

    if new_account[session.get('username')].blocked:
        abort(403)

    if session.get('want_to_delete_account') != None:
        if time.time()-session.get('want_to_delete_account')<30:
            del session['want_to_delete_account']
        else:
            return '注销请求已过期，<a href=\"/\">返回首页</a>'
    return redirect('/')

@app.route('/del-account/true')
def del_account_true():
    if session.get('username') in lock_account_list or session.get('id') in lock_account_uidlist:
        abort(403)



    if session.get('username') == None or session.get('key') == None:
        return redirect('/')
    if session.get('want_to_delete_account') == None:
        return redirect('/del-account')

    del logged[session.get('username')]
    # del account[session.get('username')]
    del new_account[session.get('username')]
    del session['key']
    del session['username']
    del session['logged-in']
    return '账户已注销'

@app.route('/account-login')
def account_login():
    return render_template('login.html')


@app.route('/account-login/upload', methods=['POST'])
def login_upload():
    if session.get('logged-in') == True:
        del session['key']
        del session['username']
        del session['logged-in']

    username = request.form.get('username')
    password = request.form.get('password')
    # if username not in account:
    #     return '用户名或密码不正确'

    if username not in new_account:
        return '用户名或密码不正确'

    # if account[username][0] != hash(password):
    #     return '用户名或密码不正确'

    if new_account[username].verify(password):
        return '用户名或密码不正确'

    session['logged-in'] = True
    logged[username] = hash(password + str(round(time.time(), 3)))
    session['key'] = logged[username]
    session['username'] = username

    return redirect('/')


@app.route('/room_list')
def rl():
    if session.get('username') in lock_account_list or session.get('id') in lock_account_uidlist:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>',403

    if new_account[session.get('username')].blocked:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>', 403

    online_list = []
    for i in online.items():
        if i[1] == 0:
            online_list.append([i[0], '无记录', 'None', '无人在线', 'blue'])
        else:
            color = 'blue'
            status = '无人在线'
            if round(time.time() - i[1], 3) < 20:
                status = '在线'
                color = 'blue'
            online_list.append(
                [i[0], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i[1])), round(time.time() - i[1], 3), status,
                 color])
    return render_template('room_list.html', online_list=online_list)






tokenl={}
"token:[room,uid]"

use_token_join_uid={}
"uid:[room]"
#使用token加入的用户禁用view/room
@app.route('/forward/join-token',methods=['POST'])
def forward_join_token():
    token = request.form.get('id')
    return redirect('/join-token/%s'%token)

@app.route('/join-token/<token>')
def join_token(token):

    if token not in tokenl:
        return '令牌失效或不存在'

    if tokenl[token][0] not in l:
        return '房间不存在'

    if tokenl[token][1] != session.get('id'):
        return '你无权使用此令牌'


    id=tokenl[token][0]
    r = rd(32)
    roomkey[r] = id
    if session.get('r') == None:
        session['r'] = {}
    session['r'][r] = id


    if session.get('use_token') == None:
        session['use_token'] = []
    session['use_token'].append(id)
    del tokenl[token]
    return redirect('/room/%s/1'%r)

@app.route('/create-token/<id>',methods=["POST"])
def create_token(id):
    if session.get('r') == None:
        return '你无权访问此页面'
    rid=id
    id=session['r'].get(id)
    tuid=request.form.get('uid')
    if creater[id] != session.get('id')  and session.get('admin') != True:
        return '你无权访问此页面'

    token=rd(16)
    tokenl[token]=[id,tuid]
    return 'token:%s 链接:/join-token/%s<br/><a href="/room/%s/1">返回</a>'%(token,token,rid)



@app.errorhandler(403)
def e403(a):
    # if session.get('username') in lock_account_list or session.get('id') in lock_account_uidlist:
    #     return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>',403
    #
    if new_account[session.get('username')].blocked:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>', 403

    return "<center><h1>403 Forbidden</h1><hr/><p>拒绝访问</p><small>常见错误：您可能访问了无法以正常方式访问到的页面，请退出或刷新此页面以修复此问题。</small></center>", 403


@app.errorhandler(404)
def e404(a):
    # if session.get('username') in lock_account_list or session.get('id') in lock_account_uidlist:
    #     return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>',403

    if new_account[session.get('username')].blocked:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>', 403
    # print(a)
    # return redirect('/err/404')
    return "<center><h1>404 Not Found</h1><hr/>页面不存在</center>", 404


@app.errorhandler(400)
def e400(a):
    # if session.get('username') in lock_account_list or session.get('id') in lock_account_uidlist:
    #     return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>',403
    if new_account[session.get('username')].blocked:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>', 403
    # print(a)
    return "<center><h1>400 Bad Request</h1><hr/><p>错误请求，服务器无法理解</p><small>常见错误：如果您没有试图以非正常方式访问此页面，您可能需要刷新网页以加载正确的表单。</small></center>", 400


@app.errorhandler(405)
def e405(a):
    # if session.get('username') in lock_account_list or session.get('id') in lock_account_uidlist:
    #     return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>',403
    if new_account[session.get('username')].blocked:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>', 403
    # print(a)
    return "<center><h1>405 Method Not Allowed</h1><hr/>请求方法错误</center>", 405


@app.errorhandler(500)
def e500(a):
    # if session.get('username') in lock_account_list or session.get('id') in lock_account_uidlist:
    #     return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>',403
    if new_account[session.get('username')].blocked:
        return '<center><h1>禁止访问</h1><hr/>账户已被锁定，您无权使用该功能</center>', 403
    return "<center><h1>500 Internal Server Error</h1><hr/>服务器内部错误，请等待管理员修复此错误。</center>", 500




@app.route('/setlevel/<user>/<level>')
def setlevel(user, level):
    level = float(level)
    # account[user][1] = level * 500
    new_account[user].exp=level*500

    return '%s -> %s:%s success' % (user, user, level)



@app.route('/draw')
def draw():
    if session.get('logged-in') == False:
        return '未登录'
    username = session.get('username')
    value = random.randint(-10, 5)
    # account[username][1] += value
    new_account[username].exp+=value
    if value >= 0:
        return '经验+%s <a href=\"/draw\">再试一次</a>' % value
    return '经验%s <a href=\"/draw\">再试一次</a><br/>' % value



@app.route('/font.css')
def fontcss():
    directory = os.getcwd() + "%s"
    return send_from_directory(directory % '\\templates', 'font.css', as_attachment=False)


@app.route('/MinecraftAE.ttf')
def font():
    directory = os.getcwd() + "%s"
    return send_from_directory(directory % '\\templates', 'MinecraftAE.ttf', as_attachment=False)






@app.route('/lock-account')
def lock_account():
    return render_template('lock-account.html')

@app.route('/lock-account/upload',methods=['POST'])
def lock_account_upload():
    username=request.form.get('username')
    password=request.form.get('password')
    if username not in new_account:
        return '账号不存在'
    if new_account[username].verify(password) == False:
        return '密码不正确'
    new_account[username].loss()
    return '成功'

@app.route('/join_',methods=["POST"])
def join_room():
    return redirect('/room/%s'%request.form.get('id'))


@app.route('/last-online/u/<uid>')
def last_onlineu(uid):
    if uid not in id_last_online:
        return '无记录'
    return "\"%s\"%s秒前上线"%(uid,round(time.time()-id_last_online[uid],3))

@app.route('/last-online/r/<name>')
def last_onlinen(name):
    if name not in u_last_online:
        return '无记录'
    return "\"%s\"%s秒前上线"%(name,round(time.time()-id_last_online[name],3))

@app.route('/reset_uid')
def reset_uid():
    session['id'] = hash(rd(32))
    idl[session['id']] = request.remote_addr
    return '成功,<a href="/">返回首页</a>'

info_dict={
    'wiki':{
        'alpha':"此状态说明FreeWiki正在测试新版本，这个版本可能不安全/不稳定",
        'first':"此状态说明FreeWiki正在使用第一个版本（1.0）",
        'no_save':"此状态说明FreeWiki不会保存任何内容，在服务器关机后会清空百科上所有内容"
    },
    'info':{
        'what':'/info页面用于解释本站上功能的用处、用法等'
    }
}
@app.route('/info/<parent>/<item>')
def info(parent,item):
    try:
        return """
        <h1>%s/%s</h1>
        <hr/>
        <p>%s</p>
        """%(parent,item,info_dict[parent][item])
    except:

        abort(404)

@app.route('/info')
def info_index():
    return redirect('/info/info/what')

# @app.route("/.well-known/acme-challenge/iZAtoAAVEXi00hpAF4c1lwv4qgawUdUU0YDX-ZpHnhI")
# def certbot_verify():
#     return "iZAtoAAVEXi00hpAF4c1lwv4qgawUdUU0YDX-ZpHnhI.8QeCC5tRm3U0Uzla4Z2rOSA1rFIJey_yqEPDUN_mGJU"


#---------------------------------

# wiki={
#     "测试":'EXAMPLE测试'
# }
# "name:text"
#
# @app.route('/wiki')
# def wiki_index():
#     return render_template('wiki-index.html')
#
# @app.route('/wiki/search',methods=["POST"])
# def wiki_search():
#     w=request.form.get('w')
#     w=w.lower()
#     result=[]
#     for i in wiki.items():
#         if w in i[0].lower() or w in i[1].lower():
#             result.append(i[0])
#
#     return render_template('wiki-search.html',l=result)
#
# @app.route('/wiki/item/<item>')
# def wiki_item(item):
#     if item not in wiki:
#         abort(404)
#
#     return render_template('wiki-item.html',item=item,result=wiki.get(item))



# @app.route('/admin/panel')
# def admin_panel():
#     return render_template('panel-admin.html')

#-------------------------
ssl_keys = ('crt/cert1.pem', 'crt/privkey1.pem')
https=True
debug=True
port=5000
#-------------------------
if __name__ == '__main__':
    print('[!]KEY:',admin_key)
    try:
        with open(sys.path[0]+'\\new_account.dat','rb') as f:
            new_account=pickle.load(f)
    except:
        print('读取失败')
    if https:
        app.run(host='0.0.0.0',port=port, debug=debug,ssl_context=ssl_keys)
    else:
        app.run(host='0.0.0.0', port=port, debug=debug)
