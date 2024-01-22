###python天气网部署手册

##部署环境
    windows版本：10
    python版本：3.7
    pycharm版本：2021.3
    mongo版本：4.0

##部署流程
先pip 安装好环境依赖库 requirement.txt

pip install -r  WeatherAnalysic/requirement.txt

爬虫/模型模块 运行  WeatherAnalysic/spider/weatherSpider.py

后台运行 WeatherAnalysic/app.py

前端运行 demo.html
