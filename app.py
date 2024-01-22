# -*- coding: utf-8 -*-
import json
import time
from loguru import logger
import requests
from flask import Flask, request, jsonify, render_template
from bs4 import BeautifulSoup
from flask_cors import CORS
import urllib
import urllib.request
from urllib.parse import urlencode
import datetime
import pandas as pd
from utils.MongoDBHelper import MongoDBHelper

app = Flask(__name__)
# r'/*' 是通配符，让本服务器所有的 URL 都允许跨域请求
# CORS(app, resources=r'/*')
CORS(app, supports_credentials=True)

# with open('spider/dataset.json', 'r', encoding='utf-8') as f:
#     local_weather = json.loads(f.read())

# with open('spider/history_city_code.json', 'r', encoding='utf-8') as f:
#     city_code_dict = json.loads(f.read())


@app.route('/')
def index():
    return 'hello world'


# 获取城市代码
def get_city_code(city):
    # 输入城市名称
    # city = input('请输入城市名称：')
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50"}
    urls = 'http://toy1.weather.com.cn/search?cityname=' + city

    try:
        resource = requests.get(url=urls, headers=headers)
        city_code = (resource.text.split('~')[0]).split('"')[3]
        city_code = str(city_code)
        return city_code
    except:
        return None


# 获取天气信息
def get_weather_info(city_code):
    headers = {"Accept-Encoding": "gzip, deflate",
               "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
               "Connection": "keep-alive",
               "Host": "d1.weather.com.cn", "Referer": "http://www.weather.com.cn/",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50"}
    milli_time = (lambda: round(time.time() * 1000))
    get_url_time = str(milli_time())
    weather_url = 'http://d1.weather.com.cn/sk_2d/' + city_code + '.html?_=' + get_url_time
    try:
        resource = requests.get(url=weather_url, headers=headers, timeout=10)
        weather_info = (resource.content.decode('utf-8')).split("=")[1]
        weather_info_json = json.loads(weather_info)
        return weather_info_json
    except:
        return None


def get_weather_info2(city_code, city):
    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Connection": "keep-alive",
        "Host": "www.weather.com.cn", "Referer": "http://www.weather.com.cn/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50"}

    weather_url = f'http://www.weather.com.cn/weather/{city_code}.shtml'
    print(f'{weather_url}')
    try:
        resp = requests.get(url=weather_url, headers=headers, timeout=60)
        time.sleep(0.5)
        html = resp.content.decode('utf-8')
        # print(html)
        soup = BeautifulSoup(html, 'lxml')
        # print(soup.find('div', id='7d'))

        ul_tag = soup.find('div', id='7d').find('ul', class_='t clearfix')

        if not ul_tag:
            return

        forecast_list = []
        for li_tag in ul_tag.find_all('li'):
            # print(li_tag)

            if len(li_tag.find('p', class_='tem').text.strip().split('/')) > 1:
                high = li_tag.find('p', class_='tem').text.strip().split('/')[0]
                low = li_tag.find('p', class_='tem').text.strip().split('/')[1]
            else:
                high = li_tag.find('p', class_='tem').text.strip()
                low = high
            if '℃' not in high:
                high = f'{high}℃'

            item_dict = {'date': li_tag.h1.text,
                         'type': li_tag.find('p', class_='wea').text,
                         'high': high,
                         'low': low,
                         'fl': li_tag.find('p', class_='win').find('i').text}

            print(item_dict)
            forecast_list.append(item_dict)

        weather_info_json = {'data': {'city': city, 'forecast': forecast_list}, 'status': 1000, 'desc': 'OK'}
        return weather_info_json
    except Exception as e:
        print(e)
        return None


# 通过get方式进行天气查询
@app.route('/weather', methods=['GET'])
def weather():
    city = request.args.get("city").strip()
    return jsonify(get_weather_list(city))


@app.route('/weather/info', methods=['GET'])
def show_weather_info():
    city = request.args.get("city").strip()
    code = get_city_code(city)
    return jsonify(get_weather_info(code))


def get_weather_list(city):
    logger.info(f'查询city={city}')
    logger.info('实时爬取查询')
    city_code = get_city_code(city)
    logger.info(f'city_code={city_code}')
    if city_code:
        item = get_weather_info2(city_code, city)
        logger.info(f'query result={item}')
        return item
    return {}


# @app.route('/weather/history', methods=['GET'])
# def show_weather_hostory_list():
#     city = request.args.get('city')
#     return jsonify(get_history_weather(city))


