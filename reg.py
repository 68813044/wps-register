import re
import requests
import time
import js2py
import urllib3
from urllib import parse, request
import ssl

NUMBER = 1                     #注册次数
PASSWORD = 'Wps123456'         #注册密码    
#调用js脚本传值受限，注册密码修改需要连同getpwd.js中的固定密码一起改，此处暂时只改到存储值
YIMA_USER = '###'           #自己填易码账号
YIMA_PASS = '###'          #自己填易码密码
YIMA_ID = '2808'               #易码wps项目ID


def start():
    pp = PhonePlatform(YIMA_USER,YIMA_PASS,YIMA_ID)
    tm = TxtManage()
    for i in range(NUMBER):
        reg(pp,tm)
        print('=====第'+str(i+1)+'次注册完毕'+'=====')

#全局取消证书验证
ssl._create_default_https_context = ssl._create_unverified_context

#下载二维码
def downImage(url,name,imgType='png'):
    imageFile = open(name+'.'+imgType,'wb')
    res = requests.get(url, verify=False)
    for chunk in res.iter_content(100000):
        imageFile.write(chunk)
    imageFile.close()

#进行js加密
def get_password(pass_key):
    jsFile = open(".\getpwd.js",'r',encoding='UTF-8').read()
    replacedStr = jsFile.replace('PASS_KEY',pass_key)
    password = js2py.eval_js(replacedStr)
    return password


