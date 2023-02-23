# allpairs_interface_test_case_generate_abnormity_utils
一个基于正交实验（allpairs）生成接口测试用例的工具
#更新日志
- 2023.2.7：修复json[key]为object类型时（allpairs解析错误），参数生成格式错误的问题
- 2023.2.7：将写入文件的策略更改为分批写入，避免在大量数据下写入时造成数据丢失（openpyxl的坑）
- 2023.02.23：
	- 1.支持用户自定义传递正交范围参数：目前支持基于参数key与参数类型两种方式指定，不在指定范围内的参数还是按照默认定义的数据处理
	- 2.增加接口黑名单配置，配置后对应的接口不生成接口用例
	- 3.已经生成的接口用例，再次运行时不会在重新生成（提高效率），如果需要每次都重新生成，设置config文件- is_rm_old_file=True即可（会重新生成所有接口的用例），如果只需要重新生成指定接口的用例，则删除excel中对应的用例，还有需要删除auto_genrate_api_case_allpairspy_params_field_detail_custom_already_generate.txt文件中对应的接口名称
	- 4.优化项目代码结构，修改bug若干
具体使用说明:
重新生成所有用例


具体例子： 重新生成接口”设备管理_内部接口:对接symphony设备注册“的接口测试用例
1.删除excle中对应的用例auto_genrate_api_case_allpairspy_params_obj_custom.xlsx
2.删除auto_genrate_api_case_allpairspy_params_obj_custom_already_generate.txt（文件名规则：excle文件名称(不包含拓展名+”already_generate.txt“)）文件中对应的接口名称
3.重新执行脚本

补充说明：如果需要删除重新生成的接口字段参数明细原理也是类似的
1.删除excle中对应的用例auto_genrate_api_case_allpairspy_params_field_details_custom.xlsx
2.删除auto_genrate_api_case_allpairspy_params_field_details_custom_already_generate.txt（文件名规则：excle文件名称(不包含拓展名+”already_generate.txt“)）文件中对应的接口名称
3.重新执行脚本



#目前支持的功能
1.基于不同的参数类型（str、int、float、bool、list、tuple、dict、set、None、date、datetime、time、timestamp）自动生成正交测试用例
2.可以自定义参数长度与内容，方便覆盖边界值测试
3.提供自定义过滤参数组合的入口，方便自定义

#实现思路
1.抓取api信息（目前公司用的swagger）： https://www.cnblogs.com/qtclm/p/17049176.html ，uri、method、params、response，解析完成后写入excle
2.读取抓取完毕的api信息，处理为allpairs所需要的ordereddict
3.调用allpairs工具生成测试用例
4.解析allpairs生成的测试用例（输出为字符串），并处理为dict
5.处理完毕后写入excel


#后期优化
1.根据接口响应实现自动断言
2.增加其他接口平台的api抓取(openapi、eolink等)
3.增加其他自动化生成用例的方法（有效、无效等价类，流量回放等）
4.集成到平台

#遇到的问题
1.allpairs只支持两个以上的参数生成，因为参数只有一个时，需要自行处理
2.参数为json嵌套时，allpairs输出的参数需要额外特殊处理，这块也是最麻烦的地方
3.可变类型在循环过程中尽量使用深拷贝对象，避免循环运行中被意外修改
4.类变量、实例变量需要合理运用，例如循环时需要合理的进行初始化

#使用说明
1.init_enum_data：生成各个数据类型枚举的方法，可以根据实际需要修改
2.dict_parse_generator：递归解析json
3.api_prams_convert：将dict所有的key对应的值根据类型推算为定义的枚举值，并完成动态参数替换
4.generate_all_cases（核心），生成正交测试用例
5.write_params_filed_detail_to_excle（单个params）：输出参数明细到excle（不仅可以输出接口测试用例，文字测试用例也可）
6.write_cases_obj_to_excle（单条case）：输出测试用例到excle
7.batch_write_params_filed_detail_to_excle：将所有params输出到excle，基于接口生成sheet
8.batch_write_cases_obj_to_excle：将所有测试用例输出到excle，基于接口模块生成sheet

#生成后的效果
##batch_write_params_filed_detail_to_excle：
![image](https://img2023.cnblogs.com/blog/1357367/202301/1357367-20230131152244372-1543690842.png)


##batch_write_cases_obj_to_excle：
![image](https://img2023.cnblogs.com/blog/1357367/202301/1357367-20230131152107805-1827420595.png)




