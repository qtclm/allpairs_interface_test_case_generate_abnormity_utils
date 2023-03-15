# _*_ coding: UTF-8 _*_
"""
@file            : send_email
@Author          : qtclm
@Date            : 2023/1/29 19:44
@Desc            : 自动生成接口测试用例：支持正交实验，等价类，边界值
"""

import smtplib
from email.mime.text import MIMEText
from typing import Union


class sendEmail:
    EmailHost='smtp.163.com'
    sendUser='18160042485@163.com'
    password='5942xphtcl'
    def send_email(self, user_list: Union[list,tuple,set], sub: str, content: str) -> None:
        user="18160042485"+"<"+self.sendUser+">"
        message=MIMEText(content,_subtype='plain',_charset='utf-8')
        message['Subject']=sub
        message['From']=user
        message['To']=';'.join(user_list)
        server=smtplib.SMTP()
        server.connect(self.EmailHost)
        server.login(self.sendUser,self.password)
        server.sendmail(user,user_list,message.as_string())
        server.close()
    def send_main(self,pass_list,failed_list):
        pass_num=float(len(pass_list))
        failed_num=float(len(failed_list))
        all_num=pass_num+failed_num
        #90%
        #格式符处理：%C:字符 %s、%r:字符串 %d：带符号的十进制整数 %u不带符号的十进制整数 %f：浮点实数（%m.nf：m表示总长度，n表示n个小数位）
        pass_result = "%.2f%%" % (pass_num / all_num * 100)
        fail_result = "%.2f%%" % (failed_num / all_num * 100)
        #定义list时将自己的邮箱地址加上，否则会报554错误（被定义为垃圾邮件从而不能发送）
        user_list = ['18160042485@163.com;248313385@qq.com;18883612485@163.com;']
        sub="接口自动化测试报告"
        content='此次一共运行接口个数为%s个，通过个数为%s个，失败个数为%s个，通过率%s，失败率%s' %(all_num,pass_num,failed_num,pass_result,fail_result)
        self.send_email(user_list,sub,content)

    def send_msg(self,sub,msg,user_list=None):
        '''

        Args:
            user_list:
            sub:
            msg:

        Returns:

        '''
        if user_list is None:
            user_list = ['18160042485@163.com;248313385@qq.com;18883612485@163.com;']
        # sub="接口自动化测试报告"
        self.send_email(user_list,sub,msg)

if __name__=='__main__':
    sen=sendEmail()
    # user_list=['18160042485@163.com;248313385@qq.com,18883612485@163.com']
    # sub='接口自动化测试报告'
    # content='此次一共运行接口个数为%s个，通过个数为%s个，失败个数为%s个，通过率%s，失败率%s' #%(all_num,pass_num,failed_num,pass_result,fail_result)
    # sen.send_email(user_list,sub,content)
    sen.send_main([1,2,3,4],[2,3,4,5,6,7])