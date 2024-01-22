# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
from CrawlData import GetData
import datetime as DT
import csv
import pandas as pd
from utils.MongoDBHelper import MongoDBHelper

def a(t):
    return t.replace(" - ", "0")


# 功能: 写csv
def write(years, b, c, city_id='59493'):
    """
    :param years: [开始日期距离现在的年份, 结束日期距离现在的年份]
    :param b: [开始日期距离现在日期的天数, 结束日期距离现在日期的天数]
    :param c: csv文件名
    :return: None
    """
    # 1. 创建文件对象
    f = open(c, 'w', encoding='utf-8', newline='')

    # 2. 基于文件对象构建 csv写入对象
    csv_writer = csv.writer(f)

    # 3. 构建列表头
    # , "negAve", "negMax", "negMin"
    csv_writer.writerow(["Time", "Ave_t", "Max_t", "Min_t", "Prec", "SLpress", "Winddir", "Windsp", "Cloud"])
    # 取现在日期
    today = DT.datetime.now()
    # 取20天前日期
    week_ago = (today - DT.timedelta(days=b[0])).date()
    # 20天后
    week_pre = (today + DT.timedelta(days=b[1])).date()
    # 城市id  广州59287 深圳59493 北京54511  上海58362
    # 如果是其他城市id 可以在"http://www.meteomanz.com/"上获取
    # 这里的城市id 我选用“广州”为例
    # id = "59287"
    # 爬取数据链接
    url = "http://www.meteomanz.com/sy2?l=1&cou=2250&ind=" + str(city_id) + "&d1=" + str(week_ago.day).zfill(2) + "&m1=" + str(
        week_ago.month).zfill(2) + "&y1=" + str(week_ago.year - years[0]) + "&d2=" + str(week_pre.day).zfill(
        2) + "&m2=" + str(week_pre.month).zfill(2) + "&y2=" + str(week_pre.year - years[1])
    # 显示获取数据集的网址
    print(url)
    g = GetData(url).Get()
    # beautifulsoup解析网页
    soup = BeautifulSoup(g, "html5lib")
    # 取<tbody>内容
    tb = soup.find(name="tbody")
    # 取tr内容
    past_tr = tb.find_all(name="tr")
    for tr in past_tr:
        # 取tr内每个td的内容
        text = tr.find_all(name="td")
        flag = False
        negA = negMax = negMin = False
        for i in range(0, len(text)):
            if i == 0:
                text[i] = text[i].a.string
                # 网站bug，会给每个月第0天，比如 00/11/2020,所以要drop掉
                if "00/" in text[i]:
                    flag = True
            elif i == 8:
                # 把/8去掉，网页显示的格式
                text[i] = text[i].string.replace("/8", "")
            elif i == 5:
                # 去掉单位
                text[i] = text[i].string.replace(" Hpa", "")
            elif i == 6:
                # 去掉风力里括号内的内容
                text[i] = re.sub(u"[º(.*?|N|W|E|S)]", "", text[i].string)
            else:
                # 取每个元素的内容
                text[i] = text[i].string
            # 丢失数据都取2(简陋做法)
            # 这么做 MAE=3.6021
            text[i] = "2" if text[i].strip() == "-" else text[i]
            text[i] = "2" if text[i].strip() == "Tr" else text[i]
        text = text[0:9]
        # ext += [str(int(negA)), str(int(negMax)), str(int(negMin))]
        # 4. 写入csv文件内容
        if not flag:
            csv_writer.writerow(text)
    # 5. 关闭文件
    f.close()


def format_num(value):
    value = str(value)
    if len(value) < 2:
        return '0%s' % value
    return '%s' % value


def str2date(s, fmt='%Y-%m-%d'):
    return DT.datetime.strptime(s, fmt).date()


def date2str(d, fmt='%Y-%m-%d'):
    return d.strftime(fmt)


def tempstr2int(c):
    return int(c.replace('℃', ''))


def write(years, b, c, city="北京"):
    cls = MongoDBHelper()
    data_list = cls.select_all_collection(collection_name='history_weather', search_col={"city": city}
                                          , sort_col="date", sort="desc"
                                          )
    for data in data_list:
        data['time'] = str2date(data['date'])

    # 取现在日期
    today = DT.datetime.now()
    # 取20天前日期
    week_ago = (today - DT.timedelta(days=b[0])).date()

    # 20天后
    week_pre = (today + DT.timedelta(days=b[1])).date()

    if years[0] == 0:
        start_year = today.year
    else:
        start_year = today.year - 1

    if years[1] == 0:
        end_year = today.year
    else:
        end_year = today.year - 1

    if b[0] > 0 and b[1] == 0:
        start_month = format_num(week_ago.month)
        start_day = format_num(week_ago.day)

        start_date = f'{start_day}/{start_month}/{start_year}'
        end_date = f'{format_num(today.day)}/{format_num(today.month)}/{end_year}'

    if b[0] == 0 and b[1] > 0:
        end_month = format_num(week_pre.month)
        end_day = format_num(week_pre.day)

        start_date = f'{format_num(today.day)}/{format_num(today.month)}/{start_year}'
        end_date = f'{end_day}/{end_month}/{end_year}'

    print(start_date, end_date)

    res = []
    for data in data_list:

        if str2date(start_date, fmt='%d/%m/%Y') <= data['time'] <= str2date(end_date, fmt='%d/%m/%Y'):
            # print(data)

            item = {'Time': date2str(data['time'], fmt='%d/%m/%Y'),
                    'Ave_t': (tempstr2int(data['high']) + tempstr2int(data['low'])) / 2,
                    'Max_t': tempstr2int(data['high']),
                    'Min_t': tempstr2int(data['low']),
                    'Prec': data['jyl'],
                    # 'SLpress': '',
                    # 'Winddir': re.findall(r'(.*)风(\d+)级', data['fl'])[0][0],
                    # 'Windsp': re.findall(r'(.*)风(\d+)级', data['fl'])[0][1],
                    # 'Cloud': ''
                    }
            print(item)
            res.append(item)
    pd.DataFrame(res).to_csv(c, index=False)


if __name__ == '__main__':
    # 用近几年的数据做训练集
    # 如 [1,0], [20, 0]就是用2023年的今天的30天前到2023年的今天数据做训练集
    # 写入csv
    write([1, 0], [30, 0], "weather_train_train.csv")
