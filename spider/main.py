from Model import LinearRegressionModel, RandomForestRegressorModel
import joblib
import matplotlib.pyplot as plt
import datetime as DT


if __name__ == '__main__':
    # 城市id  广州59287 深圳59493 北京54511  上海58362
    # 如果是其他城市id 可以在"http://www.meteomanz.com/"上获取
    # r = RandomForestRegressorModel()
    r = LinearRegressionModel(city='深圳')

    # 训练并保存模型并返回MAE
    print("MAE:", r[0])
    # 读取保存的模型
    model = joblib.load('Model.pkl')

    # 最终预测结果
    preds = model.predict(r[1])

    # 打印结果到控制台
    print("未来7天预测")
    print(preds)
    all_ave_t = []
    all_high_t = []
    all_low_t = []
    for a in range(1, 7):
        today = DT.datetime.now()
        time = (today + DT.timedelta(days=a)).date()
        print(time.year, '/', time.month, '/', time.day,
              ': 平均气温', preds[a][0],
              '最高气温', preds[a][1],
              '最低气温', preds[a][2],
              "降雨量", preds[a][3])
        all_ave_t.append(preds[a][0])
        all_high_t.append(preds[a][1])
        all_low_t.append(preds[a][2])

        if time.month < 10:
            month = '0{}'.format(time.month)
        else:
            month = '{}'.format(time.month)

        if time.day < 10:
            day = '0{}'.format(time.day)
        else:
            day = '{}'.format(time.day)

        if preds[a][3] < 0:
            jyl = 0
        else:
            jyl = preds[a][3]

        item = {'date': str(time.year) + '-' + month + '-'+ day,
                'high':  preds[a][1],
                'low': preds[a][2],
                'temp': preds[a][0],
                'jyl': preds[a][3]
        }

    temp = {"ave_t": all_ave_t, "high_t": all_high_t, "low_t": all_low_t}
    # 绘画折线图
    plt.plot(range(1, 7), temp["ave_t"], color="green", label="ave_t")
    plt.plot(range(1, 7), temp["high_t"], color="red", label="high_t")
    plt.plot(range(1, 7), temp["low_t"], color="blue", label="low_t")
    plt.legend()  # 显示图例
    plt.ylabel("Temperature(°C)")
    plt.xlabel("day")
    # 显示
    plt.show()
