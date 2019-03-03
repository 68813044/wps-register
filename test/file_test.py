import os
import time
#os.makedirs('.\text.txt')  新建文件夹


#test module    
a = TxtManage()
for i in range(100):
    if(i%3 == 0):
        a.writeUser(i)
    if(i==%5 == 0):
        a.writeUnSafeUser(i)
    if(i%7 == 0):
        a.writeSuccessUser(i)