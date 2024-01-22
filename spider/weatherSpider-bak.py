import json
import time
import requests
from bs4 import BeautifulSoup
import urllib
from urllib.parse import urlencode
from Model import run

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
    # 杭州市、宁波市、温州市、嘉兴市、湖州市、绍兴市、金华市、衢州市、舟山市、台州市、丽水市
    item_map = {'北京': '54511',
                '上海': '58362',
                '广州': '59287',
                '深圳': '59493',
                '杭州': '58457',
                '丽水': '58646',
                }

    res = {}
    for city, code in item_map.items():
        print(city, code)
        res[city] = run(item_map[city])
        print(res[city])
        time.sleep(1)

    print(res)
    with open('temp_chart_data.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(res, ensure_ascii=False))


if __name__ == '__main__':
    #spider_task()
    # spider_history_city_code()
    get_temp_chart_data()