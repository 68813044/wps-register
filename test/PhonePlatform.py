from urllib import parse, request
import time
import re
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