#注册程序
#传入平台对象（验证码处理）、管理器对象（只操作写入）
def reg(platform,file):
    s = requests.Session()
    requests.packages.urllib3.disable_warnings() 
    header_dict = {
        'Origin': 'https://account.wps.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
    regPageUrl = "https://account.wps.cn/v1/signup?cb=https%3A%2F%2Fvip.wps.cn%2Ftaskcenter%2F&from=vip&reload=true"
    r = s.get(regPageUrl,headers=header_dict, verify=False)
    print(r.cookies)

    phone = platform.getPhone()   #获取手机号码

    #send smsCode
    #input phone
    #out:{"result":"ok","msg":"ok"} or {"result":"apiRateLimitExceede","msg":"操作过于频繁"} or {'result': 'SMSLimitReached', 'msg': 'SMSLimitReached'}
    data = {
        'action':'signup',
        'phone': phone
    }
    regUrl = 'https://account.wps.cn/p/sms'
    r = s.post(regUrl,headers=header_dict,data=data, verify=False)
    if(r.json()['result']!='ok'):
        print(r.json())
        platform.isRidPhone(phone)
        return
    else:
        print("发送成功")
    
    #获取注册短信验证码
    smsCode = platform.getSms(phone)
    if(smsCode == None): 
        print("获得验证码超时")
        platform.isRidPhone(phone)
        return
    smsCode = re.findall('[0-9]*[0-9]',smsCode)
    smsCode = smsCode[0]

    
    #verify smdCode
    #input smsCode
    #out:{"result":"ok","ssid":"5nxxxxx0"} or {"result":"InvalidSMSCode","msg":"InvalidSMSCode"} or {"result":"CellPhoneBind","msg":"CellPhoneBind"}
    data2 = {
        'phone':phone,
        'smscode':smsCode
    }
    verifyUrl = 'https://account.wps.cn/api/v3/sms/verify'
    r = s.post(verifyUrl,headers=header_dict,data=data2, verify=False)
    if r.json()['result']=='ok':
        ssid = r.json()['ssid']
    else:
        print(r.json())
        return
    
    ##get pass_key
    #input ssid
    #out:
    t = int(time.time()*1000)
    getPassKeyUrl = 'https://account.wps.cn/api/v3/passkey?ssid='+ssid+'&_='+str(t)
    r = s.get(getPassKeyUrl,headers=header_dict)
    if r.json()['result']=='ok':
        pass_key = r.json()['pass_key']
    else:
        print(r.json())
        return
    
    #post reg
    #input pass_key(RSA publickey)、ssid
    #result":"PasswordKeyNotFound" or "ok"
    regUrl = 'https://account.wps.cn/api/v3/sms/safe_register'
    data3 = {
        'ssid':ssid,
        'password':get_password(pass_key),
        'nickname':'test'
    }
    r = s.post(regUrl,data=data3,headers=header_dict, verify=False)
    if r.json()['result']=='ok':
        print(phone+':注册成功')
    else:
        print(r.json())
        return

    #get usercenter ,verity login          
    Url = "https://account.wps.cn/usercenter/apps"
    r = s.get(Url,headers=header_dict)
    r.encoding = 'UTF-8'
    #print(r.cookies)        #反而显示为空？？
    html = r.text
    if(html.find(phone) == -1):
        print('登录失败')
        return
    userId = re.findall(r'"id":\d{9}',html) #获取userId
    userId = userId[0][5:]
    print('Id:'+userId+'登录成功')

    #close twice verity  
    closeUrl = 'https://account.wps.cn/p/signin/login_twice_verify/status'
    data4 = {"name":"twice_verify_status","status":0}
    r = s.put(closeUrl,data = data4,headers = header_dict)
    if r.json()['result']=='ok':
        print(phone+':解锁成功')
    else:
        print(r.json())
        return
    file.writeSuccessUser(phone)
    return

#记录管理
class TxtManage(object):
    #使用添加模式,进行存储，
    def __init__(self):
        self.time = str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        self.successUserFile = open('successUser.txt','a')
        self.successUserFile.write('========='+self.time+'========='+'\n')

    def formatWrite(self,data):
        self.successUserFile.write(str(data)+'\n')

    def writeSuccessUser(self,data):
        self.formatWrite(str(data)+'----'+PASSWORD)

    def __del__(self):
        self.successUserFile.close

#手机验证码平台API
class PhonePlatform(object):
    header_dict = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'}
    def __init__(self,user,password,projectId):
        self.username = user
        self.projectId = projectId
        self.password = password
        self.token = self.login()

    def login(self):
        url =  'http://api.fxhyd.cn/UserInterface.aspx?action=login&username=' + \
        self.username+'&password='+self.password
        TOKEN1 = request.urlopen(request.Request(
            url=url, headers=self.header_dict)).read().decode(encoding='utf-8')
        if TOKEN1.split('|')[0] == 'success':
            TOKEN = TOKEN1.split('|')[1]
            print('TOKEN是'+TOKEN)
        else:
            print('获取TOKEN错误,错误代码'+TOEKN1+'代码释义：1001参数token不能为空;1002:参数action不能为空;1003:参数action错误;1004:token失效;1005:用户名或密码错误;1006:用户名不能为空;1007:密码不能为空;1008:账户余额不足;1009:账户被禁用;1010:参数错误;1011:账户待审核;1012:登录数达到上限')
        return TOKEN

    def getPhone(self,exceptNum=''):
        ITEMID = self.projectId  # 项目编号
        EXCLUDENO = exceptNum  # 排除号段170_171
        TOKEN = self.token
        url = 'http://api.fxhyd.cn/UserInterface.aspx?action=getmobile&token=' + \
            TOKEN+'&itemid='+ITEMID+'&excludeno='+EXCLUDENO
        MOBILE1 = request.urlopen(request.Request(
            url=url, headers=self.header_dict)).read().decode(encoding='utf-8')
        if MOBILE1.split('|')[0] == 'success':
            MOBILE = MOBILE1.split('|')[1]
            print('获取号码是:'+MOBILE)
            return MOBILE
        else:
            print('获取TOKEN错误,错误代码'+MOBILE1)
            return None
    # 获取短信，注意线程挂起5秒钟，每次取短信最少间隔5秒
    def getSms(self,phone):
        TOKEN = self.token  # TOKEN
        ITEMID = self.projectId  # 项目id
        MOBILE = phone  # 手机号码
        WAIT = 100  # 接受短信时长60s
        url = 'http://api.fxhyd.cn/UserInterface.aspx?action=getsms&token=' + \
            TOKEN+'&itemid='+ITEMID+'&mobile='+MOBILE+'&release=1'
        text1 = request.urlopen(request.Request(
            url=url, headers=self.header_dict)).read().decode(encoding='utf-8')
        TIME1 = time.time()
        TIME2 = time.time()
        ROUND = 1
        while (TIME2-TIME1) < WAIT and not text1.split('|')[0] == "success":
            print('第'+str(ROUND)+'次获取'+text1)
            time.sleep(7)
            text1 = request.urlopen(request.Request(
                url=url, headers=self.header_dict)).read().decode(encoding='utf-8')
            TIME2 = time.time()
            ROUND = ROUND+1
        ROUND = str(ROUND)
        if text1.split('|')[0] == "success":
            text = text1.split('|')[1]
            TIME = str(round(TIME2-TIME1, 1))
            print(phone+':短信内容是'+text+';耗费时长'+TIME+'s,循环数是'+ROUND)
            return text
        else:
            print(phone+':获取短信超时，错误代码是'+text1+',循环数是'+ROUND)
            return None
    #释放手机号码
    def isRidPhone(self,phone):
        url = 'http://api.fxhyd.cn/UserInterface.aspx?action=release&token=' + \
        self.token+'&itemid='+self.projectId+'&mobile='+phone
        RELEASE = request.urlopen(request.Request(
            url=url, headers=self.header_dict)).read().decode(encoding='utf-8')
        if RELEASE == 'success':
            print('号码成功释放')
            return True
        return False

start()