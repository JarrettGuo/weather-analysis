import platform
import hashlib
import json
print(platform.system())
import urllib
import urllib.request
from urllib.parse import urlencode
import datetime

# 字符串转md5
# def str2md5(param_str):
#     if isinstance(param_str, str):
#         # 如果是unicode先转utf-8
#         param_str = param_str.encode("utf-8")
#     m = hashlib.md5()
#     m.update(param_str)
#     return m.hexdigest()
#
# print(str2md5('/mnt/factoring-nas/zdnet/广西人防工程设计咨询有限公司/14950950001787469399及关联登记.zip'))

with open('spiders/dataset.json', 'r', encoding='utf-8') as f:
    local_weather = json.loads(f.read())


# print(local_weather)


# def get_local_weather(city):
#     if city not in ['北京', '上海', '广州', '深圳']:
#         return None
#
#     for item in local_weather:
#         if item['data']['city'] == city:
#             return item
#
# print(get_local_weather('北京'))

with open('spiders/history_city_code.json', 'r', encoding='utf-8') as f:
    city_code_dict = json.loads(f.read())


code = city_code_dict['深圳']
url = 'http://api.k780.com'

last7_date = (datetime.datetime.now() + datetime.timedelta(days=-6)).strftime('%Y%m%d')
cur_date = datetime.datetime.now().strftime('%Y%m%d')
print(last7_date, cur_date)

params = {
    'app': 'weather.history',
    'weaId': code,
    'dateYmd': f'{last7_date}-{cur_date}',
    'appkey': '10003',
    'sign': 'b59bc3ef6191eb9f747dd4e83c99f2a4',
    'format': 'json',
}

params = urlencode(params)
print(params)
f = urllib.request.urlopen('%s?%s' % (url, params))
nowapi_call = f.read()
# print content
a_result = json.loads(nowapi_call)


dtList = a_result['result']['dtList']
print(dtList)