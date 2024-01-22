import time
import requests
from bs4 import BeautifulSoup
from utils.MongoDBHelper import MongoDBHelper
import loguru
import datetime

""" 
    最近12个月 
    如果想要指定月份 只要修改cur_month参数即可
"""


def knn_12():
    month_list = []
    now_time = datetime.datetime.now()
    year = now_time.year  # 当前年份
    year_last = now_time.year - 1  # 去年年份
    cur_month = now_time.month  # 当前月份
    for year in [year_last, year]:
        for month in range(1, 13):
            y = str(year)
            m = str(month)
            if len(m) < 2:
                m = '0%s' % m
            month_list.append(y + m)
    return month_list[cur_month - 1:cur_month + 11]


class WeatherSpider:

    def __init__(self):
        self._logger = loguru.logger
        self.mongo_cls = MongoDBHelper(db='spider_db')

    def get_requests_html(self, url):
        headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                response.encoding = response.apparent_encoding
                time.sleep(0.5)
                return response.text
        except requests.ConnectionError as e:
            self._logger.error('Error: %s' % e.args)

    def get_city_list(self):
        url = 'http://lishi.tianqi.com/'
        html = self.get_requests_html(url)
        soup = BeautifulSoup(html, 'lxml')

        for i in range(1, 27):
            print('i=', i)
            data_list = []
            letter_code = soup.find('tbody').find_all('tr')[i].find('th', class_='table_title').a.text
            print('letter_code:', letter_code)
            for item in soup.find('tbody').find_all('tr')[i].find('ul', class_='table_list').find_all('a'):
                # print('http://lishi.tianqi.com/%s' % item.attrs['href'], item.text)
                item_dict = {
                    '_id': self.mongo_cls.str_to_md5(item.text+'http://lishi.tianqi.com/%s' % item.attrs['href']),
                    'letter_code': letter_code, 'name': item.text,
                    'url': 'http://lishi.tianqi.com/%s' % item.attrs['href']}
                print(item_dict)
                data_list.append(item_dict)

            if data_list:
                self.mongo_cls.insert_batch_collection(collection_name='weather_city_dict', value_list=data_list)
            time.sleep(1)

    def get_weather_detail(self, item0):

        # url = 'http://lishi.tianqi.com/acheng/202302.html'
        html = self.get_requests_html(item0['url'])
        soup = BeautifulSoup(html, 'lxml')

        data_list = []
        for item in soup.find('div', class_='tian_three').find('ul', class_='thrui').find_all('li'):
            item_dict = {'_id': self.mongo_cls.str_to_md5(item0['name']+item0['url'] + item.find_all('div')[0].text),
                         'letter_code': item0['letter_code'],
                         'name': item0['name'],
                         'url': item0['url'],
                         'date': item.find_all('div')[0].text.split(' ')[0],
                         'week': item.find_all('div')[0].text.split(' ')[1],
                         'high_temperature': item.find_all('div')[1].text,
                         'low_temperature': item.find_all('div')[2].text,
                         'weather': item.find_all('div')[3].text,
                         'wind_direction': item.find_all('div')[4].text.split(' ')[0],
                         'wind_level': item.find_all('div')[4].text.split(' ')[1]}
            print(item_dict)
            data_list.append(item_dict)

        if data_list:
            self.mongo_cls.insert_batch_collection(collection_name='weather_detail', value_list=data_list)
        time.sleep(1)

    def get_weather_list(self):
        last_12_months = knn_12()

        data_list = self.mongo_cls.select_all_collection(collection_name='weather_city_dict')

        for month in last_12_months:
            for data in data_list:
                if data['name'] in ['北京', '上海', '广州', '深圳']:
                    # print(data['letter_code'], data['name'], data['url'].replace('index.html', '')+'%s.html' % month)

                    item = {'letter_code': data['letter_code'],  'name': data['name'],
                            'url': data['url'].replace('index.html', '')+'%s.html' % month}
                    print('item >', item)
                    self.get_weather_detail(item)

    def data_handle(self):
        data_list = self.mongo_cls.select_all_collection(collection_name='weather_detail')


if __name__ == '__main__':
    cls = WeatherSpider()
    cls.get_weather_list()