'''def get_history_weather(city, start=6, end=0):
    logger.info(f'city={city}')
    code = city_code_dict[city]
    url = 'http://api.k780.com'

    last7_date = (datetime.datetime.now() - datetime.timedelta(days=start)).strftime('%Y%m%d')
    cur_date = (datetime.datetime.now() - datetime.timedelta(days=end)).strftime('%Y%m%d')
    logger.info(f'last7_date={last7_date}, cur_date={cur_date}')
    params = {
        'app': 'weather.history',
        'weaId': code,
        'dateYmd': f'{last7_date}-{cur_date}',
        'appkey': '10003',
        'sign': 'b59bc3ef6191eb9f747dd4e83c99f2a4',
        'format': 'json',
    }
    logger.info(params)
    try:
        params = urlencode(params)
        f = urllib.request.urlopen('%s?%s' % (url, params))
        now_api_call = f.read()
        a_result = json.loads(now_api_call)
        print(a_result)
        data_list = get_everyday_onedata(a_result['result']['dtList'])
        logger.info(data_list)
        return data_list
    except Exception as e:
        logger.error(e)
    return {}
'''

# 获取列表中 居中的元素
def get_median(data):
    data = sorted(data)
    size = len(data)
    if size % 2 == 0:  # 判断列表长度为偶数
        median = data[int(size / 2)]
        data[0] = median
    if size % 2 == 1:  # 判断列表长度为奇数
        median = data[(size - 1) // 2]
        data[0] = median
    return data[0]


# 获取每天 居中的一条记录
def get_everyday_onedata(data_list):
    df = pd.DataFrame(data_list)

    df['date'] = df['upTime'].map(lambda x: x.split(' ')[0])
    date_counts = json.loads(df.groupby('date')['date'].count().to_json())

    res = []
    for date, count in date_counts.items():
        mid_val = get_median([i for i in range(1, count + 1)])
        item = json.loads(df[df['date'] == date].iloc[[mid_val], ].to_json(orient='records'))[0]
        res.append(item)
    return res


# 获取气温预测 当前仅支持城市：'北京', '上海', '广州', '深圳', '杭州', '宁波', '温州', '嘉兴', '湖州', '绍兴', '金华', '衢州', '舟山', '台州', '丽水'
@app.route('/weather/chart/temp', methods=['GET'])
def show_temp_chart_data():
    if 'city' not in request.args.keys():
        return '请传入参数city'

    city = request.args.get('city')

    citys = ['北京', '上海', '广州', '深圳', '杭州', '宁波', '温州', '嘉兴', '湖州', '绍兴', '金华', '衢州', '舟山', '台州', '丽水']
    if city in citys:
        with open('spider/temp_chart_data.json', 'r', encoding='utf-8') as fs:
            data = json.loads(fs.read())

        print(data.keys())
        res = []
        for record in data[city]:
            item_dict = {'period': record['date'],
                         'high': record['high'],
                         'temp': record['temp'],
                         'low': record['low']}
            res.append(item_dict)
        return jsonify(res)

    logger.info('当前仅支持部分城市')
    return []


# 降雨量预测 当前仅支持城市：北上广深
@app.route('/weather/chart/rainfall', methods=['GET'])
def show_rainfall_chart_data():
    if 'city' not in request.args.keys():
        return '请传入参数city'

    city = request.args.get('city')

    citys = ['北京', '上海', '广州', '深圳', '杭州', '宁波', '温州', '嘉兴', '湖州', '绍兴', '金华', '衢州', '舟山', '台州', '丽水']
    if city in citys:
        with open('spider/temp_chart_data.json', 'r', encoding='utf-8') as fs:
            data = json.loads(fs.read())

        return jsonify([{'date': item['date'], 'value': round(item['jyl'],2)} for item in data[city]])
    logger.info('当前仅支持部分城市')
    return []


# 空气湿度
@app.route('/weather/chart/humi', methods=['GET'])
def show_wtHumi_data():
    if 'city' not in request.args.keys():
        return '请传入参数city'

    city = request.args.get('city')
    # res = get_history_weather(city=city, start=0, end=0)
    # return jsonify({'空气湿度(%)': int(res[0]['wtHumi']), '其他': 100-int(res[0]['wtHumi'])})
    city_code = get_city_code(city)
    res = get_weather_info(city_code)

    return jsonify([{'label': '空气湿度(%)', 'value': int(res['SD'].replace('%', ''))},
                   {'label': '其他', 'value': 100-int(res['SD'].replace('%', ''))}])


def get_history_weather2(city):
    mongo_cls = MongoDBHelper()
    data_list = mongo_cls.select_all_collection(collection_name='history_weather', search_col={'city': city}
                                                , sort_col="date", sort="asc")
    # for data in data_list[-7:]:
    #     print(data)
    return data_list[-7:]


# 空气质量
@app.route('/weather/chart/aqi', methods=['GET'])
def show_pm2point5_data():
    if 'city' not in request.args.keys():
        return '请传入参数city'

    city = request.args.get('city')
    # res = get_history_weather(city=city)
    res = get_history_weather2(city)
    print(res)

    return jsonify([{'date': item['date'], 'value': item['AQI']} for item in res])


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
