import json
import time
import arrow
import requests
from bs4 import BeautifulSoup
from utils.MongoDBHelper import MongoDBHelper
import urllib
from urllib.parse import urlencode
import datetime as dt
from Model import run
from loguru import logger

N = 13

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


# 获取天气详情
def get_weather_info(city_code, city):
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

        weather_info_json = {'data':  {'city': city, 'forecast': forecast_list}, 'status': 1000, 'desc': 'OK'}
        return weather_info_json
    except Exception as e:
        print(e)
        return None


# 抓取北上广深天气(最近七天)
def spider_task():
    result = []
    city_list = ['北京', '上海', '广州', '深圳']
    for city in city_list:
        city_code = get_city_code(city)
        if city_code:
            item_dict = get_weather_info(city_code, city)
            print(item_dict)
            result.append(item_dict)
        time.sleep(1)
    with open('dataset.json', 'w', encoding='utf-8') as f:
        f.writelines(json.dumps(result, ensure_ascii=False))


# 获取历史天气城市code
def spider_history_city_code():
    result = {}
    url = 'http://api.k780.com'
    params = {
        'app': 'weather.city',
        'areaType': 'cn',
        'appkey': '10003',
        'sign': 'b59bc3ef6191eb9f747dd4e83c99f2a4',
        'format': 'json',
    }
    params = urlencode(params)

    f = urllib.request.urlopen('%s?%s' % (url, params))
    now_api_call = f.read()
    a_result = json.loads(now_api_call)
    for item in a_result['result']['dtList'].items():
        # print(item[1])
        result[item[1]['cityNm']] = item[1]['weaId']

    print(result)
    with open('history_city_code.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(result, ensure_ascii=False))


def get_temp_chart_data():

    citys = ['北京', '上海', '广州', '深圳', '杭州', '宁波', '温州', '嘉兴', '湖州', '绍兴', '金华', '衢州', '舟山', '台州', '丽水']

    res = {}
    for city in citys:
        print(city)
        res[city] = run(city)
        time.sleep(1)

    print(res)
    with open('temp_chart_data.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(res, ensure_ascii=False))


def get_history_weather_by_month(city_pinyin='beijing', ym='202302'):
    result = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50"}
    url = f'https://www.tianqi24.com/{city_pinyin}/history{ym}.html'
    logger.info(f'url={url}')
    resp = requests.get(url=url, headers=headers)
    html = resp.text
    time.sleep(0.5)
    soup = BeautifulSoup(html, 'lxml')
    article = soup.find('section', id='main').find_all('article')[1]
    for li_tag in article.find('ul', class_='col6').find_all('li')[1:]:
        item_dict = {'city_pinyin': city_pinyin,
                     'date': '%s-%s' % (ym[:4], li_tag.find_all('div')[0].text),
                     'type': li_tag.find_all('div')[1].text.strip().replace('\xa0', '').replace('\n', ''),
                     'high': li_tag.find_all('div')[2].text,
                     'low': li_tag.find_all('div')[3].text,
                     'AQI': li_tag.find_all('div')[4].text,
                     'fl': li_tag.find_all('div')[5].text,
                     'jyl': li_tag.find_all('div')[6].text
                     }
        logger.info('item_dict=%s' % item_dict)
        result.append(item_dict)
    return result


# 获取最近几个月[yyyy-mm]列表
def get_last_n_month(num=6):
    month_list = []
    a = arrow.now()  # 当前本地时间
    for i in range(0, num + 1):
        yearmonth = a.shift(months=-i).format("YYYYMM")
        month_list.append(yearmonth)
    return month_list


# 获取城市拼音
def get_city_pinyin(city):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50"}
    url = f'https://www.tianqi24.com/city/search/?city={city}'
    resp = requests.get(url=url, headers=headers)
    time.sleep(0.5)
    return json.loads(resp.text)[0]['pinyin']


# 爬取历史天气
def get_hweather_by_city(city='北京'):
    logger.info(f'city={city}')
    city_pinyin = get_city_pinyin(city)
    mongo_cls = MongoDBHelper()
    month_list = get_last_n_month(N)
    for ym in month_list:
        logger.info('ym=%s' % ym)
        datas = get_history_weather_by_month(city_pinyin=city_pinyin, ym=ym)
        for data in datas:
            data['_id'] = mongo_cls.str_to_md5(city + data['date'])
            data['city'] = city
            print(data)

        mongo_cls.insert_batch_collection(collection_name='history_weather', value_list=datas)
        time.sleep(1)


def multi_get_city_history_weather():
    citys = ['北京', '上海', '广州', '深圳', '杭州', '宁波', '温州', '嘉兴', '湖州', '绍兴', '金华', '衢州', '舟山', '台州', '丽水']
    for city in citys:
        logger.info(f'city={city}')
        get_hweather_by_city(city)
        time.sleep(1.5)


def get_history_weather2(city):
    mongo_cls = MongoDBHelper()
    data_list = mongo_cls.select_all_collection(collection_name='history_weather', search_col={'city': city}
                                                , sort_col="date", sort="asc")
    # for data in data_list[-7:]:
    #     print(data)
    return data_list[-7:]


if __name__ == '__main__':
    # spider_task()
    # spider_history_city_code()

    # 爬取历史数据
    multi_get_city_history_weather()

    # 加载模型 跑数据
    get_temp_chart_data()

    # get_history_weather2(city='深圳')