# _*_ coding: UTF-8 _*_
"""
@project -> file : city-test -> rr
@Author          : qinmin.vendor
@Date            : 2023/1/29 19:44
@Desc            :
"""

import json
import traceback
import requests
from utils.operation_logging import operationLogging
from utils.curl_generate_util import to_curl
from utils.other_util import otherUtil


class requestMain(object):
    requests.urllib3.disable_warnings() #禁用所有警告
    log=operationLogging()
    other_util=otherUtil()
    is_sission_request=True
    _request_obj = requests.session() if is_sission_request else requests
    request = None;__response = None;url = "";method = None
    body = {};headers = {};cookies = None;files = None

    @classmethod
    def check_headers_files(cls,files,headers):
        '''
        检查headers与files的格式是否合规
        '''
        if not (files and len(files) <= 4 and isinstance(files, dict)):
            files=None
        if not headers:
            headers={}
        return files,headers

    # @retry_wrapper(retry_num=3,retry_conditon=200,retry_conditon_judge='==')
    def request_main(self, url,method,data, headers, params=None, files=None,cookies=None,is_log_out=False):  # 封装get请求
        res=None
        url=self.other_util.build_str_obj(url);
        params=self.other_util.build_str_obj(params);cookies=self.other_util.build_str_obj(cookies)
        data=self.other_util.build_str_obj(data)
        self.url = url;self.method = method;self.body = data;self.headers = headers;self.cookies = cookies;self.files = files
        try:
            request_exec_code_obj=f"self._request_obj.{method}(url={url}, params={params}, data={data}, headers={headers}, files={files}, verify=False,cookies={cookies})"
            res=eval(request_exec_code_obj)
        except ValueError:
            '''请求参数为[{}]时报错，使用参数json代替参数data请求
            https://stackoverflow.com/questions/64596941/python-request-valueerror-too-many-values-to-unpack '''
            request_exec_code_obj=f"self._request_obj.{method}(url={url}, params={params}, json={data}, headers={headers}, files={files}, verify=False,cookies={cookies})"
            res = eval(request_exec_code_obj)
        except:
            traceback.print_exc()
            self.log.log_main('error', False, f"get请求发生错误:{traceback.format_exc()}")
        finally:
            self.request = res
            return res

    # @retry_wrapper(retry_num=3,retry_conditon='ffs',retry_conditon_judge='size')
    def run_main(self, host,uri, method,params=None,body=None, headers=None, files=None,cookies=None, res_format='json',is_log_out=False):  # 封装主请求
        '''参数1：请求方式，参数2：请求data，参数3：请求信息头，参数4：返回的数据格式'''
        # files参数示例：# files={'file': ('git.docx', open('C:/Users/Acer/Downloads/git.docx', 'rb'))}
        if not (host.startswith('http://') or host.startswith('https://')) :
            self.log.log_main('error', False, f"host:{host},格式错误")
            raise Exception(f"host:{host},格式错误")
        host=host[:-1] if host.endswith('/') and uri.startswith('/') else host
        uri='/'+uri if not (host.endswith('/') or uri.startswith('/')) else uri
        method=method.lower().strip()
        if str(body).startswith("{") and str(body).endswith("}") and isinstance(body,dict):
            body=json.dumps(body,ensure_ascii=False)
        files,headers=self.check_headers_files(files=files,headers=headers)
        # 检查cookie类型是否正确
        cookies=cookies if isinstance(cookies,str) else ''
        if cookies:
            headers['Cookie']=cookies
        url=host+uri
        res=self.request_main(url=url,method=method,data=body,headers=headers,params=params,files=files,cookies=None,is_log_out=is_log_out)
        response = None
        try:
            if not res_format in ('json','content','text'):
                res_format='json'
            get_response_code_obj=f"res.{res_format.lower()}"
            if res_format=='json':
                get_response_code_obj+='()'
            response=eval(get_response_code_obj)
        except :
            response=res.text
        finally:
            self.__response=response
            self.request_log_out(is_log_out=is_log_out)
            return response

    def request_log_out(self,is_log_out):
        if is_log_out:
            self.log.log_main('info', False, f'请求url:{self.url}')
            self.log.log_main('info', False, f'请求method:{self.method}')
            self.log.log_main('info', False, f'请求body:{self.body}')
            self.log.log_main('info', False, f'请求headers:{self.headers}')
            self.log.log_main('info', False, f'请求cookies:{self.cookies}')
            self.log.log_main('info', False, f'请求files:{self.files}')
            if "Response" in str(self.request):
                self.log.log_main('info', False, f'请求响应:{self.__response}')
                self.log.log_main('info', False, f'请求响应code:{self.request.status_code}')
                self.log.log_main('info', False, f'curl_code:\n{to_curl(self.request)}')

    def get_response_with_status_code(self):
        return int(self.request.status_code)

    def get_response(self):
        return self.__response



if __name__ == '__main__':
    r = requestMain()
    # url='https://www.baidu.com'
    url='http://10.4.196.168:31621/v2/api-docs'
    # print(r._request_obj)
    res=r.request_main(url=url, method='get', data=None, params=None, headers=None, is_log_out=False)
    print(res)
    # res=r.run_main(host=url,uri='', method='get', body=None, params=None, headers=None, is_log_out=False,res_format='json')
    # res=r.run_main(host=url,uri='', method='get', body=None, params=None, headers=None, is_log_out=False,res_format='text')

    # print(res)
    # print(type(res))
    # exec("res=requests.get(url=url)")
    # print(res)




