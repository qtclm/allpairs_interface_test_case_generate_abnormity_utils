# _*_ coding: UTF-8 _*_
"""
@project -> file : city-test -> update_api_case_allpairspy_case
@Author          : qinmin.vendor
@Date            : 2023/2/3 11:13
@Desc            : 
"""
import json
import math
import sys
from other_scripts.auto_generate_api_case_allpairspy import autoGenrateApiCaseAllpairspy
from utils.operation_datas import operationExcel
from utils.wrapper_util import exec_time_wrapper
from xpinyin import Pinyin
from utils.operation_datas import operationExcelXlsxwriter

class update_api_case_allpairspy_case(autoGenrateApiCaseAllpairspy):

    excel_name = autoGenrateApiCaseAllpairspy.excel_name_params_obj
    excel_obj=operationExcel(excel_path=autoGenrateApiCaseAllpairspy.excel_path,excel_name=excel_name)
    excel_name_update=excel_name.split('.xlsx')[0]+'-update.xlsx'
    excel_obj_update=operationExcelXlsxwriter(excel_path=autoGenrateApiCaseAllpairspy.excel_path,excel_name=excel_name_update)

    @classmethod
    @exec_time_wrapper(round_num=10, module_obj=__file__, class_obj=sys._getframe().f_code.co_name, is_send_email=False)
    def update_case_expected_api_response_code(cls):
        '''根据规则修改预期的响应code'''
        sheet_names = cls.excel_obj.get_all_sheet_name()
        for sheet_name in sheet_names:
            cls.excel_obj.data = cls.excel_obj.get_data_for_sheet_name(sheet_name=sheet_name)
            api_response_code_dict = cls.update_api_response_code(sheeet_name=sheet_name)
            lines = cls.excel_obj.get_lines()
            for line_num in range(lines + 1):
                values = cls.excel_obj.get_row_values(line_num + 1)
                # if line_num <= 17:
                expected_col_num=cls.write_excel_case_field_desc['response_body'] - 1
                expected_info = values[expected_col_num]
                if str(expected_info).startswith("{") and str(expected_info).endswith("}"):
                    expected_info = json.loads(expected_info)
                    if 'api_response_code' in expected_info.keys():
                        expected_info.update(api_response_code_dict)
                        values[expected_col_num] = json.dumps(expected_info, ensure_ascii=False)
                        cls.excel_obj.write_value(line_num+1,expected_col_num+1,values[expected_col_num])

                cls.excel_obj_update.write_values(sheet_name,line_num,0,values)

        cls.excel_obj_update.save_and_close()

    @classmethod
    def list_split(cls,list_obj:(list,set,tuple,str),split_num:int=2,splitter:str='_') -> str:
        '''

        Args:
            list_obj:
            split_num: 按多少个元素切分
            splitter: 字符拼接符
        Returns:
        '''
        if not isinstance(list_obj,(list,set,tuple)):
            list_obj=list_obj.split(splitter)

        if len(list_obj)<=split_num:
            return list_obj

        n=int(math.ceil(len(list_obj)/ split_num))
        out_list_obj=[list_obj[i*split_num:(i+1)*split_num] for i in range(0,n)]
        out_list_obj=splitter.join([''.join(i) for i in out_list_obj])
        return out_list_obj
    @classmethod
    def generate_func_code(cls,sheet_name):
        tr_obj=Pinyin()
        func_name=tr_obj.get_pinyin(sheet_name,splitter='_')
        func_name=cls.list_split(func_name,2)
        func_code=f'''
    # @pytest.mark.skip("测试通过")
    @allure.feature("{sheet_name}")
    @pytest.mark.parametrize('data', case["{sheet_name}"]["case_info"], ids=case["{sheet_name}"]["ids"])
    def test_{func_name}(self, data,  config,iam_cookies):
        self.run_web_iam_cookie(data, config,iam_cookies)'''
        print(func_code,'\n\n')


if __name__=="__main__":
    update_api_case_allpairspy_case.update_case_expected_api_response_code()
    # all_sheet_names=update_api_case_allpairspy_case.excel_obj.get_all_sheet_name()
    # print(all_sheet_names)
    # for sheet_name in all_sheet_names:
    #    update_api_case_allpairspy_case.generate_func_code(sheet_name)
    # update_api_case_allpairspy_case.generate_func_code('application_management')
    # update_api_case_allpairspy_case.generate_func_code('路段管理模块')
    # update_api_case_allpairspy_case.generate_func_code('管理')
    # update_api_case_allpairspy_case.generate_func_code('模块')