import js2py
def get_js(pass_key):
    jsFile = open(".\getpwd.js",'r',encoding='UTF-8').read()
    replacedStr = jsFile.replace('PASS_KEY',pass_key)
    password = js2py.eval_js(replacedStr)
    return password



#getpwd('MDwwDQYJKoZIhvcNAQEBBQADKwAwKAIhAL2/7WrDGfQ01A45qllGbZp6hSiaEq3XCdqRtlZtA/zhAgMBAAE=','Wps123456')

print(
get_js('MDwwDQYJKoZIhvcNAQEBBQADKwAwKAIhAL2/7WrDGfQ01A45qllGbZp6hSiaEq3XCdqRtlZtA/zhAgMBAAE='))
# jsFile = open(".\getpwd.js",'r',encoding='UTF-8').read()
# print(type(jsFile))
# data = js2py.eval_js(jsFile)
# print(data)