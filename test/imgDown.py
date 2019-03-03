import requests
url = 'http://pay.wps.cn/api/pay/qrcodelink/?data=aHR0cHM6Ly9hcGkubWNoLndlaXhpbi5xcS5jb20vcGFwYXkvZW50cnVzdHdlYj9hcHBpZD13eGI0MWE0MTg5OTBiNzNmOGImY29udHJhY3RfY29kZT0wMDAwNDIwMTkwMjI4Y2VmZmQ3JmNvbnRyYWN0X2Rpc3BsYXlfYWNjb3VudD00ODcyNzYyMTEmbWNoX2lkPTEyNDMyMjk1MDImbm90aWZ5X3VybD1odHRwcyUzQSUyRiUyRnBheS53cHMuY24lMkZhcGklMkZhdXRvX3JlbmV3JTJGbm90aWZ5JTJGd3hfY29udHJhY3RfY2FsbGJhY2smcGxhbl9pZD00NzYwMyZyZXF1ZXN0X3NlcmlhbD0xNTUxMzY3OTA2NTEyJnRpbWVzdGFtcD0xNTUxMzY3OTA2JnZlcnNpb249MS4wJnNpZ249RTBBQUQwRTBFMEZFOUI0NjIyRURBMDY1OTY1Mzg4ODg&size=c'
res = requests.get(url)
dot = '.png'
print(res.status_code)
imageFile = open('x'+dot,'wb')
for chunk in res.iter_content(100000):
    imageFile.write(chunk)
imageFile.close()



def downImage(url,name,imgType='png'):
    imageFile = open(name+'.'+imgType,'wb')
    res = requests.get(url, verify=False)
    for chunk in res.iter_content(100000):
        imageFile.write(chunk)
    imageFile.close()